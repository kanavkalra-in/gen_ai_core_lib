"""
Registry for managing agent instances.
"""
from typing import Dict, Optional
from threading import Lock

from .agent import Agent
from ..exceptions import AgentNotFoundError
from ..config.logging_config import logger


class AgentRegistry:
    """
    Registry for managing agent instances.
    Provides thread-safe access to registered agents.
    """
    
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self._lock = Lock()
    
    def register(self, agent_id: str, agent: Agent) -> None:
        """
        Register an agent instance.
        
        Args:
            agent_id: Unique agent identifier
            agent: Agent instance
        """
        with self._lock:
            self._agents[agent_id] = agent
            logger.info(f"Registered agent: {agent_id}")
    
    def get(self, agent_id: str) -> Agent:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent instance
            
        Raises:
            AgentNotFoundError: If agent is not found
        """
        with self._lock:
            if agent_id not in self._agents:
                available = list(self._agents.keys())
                raise AgentNotFoundError(
                    f"Agent '{agent_id}' not found. "
                    f"Available agents: {available}"
                )
            return self._agents[agent_id]
    
    def unregister(self, agent_id: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if agent was removed, False if not found
        """
        with self._lock:
            if agent_id in self._agents:
                del self._agents[agent_id]
                logger.info(f"Unregistered agent: {agent_id}")
                return True
            return False
    
    def list_agents(self) -> list[str]:
        """
        List all registered agent IDs.
        
        Returns:
            List of agent IDs
        """
        with self._lock:
            return list(self._agents.keys())
    
    def clear(self) -> None:
        """Clear all registered agents."""
        with self._lock:
            self._agents.clear()
            logger.info("Cleared agent registry")
