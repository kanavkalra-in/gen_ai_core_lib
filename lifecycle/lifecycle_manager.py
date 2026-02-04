"""
Lifecycle management for application startup and shutdown.
"""
from typing import Callable, List, Optional
from threading import Lock

from ..config.logging_config import logger
from ..exceptions import GenAICoreException


class LifecycleManager:
    """
    Manages application lifecycle hooks.
    Allows components to register startup and shutdown hooks.
    """
    
    def __init__(self):
        self._startup_hooks: List[Callable] = []
        self._shutdown_hooks: List[Callable] = []
        self._lock = Lock()
        self._started = False
    
    def add_startup_hook(self, hook: Callable, name: Optional[str] = None) -> None:
        """
        Register startup hook.
        
        Args:
            hook: Callable to execute on startup (can be async or sync)
            name: Optional name for logging
        """
        with self._lock:
            self._startup_hooks.append((hook, name or hook.__name__))
            logger.debug(f"Registered startup hook: {name or hook.__name__}")
    
    def add_shutdown_hook(self, hook: Callable, name: Optional[str] = None) -> None:
        """
        Register shutdown hook.
        
        Args:
            hook: Callable to execute on shutdown (can be async or sync)
            name: Optional name for logging
        """
        with self._lock:
            self._shutdown_hooks.append((hook, name or hook.__name__))
            logger.debug(f"Registered shutdown hook: {name or hook.__name__}")
    
    async def startup(self) -> None:
        """
        Execute all startup hooks.
        
        Raises:
            GenAICoreException: If startup fails
        """
        with self._lock:
            if self._started:
                logger.warning("Lifecycle manager already started")
                return
            hooks = self._startup_hooks.copy()
        
        logger.info(f"Starting application ({len(hooks)} startup hooks)")
        
        for hook, name in hooks:
            try:
                logger.debug(f"Executing startup hook: {name}")
                if callable(hook):
                    # Check if it's async
                    import asyncio
                    import inspect
                    if inspect.iscoroutinefunction(hook):
                        await hook()
                    else:
                        hook()
                logger.debug(f"Completed startup hook: {name}")
            except Exception as e:
                logger.error(f"Startup hook '{name}' failed: {e}", exc_info=True)
                raise GenAICoreException(f"Startup hook '{name}' failed: {str(e)}") from e
        
        with self._lock:
            self._started = True
        
        logger.info("Application started successfully")
    
    async def shutdown(self) -> None:
        """
        Execute all shutdown hooks in reverse order.
        
        Raises:
            GenAICoreException: If shutdown fails
        """
        with self._lock:
            if not self._started:
                logger.warning("Lifecycle manager not started")
                return
            hooks = list(reversed(self._shutdown_hooks.copy()))
            self._started = False
        
        logger.info(f"Shutting down application ({len(hooks)} shutdown hooks)")
        
        for hook, name in hooks:
            try:
                logger.debug(f"Executing shutdown hook: {name}")
                if callable(hook):
                    import asyncio
                    import inspect
                    if inspect.iscoroutinefunction(hook):
                        await hook()
                    else:
                        hook()
                logger.debug(f"Completed shutdown hook: {name}")
            except Exception as e:
                logger.error(f"Shutdown hook '{name}' failed: {e}", exc_info=True)
                # Don't raise on shutdown - log and continue
                logger.warning(f"Continuing shutdown despite hook '{name}' failure")
        
        logger.info("Application shut down successfully")
    
    @property
    def is_started(self) -> bool:
        """Check if lifecycle manager is started."""
        return self._started
