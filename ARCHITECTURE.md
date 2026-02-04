# Architecture Documentation

## Overview

`gen_ai_core_lib` is designed as a comprehensive, reusable core library for building GenAI applications, chatbots, and agents. The architecture follows SOLID principles, uses dependency injection, and provides a clean separation of concerns.

## Design Principles

1. **SOLID Principles**: All components follow SOLID principles
2. **Dependency Injection**: Pure DI via ApplicationContainer
3. **Protocol-Based Abstractions**: Use of Protocols for flexible implementations
4. **Async-First**: Core operations support async/await
5. **Extensibility**: Plugin system for adding functionality
6. **Observability**: Built-in metrics and tracing
7. **Type Safety**: Comprehensive type hints throughout
8. **Thread Safety**: Thread-safe implementations where needed

## Core Components

### 1. ApplicationContainer (`dependencies/application_container.py`)

The central dependency injection container that manages all application dependencies.

**Initialization Strategy:**
- **Core Dependencies**: Initialized immediately in `__init__`
  - LLM Manager Registry
  - LLM Manager (default instance)
  - Session Manager
  - Memory Manager
  - Agent Factory

- **Optional Dependencies**: Lazy-initialized on first access
  - Agent Registry
  - Tool Registry
  - Metrics Collector
  - Lifecycle Manager
  - Plugin Registry

**Usage:**
```python
from gen_ai_core_lib import ApplicationContainer

container = ApplicationContainer()
# Core dependencies are already initialized

# Optional dependencies are initialized on first access
agent_registry = container.get_agent_registry()
tool_registry = container.get_tool_registry()

# Or pre-initialize all optional dependencies
container.initialize()
```

**Benefits:**
- Fast startup (only core dependencies initialized)
- Memory efficient (optional features only loaded when needed)
- Thread-safe lazy initialization

### 2. LLM Management (`llm/llm_manager.py`)

Unified factory for creating and managing LLM instances across multiple providers.

**Key Components:**
- `LLMManager`: Main interface for LLM operations
- `LLMManagerRegistry`: Registry for managing multiple LLM manager instances
- `ModelProviderFactory`: Factory for creating provider-specific LLM instances
- `DefaultModelConfigRepository`: Configuration repository
- `SettingsAPIKeyProvider`: API key provider from settings
- `LLMCache`: Caching layer for LLM instances

**Supported Providers:**
- OpenAI (ChatOpenAI)
- Anthropic (ChatAnthropic)
- Google (ChatGoogleGenerativeAI)
- Ollama (ChatOllama)

**Usage:**
```python
from gen_ai_core_lib import ApplicationContainer

container = ApplicationContainer()
llm_manager = container.get_llm_manager()

# Get default LLM (uses environment configuration)
llm = llm_manager.get_llm()

# Get LLM for specific use case
llm = llm_manager.get_llm_for_use_case("chat")
```

### 3. Agent Abstraction Layer (`agents/`)

Abstract interface for creating and managing agents.

**Components:**
- **`agent.py`**: Core `Agent` interface and `AgentConfig` dataclass
- **`agent_factory.py`**: `DefaultAgentFactory` for creating agent instances
- **`agent_registry.py`**: `AgentRegistry` for managing agent instances

**Agent Interface:**
```python
class Agent(ABC):
    async def invoke(
        self,
        input: str | Dict[str, Any],
        session_id: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process user input and return response."""
        pass
    
    def get_tools(self) -> List[Any]:
        """Get available tools for this agent."""
        pass
```

**Usage:**
```python
from gen_ai_core_lib import Agent, AgentConfig, DefaultAgentFactory

factory = DefaultAgentFactory()
config = AgentConfig(
    agent_id="my-agent",
    agent_type="chatbot",
    system_prompt="You are a helpful assistant",
    memory_config=MemoryConfig(strategy=MemoryStrategy.TRIM)
)
llm = container.get_llm_manager().get_llm()
agent = factory.create_agent("chatbot", config, llm)
```

### 4. Memory Management (`memory/`)

Configurable memory strategies for managing conversation history.

**Components:**
- **`memory_manager.py`**: `MemoryManager` abstract interface and `InMemoryMemoryManager` implementation
- **`memory_config.py`**: `MemoryConfig` and `MemoryStrategy` enum

**Memory Strategies:**
- **NONE**: Keep all messages without modification
- **TRIM**: Keep only the most recent N messages
- **SUMMARIZE**: Summarize old messages when threshold is exceeded
- **TRIM_AND_SUMMARIZE**: Combine trim and summarize strategies

**Usage:**
```python
from gen_ai_core_lib import (
    InMemoryMemoryManager,
    MemoryConfig,
    MemoryStrategy
)

memory = InMemoryMemoryManager()
config = MemoryConfig(
    strategy=MemoryStrategy.TRIM_AND_SUMMARIZE,
    trim_keep_messages=20,
    summarize_threshold=50
)

# Get history
history = await memory.get_history("session-123")

# Add message
await memory.add_message("session-123", message)

# Apply memory strategy
llm = container.get_llm_manager().get_llm()
processed_history = await memory.apply_memory_strategy(
    "session-123",
    config,
    llm
)
```

