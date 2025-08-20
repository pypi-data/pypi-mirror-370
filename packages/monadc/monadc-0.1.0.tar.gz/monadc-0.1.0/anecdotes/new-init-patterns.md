# Python `__new__` and `__init__` Patterns in Factory Constructors

This document explores the subtle but critical differences between Python's object creation patterns, specifically focusing on factory constructors and why some require double initialization protection while others don't.

## Overview

In the monadc library, we have two different patterns for factory constructors:

1. **Option Pattern**: Elegant, no double initialization issues
2. **Try Pattern**: More complex, requires `hasattr` protection against double initialization

Let's explore why these patterns behave differently.

## Python Object Creation Flow

When you call a class constructor like `MyClass(args)`, Python does:

1. **Call `MyClass.__new__(MyClass, args)`** to create the instance
2. **If `__new__` returns an instance of `MyClass` (or subclass), automatically call `instance.__init__(args)`**

This automatic `__init__` call is where the complexity arises.

## Pattern 1: Option (Clean Design)

### Implementation

```python
class Option:
    def __new__(cls, value: Optional[T] = None) -> 'Option[T]':
        if cls is not Option:
            # Direct subclass instantiation (Some, Nil)
            return super().__new__(cls)
        
        # Factory behavior
        if value is None:
            return Nil()  # Singleton, handles own creation
        else:
            return Some(value)  # Create Some instance

class Some(Option):
    # No explicit __new__ - inherits from Option
    def __init__(self, value: T) -> None:
        if value is None:
            raise ValueError("Cannot create Some with None value")
        self._value = value
```

### Execution Flow

```python
Some("hello")  # Direct instantiation
```

