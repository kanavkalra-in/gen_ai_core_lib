"""
Distributed tracing support.
"""
from contextlib import contextmanager
from typing import Optional, Dict, Any
import uuid

from ..config.logging_config import logger


class TraceContext:
    """
    Context manager for distributed tracing.
    Tracks request traces across service boundaries.
    """
    
    def __init__(
        self,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize trace context.
        
        Args:
            trace_id: Trace identifier (generated if not provided)
            span_id: Span identifier (generated if not provided)
            parent_span_id: Parent span identifier
            metadata: Optional metadata
        """
        self.trace_id = trace_id or str(uuid.uuid4())
        self.span_id = span_id or str(uuid.uuid4())
        self.parent_span_id = parent_span_id
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trace context to dictionary."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TraceContext':
        """Create trace context from dictionary."""
        return cls(
            trace_id=data.get("trace_id"),
            span_id=data.get("span_id"),
            parent_span_id=data.get("parent_span_id"),
            metadata=data.get("metadata", {}),
        )
    
    @contextmanager
    def span(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Create a child span.
        
        Args:
            operation: Operation name
            metadata: Optional span metadata
        """
        child_span = TraceContext(
            trace_id=self.trace_id,
            parent_span_id=self.span_id,
            metadata={**(self.metadata), **(metadata or {})}
        )
        logger.debug(f"Starting span: {operation} (trace_id={self.trace_id}, span_id={child_span.span_id})")
        try:
            yield child_span
        finally:
            logger.debug(f"Ending span: {operation} (trace_id={self.trace_id}, span_id={child_span.span_id})")


# Global trace context storage (thread-local in production)
_trace_context: Optional[TraceContext] = None


def get_trace_context() -> Optional[TraceContext]:
    """Get current trace context."""
    return _trace_context


def set_trace_context(context: TraceContext) -> None:
    """Set current trace context."""
    global _trace_context
    _trace_context = context


def clear_trace_context() -> None:
    """Clear current trace context."""
    global _trace_context
    _trace_context = None