### 5. Tool Management (`tools/`)

Registry system for managing and accessing agent tools.

**Components:**
- **`tool_registry.py`**: `ToolRegistry` for managing tools
- **`builtin.py`**: `BuiltinToolRegistry` with common tools

**Usage:**
```python
from gen_ai_core_lib import ToolRegistry
from langchain_core.tools import tool

registry = ToolRegistry()

# Register a tool
@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    return str(eval(expression))

registry.register("calculator", calculator)

# Get tools
tools = registry.get_tools(["calculator"])
all_tools = registry.get_tools()  # Get all tools
```

### 6. Storage Backend (`storage/`)

Pluggable storage interface for persistent data.

**Components:**
- **`storage_backend.py`**: `StorageBackend` abstract interface
- **`in_memory.py`**: `InMemoryStorage` implementation
- **`session_storage_adapter.py`**: Adapter for backward compatibility

**Usage:**
```python
from gen_ai_core_lib import InMemoryStorage

storage = InMemoryStorage()
await storage.set("key", "value", ttl=3600)
value = await storage.get("key")
await storage.delete("key")
```

### 7. Session Management (`session/`)

Thread-safe session manager with configurable timeouts and limits.

**Components:**
- **`session_manager.py`**: `SessionManager` with sync and async support
- **`session_storage.py`**: Session storage interface

**Features:**
- Automatic session expiration
- Configurable session limits
- Thread-safe operations
- Async support

**Usage:**
```python
from gen_ai_core_lib import ApplicationContainer

container = ApplicationContainer()
session_manager = container.get_session_manager()

# Create session
session = session_manager.create_session("user-123")

# Get session
session = session_manager.get_session(session.session_id)

# Async operations
session = await session_manager.get_session_async(session.session_id)
```

### 8. Validation Layer (`validation/`)

Pydantic-based request validation models.

**Components:**
- **`validators.py`**: Validation models and functions
  - `ChatRequest`: Validated chat requests
  - `AgentCreateRequest`: Agent creation requests
  - `SessionCreateRequest`: Session creation requests

**Usage:**
```python
from gen_ai_core_lib import ChatRequest, validate_chat_request

# Using Pydantic model directly
request = ChatRequest(
    message="Hello",
    session_id="session-123"
)

# Or validate from dict
request = validate_chat_request({
    "message": "Hello",
    "session_id": "session-123"
})
```

### 9. Observability (`observability/`)

Built-in metrics collection and distributed tracing.

**Components:**
- **`metrics.py`**: `MetricsCollector` interface and `InMemoryMetricsCollector` implementation
- **`tracing.py`**: `TraceContext` for distributed tracing

**Metrics:**
- Operation latency
- Error tracking
- Token usage
- Custom counters

**Usage:**
```python
from gen_ai_core_lib import (
    InMemoryMetricsCollector,
    TraceContext
)

metrics = InMemoryMetricsCollector()
metrics.record_latency("chat", 0.5)
metrics.record_token_usage("gpt-4", 100, 50)
metrics.record_error("chat", exception)
metrics.increment_counter("requests")

# Get metrics summary
summary = metrics.get_metrics_summary()

# Tracing
with TraceContext().span("operation") as span:
    # Your code here
    pass
```

### 10. Lifecycle Management (`lifecycle/`)

Startup and shutdown hooks for application lifecycle.

**Components:**
- **`lifecycle_manager.py`**: `LifecycleManager` for managing lifecycle hooks

**Usage:**
```python
from gen_ai_core_lib import LifecycleManager

lifecycle = LifecycleManager()

# Add startup hook
lifecycle.add_startup_hook(lambda: print("Starting..."))

# Add shutdown hook
lifecycle.add_shutdown_hook(lambda: print("Shutting down..."))

# Execute lifecycle
await lifecycle.startup()
# ... application runs ...
await lifecycle.shutdown()
```

### 11. Plugin System (`plugins/`)

Extensible plugin architecture for adding custom functionality.

**Components:**
- **`plugin_registry.py`**: `Plugin` interface and `PluginRegistry`

**Usage:**
```python
from gen_ai_core_lib import Plugin, PluginRegistry

class MyPlugin(Plugin):
    def initialize(self, container):
        # Initialize plugin
        pass
    
    def get_name(self):
        return "my-plugin"
    
    def get_dependencies(self):
        return []

registry = PluginRegistry()
registry.register(MyPlugin())
registry.initialize_all(container)
```

### 12. Token Utilities (`utils/`)

Token counting and cost estimation utilities.

**Components:**
- **`token_counter.py`**: `TokenCounter` interface and implementations
- **`token_counting_wrapper.py`**: Wrapper for automatic token counting

**Usage:**
```python
from gen_ai_core_lib import TokenCounter, get_token_counter

counter = get_token_counter()
count = counter.count_tokens("Hello, world!", model="gpt-3.5-turbo")
```

