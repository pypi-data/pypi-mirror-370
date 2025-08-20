from typing import Callable, Union, Any, Optional, cast
from .either import Either, L, R, U


class Left(Either[L, R]):
    """
    Represents a failed computation in an Either monad.

    Left values pass through transformations unchanged, allowing error information
    to propagate through a chain of operations.
    """
    
    __match_args__ = ("_value",)

    def __new__(cls, value: L) -> 'Left[L, R]':
        """Create a new Left instance directly, bypassing Either.__new__."""
        return object.__new__(cls)

    def __init__(self, value: Any = None, **kwargs: Any) -> None:
        # If _value already exists, this is a second call from Python's object creation process
        # We should ignore it since the object has already been properly initialized
        if hasattr(self, '_value'):
            return

        # Handle factory construction: Either(left=x) calls Left.__init__(left_obj, left=x)
        if 'left' in kwargs:
            self._value = kwargs['left']
        # Handle direct construction: Left(value)
        else:
            self._value = value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Left):
            return self._value == other._value  # type: ignore[no-any-return]
        return False

    def __repr__(self) -> str:
        return f"Left({self._value!r})"

    def __str__(self) -> str:
        return self.__repr__()

    # ========================================
    # Rust / Scala Common API
    # ========================================

    def is_left(self) -> bool:
        return True

    def is_right(self) -> bool:
        return False

    def left(self) -> Any:  # Returns Option[L]
        from ..option import Some
        return Some(self._value)

    def right(self) -> Any:  # Returns Option[R]
        from ..option import Nil
        return Nil()

    def map(self, func: Callable[[Union[L, R]], U]) -> U:
        return func(self._value)

    def map_left(self, func: Callable[[L], U]) -> Either[U, R]:
        result = func(self._value)
        return Left(result)

    def map_right(self, func: Callable[[R], U]) -> Either[L, U]:
        # Left passes through unchanged
        return cast(Either[L, U], self)

    # ========================================
    # RUST API
    # ========================================

    def either(self, left_func: Callable[[L], U], right_func: Callable[[R], U]) -> U:
        """Apply left_func to Left value or right_func to Right value. Alias for fold."""
        return self.fold(left_func, right_func)

    def map_either(self, left_func: Callable[[L], U], right_func: Callable[[R], U]) -> U:
        return left_func(self._value)

    def unwrap_left(self) -> L:
        return self._value  # type: ignore[no-any-return]

    def unwrap_right(self) -> R:
        raise ValueError("Cannot unwrap right value from Left")

    def expect_left(self, message: str) -> L:
        return self._value  # type: ignore[no-any-return]

    def expect_right(self, message: str) -> R:
        raise ValueError(message)

    def left_or(self, other: Either[U, R]) -> Either[U, R]:
        # Return self (Left) rather than other
        return cast(Either[U, R], self)

    def right_or(self, other: Either[L, U]) -> Either[L, U]:
        # Return other since self is Left
        return other

    def left_or_else(self, func: Callable[[], Either[U, R]]) -> Either[U, R]:
        # Return self (Left) rather than calling func
        return cast(Either[U, R], self)

    def right_or_else(self, func: Callable[[], Either[L, U]]) -> Either[L, U]:
        # Call func and return result since self is Left
        return func()

    def left_and_then(self, func: Callable[[L], Either[U, R]]) -> Either[U, R]:
        return func(self._value)

    def right_and_then(self, func: Callable[[R], Either[L, U]]) -> Either[L, U]:
        # Left passes through unchanged
        return cast(Either[L, U], self)

    def flip(self) -> Either[R, L]:
        from .right import Right
        return Right(self._value)

    # ========================================
    # SCALA API
    # ========================================

    def swap(self) -> Either[R, L]:
        from .right import Right
        return Right(self._value)

    def fold(self, if_left: Callable[[L], U], if_right: Callable[[R], U]) -> U:
        return if_left(self._value)

    def foreach(self, func: Callable[[R], Any]) -> None:
        # Left does nothing - Scala style right-biased behavior
        pass

    def get(self) -> R:
        raise ValueError("Cannot get Right value from Left")

    def get_or_else(self, default: Union[R, Callable[[], R]]) -> R:
        if callable(default):
            return default()
        return default

    def to_option(self) -> Any:  # Returns Option[R]
        from ..option import Nil
        return Nil()

    def contains(self, value: Any) -> bool:
        # Left never contains a Right value
        return False

    def exists(self, predicate: Callable[[R], bool]) -> bool:
        # Left has no Right value to test predicate against
        return False

    def or_else(self, other: Union['Either[L, U]', Callable[[], 'Either[L, U]']]) -> 'Either[L, Union[R, U]]':
        # Return other since this is a Left
        if callable(other):
            return cast('Either[L, Union[R, U]]', other())
        return cast('Either[L, Union[R, U]]', other)
