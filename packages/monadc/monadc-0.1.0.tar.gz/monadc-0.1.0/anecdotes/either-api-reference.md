# Either API Reference

The Either API is organized into 3 logical groups for clarity and ease of use.

## 1. CONSTRUCTORS

**Factory constructor:**
```python
Either(left=y)   # Creates Left(y)
Either(right=x)  # Creates Right(x)
```

## 2. RUST / SCALA COMMON API

**Type checking:**
```python
either.is_left() -> bool   # True if Left, False if Right
either.is_right() -> bool  # True if Right, False if Left
```

**Value Extraction:**
```python
either.left() -> Option[L]        # Some(value) if Left, Nil() if Right
either.right() -> Option[R]       # Some(value) if Right, Nil() if Left
```

**Transformations:**
```python
either.map(func) -> U                     # Apply single function to either Left or Right value
either.map_left(func) -> Either[U, R]     # Transform Left value
either.map_right(func) -> Either[L, U]    # Transform Right value
```

## 3. RUST API

**Value Extraction (Rust-style):**
```python
either.unwrap_left() -> L         # Get left value or raise exception
either.unwrap_right() -> R        # Get right value or raise exception
either.expect_left(msg) -> L      # Get left value or raise with custom message
either.expect_right(msg) -> R     # Get right value or raise with custom message
```

**Transformations (Rust-style):**
```python
either.map_either(left_func, right_func) -> U   # Transform with separate left/right functions
```

**Monadic Operations (Rust-style):**
```python
either.left_and_then(func) -> Either[U, R]   # Chain Left operations
either.right_and_then(func) -> Either[L, U]  # Chain Right operations
```

**Fallback Operations (Rust-style):**
```python
either.left_or(other) -> Either[U, R]        # Return self if Left, else other
either.right_or(other) -> Either[L, U]       # Return self if Right, else other
either.left_or_else(func) -> Either[U, R]    # Return self if Left, else call func
either.right_or_else(func) -> Either[L, U]   # Return self if Right, else call func
```

**Utilities (Rust-style):**
```python
either.flip() -> Either[R, L]     # Flip Left and Right types
```

## 4. SCALA API

**Note:** These methods follow Scala conventions and are right-biased (they operate on Right values and ignore Left values).

**Folding (Scala-style):**
```python
either.fold(if_left, if_right) -> U         # Apply function based on Left/Right
either.either(left_func, right_func) -> U   # Alias for fold()
```

**Value Access (Scala-style):**
```python
either.get() -> R                    # Get Right value or raise exception
either.get_or_else(default) -> R     # Get Right value or return default
```

**Side Effects (Scala-style):**
```python
either.foreach(func) -> None         # Execute func on Right value only
```

**Predicates (Scala-style):**
```python
either.contains(value) -> bool       # True if Right contains the value
either.exists(predicate) -> bool     # True if Right satisfies predicate
```

**Fallback Operations (Scala-style):**
```python
either.or_else(other) -> Either      # Return self if Right, else other
```

**Conversions (Scala-style):**
```python
either.to_option() -> Option[R]      # Convert to Option, keeping Right value
```

**Utilities (Scala-style):**
```python
either.swap() -> Either[R, L]        # Swap Left and Right types
```

## Usage Examples

### Rust-style Error Handling
```python
from monadc import Left, Right

def divide(a: int, b: int) -> Either[str, float]:
    return Right(a / b) if b != 0 else Left("Division by zero")

def validate_positive(x: float) -> Either[str, float]:
    return Right(x) if x > 0 else Left("Must be positive")

result = (divide(10, 2)
          .right_and_then(validate_positive)
          .map_right(lambda x: f"Result: {x}"))

print(result)  # Right("Result: 5.0")
```

### Scala-style Folding
```python
def process_either(either: Either[str, int]) -> str:
    return either.fold(
        lambda error: f"Error: {error}",
        lambda value: f"Success: {value}"
    )

print(process_either(Left("failed")))     # "Error: failed"
print(process_either(Right(42)))          # "Success: 42"
```

### Method Chaining with Fallbacks
```python
result = (Left("initial error")
          .right_or(Right("fallback"))
          .map_right(str.upper)
          .right_or_else(lambda: Right("default")))

print(result)  # Right("FALLBACK")
```

### Scala-style Right-Biased Operations
```python
from monadc import Left, Right

def process_data(data: Either[str, int]) -> str:
    return (data
            .or_else(Right(0))          # Fallback to Right(0) if Left
            .get_or_else(42)            # Get value or 42 if Left
            * 2                         # Operate on the value
            )

# Success case
success = Right(10)
print(success.get())                    # 10
print(success.contains(10))             # True
print(success.exists(lambda x: x > 5))  # True
success.foreach(lambda x: print(f"Processing: {x}"))  # Prints: Processing: 10

# Failure case
failure = Left("error")
print(failure.get_or_else("default"))   # "default"
print(failure.contains(10))             # False
print(failure.exists(lambda x: x > 5))  # False
failure.foreach(lambda x: print("Won't print"))  # Does nothing
```

### Pattern Matching (Python 3.10+)
```python
from monadc import Left, Right

def handle_result(result: Either[str, int]) -> str:
    match result:
        case Left(error):
            return f"Error: {error}"
        case Right(value) if value > 100:
            return f"Large value: {value}"
        case Right(value):
            return f"Small value: {value}"
    # No case _ needed - Left/Right cases are exhaustive for Either

# Usage examples
print(handle_result(Left("not found")))    # "Error: not found"
print(handle_result(Right(150)))           # "Large value: 150"
print(handle_result(Right(42)))            # "Small value: 42"

# Complex pattern matching with guards
def process_division(dividend: int, divisor: int) -> str:
    result = Right(dividend / divisor) if divisor != 0 else Left("Division by zero")
    
    match result:
        case Left(error):
            return f"Cannot compute: {error}"
        case Right(value) if value > 1.0:
            return f"Result > 1: {value:.2f}"
        case Right(value):
            return f"Result ≤ 1: {value:.2f}"

print(process_division(10, 2))  # "Result > 1: 5.00"
print(process_division(1, 3))   # "Result ≤ 1: 0.33"
print(process_division(5, 0))   # "Cannot compute: Division by zero"
```

## Design Philosophy

- **Rust/Scala Common API**: Shared operations that work consistently across both paradigms
- **Rust API**: Explicit, type-safe operations with clear Left/Right distinctions
- **Scala API**: Complete functional programming patterns with right-biased operations (Right = success, Left = failure)
- **Python monadc approach**: `map()` applies a single function to either Left or Right value
- **Right-bias**: Scala methods operate on success values (Right) and ignore/pass through failures (Left)
- **Pattern Matching**: Full support for Python 3.10+ pattern matching with exhaustive case coverage
- **Performance**: Direct implementations avoid function call overhead (e.g., `flip()` vs `swap()`)