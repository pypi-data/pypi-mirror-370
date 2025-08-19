# Antonnia Events

Python SDK for Antonnia Events and Webhooks

## Overview

The `antonnia-events` package provides type-safe event definitions for Antonnia webhook events. It's part of the Antonnia Python SDK ecosystem and works seamlessly with other Antonnia packages.

## Installation

```bash
pip install antonnia-events
```

Note: This package has a dependency on `antonnia-conversations` for the underlying data types.

## Quick Start

```python
from antonnia.events import Event, MessageCreated, SessionCreated

# Parse webhook events
def handle_webhook(event_data: dict):
    event = Event.model_validate(event_data)
    
    if isinstance(event, MessageCreated):
        print(f"New message: {event.data.object.id}")
    elif isinstance(event, SessionCreated):
        print(f"New session: {event.data.object.id}")
```

## Event Types

### Available Events

- `MessageCreated` - Fired when a new message is created
- `SessionCreated` - Fired when a new session is created  
- `SessionFinished` - Fired when a session is finished
- `SessionTransferred` - Fired when a session is transferred

### Event Structure

All events inherit from `EventBase` and have this structure:

```python
{
    "id": "event_123",
    "created_at": "2023-12-01T12:00:00Z",
    "type": "message.created",
    "data": {
        "object": {
            # The actual Message or Session object
        }
    }
}
```

## Usage with Frameworks

### FastAPI

```python
from fastapi import FastAPI
from antonnia.events import Event

app = FastAPI()

@app.post("/webhook")
async def handle_webhook(event: Event):
    # Event is automatically validated and parsed
    return {"status": "received"}
```

### Flask

```python
from flask import Flask, request
from antonnia.events import Event

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    event = Event.model_validate(request.json)
    # Handle the event
    return {"status": "received"}
```

## Type Safety

The package provides full type safety with discriminated unions:

```python
from antonnia.events import Event, MessageCreated

def process_event(event: Event):
    # Type checker knows the event type based on isinstance check
    if isinstance(event, MessageCreated):
        # event.data.object is typed as Message
        message = event.data.object
        print(f"Message content: {message.content}")
```

## Development

### Installing for Development

```bash
pip install -e .[dev]
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy .
```

## License

MIT License - see LICENSE file for details.

## Related Packages

- [`antonnia-conversations`](https://pypi.org/project/antonnia-conversations/) - Conversations API client
- More Antonnia packages coming soon!

## Support

For support, please visit [https://antonnia.com/support](https://antonnia.com/support) or create an issue in our GitHub repository. 