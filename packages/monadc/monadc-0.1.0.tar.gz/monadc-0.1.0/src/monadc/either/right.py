from typing import Callable, Union, Any, Optional, cast
from .either import Either, L, R, U


class Right(Either[L, R]):
    """
    Represents a successful computation in an Either monad.

    Right is right-biased, meaning transformations (map, flat_map) operate on Right values
    and pass through Left values unchanged.
    """
    
    __match_args__ = ("_value",)

    def __new__(cls, value: R) -> 'Right[L, R]':
        """Create a new Right instance directly, bypassing Either.__new__."""
        return object.__new__(cls)

    def __init__(self, value: Any = None, **kwargs: Any) -> None:
        # If _value already exists, this is a second call from Python's object creation process
        # We should ignore it since the object has already been properly initialized
        if hasattr(self, '_value'):
            return

        # Handle factory construction: Either(right=x) calls Right.__init__(right_obj, right=x)
        if 'right' in kwargs:
            self._value = kwargs['right']
        # Handle direct construction: Right(value)
        else:
            self._value = value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Right):
            return self._value == other._value  # type: ignore[no-any-return]
        return False

    def __repr__(self) -> str:
        return f"Right({self._value!r})"

    def __str__(self) -> str:
        return self.__repr__()

    # ========================================
    # Rust / Scala Common API
    # ========================================

    def is_left(self) -> bool:
        return False

    def is_right(self) -> bool:
        return True

    def left(self) -> Any:  # Returns Option[L]
        from ..option import Nil
        return Nil()

    def right(self) -> Any:  # Returns Option[R]
        from ..option import Some
        return Some(self._value)

    def map(self, func: Callable[[Union[L, R]], U]) -> U:
        return func(self._value)

    def map_left(self, func: Callable[[L], U]) -> Either[U, R]:
        # Right is unchanged by map_left
        return cast(Either[U, R], self)

    def map_right(self, func: Callable[[R], U]) -> Either[L, U]:
        result = func(self._value)
        return Right(result)

    # ========================================
    # RUST API
    # ========================================

    def either(self, left_func: Callable[[L], U], right_func: Callable[[R], U]) -> U:
        """Apply left_func to Left value or right_func to Right value. Alias for fold."""
        return self.fold(left_func, right_func)

    def map_either(self, left_func: Callable[[L], U], right_func: Callable[[R], U]) -> U:
        return right_func(self._value)

    def unwrap_left(self) -> L:
        raise ValueError("Cannot unwrap left value from Right")

    def unwrap_right(self) -> R:
        return self._value  # type: ignore[no-any-return]

    def expect_left(self, message: str) -> L:
        raise ValueError(message)

    def expect_right(self, message: str) -> R:
        return self._value  # type: ignore[no-any-return]

    def left_or(self, other: Either[U, R]) -> Either[U, R]:
        # Return other since self is Right
        return other

    def right_or(self, other: Either[L, U]) -> Either[L, U]:
        # Return self (Right) rather than other
        return cast(Either[L, U], self)

    def left_or_else(self, func: Callable[[], Either[U, R]]) -> Either[U, R]:
        # Call func and return result since self is Right
        return func()

    def right_or_else(self, func: Callable[[], Either[L, U]]) -> Either[L, U]:
        # Return self (Right) rather than calling func
        return cast(Either[L, U], self)

    def left_and_then(self, func: Callable[[L], Either[U, R]]) -> Either[U, R]:
        # Right passes through unchanged
        return cast(Either[U, R], self)

    def right_and_then(self, func: Callable[[R], Either[L, U]]) -> Either[L, U]:
        return func(self._value)

    def flip(self) -> Either[R, L]:
        from .left import Left
        return Left(self._value)

    # ========================================
    # SCALA API
    # ========================================

    def swap(self) -> Either[R, L]:
        from .left import Left
        return Left(self._value)

    def fold(self, if_left: Callable[[L], U], if_right: Callable[[R], U]) -> U:
        return if_right(self._value)

    def foreach(self, func: Callable[[R], Any]) -> None:
        func(self._value)

    def get(self) -> R:
        return self._value  # type: ignore[no-any-return]

    def get_or_else(self, default: Union[R, Callable[[], R]]) -> R:
        # Return the Right value, ignore default
        return self._value  # type: ignore[no-any-return]

    def to_option(self) -> Any:  # Returns Option[R]
        from ..option import Option
        return Option(self._value)

    def contains(self, value: Any) -> bool:
        return self._value == value  # type: ignore[no-any-return]

    def exists(self, predicate: Callable[[R], bool]) -> bool:
        return predicate(self._value)

    def or_else(self, other: Union['Either[L, U]', Callable[[], 'Either[L, U]']]) -> 'Either[L, Union[R, U]]':
        # Return self since this is a Right
        return cast('Either[L, Union[R, U]]', self)
