# PolyCLI

Unified Python interface for AI coding assistants (Claude Code, Qwen Code, MiniSWE-Agent) with pattern-based multi-agent orchestration, real-time web monitoring, and REST API integration.

**Key Features:**
- 🔄 Seamless switching between AI coding assistants with unified message format
- 🎭 Pattern-based orchestration for trackable multi-agent workflows  
- 🌐 Web control panel with real-time debugging and intervention
- 🔌 REST API for third-party integration and automation
- 🏛️ Agent Hall system for persistent AI teams (coming soon)

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
npm install -g @lexicalmathical/qwen-code@0.0.7-polycli.2
```

**Mini-SWE Agent**: 
```bash
pip install mini-swe-agent
```

## Quick Start

```python
from polycli import PolyAgent

# Create a unified agent that works with all backends
agent = PolyAgent(debug=True)

# Automatic backend selection based on task
result = agent.run("What is 2+2?")  # Uses Claude by default
print(result.content)  # 4

# Explicit backend control
result = agent.run("Write a function", cli="claude-code")  # Claude with tools
result = agent.run("Analyze this", cli="qwen-code")       # Qwen with tools
result = agent.run("Just chat", cli="no-tools")           # Direct API, no tools

# Multi-model support via models.json
result = agent.run("Explain recursion", model="gpt-4o")
if result:  # Check success
    print(result.content)

# Structured outputs with Pydantic
from pydantic import BaseModel, Field

class MathResult(BaseModel):
    answer: int = Field(description="The numerical answer")
    explanation: str = Field(description="Step-by-step explanation")

result = agent.run("What is 15+27?", model="gpt-4o", schema_cls=MathResult)
if result.has_data():
    print(result.data['answer'])  # 42

# System prompts
agent = PolyAgent(system_prompt="You are a helpful Python tutor")
result = agent.run("Explain list comprehensions")

# Token management with auto-compaction
agent = PolyAgent(max_tokens=50000)  # Set token limit
# Automatically compacts conversation when approaching limit

# State persistence
agent.save_state("conversation.jsonl")  # Save in any format
new_agent = PolyAgent()
new_agent.load_state("conversation.jsonl")  # Load and continue
```

## Session Registry & Control Panel (New!)

The Session Registry system allows you to define reusable sessions as functions and automatically generates a web control panel for triggering and monitoring them.

### Defining Sessions

```python
from polycli.session_registry import session_def, get_registry
from polycli import PolyAgent
from polycli.orchestration import batch

@session_def(
    name="Code Analyzer",
    description="Analyze Python code quality",
    params={"file_path": str, "depth": int},
    category="Analysis"
)
def analyze_code(file_path: str, depth: int = 3):
    """Analyze code with configurable depth."""
    agent = PolyAgent(id="analyzer")
    
    # Use tracked=True to ensure tracking in session
    result = agent.run(
        f"Analyze {file_path} with depth {depth}", 
        cli="claude-code",
        tracked=True
    )
    
    return {
        "file": file_path,
        "analysis": result.content,
        "status": "completed"
    }

@session_def(
    name="Multi-Agent Research", 
    description="Research with multiple specialized agents",
    params={"topic": str},
    category="Research"
)
def research_topic(topic: str):
    """Coordinate multiple agents for research."""
    researcher = PolyAgent(id="researcher")
    analyst = PolyAgent(id="analyst")
    writer = PolyAgent(id="writer")
    
    # Parallel execution with tracking
    with batch():
        facts = researcher.run(f"Research facts about {topic}", tracked=True)
        analysis = analyst.run(f"Analyze trends in {topic}", tracked=True)
    
    # Sequential synthesis with tracking
    report = writer.run(
        f"Write report combining: {facts.content} and {analysis.content}",
        tracked=True
    )
    
    return {"topic": topic, "report": report.content}
```

### Starting the Control Panel

```python
from polycli.session_registry import get_registry

# Get the registry (sessions auto-register via decorator)
registry = get_registry()

# Start the web control panel
registry.serve_control_panel(port=8765)
print("Control panel at http://localhost:8765")

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down...")
```

### Control Panel Features

![Session Control Panel](assets/session-control-panel.png)

- **Web UI**: Clean interface with sidebar navigation
- **Session Library**: Browse all registered sessions by category
- **Parameter Forms**: Auto-generated forms for session parameters
- **Real-time Monitoring**: Each session gets its own monitoring port
- **Session Control**: Start, monitor, and cancel sessions
- **Resource Management**: Automatic port allocation and cleanup
- **Iframe Integration**: Monitor sessions without leaving the control panel

![Session Monitoring](assets/session-monitoring.png)

### Session Registry API

The control panel exposes REST APIs for third-party integration:

#### Available Endpoints

**List registered sessions:**
```bash
GET http://localhost:8765/api/sessions
```

**Get running sessions:**
```bash
GET http://localhost:8765/api/running
```

**Trigger a session:**
```bash
POST http://localhost:8765/api/trigger
Content-Type: application/json

{
  "session_id": "code_analyzer",
  "params": {
    "file_path": "/path/to/file.py",
    "depth": 3
  }
}
```

**Stop a session:**
```bash
POST http://localhost:8765/api/stop
Content-Type: application/json

