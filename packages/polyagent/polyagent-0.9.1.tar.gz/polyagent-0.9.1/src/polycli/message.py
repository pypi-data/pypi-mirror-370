#!/usr/bin/env python3
"""
Unified message handling for all LLM formats.
Supports OpenAI/standard, Qwen, and Claude formats.
"""

from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timezone
import uuid
import json
from .utils.llm_client import get_llm_client


class Message:
    """
    Unified message representation that can parse and convert between formats.
    Parses any format on initialization and stores normalized data.
    """
    
    def __init__(self, data: Union[dict, str]):
        """
        Initialize from any message format.
        
        Args:
            data: Message dict in any supported format, or string content for simple messages
        """
        if isinstance(data, str):
            # Simple string becomes user message
            data = {"role": "user", "content": data}
        
        self._raw = data
        self.raw_type = self._detect_format(data)  # "standard", "qwen", "claude"
        
        # Extract fields based on format with clear branching
        if self.raw_type == "claude":
            # Claude format
            self.role = self._extract_role(data)
            self.raw_content = self._extract_raw_content(data)  # Original text without tools
            self.tools = self._extract_tools(data)
            self.metadata = self._extract_metadata(data)
            
            # Build unified content field (text + serialized tools)
            if self.raw_content and self.tools:
                # Both text and tools
                self.content = self.raw_content + "\n" + self._serialize_tools_to_content()
            elif self.raw_content:
                # Only text
                self.content = self.raw_content
            elif self.tools:
                # Only tools
                self.content = self._serialize_tools_to_content()
            else:
                # Empty message
                self.content = ""
                
        elif self.raw_type == "qwen":
            # Qwen format: handle parts array
            self.role = self._extract_role(data)
            self.raw_content = self._extract_raw_content(data)  # Text from parts (empty if function call)
            self.tools = self._extract_tools(data)  # @@@untested: Qwen tool extraction needs testing
            self.metadata = self._extract_metadata(data)
            
            # Build unified content field (text + serialized tools)
            if self.raw_content and self.tools:
                self.content = self.raw_content + "\n" + self._serialize_tools_to_content()
            elif self.raw_content:
                self.content = self.raw_content
            elif self.tools:
                self.content = self._serialize_tools_to_content()
            else:
                self.content = ""
                
        else:
            # Standard format or unknown
            self.role = self._extract_role(data)
            self.raw_content = self._extract_raw_content(data)
            self.tools = self._extract_tools(data)
            self.metadata = self._extract_metadata(data)
            
            # For standard format, raw_content IS the content (no separate tools)
            self.content = self.raw_content
    
    def _detect_format(self, data: dict) -> str:
        """Detect the format of the input message."""
        # Claude format: has 'type' and 'message' fields
        if 'type' in data and 'message' in data:
            return "claude"
        
        # Qwen format: has 'parts' field
        if 'parts' in data:
            return "qwen"
        
        # Standard format: has 'role' and 'content' (or just 'role')
        if 'role' in data:
            return "standard"
        
        # Default to standard if unclear
        return "standard"
    
    def _extract_role(self, data: dict) -> str:
        """Extract role from any format."""
        # Claude format: role is in message.role (check first as it's most specific)
        if 'message' in data and isinstance(data['message'], dict):
            role = data['message'].get('role')
            if role:
                return 'assistant' if role == 'model' else role
        
        # Direct role field (standard/qwen format)
        if 'role' in data:
            role = data['role']
            # Normalize 'model' to 'assistant'
            return 'assistant' if role == 'model' else role
        
        # Claude format: type field indicates the role
        if 'type' in data:
            msg_type = data['type']
            if msg_type in ['user', 'assistant', 'system']:
                return msg_type
            elif msg_type == 'summary':
                # Summary is Claude metadata, not a real message
                return 'summary'
            else:
                return 'user' if msg_type == 'human' else 'assistant'
        
        return 'unknown'
    
    def _extract_raw_content(self, data: dict) -> str:
        """Extract raw text content (without tools) from any format."""
        # Standard format - content is directly available
        if 'content' in data and isinstance(data['content'], str):
            return data['content']
        
        # Qwen format - text is in parts[0]['text'] ONLY
        if 'parts' in data:
            parts = data.get('parts', [])
            if parts and isinstance(parts[0], dict):
                if 'text' in parts[0]:
                    return parts[0]['text']
                # If it's a function call/response, no raw text content
                elif 'functionCall' in parts[0] or 'functionResponse' in parts[0]:
                    return ''
            # Non-dict part (shouldn't happen in normal Qwen format)
            return ''
        
        # Claude format - content is in message.content[{type: text}]
        if 'message' in data:
            message = data.get('message', {})
            content = message.get('content', [])
            
            # Handle list of content items
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text = item.get('text', '').strip()
                        if text and text != '[Request interrupted by user]':
                            text_parts.append(text)
                return '\n'.join(text_parts) if text_parts else ''
            # Handle direct string content
            elif isinstance(content, str):
                return content
        
        # Claude's direct content list format (without message wrapper)
        if 'content' in data and isinstance(data['content'], list):
            text_parts = []
            for item in data['content']:
                if isinstance(item, dict) and item.get('type') == 'text':
                    text = item.get('text', '').strip()
                    if text:
                        text_parts.append(text)
            return '\n'.join(text_parts) if text_parts else ''
        
        return ''
    
    def _extract_tools(self, data: dict) -> List[Dict[str, Any]]:
        """Extract tool use information from message based on format."""
        tools = []
        
        # Extract based on the detected format
        if self.raw_type == "claude":
            # Check for message.content list (Claude format)
            content_list = None
            if 'message' in data and isinstance(data['message'], dict):
                content_list = data['message'].get('content', [])
            elif 'content' in data and isinstance(data['content'], list):
                content_list = data['content']
            
            if content_list:
                for item in content_list:
                    if isinstance(item, dict):
                        if item.get('type') == 'tool_use':
                            tools.append({
                                'type': 'tool_use',
                                'id': item.get('id'),
                                'name': item.get('name'),
                                'input': item.get('input', {})
                            })
                        elif item.get('type') == 'tool_result':
                            tools.append({
                                'type': 'tool_result',
                                'tool_use_id': item.get('tool_use_id'),
                                'content': item.get('content', '')
                            })
        
        elif self.raw_type == "qwen":
            # @@@untested: Qwen tool extraction implementation
            # Extract from parts for Qwen format
            if 'parts' in data and isinstance(data['parts'], list):
                for part in data['parts']:
                    if isinstance(part, dict):
                        # Qwen function call format
                        if 'functionCall' in part:
                            func_call = part['functionCall']
                            tools.append({
                                'type': 'tool_use',
                                'id': func_call.get('id'),
                                'name': func_call.get('name'),
                                'input': func_call.get('args', {})
                            })
                        # Qwen function response format
                        elif 'functionResponse' in part:
                            func_resp = part['functionResponse']
                            tools.append({
                                'type': 'tool_result',
                                'tool_use_id': func_resp.get('id'),
                                'content': func_resp.get('response', '')
                            })
        
        # Standard format typically doesn't have tools
        # (tools would be in text content already)
        
        return tools
    
    def _extract_metadata(self, data: dict) -> Dict[str, Any]:
        """Extract metadata like timestamps, IDs, etc."""
        metadata = {}
        
        # Common metadata fields
        for field in ['uuid', 'sessionId', 'timestamp', 'parentUuid', 'cwd', 'id']:
            if field in data:
                metadata[field] = data[field]
        
        # Claude message ID
        if 'message' in data and isinstance(data['message'], dict):
            if 'id' in data['message']:
                metadata['message_id'] = data['message']['id']
        
        return metadata
    
    def _serialize_tools_to_content(self) -> str:
        """Serialize tools to human-readable text content."""
        text_parts = []
        
        for tool in self.tools:
            if tool['type'] == 'tool_use':
                # Format Claude tool call
                name = tool.get('name', 'unknown')
                input_data = tool.get('input', {})
                # Format input data nicely
                if input_data:
                    # For simple single-key inputs, show inline
                    if len(input_data) == 1:
                        key, value = list(input_data.items())[0]
                        text_parts.append(f"[Used tool: {name}({key}='{value}')]")
                    else:
                        text_parts.append(f"[Used tool: {name} with {input_data}]")
                else:
                    text_parts.append(f"[Used tool: {name}]")
                    
            elif tool['type'] == 'tool_result':
                # Format Claude tool result - no truncation needed
                result = tool.get('content', '')
                text_parts.append(f"[Tool result: {result}]")
            
            # @@@fragile: When Qwen tools are added to _extract_tools(), handle them here
            # elif tool['type'] == 'qwen_function_call':
            #     # Format Qwen function call when implemented
            #     pass
        
        return '\n'.join(text_parts) if text_parts else ""
    
    # Format conversions
    def to_standard(self) -> dict:
        """Convert to OpenAI/standard format: {"role": "...", "content": "..."}"""
        return {
            "role": self.role,
            "content": self.content
        }
    
    def to_qwen(self) -> dict:
        """Convert to Qwen format: {"role": "...", "parts": [{"text": "..."}]}"""
        # If already in Qwen format, return the raw data
        if self.raw_type == "qwen":
            return self._raw
        
        # Map assistant to model for Qwen
        role = 'model' if self.role == 'assistant' else self.role
        return {
            "role": role,
            "parts": [{"text": self.content}]
        }
    
    def to_claude(self, session_id: Optional[str] = None, parent_uuid: Optional[str] = None, cwd: Optional[str] = None) -> dict:
        """
        Convert to Claude format with full message wrapper.
        
        Args:
            session_id: Session ID for conversation threading
            parent_uuid: UUID of parent message for conversation tree
            cwd: Working directory for the message
        """
        # If already in Claude format, return the raw data
        if self.raw_type == "claude":
            return self._raw
        
        import os
        from datetime import datetime, timezone
        
        # Generate defaults if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        now_iso = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        msg_uuid = str(uuid.uuid4())
        
        # Build content array
        content = []
        
        # Add text content if present
        if self.content:
            content.append({"type": "text", "text": self.content})
        
        # Add tool uses/results
        for tool in self.tools:
            if tool['type'] == 'tool_use':
                content.append({
                    "type": "tool_use",
                    "id": tool.get('id', f"toolu_{uuid.uuid4().hex[:8]}"),
                    "name": tool.get('name', 'unknown'),
                    "input": tool.get('input', {})
                })
            elif tool['type'] == 'tool_result':
                content.append({
                    "type": "tool_result",
                    "tool_use_id": tool.get('tool_use_id'),
                    "content": tool.get('content', '')
                })
        
        # Build message body
        message_body = {
            "role": self.role,
            "content": content
        }
        
        # Add message ID for assistant messages
        if self.role == 'assistant' and 'message_id' in self.metadata:
            message_body['id'] = self.metadata['message_id']
        elif self.role == 'assistant':
            message_body['id'] = f"msg_{uuid.uuid4().hex[:8]}"
        
        # Build full message wrapper
        message = {
            "parentUuid": parent_uuid,
            "type": self.role,
            "message": message_body,
            "uuid": self.metadata.get('uuid', msg_uuid),
            "sessionId": session_id,
            "timestamp": self.metadata.get('timestamp', now_iso)
        }
        
        # Add cwd for user messages
        if self.role == 'user':
            message['cwd'] = cwd if cwd else os.getcwd()
        
        return message
    
    # Utility properties
    @property
    def is_user(self) -> bool:
        return self.role == "user"
    
    @property
    def is_assistant(self) -> bool:
        return self.role in ("assistant", "model")
    
    @property
    def is_system(self) -> bool:
        return self.role == "system"
    
    def merge_with(self, other: 'Message') -> 'Message':
        """Merge with another message (for consecutive user messages)."""
        if self.role != other.role:
            raise ValueError(f"Cannot merge messages with different roles: {self.role} vs {other.role}")
        
        # Create merged content
        merged_content = self.content
        if other.content:
            if merged_content:
                merged_content += "\n" + other.content
            else:
                merged_content = other.content
        
        # Merge tools
        merged_tools = self.tools + other.tools
        
        # Merge metadata (prefer newer)
        merged_metadata = {**self.metadata, **other.metadata}
        
        # Create new merged message
        merged_data = {
            "role": self.role,
            "content": merged_content
        }
        
        result = Message(merged_data)
        result.tools = merged_tools
        result.metadata = merged_metadata
        
        return result
    
    def __str__(self) -> str:
        """String representation shows role and content preview."""
        content_preview = self.content[:100] + "..." if len(self.content) > 100 else self.content
        return f"Message({self.role}: {content_preview})"
    
    def __repr__(self) -> str:
        """Debug representation."""
        return f"Message(role={self.role}, format={self.raw_type}, content_len={len(self.content)}, tools={len(self.tools)})"
    
    def estimate_tokens(self) -> int:
        """Quick & dirty token estimate based on content length.
        Approximation: ~4 characters per token for most models."""
        return len(self.content) // 4 if self.content else 0


