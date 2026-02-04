"""
Session-specific configuration.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SessionConfig:
    """Configuration for session management."""
    timeout_hours: int = 24
    max_sessions: Optional[int] = None
