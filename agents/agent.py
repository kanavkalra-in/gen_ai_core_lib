"""
Agent interface and configuration for chatbots and AI agents.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from langchain_core.messages import BaseMessage
from langchain_core.language_models import BaseChatModel

from ..memory.memory_config import MemoryConfig
from ..exceptions import AgentError


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    agent_id: str
    agent_type: str
    system_prompt: str
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    tools: List[str] = None  # List of tool names
    memory_config: Optional[MemoryConfig] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = []
        if self.metadata is None:
            self.metadata = {}


class Agent(ABC):
    """
    Base interface for all agents/chatbots.
    
    This is the core abstraction that all agent implementations must follow.
    Agents handle user input, manage conversation context, and produce responses.
    """
    
    def __init__(self, config: AgentConfig, llm: BaseChatModel):
        """
        Initialize agent.
        
        Args:
            config: Agent configuration
            llm: Language model instance
        """
        self.config = config
        self.llm = llm
    
    @abstractmethod
    async def invoke(
        self,
        input: str | Dict[str, Any],
        session_id: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user input and return response.
        
        Args:
            input: User input (string or structured dict)
            session_id: Session identifier for conversation context
            config: Optional runtime configuration
            
        Returns:
            Dictionary with response and metadata:
            {
                "response": str,
                "session_id": str,
                "metadata": dict
            }
            
        Raises:
            AgentError: If agent execution fails
        """
        pass
    
    @abstractmethod
    def get_tools(self) -> List[Any]:
        """
        Get available tools for this agent.
        
        Returns:
            List of tool instances (BaseTool or compatible)
        """
        pass
    
    def get_memory_config(self) -> Optional[MemoryConfig]:
        """
        Get memory configuration for this agent.
        
        Returns:
            MemoryConfig if configured, None otherwise
        """
        return self.config.memory_config
    
    def get_agent_id(self) -> str:
        """Get agent identifier."""
        return self.config.agent_id
    
    def get_agent_type(self) -> str:
        """Get agent type."""
        return self.config.agent_type