{"exec_id": "code_analyzer-abc123"}
```

**Get session status:**
```bash
GET http://localhost:8765/api/status/{exec_id}
```

Sessions triggered via API appear in the web UI in real-time, allowing monitoring from both API clients and the control panel simultaneously.

## Multi-Agent Orchestration

PolyCLI includes a powerful orchestration system for managing multi-agent interactions with real-time monitoring.

![Session Web UI](assets/session-webui.png)

### Patterns & Sessions

Use the `@pattern` decorator to create trackable, reusable agent workflows:

```python
from polycli import PolyAgent
from polycli.orchestration import session, pattern, serve_session
from polycli.builtin_patterns import notify, tell, get_status

# Create agents with unique IDs for tracking
agent1 = PolyAgent(id="Researcher")
agent2 = PolyAgent(id="Writer")

# Start a monitoring session with web UI
with session() as s:
    server, _ = serve_session(s, port=8765)
    print("Monitor at http://localhost:8765")
    
    # Use built-in patterns
    notify(agent1, "Research quantum computing basics")
    tell(agent1, agent2, "Share your research findings")
    
    # Get status summaries
    status = get_status(agent2, n_exchanges=3)
    print(status.content)
    
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

Execute multiple patterns in parallel:

```python
from polycli.orchestration import batch

@pattern
def analyze(agent: PolyAgent, file: str):
    """Analyze a single file"""
    return agent.run(f"Analyze {file}").content

# Parallel execution (fast!)
with session() as s:
    with batch():
        result1 = analyze(agent1, "file1.py")  # Queued
        result2 = analyze(agent2, "file2.py")  # Queued
        result3 = analyze(agent3, "file3.py")  # Queued
    # All execute simultaneously here
```

### Creating Custom Patterns

```python
@pattern
def code_review(developer: PolyAgent, reviewer: PolyAgent, code_file: str):
    """Custom pattern for code review workflow"""
    # Pattern automatically tracks execution when used in a session
    code_content = developer.run(f"Read and explain {code_file}").content
    review = reviewer.run(f"Review this code: {code_content}").content
    return review

# Use with monitoring
with session() as s:
    serve_session(s, port=8765)
    result = code_review(agent1, agent2, "main.py")  # Tracked in web UI
```

### Web UI Features

- **Real-time Monitoring**: Watch patterns execute live
- **Pause & Resume**: Pause before next pattern execution
- **Message Injection**: Add messages to any agent while paused
- **Agent History**: View complete conversation history per agent
- **Pattern Timeline**: Track all pattern executions with inputs/outputs
- **Session Cancellation**: Stop running sessions and free resources

## Configuration

Create `models.json` in project root:
```json
{
  "models": {
    "gpt-4o": {
      "endpoint": "https://api.openai.com/v1",
      "api_key": "sk-...",
      "model": "gpt-4o"
    },
    "glm-4.5": {
      "endpoint": "https://api.example.com/v1",
      "api_key": "glm-...",
      "model": "glm-4.5"
    }
  }
}
```

## Architecture

![PolyCLI Architecture](assets/architecture.png)

### Core Components

- **PolyAgent**: Unified agent supporting all backends through a single interface
- **MessageList**: Single source of truth for conversation history with format auto-conversion
- **Session Registry**: Define and manage reusable sessions with web control panel
- **Orchestration**: Pattern execution with real-time monitoring and batch support
- **Token Management**: Automatic compaction when approaching limits

### Message Format Unification

The new `Message` and `MessageList` classes provide seamless conversion between:
- **Claude format**: JSONL with full metadata and tool tracking
- **Qwen format**: JSON with parts array
- **Standard format**: Simple role/content pairs

```python
# Messages are automatically converted to the right format for each backend
agent = PolyAgent()
agent.run("Hello", cli="claude-code")  # Converts to Claude format
agent.run("Hi", cli="qwen-code")       # Converts to Qwen format
agent.save_state("chat.jsonl")         # Preserves original formats
```

## RunResult Interface

All agent `.run()` calls return a unified `RunResult`:

```python
result = agent.run("Calculate 5 * 8")

# Basic usage
print(result.content)        # Always a string
print(result.is_success)     # Boolean status
if not result:               # Pythonic error checking
    print(result.error_message)

# Structured data
if result.has_data():
    data = result.data       # Dictionary access

# Metadata
print(result.get_claude_cost())    # Cost tracking
print(result.get_session_id())     # Session ID
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
    - [ ] Improve Mini-SWE integration on message history
- [x] Native Multi-agent Orchestration
    - [x] Agent registration and tracing
    - [x] Pattern & Session System
    - [x] Web UI for monitoring
    - [x] Pause/Resume with message injection
    - [x] Session Registry with Control Panel
- [ ] Context Management
    - [x] Qwen Code Memory auto-compaction
    - [x] Extend Qwen Code max session length
    - [x] Token management with auto-compaction
    - [x] Claude Code Memory auto-compaction
    - [ ] Refine memory compact strategy

---

*Simple. Stable. Universal.*
