"""
Memory manager for conversation history.
Implements memory strategies (trim, summarize, etc.)
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from threading import Lock

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from .memory_config import MemoryConfig, MemoryStrategy
from ..exceptions import MemoryStrategyError
from ..config.logging_config import logger


class MemoryManager(ABC):
    """
    Abstract memory manager for conversation history.
    Handles storage and retrieval of conversation messages.
    """
    
    @abstractmethod
    async def get_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[BaseMessage]:
        """
        Retrieve conversation history.
        
        Args:
            session_id: Session identifier
            limit: Optional limit on number of messages
            
        Returns:
            List of messages in chronological order
        """
        pass
    
    @abstractmethod
    async def add_message(
        self,
        session_id: str,
        message: BaseMessage
    ) -> None:
        """
        Add message to history.
        
        Args:
            session_id: Session identifier
            message: Message to add
        """
        pass
    
    @abstractmethod
    async def clear_history(
        self,
        session_id: str
    ) -> None:
        """
        Clear conversation history for a session.
        
        Args:
            session_id: Session identifier
        """
        pass
    
    @abstractmethod
    async def apply_memory_strategy(
        self,
        session_id: str,
        config: MemoryConfig,
        llm: Optional[BaseChatModel] = None
    ) -> List[BaseMessage]:
        """
        Apply memory strategy (trim/summarize) to conversation history.
        
        Args:
            session_id: Session identifier
            config: Memory configuration
            llm: Optional LLM for summarization
            
        Returns:
            Processed list of messages
        """
        pass


class InMemoryMemoryManager(MemoryManager):
    """
    In-memory implementation of memory manager.
    Suitable for single-process applications and testing.
    """
    
    def __init__(self):
        self._histories: dict[str, List[BaseMessage]] = {}
        self._lock = Lock()
    
    async def get_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[BaseMessage]:
        """Retrieve conversation history."""
        with self._lock:
            messages = self._histories.get(session_id, [])
            if limit:
                return messages[-limit:]
            return messages.copy()
    
    async def add_message(
        self,
        session_id: str,
        message: BaseMessage
    ) -> None:
        """Add message to history."""
        with self._lock:
            if session_id not in self._histories:
                self._histories[session_id] = []
            self._histories[session_id].append(message)
            logger.debug(f"Added message to history for session {session_id}")
    
    async def clear_history(
        self,
        session_id: str
    ) -> None:
        """Clear conversation history."""
        with self._lock:
            if session_id in self._histories:
                del self._histories[session_id]
                logger.info(f"Cleared history for session {session_id}")
    
    async def apply_memory_strategy(
        self,
        session_id: str,
        config: MemoryConfig,
        llm: Optional[BaseChatModel] = None
    ) -> List[BaseMessage]:
        """Apply memory strategy."""
        with self._lock:
            messages = self._histories.get(session_id, [])
            
            if config.strategy == MemoryStrategy.NONE:
                return messages.copy()
            
            elif config.strategy == MemoryStrategy.TRIM:
                return self._apply_trim(messages, config)
            
            elif config.strategy == MemoryStrategy.SUMMARIZE:
                if not llm:
                    raise MemoryStrategyError(
                        "LLM is required for summarize strategy"
                    )
                return await self._apply_summarize(messages, config, llm)
            
            elif config.strategy == MemoryStrategy.TRIM_AND_SUMMARIZE:
                if not llm:
                    raise MemoryStrategyError(
                        "LLM is required for trim_and_summarize strategy"
                    )
                return await self._apply_trim_and_summarize(messages, config, llm)
            
            else:
                raise MemoryStrategyError(f"Unknown strategy: {config.strategy}")
    
    def _apply_trim(
        self,
        messages: List[BaseMessage],
        config: MemoryConfig
    ) -> List[BaseMessage]:
        """Apply trim strategy - keep only recent messages."""
        if len(messages) <= config.trim_keep_messages:
            return messages.copy()
        
        # Keep system messages and recent messages
        system_messages = [m for m in messages if isinstance(m, SystemMessage)]
        other_messages = [m for m in messages if not isinstance(m, SystemMessage)]
        recent_messages = other_messages[-config.trim_keep_messages:]
        
        return system_messages + recent_messages
    
    async def _apply_summarize(
        self,
        messages: List[BaseMessage],
        config: MemoryConfig,
        llm: BaseChatModel
    ) -> List[BaseMessage]:
        """Apply summarize strategy - summarize old messages."""
        if len(messages) <= config.summarize_threshold:
            return messages.copy()
        
        # Separate system messages, old messages, and recent messages
        system_messages = [m for m in messages if isinstance(m, SystemMessage)]
        other_messages = [m for m in messages if not isinstance(m, SystemMessage)]
        
        if len(other_messages) <= config.summarize_threshold:
            return messages.copy()
        
        # Messages to summarize (all except recent ones)
        messages_to_summarize = other_messages[:-config.summarize_threshold]
        recent_messages = other_messages[-config.summarize_threshold:]
        
        # Create summary
        summary_text = self._messages_to_text(messages_to_summarize)
        summary_prompt = f"Summarize the following conversation history:\n\n{summary_text}"
        
        try:
            summary_response = await llm.ainvoke(summary_prompt)
            summary_content = summary_response.content if hasattr(summary_response, 'content') else str(summary_response)
            
            # Create summary message
            summary_message = AIMessage(content=f"[Summarized conversation history: {summary_content}]")
            
            return system_messages + [summary_message] + recent_messages
        except Exception as e:
            logger.error(f"Failed to summarize messages: {e}", exc_info=True)
            raise MemoryStrategyError(f"Summarization failed: {str(e)}") from e
    
    async def _apply_trim_and_summarize(
        self,
        messages: List[BaseMessage],
        config: MemoryConfig,
        llm: BaseChatModel
    ) -> List[BaseMessage]:
        """Apply both trim and summarize strategies."""
        # First trim
        trimmed = self._apply_trim(messages, config)
        
        # Then summarize if still over threshold
        if len(trimmed) > config.summarize_threshold:
            return await self._apply_summarize(trimmed, config, llm)
        
        return trimmed
    
    def _messages_to_text(self, messages: List[BaseMessage]) -> str:
        """Convert messages to text for summarization."""
        text_parts = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                text_parts.append(f"Human: {msg.content}")
            elif isinstance(msg, AIMessage):
                text_parts.append(f"Assistant: {msg.content}")
            else:
                text_parts.append(str(msg.content))
        return "\n".join(text_parts)
