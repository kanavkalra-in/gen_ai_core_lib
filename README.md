# gen_ai_core_lib

**gen_ai_core_lib** is a comprehensive, reusable Python library for building GenAI applications, chatbots, and agents. It provides a unified interface for managing LLMs, sessions, memory, tools, and observability across multiple projects.

## Features

### Core Capabilities

- **LLM Management**: Unified factory for OpenAI, Anthropic, Gemini, and Ollama models with caching and registry support
- **Session Management**: Thread-safe session manager with configurable timeouts and limits
- **Memory Management**: Configurable memory strategies (trim, summarize, trim-and-summarize) for conversation history
- **Agent Framework**: Abstract agent interface with factory and registry for creating and managing agents
- **Tool Management**: Registry system for managing and accessing agent tools
- **Storage Backend**: Pluggable storage interface with in-memory implementation
- **Token Utilities**: Token counting and cost estimation utilities
- **Observability**: Built-in metrics collection and distributed tracing support
- **Lifecycle Management**: Startup and shutdown hooks for application lifecycle
- **Plugin System**: Extensible plugin architecture for adding custom functionality
- **Validation**: Pydantic-based request validation models
- **Dependency Injection**: Centralized dependency container for clean architecture

## Installation

### Editable Installation (for local development)

From the project root:

```bash
pip install -e .
```

### With Optional Dependencies

```bash
# With token counting support
pip install -e ".[token-counting]"

# With FastAPI support
pip install -e ".[fastapi]"

# With Google Gemini support
pip install -e ".[google]"

# All optional dependencies
pip install -e ".[token-counting,fastapi,google]"
```

## Quick Start

### Basic Usage

```python
from gen_ai_core_lib import ApplicationContainer

# Initialize container (core dependencies are auto-initialized)
container = ApplicationContainer()

# Get LLM manager and create an LLM instance
llm_manager = container.get_llm_manager()
llm = llm_manager.get_llm()  # Uses environment-configured defaults

# Invoke the LLM
response = llm.invoke("Hello, world!")
print(response.content)
```

### Using Agents

```python
from gen_ai_core_lib import (
    ApplicationContainer,
    AgentConfig,
    MemoryConfig,
    MemoryStrategy
)

container = ApplicationContainer()
llm_manager = container.get_llm_manager()
agent_factory = container.get_agent_factory()

# Create agent configuration
config = AgentConfig(
    agent_id="my-chatbot",
    agent_type="chatbot",
    system_prompt="You are a helpful assistant.",
    memory_config=MemoryConfig(
        strategy=MemoryStrategy.TRIM,
        trim_keep_messages=10
    )
)

# Create agent (you will need to implement a concrete agent class)
llm = llm_manager.get_llm()
# agent = agent_factory.create_agent("chatbot", config, llm)
```

### Using Memory Management

```python
from gen_ai_core_lib import (
    ApplicationContainer,
    MemoryConfig,
    MemoryStrategy
)

container = ApplicationContainer()
memory_manager = container.get_memory_manager()

# Configure memory strategy
memory_config = MemoryConfig(
    strategy=MemoryStrategy.TRIM_AND_SUMMARIZE,
    trim_keep_messages=20,
    summarize_threshold=50
)

# Apply memory strategy to a session
llm = container.get_llm_manager().get_llm()
processed_history = await memory_manager.apply_memory_strategy(
    session_id="session-123",
    config=memory_config,
    llm=llm
)
```

### Using Tools

```python
from gen_ai_core_lib import ApplicationContainer
from langchain_core.tools import tool

container = ApplicationContainer()
tool_registry = container.get_tool_registry()

# Define a tool
@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    return str(eval(expression))

# Register tool
tool_registry.register("calculator", calculator)

# Get tools
tools = tool_registry.get_tools(["calculator"])
```

### Using Observability

```python
from gen_ai_core_lib import ApplicationContainer, TraceContext

container = ApplicationContainer()
metrics = container.get_metrics_collector()

# Record metrics
metrics.record_latency("chat", 0.5)
metrics.record_token_usage("gpt-4", input_tokens=100, output_tokens=50)

# Use tracing
with TraceContext().span("operation") as span:
    # Your code here
    pass

# Get metrics summary
summary = metrics.get_metrics_summary()
print(summary)
```

### Using Session Management

```python
from gen_ai_core_lib import ApplicationContainer

container = ApplicationContainer()
session_manager = container.get_session_manager()

# Create a session
session = session_manager.create_session("user-123")

# Get session
session = session_manager.get_session(session.session_id)

# Cleanup expired sessions
session_manager.cleanup_expired_sessions()
```

