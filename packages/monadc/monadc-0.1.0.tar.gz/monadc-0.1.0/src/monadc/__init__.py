"""
monadc - Comprehensive functional programming monads for Python

A complete monad library providing Option, Either, Try, and Result types
for functional programming patterns, inspired by Scala and Rust.

Features:
- Option monad with dual Scala/Rust API (get/unwrap, map/and_then, etc.)
- Either monad for error handling (Scala-inspired)
- Try monad for exception handling (Scala-inspired)
- Result monad for error handling (Rust-inspired)
- Full interoperability between all monad types
- Comprehensive utility functions and decorators

Example usage:
    from monadc import Option, Some, Nil, Result, Ok, Err

    # Option with dual API
    user = Option("john@example.com")  # Some("john@example.com")

    # Scala-style
    email = user.map(str.upper).get_or_else("no-email@example.com")

    # Rust-style
    email = user.and_then(lambda x: Some(x.upper())).unwrap_or("no-email@example.com")

    # Mixed styles work together
    result = (Option("hello")
              .map(str.upper)           # Scala
              .and_then(lambda x: Some(x + "!"))  # Rust
              .inspect(print)           # Rust
              .filter(lambda x: "!" in x))       # Scala

    # Result monad (Rust-style)
    success = Ok("data")
    error = Err("failed")
    value = success.unwrap_or("default")

    # Idiomatic patterns using monad interoperability
    config_val = Option(config.get("timeout", 30))
    attr_val = Try(lambda: obj.property).to_option()
    computed = Try(lambda: expensive_computation()).to_option()
"""

# Option monad (Scala-inspired)
from .option import Option, Some, Nil

# Either monad (Scala-inspired)
from .either import Either, Left, Right

# Try monad (Scala-inspired)
from .try_ import Try, Success, Failure

# Result monad (Rust-inspired)
from .result import Result, Ok, Err
# Note: Utility functions removed in favor of idiomatic monad patterns
from .decorators import option, try_decorator, try_, result

__version__ = "0.1.0"
__author__ = "Carl You"
__email__ = ""

__all__ = [
    # Option monad (currently available)
    "Option",  # Both type annotation and constructor: Option(x)
    "Some",    # Direct construction: Some(x)
    "Nil",     # Direct construction: Nil()

    # Either monad
    "Either", "Left", "Right",

    # Try monad
    "Try", "Success", "Failure",

    # Result monad
    "Result", "Ok", "Err",

    # Note: Utility functions removed - use idiomatic patterns:
    # Old: from_callable(lambda: func()) -> New: Try(lambda: func()).to_option()
    # Old: from_dict_get(dict, key) -> New: Option(dict.get(key))
    # Old: from_getattr(obj, attr) -> New: Try(lambda: obj.attr).to_option()

    # Decorators for automatic monad wrapping
    "option",         # @option - wrap returns in Option, exceptions propagate
    "try_decorator",  # @try_decorator - wrap returns in Try (Success/Failure)
    "try_",           # @try_ - alias for try_decorator (more natural usage)
    "result",         # @result - wrap returns in Result (Ok/Err)
]