class MessageList:
    """
    Container for multiple messages with batch operations.
    """
    
    def __init__(self, messages: Optional[List[Union[dict, Message]]] = None):
        """
        Initialize with list of message dicts or Message objects.
        
        Args:
            messages: List of message dicts or Message objects
        """
        if messages is None:
            self.messages = []
        else:
            # Convert to Message objects and skip summary messages
            self.messages = []
            for msg in messages:
                message_obj = msg if isinstance(msg, Message) else Message(msg)
                # Skip Claude summary messages - they're metadata, not conversation
                if message_obj.role != 'summary':
                    self.messages.append(message_obj)
    
    def _merge_consecutive_users(self, messages: List[Message]) -> List[Message]:
        """Merge consecutive user messages in a list. Used for format conversion only."""
        if len(messages) < 2:
            return messages
        
        merged = []
        i = 0
        while i < len(messages):
            current = messages[i]
            
            # If current is user, look ahead for more users to merge
            if current.is_user:
                merged_msg = current
                j = i + 1
                while j < len(messages) and messages[j].is_user:
                    # Merge consecutive user message
                    merged_msg = merged_msg.merge_with(messages[j])
                    j += 1
                merged.append(merged_msg)
                i = j  # Skip the merged messages
            else:
                # Not a user message, just add it
                merged.append(current)
                i += 1
        
        return merged
    
    def add_user_message(self, text: str, position: str = "end", cwd: Optional[str] = None):
        """
        Add a user message. No merging - preserve as separate message.
        Messages are the single source of truth.
        
        Args:
            text: The user message text
            position: "start" or "end" (default: "end")
            cwd: Working directory for Claude format
        """
        new_msg = Message({"role": "user", "content": text})
        
        if position == "end":
            self.messages.append(new_msg)
        elif position == "start":
            self.messages.insert(0, new_msg)
    
    def add_message(self, message: Union[dict, Message]):
        """Add a message to the list."""
        if isinstance(message, dict):
            message = Message(message)
        self.messages.append(message)
    
    def to_format(self, format: str, **kwargs) -> List[dict]:
        """
        Convert all messages to specified format.
        
        Args:
            format: "standard", "qwen", or "claude"
            **kwargs: Additional arguments:
                - merge_consecutive: If True, merge consecutive users (for Qwen compatibility)
                - session_id, cwd: For Claude format
        
        Returns:
            List of message dicts in specified format
        """
        # Get messages to convert
        messages_to_convert = self.messages
        
        # For Qwen, merge consecutive users if needed
        if format == "qwen" and kwargs.get('merge_consecutive', True):
            messages_to_convert = self._merge_consecutive_users(messages_to_convert)
        
        result = []
        
        if format == "standard":
            for msg in messages_to_convert:
                result.append(msg.to_standard())
        elif format == "qwen":
            for msg in messages_to_convert:
                result.append(msg.to_qwen())
        elif format == "claude":
            # Use the EXACT logic from fake_session_advanced.py that WORKS
            from datetime import datetime, timezone
            from pathlib import Path
            
            session_id = kwargs.get('session_id', str(uuid.uuid4()))
            cwd = kwargs.get('cwd', str(Path.cwd()))
            
            base_time = datetime(2025, 8, 16, 12, 0, 0, 0, timezone.utc)
            user_count = 0
            assistant_count = 0
            last_user_uuid = None
            last_assistant_uuid = None
            
            for i, msg in enumerate(messages_to_convert):
                minutes = i // 60
                seconds = i % 60
                timestamp = base_time.replace(minute=minutes, second=seconds).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                
                if msg.role == 'user':
                    user_count += 1
                    user_uuid = f"u{user_count}"
                    
                    # Parent is the previous message (could be user or assistant)
                    if i == 0:
                        parent_uuid = None
                    elif messages_to_convert[i-1].role == 'assistant':
                        parent_uuid = last_assistant_uuid
                    else:
                        # Previous is also a user - chain them!
                        parent_uuid = last_user_uuid
                    
                    # Build content array
                    content = []
                    
                    # Add text content if present
                    if msg.raw_type == "claude":
                        # Claude message - use raw_content (text only), tools will be added separately
                        raw_text = msg.raw_content if hasattr(msg, 'raw_content') else ""
                    else:
                        # Non-Claude message - use full content (includes serialized tools as text)
                        raw_text = msg.content
                    
                    if raw_text and raw_text.strip():
                        content.append({"type": "text", "text": raw_text})
                    
                    # Add tool results if present (only for Claude-origin messages)
                    if msg.raw_type == "claude":
                        for tool in msg.tools:
                            if tool['type'] == 'tool_result':
                                content.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool.get('tool_use_id'),
                                    "content": tool.get('content', '')
                                })
                    
                    # Add placeholder for empty messages to preserve parent chain
                    if not content:
                        content.append({"type": "text", "text": "[Empty response]"})
                    
                    claude_msg = {
                        "parentUuid": parent_uuid,
                        "type": "user",
                        "message": {
                            "role": "user",
                            "content": content
                        },
                        "uuid": user_uuid,
                        "sessionId": session_id,
                        "timestamp": timestamp,
                        "cwd": cwd
                    }
                    last_user_uuid = user_uuid
                    result.append(claude_msg)
                    
                elif msg.role == 'assistant':
                    assistant_count += 1
                    assistant_uuid = f"a{assistant_count}"
                    
                    # Parent logic from fake_session_advanced.py
                    if i > 0 and messages_to_convert[i-1].role == 'assistant':
                        # Consecutive assistant message - parent is previous assistant
                        parent_uuid = last_assistant_uuid
                    else:
                        # Normal case - parent is last user
                        parent_uuid = last_user_uuid
                    
                    fake_msg_id = f"fake_msg_{assistant_count}"
                    
                    # Build content array
                    content = []
                    
                    # Add text content if present
                    if msg.raw_type == "claude":
                        # Claude message - use raw_content (text only), tools will be added separately
                        raw_text = msg.raw_content if hasattr(msg, 'raw_content') else ""
                    else:
                        # Non-Claude message - use full content (includes serialized tools as text)
                        raw_text = msg.content
                    
                    if raw_text and raw_text.strip():
                        content.append({"type": "text", "text": raw_text})
                    
                    # Add tool uses if present (only for Claude-origin messages)
                    if msg.raw_type == "claude":
                        for tool in msg.tools:
                            if tool['type'] == 'tool_use':
                                content.append({
                                    "type": "tool_use",
                                    "id": tool.get('id', f"toolu_{assistant_count}"),
                                    "name": tool.get('name', 'unknown'),
                                    "input": tool.get('input', {})
                                })
                    
                    # Add placeholder for empty messages to preserve parent chain
                    if not content:
                        content.append({"type": "text", "text": "[Empty response]"})
                    
                    claude_msg = {
                        "parentUuid": parent_uuid,
                        "type": "assistant",
                        "message": {
                            "id": fake_msg_id,
                            "role": "assistant",
                            "content": content
                        },
                        "uuid": assistant_uuid,
                        "sessionId": session_id,
                        "timestamp": timestamp
                    }
                    last_assistant_uuid = assistant_uuid
                    result.append(claude_msg)
        else:
            raise ValueError(f"Unknown format: {format}")
        
        return result
    
    def to_raw_list(self) -> List[dict]:
        """Return messages in their original raw format."""
        return [msg._raw for msg in self.messages]
    
    def compact(self, model: str = "glm-4.5", debug: bool = False) -> 'MessageList':
        """
        Compact messages while preserving context.
        
        Args:
            model: Model to use for generating summary
            debug: Enable debug output
        
        Returns:
            New MessageList with compacted messages
        """
        if len(self.messages) < 4:
            if debug:
                print(f"[DEBUG] compact: Too few messages ({len(self.messages)}) to compact")
            return self  # Return self, don't recreate
        
        # Calculate split point (first half)
        split_point = len(self.messages) // 2
        first_half = self.messages[:split_point]
        second_half = self.messages[split_point:]
        
        if debug:
            print(f"[DEBUG] compact: Compacting {len(first_half)} messages, keeping {len(second_half)}")
        
        # Format first half as conversation text for LLM
        conversation_text = []
        for msg in first_half:
            role_label = "User" if msg.is_user else "Assistant"
            # Use full content - no truncation
            full_content = msg.content if msg.content else "[Empty message]"
            conversation_text.append(f"{role_label}: {full_content}")
        
        # Use LLM to generate summary
        try:
            # Prepare prompt for summarization using Claude's comprehensive compact prompt
            prompt = f"""Your task is to create a detailed summary of the conversation so far, paying close attention to the user's explicit requests and your previous actions.
This summary should be thorough in capturing technical details, code patterns, and architectural decisions that would be essential for continuing development work without losing context.

Before providing your final summary, wrap your analysis in <analysis> tags to organize your thoughts and ensure you've covered all necessary points. In your analysis process:

1. Chronologically analyze each message and section of the conversation. For each section thoroughly identify:
   - The user's explicit requests and intents
   - Your approach to addressing the user's requests
   - Key decisions, technical concepts and code patterns
   - Specific details like:
     - file names
     - full code snippets
     - function signatures
     - file edits

- Errors that you ran into and how you fixed them
- Pay special attention to specific user feedback that you received, especially if the user told you to do something differently.

2. Double-check for technical accuracy and completeness, addressing each required element thoroughly.

Your summary should include the following sections:

1. Primary Request and Intent: Capture all of the user's explicit requests and intents in detail
2. Key Technical Concepts: List all important technical concepts, technologies, and frameworks discussed.
3. Files and Code Sections: Enumerate specific files and code sections examined, modified, or created. Pay special attention to the most recent messages and include full code snippets where applicable and include a summary of why this file read or edit is important.
4. Errors and fixes: List all errors that you ran into, and how you fixed them. Pay special attention to specific user feedback that you received, especially if the user told you to do something differently.
5. Problem Solving: Document problems solved and any ongoing troubleshooting efforts.
6. All user messages: List ALL user messages that are not tool results. These are critical for understanding the users' feedback and changing intent.
7. Pending Tasks: Outline any pending tasks that you have explicitly been asked to work on.
8. Current Work: Describe in detail precisely what was being worked on immediately before this summary request, paying special attention to the most recent messages from both user and assistant. Include file names and code snippets where applicable.
9. Optional Next Step: List the next step that you will take that is related to the most recent work you were doing. IMPORTANT: ensure that this step is DIRECTLY in line with the user's explicit requests, and the task you were working on immediately before this summary request. If your last task was concluded, then only list next steps if they are explicitly in line with the users request. Do not start on tangential requests without confirming with the user first.
   If there is a next step, include direct quotes from the most recent conversation showing exactly what task you were working on and where you left off. This should be verbatim to ensure there's no drift in task interpretation.

# Conversation to summarize

{chr(10).join(conversation_text)}

Please provide your summary based on the conversation above, following the required structure and ensuring precision and thoroughness in your response."""
            
            if debug:
                print(f"[DEBUG] compact: Calling {model} to summarize {len(first_half)} messages")
            
            # Get LLM client and generate summary
            llm_client, actual_model = get_llm_client(model)
            
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            response = llm_client.client.chat.completions.create(
                model=actual_model,
                messages=messages
            )
            
            summary_text = response.choices[0].message.content or "Failed to generate summary"
            
            if debug:
                print(f"[DEBUG] compact: Generated summary of {len(summary_text)} chars")
                
        except Exception as e:
            if debug:
                print(f"[DEBUG] compact: LLM call failed: {e}, falling back to concatenation")
            # Fallback to simple concatenation if LLM fails
            summary_text = "[CONVERSATION SUMMARY - Concatenated]\n" + "\n".join(conversation_text)
        
        # Prepend label to summary
        summary_text = f"[CONVERSATION SUMMARY via {model}]\n{summary_text}"
        
        # Create new MessageList with summary + second half
        new_messages = MessageList()
        new_messages.add_user_message(summary_text, position="end")
        # Preserve second half messages by re-adding them (preserves their raw format)
        for msg in second_half:
            # Pass the raw format to preserve source
            if hasattr(msg, '_raw') and msg._raw:
                new_messages.add_message(msg._raw)
            else:
                new_messages.add_message(msg)
        
        if debug:
            print(f"[DEBUG] compact: Reduced from {len(self.messages)} to {len(new_messages)} messages")
        
        return new_messages
    
    def normalize_for_display(self) -> List[dict]:
        """Normalize messages for UI display."""
        normalized = []
        for msg in self.messages:
            # Use content which already includes serialized tools
            norm_msg = {
                'role': msg.role,
                'content': msg.content if msg.content else ""
            }
            
            # Add metadata if present
            if msg.metadata:
                for key, value in msg.metadata.items():
                    if key not in norm_msg:
                        norm_msg[key] = value
            
            # Don't add tools again - they're already in content!
            # Adding raw_type for debugging
            norm_msg['_format'] = msg.raw_type if hasattr(msg, 'raw_type') else 'unknown'
            
            normalized.append(norm_msg)
        
        return normalized
    
    def __len__(self) -> int:
        return len(self.messages)
    
    def __iter__(self):
        return iter(self.messages)
    
    def __getitem__(self, index):
        return self.messages[index]
    
    def __str__(self) -> str:
        return f"MessageList({len(self.messages)} messages)"
    
    def __repr__(self) -> str:
        roles = [msg.role for msg in self.messages[-5:]]  # Last 5 message roles
        return f"MessageList(count={len(self.messages)}, recent_roles={roles})"
    
    def estimate_tokens(self) -> int:
        """Sum of all message tokens."""
        return sum(msg.estimate_tokens() for msg in self.messages)