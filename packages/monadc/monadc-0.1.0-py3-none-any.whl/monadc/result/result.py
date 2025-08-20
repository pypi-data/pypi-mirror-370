from typing import TypeVar, Generic, Callable, Union, Any, Optional

T = TypeVar('T')  # Ok type (success/value)
E = TypeVar('E')  # Err type (error/failure)
U = TypeVar('U')  # Generic result type

class Result(Generic[T, E]):
    """
    Rust-inspired Result monad for representing computations that can succeed or fail.

    Result[T, E] represents a value that can be either:
    - Ok[T]: A successful value of type T
    - Err[E]: An error value of type E

    This follows Rust conventions where Ok represents success and Err represents failure.
    """

    _UNSET = object()  # Sentinel value to distinguish from None

    def __new__(cls, ok_value: Any = _UNSET, err_value: Any = _UNSET) -> 'Result[T, E]':
        """Factory constructor for Result. Prefer explicit Ok()/Err() construction."""
        if cls is not Result:
            # Direct subclass instantiation (Ok, Err)
            return super().__new__(cls)

        if ok_value is not cls._UNSET and err_value is not cls._UNSET:
            raise ValueError("Cannot specify both ok_value and err_value")

        if ok_value is not cls._UNSET:
            from .ok import Ok
            return Ok(ok_value)
        elif err_value is not cls._UNSET:
            from .err import Err
            return Err(err_value)
        else:
            raise ValueError("Must specify either ok_value or err_value")

    # Type checking methods
    def is_ok(self) -> bool:
        """Returns True if this Result is an Ok, False otherwise."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    def is_err(self) -> bool:
        """Returns True if this Result is an Err, False otherwise."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    # Value extraction (Rust-style)
    def ok(self) -> 'Any':  # Returns Option[T]
        """Get the ok value as Option - Some(value) if Ok, Nil() if Err."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    def err(self) -> 'Any':  # Returns Option[E]
        """Get the err value as Option - Some(error) if Err, Nil() if Ok."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    def unwrap(self) -> T:
        """Get the ok value. Panics (raises exception) if this is an Err."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    def unwrap_err(self) -> E:
        """Get the err value. Panics (raises exception) if this is an Ok."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    def unwrap_or(self, default: T) -> T:
        """Get the ok value or return default if this is an Err."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        """Get the ok value or compute default from error if this is an Err."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    # Transformations (Ok-biased)
    def map(self, func: Callable[[T], U]) -> 'Result[U, E]':
        """Transform the Ok value if present, otherwise return unchanged Err."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    def map_err(self, func: Callable[[E], U]) -> 'Result[T, U]':
        """Transform the Err value if present, otherwise return unchanged Ok."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    def map_or(self, default: U, func: Callable[[T], U]) -> U:
        """Apply func to Ok value or return default if Err."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    def map_or_else(self, default_func: Callable[[E], U], func: Callable[[T], U]) -> U:
        """Apply func to Ok value or call default_func with Err value."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    def and_then(self, func: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        """Transform Ok value to Result if present, otherwise return unchanged Err."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    def or_else(self, func: Callable[[E], 'Result[T, U]']) -> 'Result[T, U]':
        """Transform Err value to Result if present, otherwise return unchanged Ok."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    def flatten(self) -> 'Result[Any, E]':
        """Flatten Result[Result[T, E], E] to Result[T, E]."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    def transpose(self) -> 'Any':  # Returns Option[Result[T, E]]
        """Transpose Result[Option[T], E] to Option[Result[T, E]]."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    # Logical operations
    def and_(self, other: 'Result[U, E]') -> 'Result[U, E]':
        """Return other if self is Ok, otherwise return self."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    def or_(self, other: 'Result[T, U]') -> 'Result[T, U]':
        """Return self if self is Ok, otherwise return other."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    # Inspection
    def inspect(self, func: Callable[[T], Any]) -> 'Result[T, E]':
        """Call func with the Ok value if present, return self unchanged."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    def inspect_err(self, func: Callable[[E], Any]) -> 'Result[T, E]':
        """Call func with the Err value if present, return self unchanged."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    # Conversions
    def to_option(self) -> 'Any':  # Returns Option[T]
        """Convert Result to Option, losing error information."""
        raise NotImplementedError("Use Ok or Err, not Result directly")

    def to_try(self) -> 'Any':  # Returns Try[T]
        """Convert Result to Try, converting Err to Failure."""
        raise NotImplementedError("Use Ok or Err, not Result directly")