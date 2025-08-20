from typing import Callable, Union, Any, Optional, cast
from .result import Result, T, E, U


class Err(Result[T, E]):
    """
    Represents a failed computation in a Result monad.

    Err contains the error value, following Rust conventions.
    Err values pass through transformations unchanged, allowing error information
    to propagate through a chain of operations.
    """
    
    __match_args__ = ("_value",)

    def __new__(cls, value: E) -> 'Err[T, E]':
        """Create a new Err instance directly, bypassing Result.__new__."""
        return object.__new__(cls)

    def __init__(self, value: Any = None, **kwargs: Any) -> None:
        # If _value already exists, this is a second call from Python's object creation process
        # We should ignore it since the object has already been properly initialized
        if hasattr(self, '_value'):
            return

        # Handle factory construction: Result(err_value=x) calls Err.__init__(err_obj, err_value=x)
        if 'err_value' in kwargs:
            self._value = kwargs['err_value']
        # Handle direct construction: Err(value)
        else:
            self._value = value

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def __bool__(self) -> bool:
        """Err is falsy (following Rust conventions)."""
        return False

    def ok(self) -> Any:  # Returns Nil()
        from ..option import Nil
        return Nil()

    def err(self) -> Any:  # Returns Some(error)
        from ..option import Some
        return Some(self._value)

    def unwrap(self) -> T:
        raise ValueError(f"Called unwrap() on an Err value: {self._value}")

    def unwrap_err(self) -> E:
        return self._value  # type: ignore[no-any-return]

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        return func(self._value)

    def map(self, func: Callable[[T], U]) -> Result[U, E]:
        # Err passes through unchanged
        return cast(Result[U, E], self)

    def map_err(self, func: Callable[[E], U]) -> Result[T, U]:
        result = func(self._value)
        return Err(result)

    def and_then(self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        # Err passes through unchanged
        return cast(Result[U, E], self)

    def or_else(self, func: Callable[[E], Result[T, U]]) -> Result[T, U]:
        return func(self._value)

    def map_or(self, default: U, func: Callable[[T], U]) -> U:
        # Return default for Err (ignore func)
        return default

    def map_or_else(self, default_func: Callable[[E], U], func: Callable[[T], U]) -> U:
        # Apply default_func to Err value (ignore func)
        return default_func(self._value)

    def flatten(self) -> 'Result[Any, E]':
        # Err values are unchanged by flatten
        return self

    def transpose(self) -> 'Any':  # Returns Option[Result[T, E]]
        # Err values transpose to Some(Err(...))
        from ..option import Some
        return Some(self)

    def and_(self, other: Result[U, E]) -> Result[U, E]:
        return cast(Result[U, E], self)

    def or_(self, other: Result[T, U]) -> Result[T, U]:
        return other

    def inspect(self, func: Callable[[T], Any]) -> Result[T, E]:
        # Err has no ok value to inspect
        return self

    def inspect_err(self, func: Callable[[E], Any]) -> Result[T, E]:
        func(self._value)
        return self

    def to_option(self) -> Any:  # Returns Option[T]
        from ..option import Nil
        return Nil()

    def to_try(self) -> Any:  # Returns Try[T]
        from ..try_ import Failure
        # Convert error value to Exception if it's not already one
        if isinstance(self._value, Exception):
            return Failure(self._value)
        else:
            # Wrap non-exception errors in a RuntimeError
            return Failure(RuntimeError(str(self._value)))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Err):
            return self._value == other._value  # type: ignore[no-any-return]
        return False

    def __repr__(self) -> str:
        return f"Err({self._value!r})"

    def __str__(self) -> str:
        return self.__repr__()
