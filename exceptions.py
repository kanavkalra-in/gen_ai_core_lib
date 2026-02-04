"""
Custom exceptions for gen_ai_core_lib.

All exceptions inherit from GenAICoreException for easy catching.
"""


class GenAICoreException(Exception):
    """Base exception for all gen_ai_core_lib errors."""
    pass


class SessionError(GenAICoreException):
    """Base exception for session-related errors."""
    pass


class SessionNotFoundError(SessionError):
    """Raised when a session is not found."""
    pass


class SessionExpiredError(SessionError):
    """Raised when a session has expired."""
    pass


class SessionLimitExceededError(SessionError):
    """Raised when maximum session limit is reached."""
    pass


class LLMError(GenAICoreException):
    """Base exception for LLM-related errors."""
    pass


class LLMProviderError(LLMError):
    """Raised when LLM provider fails."""
    pass


class ModelNotFoundError(LLMError):
    """Raised when a model is not found or not supported."""
    pass


class APIKeyError(LLMError):
    """Raised when API key is missing or invalid."""
    pass


class MemoryError(GenAICoreException):
    """Base exception for memory-related errors."""
    pass


class MemoryStrategyError(MemoryError):
    """Raised when memory strategy fails."""
    pass


class AgentError(GenAICoreException):
    """Base exception for agent-related errors."""
    pass


class AgentNotFoundError(AgentError):
    """Raised when an agent is not found."""
    pass


class AgentInitializationError(AgentError):
    """Raised when agent initialization fails."""
    pass


class ToolError(GenAICoreException):
    """Base exception for tool-related errors."""
    pass


class ToolNotFoundError(ToolError):
    """Raised when a tool is not found."""
    pass


class ToolExecutionError(ToolError):
    """Raised when tool execution fails."""
    pass


class StorageError(GenAICoreException):
    """Base exception for storage-related errors."""
    pass


class StorageBackendError(StorageError):
    """Raised when storage backend operation fails."""
    pass


class ConfigurationError(GenAICoreException):
    """Raised when configuration is invalid."""
    pass


class ValidationError(GenAICoreException):
    """Raised when input validation fails."""
    pass
