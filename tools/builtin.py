"""
Built-in tool registry with common tools.
"""
from typing import Dict

from langchain_core.tools import BaseTool

from .tool_registry import ToolRegistry
from ..config.logging_config import logger


class BuiltinToolRegistry(ToolRegistry):
    """
    Tool registry with built-in common tools.
    Extends ToolRegistry with pre-registered tools.
    """
    
    def __init__(self, include_builtins: bool = True):
        """
        Initialize built-in tool registry.
        
        Args:
            include_builtins: Whether to include built-in tools
        """
        super().__init__()
        if include_builtins:
            self._register_builtins()
    
    def _register_builtins(self) -> None:
        """Register built-in tools."""
        # Built-in tools can be added here
        # For now, this is a placeholder for future common tools
        logger.debug("Built-in tool registry initialized (no built-ins yet)")
