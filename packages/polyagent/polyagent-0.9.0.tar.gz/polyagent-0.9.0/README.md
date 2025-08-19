# PolyCLI

A unified interface for stateful conversations with CLI-based AI agents.

## Installation

```bash
pip install polyagent
```

### CLI Tools Setup

**Claude Code**: Follow official Anthropic installation

**Qwen Code**: 
```bash
# Remove original version if installed
npm uninstall -g @qwen-code/qwen-code

# Install special version with --save/--resume support
npm install -g @lexicalmathical/qwen-code@0.0.6-polycli.1
```

**Mini-SWE Agent**: 
```bash
pip install mini-swe-agent
```

## Quick Start

```python
from polycli import ClaudeAgent, OpenSourceAgent

# Basic usage with Claude
agent = ClaudeAgent()
result = agent.run("What is 2+2?")
print(result.content)  # 4
print(f"Success: {result.is_success}")

# Multi-model support via models.json
result = agent.run("Explain recursion", model="gpt-4o")
if result:  # Check success
    print(result.content)

# Access Claude-specific metadata
if result.get_claude_cost():
    print(f"Cost: ${result.get_claude_cost()}")

# Structured outputs with Pydantic
from pydantic import BaseModel, Field

class MathResult(BaseModel):
    answer: int = Field(description="The numerical answer")
    explanation: str = Field(description="Step-by-step explanation")

result = agent.run("What is 15+27?", model="gpt-4o", schema_cls=MathResult)
if result.has_data():  # Check for structured data
    print(result.data['answer'])  # 42
    print(result.content)  # Formatted JSON string

# System prompts
agent_with_prompt = ClaudeAgent(system_prompt="You are a helpful Python tutor")
result = agent_with_prompt.run("Explain list comprehensions")

# Override system prompt for specific calls
result = agent.run(
    "Translate to French", 
    system_prompt="You are a French translator. Respond only in French."
)

# State persistence
agent.save_state("conversation.jsonl")
agent.load_state("conversation.jsonl")
```

## Configuration

Create `models.json` in project root:
```json
{
  "models": {
    "gpt-4o": {
      "endpoint": "https://api.openai.com/v1",
      "api_key": "sk-...",
      "model": "gpt-4o"
    }
  }
}
```

## Architecture

![PolyCLI Architecture](assets/information-edge-ui.png)

### System Components

- **Core Module**: LLM APIs management, structured output, memory compaction, and atomic agent integrations
- **Agent Persistence**: State load/save API, PromptLib, memory management, and knowledge exchange
- **Orchestration**: Session management with Pattern and Batch execution capabilities
- **Web UIs**: Both Agent Hall and Session Inspection interfaces for monitoring
- **Project Map**: Centralized agent store with pattern definitions

### Agents

**ClaudeAgent** (default)
- No model specified → Claude CLI with full tool access
- Model specified → Any LLM via models.json (single round, no tools)

**OpenSourceAgent**
- `cli="qwen-code"` → Production-ready for all tasks including code (default)
- `cli="mini-swe"` → Experimental, lightweight, suitable for testing
- `cli="no-tools"` → Direct LLM API calls without code execution (supports structured output)

### Tech Stack
- **LLM Client**: Instructor + OpenAI client (no litellm)
- **Message Formats**: Auto-conversion between Claude (JSONL), Mini-SWE (role/content), Qwen (role/parts)
- **State**: JSON/JSONL with seamless format switching

## RunResult Interface

All agent `.run()` calls return a `RunResult` object with a clean, unified interface:

```python
from polycli import OpenSourceAgent

agent = OpenSourceAgent()
result = agent.run("Calculate 5 * 8", model="gpt-4o", cli="no-tools", schema_cls=MathResult)

# Basic usage
print(result.content)        # Always a string (for display)
print(result.is_success)     # Boolean success status
if not result:               # Pythonic error checking
    print(result.error_message)

# Structured data access
if result.has_data():        # Check for structured response
    calc = result.data['calculation']  # Raw dictionary access
    answer = result.data['result']

# Metadata access
print(result.get_claude_cost())    # Cost for Claude calls
print(result.get_claude_tokens())  # Token usage details
print(result.get_session_id())     # Session tracking

# Status reports
status = agent.get_status(n_exchanges=3)  # Summarize recent work
if status:
    print(status.content)  # AI-generated status report
```

## Multi-Agent Orchestration

PolyCLI includes a powerful yet simple orchestration system for managing multi-agent interactions with real-time monitoring.