1. **`Option.__new__(Some, "hello")`** called (Some inherits Option's `__new__`)
2. **`cls is not Option`** → True (cls=Some)
3. **Returns `super().__new__(Some)`** → `object.__new__(Some)` 
4. **Python calls `Some.__init__(instance, "hello")`** ✅
5. **Single initialization, correct arguments**

```python
Option("hello")  # Factory usage
```

1. **`Option.__new__(Option, "hello")`** called
2. **`cls is not Option`** → False (cls=Option)
3. **`value is None`** → False
4. **Returns `Some("hello")`**:
   - Calls `Option.__new__(Some, "hello")` → `object.__new__(Some)`
   - Calls `Some.__init__(instance, "hello")` ✅
5. **Python calls `Some.__init__(instance, "hello")` again** ✅
6. **Double initialization with SAME arguments - no problem!**

### Why Option Works

**Key insight**: The factory arguments and constructor arguments are **identical**.

- `Option("hello")` creates `Some("hello")`
- Both use the same argument `"hello"`  
- Double initialization is harmless because `_value` gets set to the same value twice

## Pattern 2: Try (Complex Design)

### Implementation

```python
class Try:
    def __new__(cls, func: Callable[[], T]) -> 'Try[T]':
        if cls is not Try:
            return super().__new__(cls)
        
        # Factory behavior - TRANSFORMS arguments
        try:
            result = func()  # Execute function, get result
            return Success(result)  # Create with DIFFERENT argument
        except Exception as e:
            return Failure(e)

class Success(Try):
    def __new__(cls, value: T) -> 'Success[T]':
        return object.__new__(cls)
        
    def __init__(self, value: T) -> None:
        if hasattr(self, '_value'):  # DOUBLE-INIT PROTECTION!
            return
        self._value = value
```

### Execution Flow

```python
Try(lambda: "hello")  # Factory usage
```

1. **`Try.__new__(Try, lambda: "hello")`** called
2. **Executes `lambda()` → gets `"hello"`**
3. **Returns `Success("hello")`**:
   - Calls `Success.__new__(Success, "hello")` → `object.__new__(Success)`
   - Calls `Success.__init__(instance, "hello")` → sets `_value = "hello"` ✅
4. **Python calls `Success.__init__(instance, lambda: "hello")` again!** ❌
   - **Wrong arguments!** Gets lambda function instead of result
   - **Without `hasattr` protection, `_value` would be overwritten with the lambda!**

### The Problem Visualized

```python
# What Try.__new__ does:
func = lambda: "hello"
result = func()  # "hello" 
return Success(result)  # Success("hello") - DIFFERENT ARGUMENT

# What Python then does automatically:
success_instance.__init__(func)  # Wrong! Should be __init__("hello")
```

### Why Try Needs Protection

**Key insight**: The factory arguments and constructor arguments are **different**.

- `Try(lambda: "hello")` creates `Success("hello")`
- Factory argument: `lambda: "hello"` (function)
- Constructor argument: `"hello"` (result) 
- **Argument transformation breaks the automatic `__init__` call**

## The `hasattr` Protection Pattern

```python
def __init__(self, value: T) -> None:
    if hasattr(self, '_value'):  # Already initialized?
        return  # Skip second initialization
    self._value = value
```

This pattern prevents the second (incorrect) initialization from overwriting the first (correct) one.

## Why Some is NOT Missing `__new__`

Initially, we thought `Some` was missing an explicit `__new__` method like `Success` and `Failure` have. But actually:

### Some's Design is Correct

```python
class Some(Option):
    # No explicit __new__ - this is INTENTIONAL and CORRECT
    def __init__(self, value: T) -> None:
        self._value = value
```

**Why this works:**
1. `Some` inherits `Option.__new__`
2. `Option.__new__` has smart logic: if `cls is not Option`, use `super().__new__(cls)`
3. This handles both factory usage (`Option(x)`) and direct usage (`Some(x)`) correctly
4. No argument transformation means no double-init problems

### Success/Failure Need Explicit `__new__`

```python
class Success(Try):
    def __new__(cls, value: T) -> 'Success[T]':
        return object.__new__(cls)  # REQUIRED to bypass Try.__new__
```

**Why this is necessary:**
1. Without explicit `__new__`, `Success(value)` would call `Try.__new__`
2. `Try.__new__` expects a function, not a value → TypeError
3. Explicit `__new__` bypasses the factory logic for direct instantiation

## Comparison Summary

| Aspect | Option Pattern | Try Pattern |
|--------|----------------|-------------|
| **Factory args** | `Option(value)` | `Try(function)` |
| **Constructor args** | `Some(value)` | `Success(result)` |
| **Argument transformation** | None | `function → result` |
| **Double initialization** | Harmless | Destructive |
| **Protection needed** | No | Yes (`hasattr` checks) |
| **Subclass `__new__`** | Not needed | Required |
| **Complexity** | Low | High |

## Key Lessons

### 1. Factory Argument Transformation is Dangerous

When your factory transforms arguments (`function → result`), you create a mismatch between what Python's automatic `__init__` expects and what the object actually needs.

### 2. Consistent Arguments are Safe  

When factory and constructor use the same arguments (`value → value`), double initialization is harmless.

### 3. `hasattr` Checks are Band-Aids

The `hasattr` pattern works but indicates a design issue. It's protecting against Python's automatic behavior rather than working with it.

### 4. Option's Design is Superior

Option's design elegantly avoids the double initialization problem entirely by maintaining argument consistency.

## Alternative Approaches

### Option 1: Avoid Argument Transformation

Instead of transforming in `__new__`, do it elsewhere:

```python
# Current (problematic)
def __new__(cls, func):
    result = func()  # Transform here
    return Success(result)

# Alternative (cleaner)  
def __new__(cls, func):
    return Success.from_function(func)  # Move transformation to factory method
```

### Option 2: Use Class Methods

```python
class Try:
    @classmethod
    def from_function(cls, func):
        try:
            return Success(func())
        except Exception as e:
            return Failure(e)
```

### Option 3: Separate Factory Classes

Keep the factory separate from the inheritance hierarchy entirely.

## Conclusion

The double initialization issue in Try stems from a fundamental mismatch between Python's automatic object creation flow and factory constructor patterns that transform arguments. While the `hasattr` protection works, Option's design demonstrates a cleaner approach that works with Python's object creation model rather than against it.

Understanding these patterns is crucial for designing robust factory constructors in Python that avoid subtle initialization bugs.