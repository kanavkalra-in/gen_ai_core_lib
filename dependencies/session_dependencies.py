"""
Session Management Dependencies for FastAPI

Provides dependency injection for session management to reduce boilerplate.
These helpers are optional and only required when using FastAPI.
"""
from typing import Optional
from datetime import timedelta
from threading import Lock

from fastapi import Depends, HTTPException, Header, Cookie

from ..config.logging_config import logger
from ..config.settings import settings
from ..session.session_manager import Session, SessionManager


# Global session manager singleton
_session_manager: Optional[SessionManager] = None
_session_manager_lock = Lock()


def get_session_manager() -> SessionManager:
    """
    Get or create the global session manager singleton.
    Thread-safe double-checked locking pattern.
    
    Returns:
        SessionManager instance
    """
    global _session_manager
    if _session_manager is None:
        with _session_manager_lock:
            # Double-check after acquiring lock
            if _session_manager is None:
                _session_manager = SessionManager(
                    session_timeout=timedelta(hours=settings.SESSION_TIMEOUT_HOURS),
                    max_sessions=settings.MAX_CONCURRENT_SESSIONS
                )
                logger.info("Session manager initialized")
    
    return _session_manager


def get_or_create_session(
    session_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> Session:
    """
    FastAPI dependency that gets or creates a session.
    Activity is automatically updated and persisted to Redis.
    
    Usage:
        @router.post("/chat")
        async def chat(
            request: ChatRequest,
            session: ChatbotSession = Depends(get_or_create_session)
        ):
            # session is automatically available
            ...
    
    Args:
        session_id: Optional session ID
        user_id: Optional user ID
        
        Returns:
            Session instance
        
    Raises:
        HTTPException: If session creation fails
    """
    try:
        session_manager = get_session_manager()
        # get_or_create_session already updates activity and saves to Redis
        session = session_manager.get_or_create_session(
            session_id=session_id,
            user_id=user_id
        )
        return session
    except RuntimeError as e:
        logger.error(f"Failed to get or create session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Session management error: {str(e)}"
        )


def get_session_from_path(session_id: str) -> Session:
    """
    FastAPI dependency that gets an EXISTING session from URL path parameter.
    Raises 404 if session doesn't exist. Does NOT create new sessions.
    
    **When to use:**
    - For endpoints where session_id is in the URL path (e.g., `/sessions/{session_id}`)
    - When you need to validate that a session exists before proceeding
    - For GET, DELETE, or UPDATE operations on specific sessions
    - When you want to return 404 if session doesn't exist (not create a new one)
    
    **Examples:**
        # GET session info - validates session exists
        @router.get("/sessions/{session_id}")
        async def get_session_info(
            session_id: str,
            session: ChatbotSession = Depends(get_session_from_path)
        ):
            return session.to_dict()
        
        # DELETE session - validates session exists first
        @router.delete("/sessions/{session_id}")
        async def delete_session(
            session_id: str,
            session: ChatbotSession = Depends(get_session_from_path)
        ):
            # session is guaranteed to exist here
            ...
    
    **Do NOT use for:**
    - POST endpoints that should create sessions if they don't exist
    - Endpoints where session comes from headers/cookies (use get_session_from_headers)
    
    Args:
        session_id: Session ID from path parameter (automatically injected by FastAPI)
        
        Returns:
            Session instance
        
    Raises:
        HTTPException: 404 if session not found
    """
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    return session


def get_session_from_headers(
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID", description="Session ID from header"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID", description="User ID from header"),
    session_id: Optional[str] = Cookie(None, description="Session ID from cookie"),
    user_id: Optional[str] = Cookie(None, description="User ID from cookie")
    ) -> Session:
    """
    Dependency that extracts session info from HTTP headers or cookies and gets/creates session.
    Creates a new session if one doesn't exist. Priority: X-Session-ID/X-User-ID headers > session_id/user_id cookies
    
    **When to use:**
    - For POST/PUT endpoints where session comes from headers/cookies (not URL path)
    - When you want to automatically create a session if it doesn't exist
    - For chat endpoints, API calls from web/mobile clients
    - When session_id is NOT in the URL path
    
    **Examples:**
        # Chat endpoint - creates session if needed
        @router.post("/chat")
        async def chat(
            request: ChatRequest,
            session: ChatbotSession = Depends(get_session_from_headers)
        ):
            # If no X-Session-ID header, a new session is created automatically
            return {"response": "...", "session_id": session.session_id}
        
        # Update endpoint with session from headers
        @router.put("/preferences")
        async def update_preferences(
            prefs: Preferences,
            session: ChatbotSession = Depends(get_session_from_headers)
        ):
            # Uses existing session or creates new one
            ...
    
    **Do NOT use for:**
    - Endpoints where session_id is in the URL path (use get_session_from_path)
    - When you need to return 404 if session doesn't exist (use get_session_from_path)
    
    **Session ID Sources (priority order):**
    1. X-Session-ID header (highest priority)
    2. session_id cookie (fallback)
    3. New session created if neither provided
    
    **User ID Sources (priority order):**
    1. X-User-ID header (highest priority)
    2. user_id cookie (fallback)
    3. None if neither provided
    
    Args:
        x_session_id: Session ID from X-Session-ID header
        x_user_id: User ID from X-User-ID header
        session_id: Session ID from cookie (fallback)
        user_id: User ID from cookie (fallback)
        
        Returns:
            Session instance (existing or newly created)
        
    Raises:
        HTTPException: If session creation fails
    """
    # Prefer headers over cookies
    final_session_id = x_session_id or session_id
    final_user_id = x_user_id or user_id
    
    return get_or_create_session(
        session_id=final_session_id,
        user_id=final_user_id
    )


def get_session_manager_dependency() -> SessionManager:
    """
    FastAPI dependency that returns the session manager.
    
        Usage:
            @router.get("/sessions/stats")
            async def get_stats(
                manager: SessionManager = Depends(get_session_manager_dependency)
            ):
                return manager.get_session_stats()
    
        Returns:
            SessionManager instance
    """
    return get_session_manager()

