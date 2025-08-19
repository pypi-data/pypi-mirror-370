"""Main Event union type for all Antonnia events."""

from typing import Annotated, Union

from pydantic import Tag, Discriminator

from .message_created import MessageCreated
from .session_created import SessionCreated
from .session_finished import SessionFinished
from .session_transferred import SessionTransferred


def get_event_type(v: dict) -> str:
    """Extract event type from event data for discrimination."""
    event_type = str(v.get('type'))   
    if not event_type:
        raise ValueError(f"Event type not found in {v}")
    return event_type


Event = Annotated[
    Union[
        Annotated[MessageCreated, Tag('message.created')],
        Annotated[SessionCreated, Tag('session.created')],
        Annotated[SessionFinished, Tag('session.finished')],
        Annotated[SessionTransferred, Tag('session.transferred')]
    ],
    Discriminator(get_event_type),
] 