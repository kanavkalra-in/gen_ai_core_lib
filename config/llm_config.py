"""
LLM-specific configuration.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMConfig:
    """Configuration for LLM models."""
    model: str
    temperature: float = 0.7
    max_tokens: int = 2000
    api_key: Optional[str] = None
    base_url: Optional[str] = None
