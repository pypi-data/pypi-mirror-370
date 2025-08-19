"""SessionTransferred event type."""

from typing import Literal
from pydantic import BaseModel

from .event_base import EventBase

# Import Session from conversations package
# This creates a dependency on antonnia-conversations
from antonnia.conversations.types import Session

class SessionTransferredData(BaseModel):
    """Data payload for session.transferred event."""
    
    object: Session

class SessionTransferred(EventBase[SessionTransferredData, Literal["session.transferred"]]):
    """Event fired when a session is transferred."""
    
    type: Literal["session.transferred"] = "session.transferred" 