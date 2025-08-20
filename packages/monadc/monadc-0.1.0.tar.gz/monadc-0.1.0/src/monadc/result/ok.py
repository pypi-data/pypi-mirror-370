from typing import Callable, Union, Any, Optional, cast
from .result import Result, T, E, U


class Ok(Result[T, E]):
    """
    Represents a successful computation in a Result monad.

    Ok contains the successful result value, following Rust conventions.
    Ok is result-biased, meaning transformations (map, and_then) operate on Ok values
    and pass through Err values unchanged.
    """
    
    __match_args__ = ("_value",)

    def __new__(cls, value: T) -> 'Ok[T, E]':
        """Create a new Ok instance directly, bypassing Result.__new__."""
        return object.__new__(cls)

    def __init__(self, value: Any = None, **kwargs: Any) -> None:
        # If _value already exists, this is a second call from Python's object creation process
        # We should ignore it since the object has already been properly initialized
        if hasattr(self, '_value'):
            return

        # Handle factory construction: Result(ok_value=x) calls Ok.__init__(ok_obj, ok_value=x)
        if 'ok_value' in kwargs:
            self._value = kwargs['ok_value']
        # Handle direct construction: Ok(value)
        else:
            self._value = value

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def __bool__(self) -> bool:
        """Ok is truthy (following Rust conventions)."""
        return True

    def ok(self) -> Any:  # Returns Some(value)
        from ..option import Some
        return Some(self._value)

    def err(self) -> Any:  # Returns Nil()
        from ..option import Nil
        return Nil()

    def unwrap(self) -> T:
        return self._value  # type: ignore[no-any-return]

    def unwrap_err(self) -> E:
        raise ValueError("Called unwrap_err() on an Ok value")

    def unwrap_or(self, default: T) -> T:
        return self._value  # type: ignore[no-any-return]

    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        return self._value  # type: ignore[no-any-return]

    def map(self, func: Callable[[T], U]) -> Result[U, E]:
        result = func(self._value)
        return Ok(result)

    def map_err(self, func: Callable[[E], U]) -> Result[T, U]:
        # Ok is unchanged by map_err
        return cast(Result[T, U], self)

    def and_then(self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return func(self._value)

    def or_else(self, func: Callable[[E], Result[T, U]]) -> Result[T, U]:
        # Ok doesn't need alternative
        return cast(Result[T, U], self)

    def map_or(self, default: U, func: Callable[[T], U]) -> U:
        # Apply func to Ok value
        return func(self._value)

    def map_or_else(self, default_func: Callable[[E], U], func: Callable[[T], U]) -> U:
        # Apply func to Ok value (ignore default_func)
        return func(self._value)

    def flatten(self) -> 'Result[Any, E]':
        # If the Ok value is itself a Result, unwrap it
        if isinstance(self._value, Result):
            return self._value
        # Otherwise return self unchanged
        return self

    def transpose(self) -> 'Any':  # Returns Option[Result[T, E]]
        # If the Ok value is an Option, transpose Result[Option[T], E] to Option[Result[T, E]]
        from ..option import Option, Some, Nil
        if hasattr(self._value, 'is_empty') and callable(getattr(self._value, 'is_empty')):  # Duck typing for Option
            if self._value.is_empty():
                return Nil()
            else:
                # Extract value from Some and wrap in Ok
                return Some(Ok(self._value.unwrap()))
        # If not an Option, wrap self in Some
        return Some(self)

    def and_(self, other: Result[U, E]) -> Result[U, E]:
        return other

    def or_(self, other: Result[T, U]) -> Result[T, U]:
        return cast(Result[T, U], self)

    def inspect(self, func: Callable[[T], Any]) -> Result[T, E]:
        func(self._value)
        return self

    def inspect_err(self, func: Callable[[E], Any]) -> Result[T, E]:
        # Ok has no error to inspect
        return self

    def to_option(self) -> Any:  # Returns Option[T]
        from ..option import Option
        return Option(self._value)

    def to_try(self) -> Any:  # Returns Try[T]
        from ..try_ import Success
        return Success(self._value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Ok):
            return self._value == other._value  # type: ignore[no-any-return]
        return False

    def __repr__(self) -> str:
        return f"Ok({self._value!r})"

    def __str__(self) -> str:
        return self.__repr__()
