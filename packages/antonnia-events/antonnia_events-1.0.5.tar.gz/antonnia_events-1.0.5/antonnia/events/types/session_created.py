"""SessionCreated event type."""

from typing import Literal
from pydantic import BaseModel

from .event_base import EventBase

# Import Session from conversations package
# This creates a dependency on antonnia-conversations
from antonnia.conversations.types import Session

class SessionCreatedData(BaseModel):
    """Data payload for session.created event."""
    
    object: Session

class SessionCreated(EventBase[SessionCreatedData, Literal["session.created"]]):
    """Event fired when a new session is created."""
    
    type: Literal["session.created"] = "session.created" 