"""
gen_ai_core_lib
================

Reusable core library for managing LLMs, sessions, memory configuration,
and token counting across Python projects.

Typical usage:

    from gen_ai_core_lib import ApplicationContainer

    container = ApplicationContainer()
    container.initialize()
    llm_manager = container.get_llm_manager()
    llm = llm_manager.get_llm()
"""

from .config.settings import Settings, settings
from .config.logging_config import logger, setup_logger

from .llm.llm_manager import (
    LLMManager,
    DefaultModelConfigRepository,
    SettingsAPIKeyProvider,
    ModelProviderFactory,
    UseCaseConfig,
    LLMCache,
    LLMManagerRegistry,
)

from .session.session_manager import Session, SessionManager
from .dependencies.application_container import ApplicationContainer

from .memory.memory_config import MemoryConfig, MemoryConfigFactory, MemoryStrategy
from .memory.memory_manager import MemoryManager, InMemoryMemoryManager

from .agents.agent import Agent, AgentConfig
from .agents.agent_factory import DefaultAgentFactory
from .agents.agent_registry import AgentRegistry

from .tools.tool_registry import ToolRegistry
from .tools.builtin import BuiltinToolRegistry

from .storage.storage_backend import StorageBackend
from .storage.in_memory import InMemoryStorage

from .validation.validators import (
    ChatRequest,
    AgentCreateRequest,
    SessionCreateRequest,
    validate_chat_request,
)

from .observability.metrics import MetricsCollector, InMemoryMetricsCollector
from .observability.tracing import TraceContext, get_trace_context

from .lifecycle.lifecycle_manager import LifecycleManager

from .plugins.plugin_registry import Plugin, PluginRegistry

from .exceptions import (
    GenAICoreException,
    SessionError,
    SessionNotFoundError,
    SessionExpiredError,
    SessionLimitExceededError,
    LLMError,
    LLMProviderError,
    ModelNotFoundError,
    APIKeyError,
    MemoryError,
    MemoryStrategyError,
    AgentError,
    AgentNotFoundError,
    AgentInitializationError,
    ToolError,
    ToolNotFoundError,
    ToolExecutionError,
    StorageError,
    StorageBackendError,
    ConfigurationError,
    ValidationError,
)

from .utils.token_counter import TokenCounter, TokenCount, get_token_counter
from .utils.token_counting_wrapper import (
    TokenCountingObserver,
    TokenCountingWrapper,
    ChatEvent,
    should_enable_token_counting,
    collect_token_data,
    update_token_data_with_result,
    process_token_counting,
)

__all__ = [
    # Config / logging
    "Settings",
    "settings",
    "logger",
    "setup_logger",
    # LLM manager
    "LLMManager",
    "DefaultModelConfigRepository",
    "SettingsAPIKeyProvider",
    "ModelProviderFactory",
    "UseCaseConfig",
    "LLMCache",
    "LLMManagerRegistry",
    # Sessions
    "Session",
    "SessionManager",
    # DI container
    "ApplicationContainer",
    # Memory
    "MemoryConfig",
    "MemoryConfigFactory",
    "MemoryStrategy",
    "MemoryManager",
    "InMemoryMemoryManager",
    # Agents
    "Agent",
    "AgentConfig",
    "DefaultAgentFactory",
    "AgentRegistry",
    # Tools
    "ToolRegistry",
    "BuiltinToolRegistry",
    # Storage
    "StorageBackend",
    "InMemoryStorage",
    # Validation
    "ChatRequest",
    "AgentCreateRequest",
    "SessionCreateRequest",
    "validate_chat_request",
    # Observability
    "MetricsCollector",
    "InMemoryMetricsCollector",
    "TraceContext",
    "get_trace_context",
    # Lifecycle
    "LifecycleManager",
    # Plugins
    "Plugin",
    "PluginRegistry",
    # Exceptions
    "GenAICoreException",
    "SessionError",
    "SessionNotFoundError",
    "SessionExpiredError",
    "SessionLimitExceededError",
    "LLMError",
    "LLMProviderError",
    "ModelNotFoundError",
    "APIKeyError",
    "MemoryError",
    "MemoryStrategyError",
    "AgentError",
    "AgentNotFoundError",
    "AgentInitializationError",
    "ToolError",
    "ToolNotFoundError",
    "ToolExecutionError",
    "StorageError",
    "StorageBackendError",
    "ConfigurationError",
    "ValidationError",
    # Tokens
    "TokenCounter",
    "TokenCount",
    "get_token_counter",
    "TokenCountingObserver",
    "TokenCountingWrapper",
    "ChatEvent",
    "should_enable_token_counting",
    "collect_token_data",
    "update_token_data_with_result",
    "process_token_counting",
]

