"""
In-memory storage implementation.
"""
from typing import Any, Optional, List, Dict
from threading import Lock
from datetime import datetime, timedelta

from .storage_backend import StorageBackend
from ..config.logging_config import logger


class InMemoryStorage(StorageBackend):
    """
    In-memory storage backend.
    Suitable for single-process applications and testing.
    """
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._ttls: Dict[str, datetime] = {}
        self._lock = Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        with self._lock:
            # Check if expired
            if key in self._ttls:
                if datetime.now() > self._ttls[key]:
                    del self._data[key]
                    del self._ttls[key]
                    return None
            
            return self._data.get(key)
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """Set value with optional TTL."""
        with self._lock:
            self._data[key] = value
            if ttl:
                self._ttls[key] = datetime.now() + timedelta(seconds=ttl)
            elif key in self._ttls:
                del self._ttls[key]
    
    async def delete(self, key: str) -> bool:
        """Delete value by key."""
        with self._lock:
            existed = key in self._data
            self._data.pop(key, None)
            self._ttls.pop(key, None)
            return existed
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        with self._lock:
            # Check if expired
            if key in self._ttls:
                if datetime.now() > self._ttls[key]:
                    del self._data[key]
                    del self._ttls[key]
                    return False
            return key in self._data
    
    async def keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get all keys, optionally filtered by pattern."""
        with self._lock:
            # Clean up expired keys
            now = datetime.now()
            expired = [k for k, expiry in self._ttls.items() if now > expiry]
            for key in expired:
                self._data.pop(key, None)
                self._ttls.pop(key, None)
            
            all_keys = list(self._data.keys())
            
            if pattern:
                # Simple pattern matching (supports * wildcard)
                import fnmatch
                return [k for k in all_keys if fnmatch.fnmatch(k, pattern)]
            
            return all_keys
    
    async def clear(self) -> None:
        """Clear all stored data."""
        with self._lock:
            self._data.clear()
            self._ttls.clear()
            logger.info("Cleared in-memory storage")
