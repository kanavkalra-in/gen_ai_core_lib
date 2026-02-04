"""
Metrics collection for observability.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from threading import Lock
from datetime import datetime
from collections import defaultdict

from ..config.logging_config import logger


class MetricsCollector(ABC):
    """
    Abstract metrics collector.
    Implementations can send metrics to Prometheus, StatsD, etc.
    """
    
    @abstractmethod
    def record_latency(
        self,
        operation: str,
        duration: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record operation latency.
        
        Args:
            operation: Operation name
            duration: Duration in seconds
            tags: Optional tags for filtering
        """
        pass
    
    @abstractmethod
    def record_error(
        self,
        operation: str,
        error: Exception,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record error occurrence.
        
        Args:
            operation: Operation name
            error: Exception instance
            tags: Optional tags for filtering
        """
        pass
    
    @abstractmethod
    def record_token_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record token usage.
        
        Args:
            model: Model name
            input_tokens: Input token count
            output_tokens: Output token count
            tags: Optional tags for filtering
        """
        pass
    
    @abstractmethod
    def increment_counter(
        self,
        name: str,
        value: int = 1,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Increment a counter.
        
        Args:
            name: Counter name
            value: Increment value
            tags: Optional tags for filtering
        """
        pass


class InMemoryMetricsCollector(MetricsCollector):
    """
    In-memory metrics collector.
    Stores metrics in memory for testing and development.
    """
    
    def __init__(self):
        self._latencies: Dict[str, List[float]] = defaultdict(list)
        self._errors: Dict[str, List[Exception]] = defaultdict(list)
        self._token_usage: Dict[str, List[Dict]] = defaultdict(list)
        self._counters: Dict[str, int] = defaultdict(int)
        self._lock = Lock()
    
    def record_latency(
        self,
        operation: str,
        duration: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record operation latency."""
        with self._lock:
            self._latencies[operation].append(duration)
            logger.debug(f"Recorded latency: {operation}={duration}s")
    
    def record_error(
        self,
        operation: str,
        error: Exception,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record error occurrence."""
        with self._lock:
            self._errors[operation].append(error)
            logger.warning(f"Recorded error: {operation}={type(error).__name__}: {str(error)}")
    
    def record_token_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record token usage."""
        with self._lock:
            self._token_usage[model].append({
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "timestamp": datetime.now().isoformat()
            })
            logger.debug(f"Recorded token usage: {model} (in={input_tokens}, out={output_tokens})")
    
    def increment_counter(
        self,
        name: str,
        value: int = 1,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Increment a counter."""
        with self._lock:
            self._counters[name] += value
            logger.debug(f"Incremented counter: {name}={self._counters[name]}")
    
    def get_metrics_summary(self) -> Dict:
        """
        Get summary of collected metrics.
        
        Returns:
            Dictionary with metrics summary
        """
        with self._lock:
            summary = {
                "latencies": {
                    op: {
                        "count": len(latencies),
                        "avg": sum(latencies) / len(latencies) if latencies else 0,
                        "min": min(latencies) if latencies else 0,
                        "max": max(latencies) if latencies else 0,
                    }
                    for op, latencies in self._latencies.items()
                },
                "errors": {
                    op: len(errors)
                    for op, errors in self._errors.items()
                },
                "token_usage": {
                    model: {
                        "total_requests": len(usage),
                        "total_input_tokens": sum(u["input_tokens"] for u in usage),
                        "total_output_tokens": sum(u["output_tokens"] for u in usage),
                    }
                    for model, usage in self._token_usage.items()
                },
                "counters": dict(self._counters),
            }
            return summary
    
    def clear(self) -> None:
        """Clear all collected metrics."""
        with self._lock:
            self._latencies.clear()
            self._errors.clear()
            self._token_usage.clear()
            self._counters.clear()
            logger.info("Cleared metrics")
