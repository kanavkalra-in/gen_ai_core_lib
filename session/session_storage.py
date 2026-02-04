"""
Session storage abstraction used by ``ChatbotSessionManager``.

The default implementation provided here is an in-memory store so that the
library works out-of-the-box in any project. For production, you can copy this
interface and provide your own Redis or database-backed implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Iterable, Optional
from threading import Lock


@dataclass
class _SessionRecord:
    data: Dict[str, Any]


class SessionStorage:
    """
    Simple in-memory session storage.

    This mirrors the minimal API expected by ``ChatbotSessionManager`` without
    introducing external dependencies. It is intentionally lightweight and is
    suitable for single-process applications and tests.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, _SessionRecord] = {}
        self._count: int = 0
        self._lock = Lock()

    # Core CRUD operations -------------------------------------------------

    def save_session(self, session_id: str, data: Dict[str, Any], ttl_seconds: int) -> None:
        """Save or update session data. ``ttl_seconds`` is accepted but ignored in-memory."""
        with self._lock:
            self._sessions[session_id] = _SessionRecord(data=data)

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID."""
        with self._lock:
            record = self._sessions.get(session_id)
            return dict(record.data) if record else None

    def delete_session(self, session_id: str) -> bool:
        """Delete session by ID. Returns True if it existed."""
        with self._lock:
            existed = session_id in self._sessions
            self._sessions.pop(session_id, None)
            return existed

    # Session count helpers ------------------------------------------------

    def increment_session_count(self) -> None:
        with self._lock:
            self._count += 1

    def decrement_session_count(self) -> None:
        with self._lock:
            if self._count > 0:
                self._count -= 1

    def get_session_count(self) -> int:
        with self._lock:
            return self._count

    # Scanning helpers -----------------------------------------------------

    def scan_sessions(self) -> Iterable[str]:
        """Return iterable of internal session keys."""
        with self._lock:
            return list(self._sessions.keys())

    def extract_session_id_from_key(self, key: str) -> str:
        """For compatibility with Redis-style keys; here key is already the ID."""
        return key

