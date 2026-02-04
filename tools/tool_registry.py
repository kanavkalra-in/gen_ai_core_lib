"""
Tool registry for managing and accessing agent tools.
"""
from typing import Dict, List, Optional
from threading import Lock

from langchain_core.tools import BaseTool

from ..exceptions import ToolNotFoundError
from ..config.logging_config import logger


class ToolRegistry:
    """
    Registry for managing agent tools.
    Provides thread-safe access to registered tools.
    """
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._lock = Lock()
    
    def register(self, name: str, tool: BaseTool) -> None:
        """
        Register a tool.
        
        Args:
            name: Tool name (must be unique)
            tool: Tool instance
        """
        with self._lock:
            if name in self._tools:
                logger.warning(f"Tool '{name}' already registered, overwriting")
            self._tools[name] = tool
            logger.info(f"Registered tool: {name}")
    
    def register_many(self, tools: Dict[str, BaseTool]) -> None:
        """
        Register multiple tools at once.
        
        Args:
            tools: Dictionary mapping tool names to tool instances
        """
        with self._lock:
            for name, tool in tools.items():
                self._tools[name] = tool
            logger.info(f"Registered {len(tools)} tools")
    
    def get_tool(self, name: str) -> BaseTool:
        """
        Get tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance
            
        Raises:
            ToolNotFoundError: If tool is not found
        """
        with self._lock:
            if name not in self._tools:
                available = list(self._tools.keys())
                raise ToolNotFoundError(
                    f"Tool '{name}' not found. Available tools: {available}"
                )
            return self._tools[name]
    
    def get_tools(self, names: Optional[List[str]] = None) -> List[BaseTool]:
        """
        Get tools by names, or all tools if names not provided.
        
        Args:
            names: Optional list of tool names
            
        Returns:
            List of tool instances
        """
        with self._lock:
            if names is None:
                return list(self._tools.values())
            
            tools = []
            for name in names:
                if name in self._tools:
                    tools.append(self._tools[name])
                else:
                    logger.warning(f"Tool '{name}' not found, skipping")
            return tools
    
    def list_tools(self) -> List[str]:
        """
        List all registered tool names.
        
        Returns:
            List of tool names
        """
        with self._lock:
            return list(self._tools.keys())
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            name: Tool name
            
        Returns:
            True if tool was removed, False if not found
        """
        with self._lock:
            if name in self._tools:
                del self._tools[name]
                logger.info(f"Unregistered tool: {name}")
                return True
            return False
    
    def clear(self) -> None:
        """Clear all registered tools."""
        with self._lock:
            self._tools.clear()
            logger.info("Cleared tool registry")
