# Serialization Support

## Overview
Add JSON and pickle serialization support for Option types, enabling persistence and API integration.

## Implementation Plan

### 1. JSON Serialization
```python
# src/optionc/serialization.py

import json
from typing import Any, Dict, TypeVar, Type
from .option import Option
from .some import Some
from .nil import Nil

T = TypeVar('T')

class OptionEncoder(json.JSONEncoder):
    """JSON encoder that can serialize Option types."""

    def default(self, obj: Any) -> Dict[str, Any]:
        if isinstance(obj, Some):
            return {
                "type": "Some",
                "value": obj.get()
            }
        elif isinstance(obj, type(Nil())):
            return {
                "type": "Nil"
            }
        return super().default(obj)

def option_decoder(dct: Dict[str, Any]) -> Any:
    """JSON decoder that can deserialize Option types."""
    if "type" in dct:
        if dct["type"] == "Some":
            return Some(dct["value"])
        elif dct["type"] == "Nil":
            return Nil()
    return dct

# Extension methods for Option classes
def to_json(self) -> str:
    """Serialize Option to JSON string."""
    return json.dumps(self, cls=OptionEncoder)

def to_dict(self) -> Dict[str, Any]:
    """Serialize Option to dictionary."""
    if isinstance(self, Some):
        return {"type": "Some", "value": self.get()}
    else:
        return {"type": "Nil"}

@staticmethod
def from_json(json_str: str) -> Option[Any]:
    """Deserialize Option from JSON string."""
    return json.loads(json_str, object_hook=option_decoder)

@staticmethod
def from_dict(data: Dict[str, Any]) -> Option[Any]:
    """Deserialize Option from dictionary."""
    return option_decoder(data)

# Add methods to Option classes
Some.to_json = to_json
Some.to_dict = to_dict
NilType.to_json = to_json
NilType.to_dict = to_dict
Option.from_json = from_json
Option.from_dict = from_dict
```

### 2. Pickle Support
```python
# Add to Some class
def __getstate__(self):
    """Support for pickle serialization."""
    return {"value": self._value}

def __setstate__(self, state):
    """Support for pickle deserialization."""
    self._value = state["value"]

# Add to NilType class
def __getstate__(self):
    """Support for pickle serialization."""
    return {}

def __setstate__(self, state):
    """Support for pickle deserialization."""
    pass  # Nil has no state
```

### 3. Custom Serialization for Complex Types
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int
    name: str
    created_at: datetime

class AdvancedOptionEncoder(OptionEncoder):
    """Extended encoder for complex types."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return {
                "type": "datetime",
                "value": obj.isoformat()
            }
        elif hasattr(obj, '__dict__'):
            # Handle dataclasses and simple objects
            return {
                "type": obj.__class__.__name__,
                "module": obj.__class__.__module__,
                "value": obj.__dict__
            }
        return super().default(obj)

def advanced_option_decoder(dct: Dict[str, Any]) -> Any:
    """Decoder that handles complex types."""
    if "type" in dct:
        if dct["type"] == "Some":
            return Some(dct["value"])
        elif dct["type"] == "Nil":
            return Nil()
        elif dct["type"] == "datetime":
            return datetime.fromisoformat(dct["value"])
        # Add more type handlers as needed
    return dct
```

### 4. Usage Examples
```python
# Basic JSON serialization
user_option = Some({"id": 123, "name": "Alice"})
json_str = user_option.to_json()  # '{"type": "Some", "value": {"id": 123, "name": "Alice"}}'
restored = Option.from_json(json_str)  # Some({"id": 123, "name": "Alice"})

# Nil serialization
empty_option = Nil()
json_str = empty_option.to_json()  # '{"type": "Nil"}'
restored = Option.from_json(json_str)  # Nil()

# Complex object serialization
user = User(id=1, name="Alice", created_at=datetime.now())
user_option = Some(user)
json_str = json.dumps(user_option, cls=AdvancedOptionEncoder)

# Pickle support
import pickle
user_option = Some("hello world")
pickled = pickle.dumps(user_option)
restored = pickle.loads(pickled)  # Some("hello world")

# API integration example
def save_user_preference(user_id: int, preference: Option[str]):
    """Save user preference to database."""
    data = {
        "user_id": user_id,
        "preference": preference.to_dict()
    }
    requests.post("/api/preferences", json=data)

def load_user_preference(user_id: int) -> Option[str]:
    """Load user preference from API."""
    response = requests.get(f"/api/preferences/{user_id}")
    if response.status_code == 200:
        data = response.json()
        return Option.from_dict(data["preference"])
    return Nil()
```

### 5. Database Integration
```python
# SQLAlchemy integration example
from sqlalchemy import TypeDecorator, String
import json

class OptionType(TypeDecorator):
    """SQLAlchemy type for storing Options in database."""

    impl = String
    cache_ok = True

    def process_bind_param(self, value: Option, dialect):
        """Convert Option to string for database storage."""
        if value is None:
            return None
        return json.dumps(value.to_dict())

    def process_result_value(self, value: str, dialect) -> Option:
        """Convert string from database back to Option."""
        if value is None:
            return Nil()
        data = json.loads(value)
        return Option.from_dict(data)

# Usage in SQLAlchemy model
class UserPreference(Base):
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    setting_value = Column(OptionType)  # Stores Option[str]
```

### 6. Validation and Error Handling
```python
def safe_from_json(json_str: str) -> Option[Option]:
    """
    Safely deserialize JSON that might not contain valid Option data.
    Returns Some(Option) if successful, Nil() if invalid.
    """
    try:
        result = json.loads(json_str, object_hook=option_decoder)
        if isinstance(result, (Some, type(Nil()))):
            return Some(result)
        else:
            return Nil()
    except (json.JSONDecodeError, KeyError, TypeError):
        return Nil()

def validate_option_dict(data: Dict[str, Any]) -> bool:
    """Validate that dictionary represents a valid Option."""
    if not isinstance(data, dict) or "type" not in data:
        return False

    if data["type"] == "Some":
        return "value" in data
    elif data["type"] == "Nil":
        return len(data) == 1  # Only "type" key

    return False
```

## Files to Create
- `src/optionc/serialization.py`
- `tests/test_serialization.py`
- `examples/api_integration.py`
- `examples/database_integration.py`

## Dependencies
- Standard library only (json, pickle)
- Optional: SQLAlchemy for database integration examples
- Optional: requests for API examples

## Integration Points
- Add methods to existing Option classes
- Update `__init__.py` with serialization exports
- Document in README.md

## Priority
**Medium-High** - Very useful for real-world applications that need persistence or API integration.

## Testing Strategy
- Round-trip testing (serialize → deserialize → compare)
- Edge cases (nested objects, complex types)
- Error handling (malformed JSON, invalid data)
- Performance testing with large objects
- Database integration tests