## Configuration

`gen_ai_core_lib` reads environment variables via **python-dotenv** from a `.env` file in your application's **current working directory** (where you start your Python process).

### Required Environment Variables

```bash
# OpenAI (required for default setup)
OPENAI_API_KEY=your-openai-api-key
CHAT_MODEL=gpt-3.5-turbo  # or gpt-4, gpt-4-turbo, etc.
```

### Optional Environment Variables

```bash
# Anthropic
ANTHROPIC_API_KEY=your-anthropic-api-key

# Google Gemini
GOOGLE_API_KEY=your-google-api-key

# Ollama (local models)
OLLAMA_BASE_URL=http://localhost:11434

# Session Management
MAX_CONCURRENT_SESSIONS=100
SESSION_TIMEOUT_HOURS=24

# LLM Configuration
CHAT_MODEL_TEMPERATURE=0.7
CHAT_MODEL_MAX_TOKENS=2000

# Logging
LOG_LEVEL=INFO

# LangSmith Tracing (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=gen-ai-core
```

See `config/settings.py` for the complete list of supported environment variables.

## Architecture

The library follows SOLID principles and uses dependency injection for clean architecture:

- **Core Dependencies**: Automatically initialized (LLM manager, session manager, memory manager, agent factory)
- **Optional Dependencies**: Lazy-initialized on first access (agent registry, tool registry, metrics, lifecycle manager, plugins)

### ApplicationContainer

The `ApplicationContainer` is the central dependency injection container:

```python
container = ApplicationContainer()

# Core dependencies (always available)
llm_manager = container.get_llm_manager()
session_manager = container.get_session_manager()
memory_manager = container.get_memory_manager()
agent_factory = container.get_agent_factory()

# Optional dependencies (lazy-initialized)
agent_registry = container.get_agent_registry()
tool_registry = container.get_tool_registry()
metrics_collector = container.get_metrics_collector()
lifecycle_manager = container.get_lifecycle_manager()
plugin_registry = container.get_plugin_registry()
```

## Project Structure

```
gen_ai_core_lib/
├── agents/              # Agent abstractions and factories
├── config/              # Configuration and settings
├── dependencies/        # Dependency injection container
├── lifecycle/           # Lifecycle management
├── llm/                 # LLM management and factories
├── memory/              # Memory management and strategies
├── observability/       # Metrics and tracing
├── plugins/             # Plugin system
├── session/             # Session management
├── storage/             # Storage backends
├── tools/               # Tool registry and built-in tools
├── utils/               # Token counting utilities
├── validation/          # Request validation
└── testing/             # Test fixtures and utilities
```

## Requirements

- Python >= 3.9
- Core dependencies:
  - `python-dotenv >= 1.0.0`
  - `langchain-core >= 0.3.0`
  - `langchain-openai >= 0.3.0` (requires `openai >= 2.0.0`)
  - `pydantic >= 2.0.0`

### Note on OpenAI Version

This library uses `langchain-openai >= 0.3.0`, which requires `openai >= 2.0.0`. If you need to use packages that require `openai < 2.0.0`, consider using separate virtual environments for different projects.

## Supported LLM Providers

- **OpenAI**: GPT-3.5, GPT-4, GPT-4 Turbo, GPT-4o
- **Anthropic**: Claude 3 Opus, Claude 3 Sonnet
- **Google**: Gemini Pro, Gemini 1.5 Flash/Pro, Gemini 2.5 Flash/Pro
- **Ollama**: Local models (Llama, Mistral, etc.)

## Memory Strategies

- **NONE**: Keep all messages
- **TRIM**: Keep only the most recent N messages
- **SUMMARIZE**: Summarize old messages when threshold is exceeded
- **TRIM_AND_SUMMARIZE**: Combine trim and summarize strategies

## Error Handling

The library provides a comprehensive exception hierarchy:

```python
from gen_ai_core_lib import (
    GenAICoreException,
    SessionError,
    LLMError,
    AgentError,
    ToolError,
    MemoryError,
    # ... and more
)
```

## Testing

Use the testing fixtures for easy testing:

```python
from gen_ai_core_lib.testing import test_container, test_llm_manager

container = test_container()
llm_manager = test_llm_manager()
```

## Contributing

This is a core library designed for reuse across multiple projects. When adding features:

1. Follow SOLID principles
2. Use dependency injection via ApplicationContainer
3. Add comprehensive type hints
4. Update documentation
5. Add tests

## License

MIT

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed architecture documentation
- `config/settings.py` - Complete configuration reference
