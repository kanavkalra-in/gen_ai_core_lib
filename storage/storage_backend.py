"""
Storage backend interface for key-value storage implementations.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, List


class StorageBackend(ABC):
    """
    Abstract storage backend for key-value storage.
    Implementations can use Redis, database, in-memory, etc.
    """
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value by key.
        
        Args:
            key: Storage key
            
        Returns:
            Stored value or None if not found
        """
        pass
    
    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Set value with optional TTL.
        
        Args:
            key: Storage key
            value: Value to store
            ttl: Optional time-to-live in seconds
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete value by key.
        
        Args:
            key: Storage key
            
        Returns:
            True if key existed and was deleted, False otherwise
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if key exists.
        
        Args:
            key: Storage key
            
        Returns:
            True if key exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        Get all keys, optionally filtered by pattern.
        
        Args:
            pattern: Optional pattern to filter keys (implementation-specific)
            
        Returns:
            List of keys
        """
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all stored data."""
        pass
