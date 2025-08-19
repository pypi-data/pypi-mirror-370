"""
Antonnia Events SDK

This package provides event types and utilities for working with Antonnia webhook events.
"""

from .types import (
    # Event types
    Event,
    EventBase,
    MessageCreated,
    MessageCreatedData,
    SessionCreated,
    SessionCreatedData,
    SessionFinished,
    SessionFinishedData,
    SessionTransferred,
    SessionTransferredData,
)

__version__ = "1.0.2"

__all__ = [
    # Event types
    "Event",
    "EventBase", 
    "MessageCreated",
    "MessageCreatedData",
    "SessionCreated",
    "SessionCreatedData",
    "SessionFinished",
    "SessionFinishedData",
    "SessionTransferred",
    "SessionTransferredData",
] 