"""SessionFinished event type."""

from typing import Literal, Optional
from pydantic import BaseModel

from .event_base import EventBase

# Import Session from conversations package
# This creates a dependency on antonnia-conversations
from antonnia.conversations.types import Session

class SessionFinishedData(BaseModel):
    """Data payload for session.finished event."""
    
    object: Session
    action: Optional[Literal["expired"]] = None

class SessionFinished(EventBase[SessionFinishedData, Literal["session.finished"]]):
    """Event fired when a session is finished."""
    
    type: Literal["session.finished"] = "session.finished" 