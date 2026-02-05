"""
Application Dependency Container
Central place to wire all dependencies for the application.

Core dependencies (session_manager, llm_manager, llm_registry, memory_manager,
agent_factory) are initialized immediately in __init__. Other dependencies use
lazy initialization and are created only when requested.

This ensures core functionality is always available while keeping optional
features lazy-loaded for better performance.
"""
from typing import Optional, Callable, Any, TYPE_CHECKING
from datetime import timedelta
from functools import wraps
import threading

from ..llm.llm_manager import (
    LLMManager,
    DefaultModelConfigRepository,
    SettingsAPIKeyProvider,
    ModelProviderFactory,
    UseCaseConfig,
    LLMCache,
    LLMManagerRegistry,
)
from ..session.session_manager import SessionManager
from ..memory.memory_manager import MemoryManager, InMemoryMemoryManager
from ..agents.agent_factory import DefaultAgentFactory
from ..agents.agent_registry import AgentRegistry
from ..tools.tool_registry import ToolRegistry
from ..observability.metrics import MetricsCollector, InMemoryMetricsCollector
from ..lifecycle.lifecycle_manager import LifecycleManager
from ..config.settings import settings
from ..config.logging_config import logger

if TYPE_CHECKING:
    from ..plugins.plugin_registry import PluginRegistry


def _lazy_property(initializer: Callable[[], Any]) -> property:
    """
    Create a lazy-initialized property that is thread-safe.
    The initializer is called once on first access.
    """
    attr_name = f"_{initializer.__name__}"
    
    @property
    @wraps(initializer)
    def prop(self):
        if not hasattr(self, attr_name) or getattr(self, attr_name) is None:
            with self._lock:
                # Double-check after acquiring lock
                if not hasattr(self, attr_name) or getattr(self, attr_name) is None:
                    value = initializer(self)
                    setattr(self, attr_name, value)
                    logger.debug(f"{initializer.__name__} initialized on first access")
        return getattr(self, attr_name)
    
    return prop


