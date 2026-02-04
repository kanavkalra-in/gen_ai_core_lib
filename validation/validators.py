"""
Pydantic validators for input validation.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, validator, Field

from ..exceptions import ValidationError


class ChatRequest(BaseModel):
    """Validated chat request."""
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Message cannot be empty")
        return v.strip()
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"


class AgentCreateRequest(BaseModel):
    """Validated agent creation request."""
    agent_id: str = Field(..., min_length=1, max_length=100)
    agent_type: str = Field(..., min_length=1, max_length=100)
    system_prompt: str = Field(..., min_length=1, max_length=50000)
    model_name: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=100000)
    tools: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"


class SessionCreateRequest(BaseModel):
    """Validated session creation request."""
    session_id: Optional[str] = Field(None, max_length=200)
    user_id: Optional[str] = Field(None, max_length=200)
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"


def validate_chat_request(data: Dict[str, Any]) -> ChatRequest:
    """
    Validate and create ChatRequest from dictionary.
    
    Args:
        data: Request data dictionary
        
    Returns:
        Validated ChatRequest
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        return ChatRequest(**data)
    except Exception as e:
        raise ValidationError(f"Invalid chat request: {str(e)}") from e