### 13. Exception Hierarchy (`exceptions.py`)

Comprehensive exception hierarchy for error handling.

**Exception Types:**
- `GenAICoreException`: Base exception
- `SessionError`, `SessionNotFoundError`, `SessionExpiredError`
- `LLMError`, `LLMProviderError`, `ModelNotFoundError`, `APIKeyError`
- `MemoryError`, `MemoryStrategyError`
- `AgentError`, `AgentNotFoundError`, `AgentInitializationError`
- `ToolError`, `ToolNotFoundError`, `ToolExecutionError`
- `StorageError`, `StorageBackendError`
- `ConfigurationError`, `ValidationError`

## Directory Structure

```
gen_ai_core_lib/
├── agents/              # Agent abstractions
│   ├── __init__.py
│   ├── agent.py         # Agent interface and config
│   ├── agent_factory.py # Agent factory
│   └── agent_registry.py # Agent registry
├── config/              # Configuration
│   ├── llm_config.py    # LLM configuration
│   ├── logging_config.py # Logging setup
│   ├── session_config.py # Session configuration
│   └── settings.py      # Environment settings
├── dependencies/        # Dependency injection
│   └── application_container.py # Main DI container
├── lifecycle/           # Lifecycle management
│   └── lifecycle_manager.py
├── llm/                 # LLM management
│   └── llm_manager.py   # LLM factory and registry
├── memory/              # Memory management
│   ├── memory_config.py # Memory configuration
│   └── memory_manager.py # Memory manager
├── observability/       # Observability
│   ├── metrics.py       # Metrics collection
│   └── tracing.py       # Distributed tracing
├── plugins/             # Plugin system
│   └── plugin_registry.py
├── session/             # Session management
│   ├── session_manager.py
│   └── session_storage.py
├── storage/             # Storage backends
│   ├── storage_backend.py
│   ├── in_memory.py
│   └── session_storage_adapter.py
├── tools/               # Tool management
│   ├── tool_registry.py
│   └── builtin.py
├── utils/               # Utilities
│   ├── token_counter.py
│   └── token_counting_wrapper.py
├── validation/          # Validation
│   └── validators.py
├── testing/             # Test infrastructure
│   └── fixtures.py
├── exceptions.py        # Exception hierarchy
└── __init__.py          # Public API
```

## Initialization Flow

1. **ApplicationContainer.__init__()**
   - Initialize core dependencies:
     - LLM Manager Registry
     - LLM Manager (default)
     - Session Manager
     - Memory Manager
     - Agent Factory

2. **First Access to Optional Dependencies**
   - Agent Registry (lazy)
   - Tool Registry (lazy)
   - Metrics Collector (lazy)
   - Lifecycle Manager (lazy)
   - Plugin Registry (lazy)

3. **container.initialize()** (optional)
   - Pre-initialize all optional dependencies

## Thread Safety

- **ApplicationContainer**: Thread-safe lazy initialization using locks
- **SessionManager**: Thread-safe session operations
- **MemoryManager**: Thread-safe history operations
- **ToolRegistry**: Thread-safe tool registration
- **MetricsCollector**: Thread-safe metrics collection

## Extension Points

1. **Custom Agents**: Implement `Agent` interface
2. **Custom Memory Managers**: Implement `MemoryManager` interface
3. **Custom Storage Backends**: Implement `StorageBackend` interface
4. **Custom Metrics Collectors**: Implement `MetricsCollector` interface
5. **Plugins**: Implement `Plugin` interface
6. **Tools**: Register custom tools via `ToolRegistry`

## Migration Guide

### For Existing Code

1. **SessionManager**: Existing sync methods still work. Use async methods for new code.
2. **ApplicationContainer**: New components are optional. Existing code continues to work.
3. **Storage**: `SessionStorage` still works. Use `StorageBackend` for new implementations.

### For New Code

1. Use `Agent` interface for chatbot implementations
2. Use `MemoryManager` for conversation history
3. Use `ToolRegistry` for managing tools
4. Use `MetricsCollector` for observability
5. Use `LifecycleManager` for startup/shutdown logic
6. Use validation models for request validation
7. Prefer async methods where available

## Best Practices

1. **Always use ApplicationContainer**: Don't instantiate components directly
2. **Use async methods**: Prefer async methods for I/O operations
3. **Handle exceptions**: Use the exception hierarchy for proper error handling
4. **Configure memory strategies**: Use appropriate memory strategies for your use case
5. **Register tools**: Use ToolRegistry for managing agent tools
6. **Collect metrics**: Use MetricsCollector for observability
7. **Use validation**: Validate requests using Pydantic models

## Future Enhancements

1. Implement concrete agent types (e.g., `ChatbotAgent`, `RAGAgent`)
2. Add Redis storage backend implementation
3. Add Prometheus metrics exporter
4. Add more built-in tools
5. Add vector store integration
6. Add streaming support for LLM responses
7. Add retry logic and circuit breakers