![Session Web UI](assets/session-webui.png)

### Patterns & Sessions

Use the `@pattern` decorator to create trackable, reusable agent workflows:

```python
from polycli import OpenSourceAgent, ClaudeAgent
from polycli.orchestration import session, pattern, serve_session
from polycli.builtin_patterns import notify, tell, get_status

# Create agents with unique IDs
agent1 = OpenSourceAgent(id="Researcher")
agent2 = ClaudeAgent(id="Writer")

# Start a monitoring session with web UI
with session() as s:
    server, _ = serve_session(s, port=8765)
    print("Monitor at http://localhost:8765")
    
    # Use built-in patterns
    notify(agent1, "Research quantum computing basics")
    tell(agent1, agent2, "Share your research findings")
    
    # Get status summaries
    status = get_status(agent2, n_exchanges=3)
    print(status)
    
    input("Press Enter to stop...")
```

### Built-in Patterns

**`notify(agent, message)`** - Send notifications to agents
```python
notify(agent, "Your task is to analyze this code", source="System")
```

**`tell(speaker, listener, instruction)`** - Agent-to-agent communication
```python
tell(agent1, agent2, "Explain your findings about the bug")
```

**`get_status(agent, n_exchanges=3)`** - Generate work summaries
```python
status = get_status(agent, n_exchanges=5, model="gpt-4o")
```

### Batch Execution

Execute multiple patterns in parallel with the `batch()` context manager - perfect for concurrent analysis, testing, or processing:

```python
from polycli.orchestration import batch

@pattern
def analyze(agent: BaseAgent, file: str):
    """Analyze a single file"""
    return agent.run(f"Analyze {file}").content

# Sequential execution (slow)
with session() as s:
    analyze(agent1, "file1.py")  # Waits...
    analyze(agent2, "file2.py")  # Waits...
    analyze(agent3, "file3.py")  # Waits...

# Parallel execution (fast!)
with session() as s:
    with batch():
        analyze(agent1, "file1.py")  # Queued
        analyze(agent2, "file2.py")  # Queued
        analyze(agent3, "file3.py")  # Queued
    # All execute simultaneously here
```

Batched patterns appear as tabbed groups in the web UI, making it easy to monitor parallel workflows.

### Creating Custom Patterns

```python
@pattern
def code_review(developer: BaseAgent, reviewer: BaseAgent, code_file: str):
    """Custom pattern for code review workflow"""
    # Pattern automatically tracks execution when used in a session
    code_content = developer.run(f"Read and explain {code_file}").content
    review = reviewer.run(f"Review this code: {code_content}").content
    return review

# Use with or without session monitoring
with session() as s:
    result = code_review(agent1, agent2, "main.py")  # Tracked in web UI
    
# Or standalone without monitoring
result = code_review(agent1, agent2, "main.py")  # Works normally
```

### Web UI Features

- **Real-time Monitoring**: Watch patterns execute live
- **Pause & Resume**: Pause before next pattern execution
- **Message Injection**: Add messages to any agent while paused
- **Agent History**: View complete conversation history per agent
- **Pattern Timeline**: Track all pattern executions with inputs/outputs

### Flexible CLI Switching

OpenSourceAgent supports seamless switching between different CLI backends while maintaining conversation context:

```python
agent = OpenSourceAgent()

# Use different CLIs for different tasks
agent.run("Write a function", model="gpt-4o", cli="qwen-code")  # Best for coding
agent.run("Run tests", model="gpt-4o", cli="mini-swe")          # Good for testing
agent.run("Explain the logic", model="gpt-4o", cli="no-tools")  # Pure conversation
```

## Requirements
- Python 3.11+
- One or more CLI tools installed
- models.json for LLM configuration

## Roadmap
- [ ] Agent & LLM Integration
    - [x] Mini SWE-agent Integration
    - [x] Qwen Code Integration
    - [ ] Dify Integration
    - [ ] Use Gemini Core for integration instead of commands
    - [ ] Handling LLM thinking mode
- [x] Native Multi-agent Orchestration
    - [x] Agent registration and tracing
    - [x] Pattern & Session System
    - [x] Web UI for monitoring
    - [x] Pause/Resume with message injection
- [ ] Context Management
    - [x] Qwen Code Memory auto-compaction
    - [x] Extend Qwen Code max session length
    - [ ] Claude Code Memory auto-compaction
    - [ ] Refine memory compact strategy

---

*Simple. Stable. Universal.*
