# Pattern Matching Support (Python 3.10+)

## Overview
Add support for Python's `match` statement pattern matching with Option types.

## Implementation Plan

### 1. Add __match_args__ to Option Classes
```python
class Some(Option[T]):
    __match_args__ = ("value",)

    def __init__(self, value: T):
        if value is None:
            raise ValueError("Some cannot contain None")
        self._value = value

class NilType(Option[T]):
    __match_args__ = ()

    # Rest of implementation...
```

### 2. Usage Examples
```python
def process_user(user_option: Option[User]) -> str:
    match user_option:
        case Some(User(name=name, age=age)) if age >= 18:
            return f"Adult user: {name}"
        case Some(User(name=name, age=age)) if age < 18:
            return f"Minor user: {name}"
        case Some(user):
            return f"User: {user.name}"
        case Nil():
            return "No user found"

def extract_email_domain(email_option: Option[str]) -> Option[str]:
    match email_option:
        case Some(email) if "@" in email:
            return Some(email.split("@")[1])
        case Some(_) | Nil():
            return Nil()

# Nested matching
def process_nested_data(data: Option[Dict[str, Any]]) -> str:
    match data:
        case Some({"user": {"email": email}}) if isinstance(email, str):
            return f"Email: {email}"
        case Some({"user": user_data}):
            return f"User data: {user_data}"
        case Some(value):
            return f"Some data: {value}"
        case Nil():
            return "No data"
```

### 3. Advanced Pattern Matching
```python
def chain_matching(options: List[Option[int]]) -> str:
    match options:
        case [Some(x), Some(y)] if x + y > 10:
            return f"Sum > 10: {x + y}"
        case [Some(x), Nil()]:
            return f"First only: {x}"
        case [Nil(), Some(y)]:
            return f"Second only: {y}"
        case [Nil(), Nil()]:
            return "Both nil"
        case [Some(x), Some(y)]:
            return f"Sum <= 10: {x + y}"
        case _:
            return "Other pattern"
```

### 4. Guard Patterns with Option Methods
```python
def smart_processing(value_option: Option[str]) -> Option[int]:
    match value_option:
        case Some(value) if value.isdigit():
            return Some(int(value))
        case Some(value) if value.replace(".", "").isdigit():
            return Some(int(float(value)))
        case _:
            return Nil()
```

## Files to Modify
- `src/optionc/some.py` - Add `__match_args__`
- `src/optionc/nil.py` - Add `__match_args__`

## Files to Create
- `tests/test_pattern_matching.py`
- `docs/pattern_matching_examples.md`

## Requirements
- Python 3.10+ only
- Add version check in setup
- Consider making this an optional import for older Python versions

## Testing Strategy
```python
def test_basic_some_matching():
    value = Some(42)
    match value:
        case Some(x):
            assert x == 42
        case _:
            pytest.fail("Should match Some")

def test_nil_matching():
    value = Nil()
    match value:
        case Nil():
            assert True
        case _:
            pytest.fail("Should match Nil")

def test_guard_patterns():
    values = [Some(5), Some(15), Nil()]
    results = []

    for value in values:
        match value:
            case Some(x) if x > 10:
                results.append("big")
            case Some(x):
                results.append("small")
            case Nil():
                results.append("nil")

    assert results == ["small", "big", "nil"]
```

## Priority
**Low-Medium** - Nice quality of life improvement for Python 3.10+ users, but not essential functionality.