"""
Test fixtures and utilities for testing.
"""
from typing import Optional
from unittest.mock import Mock, MagicMock
import threading

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage

from ..dependencies.application_container import ApplicationContainer
from ..llm.llm_manager import LLMManager
from ..session.session_manager import SessionManager
from ..memory.memory_manager import MemoryManager, InMemoryMemoryManager
from ..config.logging_config import logger


class TestLLMManager(LLMManager):
    """Mock LLM manager for testing."""
    
    def __init__(self):
        # Initialize with minimal dependencies
        super().__init__()
        self._mock_llm = None
    
    def get_llm(self, **kwargs) -> BaseChatModel:
        """Get mock LLM for testing."""
        if self._mock_llm is None:
            self._mock_llm = Mock(spec=BaseChatModel)
            # Make it callable
            self._mock_llm.invoke = Mock(return_value=AIMessage(content="Test response"))
            self._mock_llm.ainvoke = Mock(return_value=AIMessage(content="Test async response"))
        return self._mock_llm
    
    def set_mock_llm(self, mock_llm: BaseChatModel) -> None:
        """Set custom mock LLM."""
        self._mock_llm = mock_llm


class TestSessionManager(SessionManager):
    """Mock session manager for testing."""
    
    def __init__(self):
        # Initialize with minimal configuration
        from datetime import timedelta
        super().__init__(
            session_timeout=timedelta(hours=1),
            max_sessions=None
        )


class TestMemoryManager(InMemoryMemoryManager):
    """Test memory manager (uses in-memory implementation)."""
    pass


class TestApplicationContainer(ApplicationContainer):
    """Test application container with test dependencies."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._initialized_services = set()
        self._test_mode = True
        # Override core dependencies initialization with test versions
        self._initialize_test_core_dependencies()
    
    def _initialize_test_core_dependencies(self) -> None:
        """Initialize core dependencies with test implementations."""
        # Initialize test LLM registry (simplified for testing)
        from ..llm.llm_manager import LLMManagerRegistry
        self._llm_registry = LLMManagerRegistry()
        self._initialized_services.add("llm_registry")
        logger.info("Test LLM registry initialized")
        
        # Initialize test LLM manager
        self._llm_manager = TestLLMManager()
        self._initialized_services.add("llm_manager")
        logger.info("Test LLM manager initialized")
        
        # Initialize test session manager
        self._session_manager = TestSessionManager()
        self._initialized_services.add("session_manager")
        logger.info("Test session manager initialized")
        
        # Initialize test memory manager
        self._memory_manager = TestMemoryManager()
        self._initialized_services.add("memory_manager")
        logger.info("Test memory manager initialized")
        
        # Initialize test agent factory
        from ..agents.agent_factory import DefaultAgentFactory
        self._agent_factory = DefaultAgentFactory()
        self._initialized_services.add("agent_factory")
        logger.info("Test agent factory initialized")
        
        logger.info("Test core dependencies initialized")
    
    def initialize(self) -> None:
        """
        Optional: Pre-initialize optional test dependencies.
        Core dependencies are already initialized in __init__.
        """
        logger.info(f"Test application container initialized: {self._initialized_services}")


# Pytest-style fixtures (can be used with pytest or manually)
def test_container() -> TestApplicationContainer:
    """Create test application container."""
    container = TestApplicationContainer()
    container.initialize()
    return container


def test_llm_manager() -> TestLLMManager:
    """Create test LLM manager."""
    return TestLLMManager()


def test_session_manager() -> TestSessionManager:
    """Create test session manager."""
    return TestSessionManager()


def test_memory_manager() -> TestMemoryManager:
    """Create test memory manager."""
    return TestMemoryManager()
