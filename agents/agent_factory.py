"""
Factory for creating agent instances.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable

from langchain_core.language_models import BaseChatModel

from .agent import Agent, AgentConfig
from ..exceptions import AgentInitializationError, AgentNotFoundError
from ..config.logging_config import logger


class AgentFactory(ABC):
    """
    Abstract factory for creating agents.
    Implementations should register agent types and create instances.
    """
    
    @abstractmethod
    def create_agent(
        self,
        agent_type: str,
        config: Dict[str, Any],
        llm: Optional[BaseChatModel] = None
    ) -> Agent:
        """
        Create an agent instance.
        
        Args:
            agent_type: Type of agent to create
            config: Agent configuration dictionary
            llm: Optional LLM instance (will be created if not provided)
            
        Returns:
            Agent instance
            
        Raises:
            AgentNotFoundError: If agent type is not registered
            AgentInitializationError: If agent creation fails
        """
        pass


class DefaultAgentFactory(AgentFactory):
    """
    Default implementation of agent factory.
    Registers agent types and creates instances.
    """
    
    def __init__(self):
        self._agent_builders: Dict[str, Callable[[AgentConfig, Optional[BaseChatModel]], Agent]] = {}
    
    def register_agent_type(
        self,
        agent_type: str,
        builder: Callable[[AgentConfig, Optional[BaseChatModel]], Agent]
    ) -> None:
        """
        Register an agent type builder.
        
        Args:
            agent_type: Agent type identifier
            builder: Callable that takes (config: AgentConfig, llm: BaseChatModel) -> Agent
        """
        self._agent_builders[agent_type] = builder
        logger.info(f"Registered agent type: {agent_type}")
    
    def create_agent(
        self,
        agent_type: str,
        config: Dict[str, Any],
        llm: Optional[BaseChatModel] = None
    ) -> Agent:
        """
        Create an agent instance.
        
        Args:
            agent_type: Type of agent to create
            config: Agent configuration dictionary
            llm: Optional LLM instance
            
        Returns:
            Agent instance
            
        Raises:
            AgentNotFoundError: If agent type is not registered
            AgentInitializationError: If agent creation fails
        """
        if agent_type not in self._agent_builders:
            available = ", ".join(self._agent_builders.keys())
            raise AgentNotFoundError(
                f"Agent type '{agent_type}' is not registered. "
                f"Available types: {available}"
            )
        
        try:
            # Convert config dict to AgentConfig if needed
            if isinstance(config, dict):
                agent_config = AgentConfig(**config)
            else:
                agent_config = config
            
            builder = self._agent_builders[agent_type]
            agent = builder(agent_config, llm)
            logger.info(f"Created agent: {agent_config.agent_id} (type: {agent_type})")
            return agent
        except Exception as e:
            logger.error(f"Failed to create agent {agent_type}: {e}", exc_info=True)
            raise AgentInitializationError(
                f"Failed to create agent '{agent_type}': {str(e)}"
            ) from e