class ApplicationContainer:
    """
    Container for all application dependencies.
    
    Core dependencies (session_manager, llm_manager, llm_registry, memory_manager, 
    agent_factory) are initialized immediately. Other dependencies use lazy initialization.
    
    This ensures core functionality is always available while keeping optional
    features lazy-loaded.
    """

    def __init__(self):
        self._lock = threading.Lock()
        # Track what has been initialized
        self._initialized_services = set()
        
        # Initialize core mandatory dependencies immediately
        self._initialize_core_dependencies()

    def _initialize_core_dependencies(self) -> None:
        """Initialize core mandatory dependencies immediately."""
        # Initialize LLM registry first (required for LLM manager)
        self._llm_registry = LLMManagerRegistry()
        self._initialized_services.add("llm_registry")
        logger.info("LLM registry initialized (mandatory)")
        
        # Initialize LLM manager (mandatory)
        self._llm_manager = self._llm_registry.create_and_register(
            instance_id="default",
            config_repository=DefaultModelConfigRepository(),
            api_key_provider=SettingsAPIKeyProvider(),
            provider_factory=ModelProviderFactory(),
            use_case_config=UseCaseConfig(),
            cache=LLMCache(),
        )
        self._initialized_services.add("llm_manager")
        logger.info("LLM manager initialized (mandatory)")
        
        # Initialize session manager (mandatory)
        self._session_manager = SessionManager(
            session_timeout=timedelta(hours=settings.SESSION_TIMEOUT_HOURS),
            max_sessions=settings.MAX_CONCURRENT_SESSIONS,
        )
        self._initialized_services.add("session_manager")
        logger.info("Session manager initialized (mandatory)")
        
        # Initialize memory manager (mandatory)
        self._memory_manager = InMemoryMemoryManager()
        self._initialized_services.add("memory_manager")
        logger.info("Memory manager initialized (mandatory)")
        
        # Initialize agent factory (mandatory)
        self._agent_factory = DefaultAgentFactory()
        self._initialized_services.add("agent_factory")
        logger.info("Agent factory initialized (mandatory)")
        
        logger.info("Core dependencies initialized")

    # Lazy-initialized properties for optional registries
    @_lazy_property
    def _agent_registry(self) -> AgentRegistry:
        """Initialize agent registry on first access."""
        registry = AgentRegistry()
        self._initialized_services.add("agent_registry")
        logger.info("Agent registry initialized")
        return registry

    @_lazy_property
    def _tool_registry(self) -> ToolRegistry:
        """Initialize tool registry on first access."""
        registry = ToolRegistry()
        self._initialized_services.add("tool_registry")
        logger.info("Tool registry initialized")
        return registry

    @_lazy_property
    def _plugin_registry(self) -> "PluginRegistry":
        """Initialize plugin registry on first access."""
        from ..plugins.plugin_registry import PluginRegistry
        registry = PluginRegistry()
        self._initialized_services.add("plugin_registry")
        logger.info("Plugin registry initialized")
        return registry

    @_lazy_property
    def _lifecycle_manager(self) -> LifecycleManager:
        """Initialize lifecycle manager on first access."""
        manager = LifecycleManager()
        self._initialized_services.add("lifecycle_manager")
        logger.info("Lifecycle manager initialized")
        return manager

    # Core dependencies are already initialized in __init__, no lazy properties needed

    @_lazy_property
    def _metrics_collector(self) -> MetricsCollector:
        """Initialize metrics collector on first access."""
        collector = InMemoryMetricsCollector()
        self._initialized_services.add("metrics_collector")
        logger.info("Metrics collector initialized")
        return collector

    # Public getter methods (maintain same interface)
    def get_llm_manager(self) -> LLMManager:
        """Get the default LLM manager (mandatory, always initialized)."""
        return self._llm_manager

    def get_session_manager(self) -> SessionManager:
        """Get the session manager (mandatory, always initialized)."""
        return self._session_manager

    def get_llm_registry(self) -> LLMManagerRegistry:
        """Get the LLM manager registry (mandatory, always initialized)."""
        return self._llm_registry

    def get_memory_manager(self) -> MemoryManager:
        """Get the memory manager (mandatory, always initialized)."""
        return self._memory_manager

    def get_agent_factory(self) -> DefaultAgentFactory:
        """Get the agent factory (mandatory, always initialized)."""
        return self._agent_factory

    def get_agent_registry(self) -> AgentRegistry:
        """Get the agent registry (lazy-initialized)."""
        return self._agent_registry

    def get_tool_registry(self) -> ToolRegistry:
        """Get the tool registry (lazy-initialized)."""
        return self._tool_registry

    def get_metrics_collector(self) -> MetricsCollector:
        """Get the metrics collector (lazy-initialized)."""
        return self._metrics_collector

    def get_lifecycle_manager(self) -> LifecycleManager:
        """Get the lifecycle manager (lazy-initialized)."""
        return self._lifecycle_manager

    def get_plugin_registry(self) -> "PluginRegistry":
        """Get the plugin registry (lazy-initialized)."""
        return self._plugin_registry

    @property
    def is_initialized(self) -> bool:
        """Check if core services have been initialized (always True after __init__)."""
        return len(self._initialized_services) > 0

    def get_initialized_services(self) -> set[str]:
        """Get set of initialized service names."""
        return self._initialized_services.copy()

    def initialize(self) -> None:
        """
        Optional: Pre-initialize all optional dependencies.
        
        Core dependencies (llm_manager, session_manager, memory_manager, 
        agent_factory, llm_registry) are already initialized in __init__.
        This method pre-initializes optional dependencies.
        """
        # Touch optional properties to trigger initialization
        _ = (
            self._metrics_collector,
            self._agent_registry,
            self._tool_registry,
            self._plugin_registry,
            self._lifecycle_manager,
        )
        logger.info(f"All optional services pre-initialized: {self._initialized_services}")

