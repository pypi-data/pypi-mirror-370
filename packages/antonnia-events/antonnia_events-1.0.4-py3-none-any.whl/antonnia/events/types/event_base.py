"""Base event class for all Antonnia events."""

from datetime import datetime, timezone
from typing import TypeVar, Generic
from uuid import uuid4

from pydantic import BaseModel, Field

D = TypeVar('D', bound=BaseModel)
T = TypeVar('T', bound=str)


class EventBase(BaseModel, Generic[D, T]):
    """Base class for all Antonnia events."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    type: T
    data: D 