"""
Session management for kernel subsystem.
Manages user sessions, each with its own kernel manager instance.
"""

import uuid
import time
from typing import Optional, Dict
from .manager import KernelManager

class Session:
    """
    Encapsulates per-session state, including a dedicated kernel manager.
    """
    def __init__(self, user: Optional[str] = None, notebook_path: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.user = user
        self.notebook_path = notebook_path
        self.kernel_manager = KernelManager()
        self.last_active = time.time()

    async def shutdown(self):
        await self.kernel_manager.shutdown()

# Global session registry
_SESSIONS: Dict[str, Session] = {}

def create_session(user: Optional[str] = None, notebook_path: Optional[str] = None) -> str:
    """
    Create a new session and return its ID.
    """
    session = Session(user=user, notebook_path=notebook_path)
    _SESSIONS[session.id] = session
    return session.id

def get_session(session_id: str) -> Optional[Session]:
    """
    Retrieve a session by its ID.
    """
    return _SESSIONS.get(session_id)

async def destroy_session(session_id: str):
    """
    Destroy a session and shut down its kernel manager.
    """
    session = _SESSIONS.pop(session_id, None)
    if session:
        await session.shutdown()
