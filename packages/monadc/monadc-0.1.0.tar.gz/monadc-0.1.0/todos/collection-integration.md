# Collection Integration

## Overview
Add utilities for working with collections of Options and Option-returning operations on collections.

## Implementation Plan

### 1. Collection Utility Functions
```python
# src/optionc/collections.py

from typing import List, Iterator, Callable, TypeVar
from .option import Option
from .some import Some
from .nil import Nil

T = TypeVar('T')
U = TypeVar('U')

def sequence(options: List[Option[T]]) -> Option[List[T]]:
    """
    Convert List[Option[T]] to Option[List[T]].
    Returns Some([values]) if all are Some, Nil() if any is Nil.
    """
    values = []
    for option in options:
        if option.is_empty():
            return Nil()
        values.append(option.get())
    return Some(values)

def traverse(items: List[T], func: Callable[[T], Option[U]]) -> Option[List[U]]:
    """
    Map function over list, then sequence the results.
    Returns Some([results]) if all succeed, Nil() if any fails.
    """
    results = [func(item) for item in items]
    return sequence(results)

def collect_some(options: List[Option[T]]) -> List[T]:
    """
    Extract all Some values from a list of Options, discarding Nils.
    """
    return [opt.get() for opt in options if opt.is_defined()]

def partition_options(options: List[Option[T]]) -> tuple[List[T], int]:
    """
    Partition options into (some_values, nil_count).
    """
    some_values = []
    nil_count = 0

    for option in options:
        if option.is_defined():
            some_values.append(option.get())
        else:
            nil_count += 1

    return some_values, nil_count

def find_first_some(options: List[Option[T]]) -> Option[T]:
    """
    Return the first Some value found, or Nil if all are Nil.
    """
    for option in options:
        if option.is_defined():
            return option
    return Nil()

def all_some(options: List[Option[T]]) -> bool:
    """
    Check if all options are Some.
    """
    return all(opt.is_defined() for opt in options)

def any_some(options: List[Option[T]]) -> bool:
    """
    Check if any option is Some.
    """
    return any(opt.is_defined() for opt in options)
```

### 2. Generator Support
```python
def option_generator(func: Callable[[], Iterator[T]]) -> Option[Iterator[T]]:
    """
    Safely create an Option-wrapped generator.
    """
    try:
        gen = func()
        return Some(gen)
    except Exception:
        return Nil()

def safe_generator_map(items: Iterator[T],
                      func: Callable[[T], Option[U]]) -> Iterator[U]:
    """
    Map a function over generator items, yielding only Some values.
    """
    for item in items:
        result = func(item)
        if result.is_defined():
            yield result.get()

@option_safe
def process_generator(items: Iterator[T]) -> Iterator[U]:
    """
    Example decorator usage with generators.
    """
    for item in items:
        yield expensive_process(item)
```

### 3. Comprehension Utilities
```python
class OptionComprehension:
    """
    Helper for option-aware list comprehensions.
    """
    @staticmethod
    def filter_map(items: List[T], func: Callable[[T], Option[U]]) -> List[U]:
        """
        Combined filter and map: apply func, keep only Some results.
        """
        return [result.get() for item in items
                for result in [func(item)] if result.is_defined()]

    @staticmethod
    def safe_map(items: List[T], func: Callable[[T], U]) -> List[U]:
        """
        Map function safely, keeping only successful results.
        """
        results = []
        for item in items:
            try:
                results.append(func(item))
            except Exception:
                continue
        return results
```

### 4. Usage Examples
```python
# Sequence example
user_ids = ["1", "2", "3"]
users = traverse(user_ids, fetch_user)  # Option[List[User]]

match users:
    case Some(user_list):
        print(f"Loaded {len(user_list)} users")
    case Nil():
        print("Failed to load some users")

# Collect example
partial_data = [
    Some("alice@example.com"),
    Nil(),
    Some("bob@example.com"),
    None  # Will be filtered out
]
valid_emails = collect_some(partial_data)  # ["alice@example.com", "bob@example.com"]

# Filter-map example
raw_numbers = ["1", "not-a-number", "3", "4.5", "invalid"]
parsed = OptionComprehension.filter_map(
    raw_numbers,
    lambda s: Option(int(s)) if s.isdigit() else Nil()
)  # [1, 3]

# Generator processing
def process_files(directory: str) -> Iterator[ProcessedFile]:
    for filename in os.listdir(directory):
        result = safe_process_file(filename)  # Returns Option[ProcessedFile]
        if result.is_defined():
            yield result.get()

# Safe generator with error handling
@option_safe
def read_lines_safe(filename: str) -> Iterator[str]:
    with open(filename) as f:
        for line in f:
            yield line.strip()

file_lines = read_lines_safe("config.txt")  # Option[Iterator[str]]
```

### 5. Integration with Standard Library
```python
# Enhanced map/filter
def option_map(func: Callable[[T], U], items: Iterator[T]) -> Iterator[Option[U]]:
    """
    Map function over items, wrapping results in Options.
    """
    for item in items:
        try:
            yield Some(func(item))
        except Exception:
            yield Nil()

def option_filter(predicate: Callable[[T], bool],
                 items: Iterator[T]) -> Iterator[Option[T]]:
    """
    Filter items with Option-wrapped results.
    """
    for item in items:
        try:
            if predicate(item):
                yield Some(item)
            else:
                yield Nil()
        except Exception:
            yield Nil()
```

## Files to Create
- `src/optionc/collections.py`
- `tests/test_collections.py`
- `examples/collection_examples.py`

## Dependencies
- No new external dependencies
- Consider `more-itertools` for advanced iterator utilities

## Integration Points
- Add imports to `__init__.py`
- Document in README.md
- Consider pandas integration in separate module

## Priority
**High** - Collection operations are very common in real-world usage of Option types.

## Performance Considerations
- Use generators where possible for memory efficiency
- Consider lazy evaluation for large collections
- Add type hints for better IDE support
- Benchmark against equivalent non-Option operations