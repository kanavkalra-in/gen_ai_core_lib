"""
Adapter to make SessionStorage compatible with StorageBackend interface.
"""
from typing import Dict, Any, Iterable, Optional, List

from ..session.session_storage import SessionStorage
from .storage_backend import StorageBackend


class SessionStorageAdapter(StorageBackend):
    """
    Adapter that wraps SessionStorage to implement StorageBackend interface.
    Maintains backward compatibility with existing SessionStorage.
    """
    
    def __init__(self, session_storage: Optional[SessionStorage] = None):
        """
        Initialize adapter.
        
        Args:
            session_storage: Optional SessionStorage instance (creates new if not provided)
        """
        self._storage = session_storage or SessionStorage()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get session data by key."""
        return self._storage.get_session(key)
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """Set session data with optional TTL."""
        if isinstance(value, dict):
            self._storage.save_session(key, value, ttl or 0)
        else:
            raise ValueError("SessionStorage only accepts dict values")
    
    async def delete(self, key: str) -> bool:
        """Delete session by key."""
        return self._storage.delete_session(key)
    
    async def exists(self, key: str) -> bool:
        """Check if session exists."""
        return self._storage.get_session(key) is not None
    
    async def keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get all session keys."""
        keys = list(self._storage.scan_sessions())
        if pattern:
            import fnmatch
            return [k for k in keys if fnmatch.fnmatch(k, pattern)]
        return keys
    
    async def clear(self) -> None:
        """Clear all sessions."""
        keys = await self.keys()
        for key in keys:
            await self.delete(key)
