"""
Plugin interface and registry for extending functionality.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from threading import Lock

from ..dependencies.application_container import ApplicationContainer
from ..config.logging_config import logger
from ..exceptions import GenAICoreException


class Plugin(ABC):
    """
    Base plugin interface.
    Plugins can extend functionality by registering components.
    """
    
    @abstractmethod
    def initialize(self, container: ApplicationContainer) -> None:
        """
        Initialize plugin with application container.
        
        Args:
            container: Application container with all dependencies
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get plugin name.
        
        Returns:
            Plugin name
        """
        pass
    
    def get_version(self) -> str:
        """
        Get plugin version.
        
        Returns:
            Plugin version (default: "1.0.0")
        """
        return "1.0.0"
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get plugin metadata.
        
        Returns:
            Dictionary with plugin metadata
        """
        return {}


class PluginRegistry:
    """
    Registry for managing plugins.
    """
    
    def __init__(self):
        self._plugins: Dict[str, Plugin] = {}
        self._lock = Lock()
    
    def register(self, plugin: Plugin) -> None:
        """
        Register a plugin.
        
        Args:
            plugin: Plugin instance
        """
        with self._lock:
            name = plugin.get_name()
            if name in self._plugins:
                logger.warning(f"Plugin '{name}' already registered, overwriting")
            self._plugins[name] = plugin
            logger.info(f"Registered plugin: {name} (version: {plugin.get_version()})")
    
    def initialize_all(self, container: ApplicationContainer) -> None:
        """
        Initialize all registered plugins.
        
        Args:
            container: Application container
            
        Raises:
            GenAICoreException: If plugin initialization fails
        """
        with self._lock:
            plugins = list(self._plugins.values())
        
        logger.info(f"Initializing {len(plugins)} plugins")
        
        for plugin in plugins:
            try:
                logger.debug(f"Initializing plugin: {plugin.get_name()}")
                plugin.initialize(container)
                logger.debug(f"Initialized plugin: {plugin.get_name()}")
            except Exception as e:
                logger.error(f"Failed to initialize plugin '{plugin.get_name()}': {e}", exc_info=True)
                raise GenAICoreException(
                    f"Plugin '{plugin.get_name()}' initialization failed: {str(e)}"
                ) from e
        
        logger.info("All plugins initialized successfully")
    
    def get_plugin(self, name: str) -> Plugin:
        """
        Get plugin by name.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin instance
            
        Raises:
            KeyError: If plugin not found
        """
        with self._lock:
            if name not in self._plugins:
                available = list(self._plugins.keys())
                raise KeyError(
                    f"Plugin '{name}' not found. Available plugins: {available}"
                )
            return self._plugins[name]
    
    def list_plugins(self) -> List[str]:
        """
        List all registered plugin names.
        
        Returns:
            List of plugin names
        """
        with self._lock:
            return list(self._plugins.keys())
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a plugin.
        
        Args:
            name: Plugin name
            
        Returns:
            True if plugin was removed, False if not found
        """
        with self._lock:
            if name in self._plugins:
                del self._plugins[name]
                logger.info(f"Unregistered plugin: {name}")
                return True
            return False
    
    def clear(self) -> None:
        """Clear all registered plugins."""
        with self._lock:
            self._plugins.clear()
            logger.info("Cleared plugin registry")
