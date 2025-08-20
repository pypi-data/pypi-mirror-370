# RaceResult Python Web API Library

A Python client library for the RaceResult Web API that mirrors the functionality of the Go library.

## Features

- Pythonic API design with dataclasses
- Session management with automatic cleanup
- Event and participant operations
- Raw timing data retrieval
- Easy-to-use endpoint classes
- Type hints for better IDE support

## Installation

```bash
pip install -e .
# or for development:
pip install -r requirements.txt
```

## Quick Start

### Environment Setup

Create a `.env` file with your credentials:
```bash
RACERESULT_API_KEY=your_api_key_here
RACERESULT_USERNAME=your_username
RACERESULT_PASSWORD=your_password
```

### Basic Usage

```python
from rr_webapi import API
import os

# Create API client
api = API("events.raceresult.com", use_https=True)

# Login with API key
api.public().login(api_key=os.getenv("RACERESULT_API_KEY"))

try:
    # Get your events
    events = api.public().event_list()
    print(f"You have {len(events)} events")
    
    # Open an event
    if events:
        event_api = api.event_api(events[0].id)
        
        # Get participants
        participants = event_api.data.list([
            "ID", "BIB", "FIRSTNAME", "LASTNAME", "CONTEST.NAME"
        ])
        print(f"Event has {len(participants)} participants")
        
        # Get raw data for a participant
        if participants:
            raw_data = event_api.rawdata.get_by_pid(participants[0][0])  # ID is first field
            print(f"Participant has {len(raw_data)} raw data entries")

finally:
    # Always logout
    api.public().logout()
```

## API Structure

### Main Components

- **API**: Main client with session management
- **Public**: Authentication and account operations  
- **EventAPI**: Event-specific operations

### Event API Endpoints

- **data**: Participant data retrieval and filtering
- **participants**: Participant management (CRUD)
- **contests**: Contest/category management
- **rawdata**: Raw timing data access

## Authentication

### API Key Authentication
```python
api.public().login(api_key="your_api_key")
```

### Username/Password Authentication  
```python
api.public().login(username="username", password="password")
```

## Data Models

The library uses dataclasses for structured data:

```python
@dataclass
class EventListItem:
    id: str
    name: str
    date: str
    participants: int
    # ... other fields
```

## Examples

See the `../../examples/python/` directory for complete examples:
- `basic_usage.py`: Authentication and basic operations
- `participant_and_rawdata.py`: Advanced participant and timing data operations

## Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

## Requirements

- Python 3.7+
- requests
- python-dateutil
- python-dotenv

## Package Structure

```
rr_webapi/
├── __init__.py          # Main API class
├── api.py              # Core HTTP client
├── public.py           # Public API endpoints
├── eventapi.py         # Event API wrapper
├── general.py          # General utilities
└── endpoints/          # Endpoint implementations
    ├── data.py
    ├── contests.py
    ├── participants.py
    └── rawdata.py
```

## License

This library follows the same license as the original Go library.

## Contributing

1. Follow the existing code patterns
2. Add tests for new functionality
3. Update documentation
4. Ensure examples work with changes 