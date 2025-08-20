#!/usr/bin/env python3
"""
PolyAgent: A unified agent that works with all backends.
Built on single source of truth (MessageList) with format conversion.
"""

import json
import subprocess
import os
import sys
from pathlib import Path
import shutil
import uuid
from typing import Optional, Type, Callable
from pydantic import BaseModel
from .message import MessageList, Message
from .adapters import RunResult
from .utils.llm_client import get_llm_client
from .utils.serializers import default_json_serializer
import tempfile
import hashlib
import copy
from .orchestration import pattern


@pattern
def tracked_run(agent, prompt, **run_kwargs):
    """Pattern wrapper for tracked agent.run() calls."""
    # Call run without tracked to avoid recursion
    return agent.run(prompt, tracked=False, **run_kwargs)


class PolyAgent:
    """
    Unified agent that works with all backends through a single interface.
    
    Core principle: MessageList is the single source of truth.
    All format conversions happen only when sending to specific backends.
    """
    
    def __init__(self, debug=False, system_prompt=None, cwd=None, id=None, max_tokens=None):
        """
        Initialize PolyAgent.
        
        Args:
            debug: Enable debug output
            system_prompt: Default system prompt for all runs
            cwd: Working directory for CLI tools
            id: Unique identifier for the agent
            max_tokens: Default token limit for all runs
        """
        # Single source of truth for messages
        self.messages = MessageList()
        
        # Configuration
        self.debug = debug
        self.system_prompt = system_prompt
        self.cwd = str(Path(cwd)) if cwd else os.getcwd()
        self.id = id  # None if not provided
        self.max_tokens = max_tokens  # Default limit for all runs
        
        # Detect available CLI tools
        self._detect_cli_tools()
    
    def _detect_cli_tools(self):
        """Detect which CLI tools are available."""
        self._claude_cmd = shutil.which('claude')
        self._qwen_cmd = shutil.which('qwen')
        
        if self.debug:
            print(f"[DEBUG] Claude CLI available: {bool(self._claude_cmd)}")
            print(f"[DEBUG] Qwen CLI available: {bool(self._qwen_cmd)}")
    
    def add_user_message(self, user_text: str, position: str = "end"):
        """
        Add a user message to the conversation.
        
        Args:
            user_text: The message content
            position: Where to add the message ("start" or "end")
        """
        self.messages.add_user_message(user_text, position)
        
        if self.debug:
            print(f"[DEBUG] Added user message. Total messages: {len(self.messages)}")
    
    def run(self, 
            prompt: str,
            model: Optional[str] = None,
            cli: Optional[str] = None,
            system_prompt: Optional[str] = None,
            ephemeral: bool = False,
            schema_cls: Optional[Type[BaseModel]] = None,
            memory_serializer: Optional[Callable[[BaseModel], str]] = None,
            max_tokens: Optional[int] = None,
            tracked: bool = False,
            **kwargs) -> RunResult:
        """
        Run a prompt with automatic backend selection and token management.
        
        Args:
            prompt: The prompt to execute
            model: Model name (e.g., "gpt-4", "claude-3", "glm-4.5")
            cli: Backend to use:
                - "claude-code": Use Claude CLI
                - "qwen-code": Use Qwen CLI  
                - "mini-swe": Use Mini-SWE
                - "no-tools": Use direct API without tools
                - None: Auto-detect based on model/availability
            system_prompt: System prompt for this run
            ephemeral: If True, don't save to message history
            schema_cls: Pydantic model for structured output
            memory_serializer: Custom serializer for structured output
            max_tokens: Token limit for this run (overrides agent default)
            tracked: If True, wrap this call in a pattern for orchestration tracking
            **kwargs: Additional backend-specific parameters
        
        Returns:
            RunResult with the response
        """
        # If tracked, delegate to the pattern-wrapped version
        if tracked:
            return tracked_run(
                self, prompt,
                model=model, cli=cli, system_prompt=system_prompt,
                ephemeral=ephemeral, schema_cls=schema_cls,
                memory_serializer=memory_serializer, max_tokens=max_tokens,
                **kwargs
            )
        
        # Determine effective token limit
        # @@@qwen-session-limit: Default 100k but Qwen is limited to 80k globally in __init__.py
        effective_limit = max_tokens or self.max_tokens or 100000
        
        # Pre-emptive compaction check (before routing to backend)
        current_tokens = self.messages.estimate_tokens()
        if current_tokens > effective_limit * 0.8:  # 80% threshold
            if self.debug:
                print(f"[DEBUG] Pre-emptive compaction: {current_tokens} tokens > 80% of {effective_limit} limit")
            self.compact_messages(model or "glm-4.5")
            current_tokens = self.messages.estimate_tokens()  # Update count
        
        # Determine which backend to use
        backend = self._determine_backend(cli, model)
        
        if self.debug:
            print(f"[DEBUG] PolyAgent routing to backend: {backend}")
        
        # Try the request with retry on token-related failures
        max_retries = 2  # Try original + 1 retry after compaction
        for attempt in range(max_retries):
            # Route to backend
            if backend == "claude-code":
                result = self._run_claude_cli(prompt, system_prompt, ephemeral)
            elif backend == "qwen-code":
                result = self._run_qwen_cli(prompt, model or "glm-4.5", system_prompt, ephemeral)
            elif backend == "mini-swe":
                result = self._run_mini_swe(prompt, model or "glm-4.5", system_prompt, ephemeral, schema_cls, memory_serializer)
            else:  # no-tools
                result = self._run_api(prompt, model or "glm-4.5", system_prompt, ephemeral, schema_cls, memory_serializer)
            
            # Check if we should retry with compaction
            if attempt == 0 and self._should_retry_with_compact(result, current_tokens, effective_limit):
                if self.debug:
                    print(f"[DEBUG] Attempting compact-and-retry due to suspected token limit issue")
                    print(f"[DEBUG] Current tokens: {current_tokens}, Limit: {effective_limit}")
                
                # Save state before compaction
                original_messages = self.messages.messages[:]
                
                try:
                    self.compact_messages(model or "glm-4.5")
                    new_tokens = self.messages.estimate_tokens()
                    if self.debug:
                        print(f"[DEBUG] Compacted from {current_tokens} to {new_tokens} tokens")
                    current_tokens = new_tokens
                    # Continue to next iteration for retry
                    continue
                except Exception as e:
                    # Restore on failure
                    self.messages.messages = original_messages
                    if self.debug:
                        print(f"[DEBUG] Compaction failed, returning original error: {e}")
                    # Fall through to return original result
            
            # Return result (either success or final failure)
            return result
        
        # Should never reach here, but just in case
        return result
    
    def _determine_backend(self, cli: Optional[str], model: Optional[str]) -> str:
        """
        Determine which backend to use.
        
        Priority:
        1. Explicit cli parameter
        2. Model-based detection
        3. Available CLI tools
        4. Default to API
        """
        # Explicit CLI specification takes precedence
        if cli:
            return cli
        
        # Model-based detection
        if model:
            model_lower = model.lower()
            if "claude" in model_lower:
                # Claude model - use Claude CLI if available
                if self._claude_cmd:
                    return "claude-code"
                else:
                    return "no-tools"
            else:
                # Non-Claude model - default to no-tools
                return "no-tools"
        
        # No model specified - use available CLI tools
        if self._claude_cmd:
            return "claude-code"
        elif self._qwen_cmd:
            return "qwen-code"
        else:
            return "no-tools"
    
    def _run_claude_cli(self, prompt: str, system_prompt: Optional[str], ephemeral: bool) -> RunResult:
        """Run using Claude CLI."""
        if self.debug:
            print("[DEBUG] Running with Claude CLI")
        
        if not self._claude_cmd:
            return RunResult({"status": "error", "message": "Claude CLI not found"})
        
        # Prepare session management
        claude_projects_dir = Path.home() / ".claude" / "projects"
        cwd_encoded = self._encode_path(self.cwd)
        session_dir = claude_projects_dir / cwd_encoded
        
        # If we have messages, we need to resume (even for ephemeral)
        resume_id = None
        if len(self.messages) > 0:
            last_msg = self.messages[-1]
            if hasattr(last_msg, 'metadata') and last_msg.metadata:
                resume_id = last_msg.metadata.get('sessionId')
            if not resume_id:
                # Generate a fake session ID for loaded conversations
                import uuid
                resume_id = str(uuid.uuid4())
                if self.debug:
                    print(f"[DEBUG] Generated resume ID for loaded conversation: {resume_id}")
        
        # Build command
        cmd = [self._claude_cmd, prompt, '-p', '--output-format', 'json', '--dangerously-skip-permissions']
        
        # Add system prompt
        effective_system = system_prompt or self.system_prompt
        if effective_system:
            cmd.extend(['--system-prompt', effective_system])
        
        session_file = None
        try:
            if resume_id:
                # Resume conversation - create session file with history
                if self.debug:
                    print(f"[DEBUG] Resuming session: {resume_id}")
                
                session_dir.mkdir(parents=True, exist_ok=True)
                session_file = session_dir / f"{resume_id}.jsonl"
                
                # Convert messages to Claude format
                claude_messages = self.messages.to_format("claude", session_id=resume_id, cwd=self.cwd)
                
                # Write session file
                with open(session_file, 'w', encoding='utf-8') as f:
                    for msg in claude_messages:
                        f.write(json.dumps(msg, ensure_ascii=False) + '\n')
                
                if self.debug:
                    print(f"[DEBUG] Wrote {len(claude_messages)} messages to resume file")
                    print(f"[DEBUG] Current messages in memory: {len(self.messages)}")
                
                cmd.extend(['--resume', resume_id])
            
            # Run command
            if self.debug:
                print(f"[DEBUG] Running command: {' '.join(cmd)}")
                print(f"[DEBUG] Session file exists: {session_file.exists() if session_file else 'No session file'}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.cwd,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                response_data = json.loads(result.stdout)
                
                # Load updated conversation if not ephemeral
                if not ephemeral:
                    new_session_id = response_data.get('session_id')
                    if new_session_id:
                        new_session_file = session_dir / f"{new_session_id}.jsonl"
                        if new_session_file.exists():
                            # Load messages from Claude's session file, filtering out summaries
                            raw_messages = []
                            with open(new_session_file, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if line.strip():
                                        msg = json.loads(line)
                                        # Filter out summary messages at load time
                                        if msg.get('type') != 'summary':
                                            raw_messages.append(msg)
                                        elif self.debug:
                                            print(f"[DEBUG] Filtered out summary message during load")
                            
                            # Extract only NEW messages from Claude response
                            # Count existing messages before the Claude call
                            existing_count = len(self.messages)
                            
                            if self.debug:
                                print(f"[DEBUG] Messages before loading Claude response: {existing_count}")
                                print(f"[DEBUG] Total messages in Claude session file (after filtering): {len(raw_messages)}")
                            
                            # Only append messages that are NEW (after our existing count)
                            if len(raw_messages) > existing_count:
                                new_messages_only = raw_messages[existing_count:]
                                if self.debug:
                                    print(f"[DEBUG] Adding {len(new_messages_only)} new messages from Claude")
                                
                                # Append each new message incrementally, filtering out "No response requested."
                                for msg in new_messages_only:
                                    # Create Message object first to properly extract content
                                    message_obj = Message(msg)
                                    
                                    # Skip assistant messages that are just "No response requested."
                                    if (message_obj.role == 'assistant' and 
                                        message_obj.content.strip() == 'No response requested.'):
                                        if self.debug:
                                            print(f"[DEBUG] Filtered out 'No response requested.' message")
                                        continue
                                    
                                    # Add the Message object directly (add_message accepts it)
                                    self.messages.add_message(message_obj)
                            else:
                                if self.debug:
                                    print(f"[DEBUG] No new messages to add from Claude response")
                            
                            if self.debug:
                                print(f"[DEBUG] Total messages after Claude response: {len(self.messages)}")
                            
                            # Clean up
                            new_session_file.unlink()
                else:
                    # Ephemeral mode - keep existing messages, don't add new ones
                    if self.debug:
                        print(f"[DEBUG] Ephemeral mode - keeping {len(self.messages)} existing messages")
                
                # Return result
                return RunResult({
                    "result": response_data.get('result'),
                    "session_id": response_data.get('session_id'),
                    "model": "claude-code",
                    "_claude_metadata": response_data
                })
            else:
                return RunResult({
                    "status": "error",
                    "message": f"Claude CLI failed: {result.stderr}"
                })
        
        finally:
            # Clean up session file
            if session_file and session_file.exists():
                if self.debug:
                    print(f"[DEBUG] NOT deleting session file for inspection: {session_file}")
                else:
                    session_file.unlink()
    
    def _run_qwen_cli(self, prompt: str, model: str, system_prompt: Optional[str], ephemeral: bool) -> RunResult:
        """Run using Qwen CLI."""
        if self.debug:
            print(f"[DEBUG] Running with Qwen CLI, model: {model}")
        
        if not self._qwen_cmd:
            return RunResult({"status": "error", "message": "Qwen CLI not found"})
        
        # Get model configuration
        from .utils.model_config import get_model_config
        model_cfg = get_model_config().get_model(model)
        if not model_cfg:
            return RunResult({"status": "error", "message": f"Model '{model}' not configured"})
        
        # Prepare messages for checkpoint
        messages_to_save = []
        effective_system = system_prompt or self.system_prompt
        
        if len(self.messages) > 0:
            # Convert existing messages to standard format
            messages_to_save = self.messages.to_format("standard")
        
        # Inject system prompt if needed
        if effective_system:
            system_user = {"role": "user", "content": f"[System]: {effective_system}"}
            system_assistant = {"role": "assistant", "content": "I understand and will follow these instructions."}
            
            # Check if we need to replace or inject
            if len(messages_to_save) >= 2 and "[System]:" in str(messages_to_save[0].get('content', '')):
                messages_to_save[0] = system_user
                messages_to_save[1] = system_assistant
            else:
                messages_to_save = [system_user, system_assistant] + messages_to_save
        
        # Create checkpoint file if we have messages
        checkpoint_file = None
        if messages_to_save:
            # Convert to Qwen format with consecutive user merging
            temp_list = MessageList(messages_to_save)
            qwen_messages = temp_list.to_format("qwen", merge_consecutive=True)
            
            # Save checkpoint
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump(qwen_messages, f, ensure_ascii=False)
                checkpoint_file = f.name
        
        # Generate unique save tag
        save_tag = f"polycli-{uuid.uuid4().hex[:8]}"
        
        # Track what we're sending to Qwen (after merging)
        messages_sent_count = len(qwen_messages) if checkpoint_file else 0
        
        try:
            # Build command
            cmd = [
                self._qwen_cmd,
                '--save', save_tag,
                '--yolo',
                '--openai-api-key', model_cfg['api_key'],
                '--openai-base-url', model_cfg['endpoint'],
                '--model', model_cfg['model']
            ]
            
            if checkpoint_file:
                cmd.extend(['--resume', checkpoint_file])
            
            # Set environment
            env = os.environ.copy()
            env.update({
                'OPENAI_MODEL': model_cfg['model'],
                'OPENAI_API_KEY': model_cfg['api_key'],
                'OPENAI_BASE_URL': model_cfg['endpoint']
            })
            
            # Run command
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                cwd=self.cwd,
                env=env,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                # Load saved checkpoint if not ephemeral
                if not ephemeral:
                    project_hash = hashlib.sha256(self.cwd.encode()).hexdigest()
                    qwen_dir = Path.home() / ".qwen" / "tmp" / project_hash
                    saved_checkpoint = qwen_dir / f"checkpoint-{save_tag}.json"
                    
                    if saved_checkpoint.exists():
                        with open(saved_checkpoint, 'r', encoding='utf-8') as f:
                            new_messages = json.load(f)
                        
                        # Track original count before removing system prompt
                        original_new_count = len(new_messages)
                        system_removed = False
                        
                        # Remove injected system prompt if present
                        if effective_system and len(new_messages) >= 2:
                            if "[System]:" in str(new_messages[0].get('parts', [{}])[0].get('text', '')):
                                new_messages = new_messages[2:]
                                system_removed = True
                        
                        # Adjust expected count if we removed system messages
                        expected_count = messages_sent_count
                        if system_removed and messages_sent_count > 0:
                            # We sent messages WITH system, but removed it from response
                            expected_count = messages_sent_count - 2
                        
                        # Only append NEW messages (those after what we sent)
                        if self.debug:
                            print(f"[DEBUG] Checkpoint has {len(new_messages)} messages (was {original_new_count}), expected {expected_count} existing")
                        
                        if len(new_messages) > expected_count:
                            # Get only the new messages (prompt + response)
                            new_msgs_only = new_messages[expected_count:]
                            if self.debug:
                                print(f"[DEBUG] Adding {len(new_msgs_only)} new messages")
                            
                            # Add them to our MessageList
                            for msg in new_msgs_only:
                                self.messages.add_message(msg)
                        else:
                            if self.debug:
                                print(f"[DEBUG] No new messages to add")
                        
                        # Clean up
                        saved_checkpoint.unlink()
                
                # Extract last response
                last_response = result.stdout.strip()
                
                return RunResult({
                    "status": "success",
                    "message": {"role": "assistant", "content": last_response},
                    "type": "assistant"
                })
            else:
                return RunResult({
                    "status": "error",
                    "message": f"Qwen CLI failed: {result.stderr}"
                })
        
        finally:
            if checkpoint_file and os.path.exists(checkpoint_file):
                os.unlink(checkpoint_file)
    
    def _run_api(self, prompt: str, model: str, system_prompt: Optional[str], ephemeral: bool,
                 schema_cls: Optional[Type[BaseModel]], memory_serializer: Optional[Callable]) -> RunResult:
        """Run using direct API calls."""
        if self.debug:
            print(f"[DEBUG] Running with API, model: {model}")
        
        # Get LLM client
        try:
            llm_client, actual_model = get_llm_client(model)
        except Exception as e:
            return RunResult({"status": "error", "message": str(e)})
        
        # Prepare messages
        messages = []
        
        # Add system prompt
        effective_system = system_prompt or self.system_prompt
        if effective_system:
            messages.append({"role": "system", "content": effective_system})
        
        # Add conversation history (convert to standard format)
        for msg in self.messages:
            if msg.content:
                role = "assistant" if msg.role == "model" else msg.role
                messages.append({"role": role, "content": msg.content})
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        try:
            if schema_cls:
                # Structured output
                result = llm_client.chat.completions.create(
                    response_model=schema_cls,
                    model=actual_model,
                    messages=messages
                )
                
                # Serialize response
                serializer = memory_serializer or default_json_serializer
                response_text = serializer(result)
                
                # Update messages if not ephemeral
                if not ephemeral:
                    self.messages.add_message({"role": "user", "content": prompt})
                    self.messages.add_message({
                        "role": "assistant",
                        "content": f"[Structured response ({schema_cls.__name__})]\n{response_text}"
                    })
                
                return RunResult({
                    "status": "success",
                    "result": result.model_dump(),
                    "type": "structured",
                    "schema": schema_cls.__name__
                })
            else:
                # Plain text response
                result = llm_client.client.chat.completions.create(
                    model=actual_model,
                    messages=messages
                )
                
                response_content = ""
                if result and result.choices and result.choices[0].message:
                    response_content = result.choices[0].message.content or ""
                
                # Update messages if not ephemeral
                if not ephemeral:
                    self.messages.add_message({"role": "user", "content": prompt})
                    self.messages.add_message({"role": "assistant", "content": response_content})
                
                return RunResult({
                    "status": "success",
                    "message": {"role": "assistant", "content": response_content},
                    "type": "assistant"
                })
        
        except Exception as e:
            return RunResult({
                "status": "error",
                "message": f"API call failed: {str(e)}"
            })
    
    def _run_mini_swe(self, prompt: str, model: str, system_prompt: Optional[str], ephemeral: bool,
                      schema_cls: Optional[Type[BaseModel]], memory_serializer: Optional[Callable]) -> RunResult:
        """Run using Mini-SWE agent."""
        if self.debug:
            print(f"[DEBUG] Running with Mini-SWE, model: {model}")
        
        # Import Mini-SWE dependencies
        try:
            from minisweagent.agents.default import DefaultAgent
            from minisweagent.environments.local import LocalEnvironment
            from .utils.llm_client import CustomMiniSweModel
        except ImportError:
            return RunResult({
                "status": "error",
                "message": "Mini-SWE not installed"
            })
        
        # Create Mini-SWE agent
        temp_agent = DefaultAgent(
            CustomMiniSweModel(model_name=model),
            LocalEnvironment(cwd=self.cwd)
        )
        
        # Configure agent
        temp_agent.config.step_limit = 10
        if system_prompt:
            temp_agent.config.system_template = system_prompt
        
        # Prepare input with history
        if len(self.messages) > 0:
            # Convert messages to standard format
            history = []
            for msg in self.messages:
                if msg.content:
                    role = "assistant" if msg.role == "model" else msg.role
                    history.append({"role": role, "content": msg.content})
            
            # Format as conversation
            input_text = ""
            for msg in history:
                input_text += f"{msg['role']}: {msg['content']}\n"
            input_text += f"user: {prompt}"
        else:
            input_text = prompt
        
        # Run agent
        status, message = temp_agent.run(input_text)
        
        # Update messages if not ephemeral
        if not ephemeral:
            self.messages.add_message({"role": "user", "content": prompt})
            # Add agent messages (skip first two which are system messages)
            for msg in temp_agent.messages[2:]:
                self.messages.add_message(msg)
        
        return RunResult({
            "status": status,
            "message": {"role": "assistant", "content": message},
            "type": "assistant"
        })
    
    def save_state(self, file_path: str):
        """
        Save conversation state to a file in original raw formats.
        This preserves the source format of each message.
        
        Args:
            file_path: Path to save to (.json or .jsonl)
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Extract raw messages
        raw_messages = []
        for msg in self.messages:
            if hasattr(msg, '_raw') and msg._raw:
                raw_messages.append(msg._raw)
            else:
                # Fallback if no _raw field (shouldn't happen)
                raw_messages.append({"role": msg.role, "content": msg.content})
        
        # Write based on file extension
        if path.suffix == '.jsonl':
            # JSONL format (one message per line)
            with open(path, 'w', encoding='utf-8') as f:
                for msg in raw_messages:
                    f.write(json.dumps(msg, ensure_ascii=False) + '\n')
        else:
            # JSON array format
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(raw_messages, f, ensure_ascii=False, indent=2)
        
        if self.debug:
            print(f"[DEBUG] Saved {len(raw_messages)} messages to {path} (preserving original formats)")
    
    def load_state(self, file_path: str):
        """
        Load conversation state from a file.
        Auto-detects format.
        """
        path = Path(file_path)
        
        if not path.exists():
            if self.debug:
                print(f"[DEBUG] File not found: {path}")
            return
        
        # Load based on extension
        if path.suffix == '.jsonl':
            # Claude JSONL format - load all messages including tool interactions
            messages = []
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        messages.append(json.loads(line))
            
            # MessageList will handle the format conversion properly
            self.messages = MessageList(messages)
        
        else:
            # JSON format (Qwen or standard)
            with open(path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            self.messages = MessageList(messages)
        
        if self.debug:
            print(f"[DEBUG] Loaded {len(self.messages)} messages from {path}")
    
    def _encode_path(self, path_str: str) -> str:
        """Encode path for Claude session files."""
        if sys.platform == "win32" and ":" in path_str:
            drive, rest = path_str.split(":", 1)
            rest = rest.lstrip(os.path.sep)
            path_str = f"{drive}--{rest}"
        # Replace path separators with dashes, then replace underscores with dashes
        # This matches Claude CLI's own encoding behavior
        return path_str.replace(os.path.sep, '-').replace('_', '-')
    
    def _should_retry_with_compact(self, result: RunResult, token_estimate: int, limit: int) -> bool:
        """Check if we should compact and retry based on result.
        
        Args:
            result: The result from the backend
            token_estimate: Current estimated token count
            limit: Token limit
            
        Returns:
            True if we should compact and retry
        """
        # Only compact if we're using significant tokens
        if token_estimate < limit * 0.5:  # Less than 50% usage
            return False
        
        # Check if result indicates failure
        if not isinstance(result, RunResult):
            return False
        
        # Check 1: Error status
        if result.get('status') == 'error':
            return True
        
        # Check 2: Empty response (Qwen's silent failure mode)
        # This happens when Qwen fails due to token limit
        if 'message' in result:
            msg = result.get('message', {})
            if isinstance(msg, dict) and not msg.get('content', '').strip():
                if self.debug:
                    print("[DEBUG] Empty assistant response detected with high token usage")
                return True
        
        # Check 3: Placeholder for future checks
        # Could add patterns like "context length exceeded" in error messages
        
        return False
    
    def compact_messages(self, model: str = "glm-4.5"):
        """
        Compact conversation history by summarizing.
        Delegates to MessageList's compact method.
        """
        if hasattr(self.messages, 'compact'):
            self.messages = self.messages.compact(model=model, debug=self.debug)
        else:
            if self.debug:
                print("[DEBUG] MessageList doesn't support compaction")