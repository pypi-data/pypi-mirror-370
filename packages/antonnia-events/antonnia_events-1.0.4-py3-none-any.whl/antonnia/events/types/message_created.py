"""MessageCreated event type."""

from typing import Literal
from pydantic import BaseModel

from .event_base import EventBase

# Import Message from conversations package
# This creates a dependency on antonnia-conversations
from antonnia.conversations.types import Message

class MessageCreatedData(BaseModel):
    """Data payload for message.created event."""
    
    object: Message

class MessageCreated(EventBase[MessageCreatedData, Literal["message.created"]]):
    """Event fired when a new message is created."""
    
    type: Literal["message.created"] = "message.created" 