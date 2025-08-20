from typing import TypeVar, Generic, Callable, Union, Any, Optional, cast

L = TypeVar('L')  # Left type (error/failure)
R = TypeVar('R')  # Right type (success/value)
U = TypeVar('U')  # Generic result type

class Either(Generic[L, R]):
    """
    Rust and Scala inspired Either monad for representing computations that can succeed or fail.

    Either[L, R] represents a value that can be either:
    - Left[L]: A failure/error value of type L
    - Right[R]: A success value of type R
    """

    _UNSET = object()  # Sentinel value to distinguish from None

    def __new__(cls, left: Any = _UNSET, right: Any = _UNSET) -> 'Either[L, R]':
        """Factory constructor for Either. Prefer explicit Right()/Left() construction."""
        if cls is not Either:
            # Direct subclass instantiation (Left, Right)
            return super().__new__(cls)

        if left is not cls._UNSET and right is not cls._UNSET:
            raise ValueError("Cannot specify both left and right")

        if left is not cls._UNSET:
            from .left import Left
            return Left(left)
        elif right is not cls._UNSET:
            from .right import Right
            return Right(right)
        else:
            raise ValueError("Must specify either left or right")

    # ========================================
    # Rust / Scala Common API
    # ========================================

    def is_left(self) -> bool:
        """Returns True if this Either is a Left, False otherwise."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def is_right(self) -> bool:
        """Returns True if this Either is a Right, False otherwise."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def left(self) -> 'Any':  # Returns Option[L]
        """Get the left value as Option - Some(value) if Left, Nil() if Right."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def right(self) -> 'Any':  # Returns Option[R]
        """Get the right value as Option - Some(value) if Right, Nil() if Left."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def map(self, func: Callable[[Union[L, R]], U]) -> U:
        """
        Map both Left and Right values to the same type. Note:
        - Rust: requires the same type for both left and right.
        - Scala: maps the right value only.
        - Python(monadc): blindly applies func to left or right, whichever is present.
        Also see `map_either` below.
        """
        raise NotImplementedError("Use Left or Right, not Either directly")

    def map_left(self, func: Callable[[L], U]) -> 'Either[U, R]':
        """Transform the Left value if present, otherwise return unchanged Right."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def map_right(self, func: Callable[[R], U]) -> 'Either[L, U]':
        """Transform the Right value if present, otherwise return unchanged Left."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    # ========================================
    # RUST API
    # ========================================

    def either(self, left_func: Callable[[L], U], right_func: Callable[[R], U]) -> U:
        """Apply left_func to Left value or right_func to Right value. Alias for fold."""
        return self.fold(left_func, right_func)

    def map_either(self, left_func: Callable[[L], U], right_func: Callable[[R], U]) -> U:
        """Transform both sides to same type using explicit left/right functions (Rust-style)."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def unwrap_left(self) -> L:
        """Get the left value. Raises exception if this is a Right."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def unwrap_right(self) -> R:
        """Get the right value. Raises exception if this is a Left."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def expect_left(self, message: str) -> L:
        """Get the left value. Raises exception with custom message if this is a Right."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def expect_right(self, message: str) -> R:
        """Get the right value. Raises exception with custom message if this is a Left."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def left_or(self, other: 'Either[U, R]') -> 'Either[U, R]':
        """Return self if Left, otherwise return other."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def right_or(self, other: 'Either[L, U]') -> 'Either[L, U]':
        """Return self if Right, otherwise return other."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def left_or_else(self, func: Callable[[], 'Either[U, R]']) -> 'Either[U, R]':
        """Return self if Left, otherwise call func and return result."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def right_or_else(self, func: Callable[[], 'Either[L, U]']) -> 'Either[L, U]':
        """Return self if Right, otherwise call func and return result."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def left_and_then(self, func: Callable[[L], 'Either[U, R]']) -> 'Either[U, R]':
        """Transform Left value to Either if present, otherwise return unchanged Right."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def right_and_then(self, func: Callable[[R], 'Either[L, U]']) -> 'Either[L, U]':
        """Transform Right value to Either if present, otherwise return unchanged Left."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def flip(self) -> 'Either[R, L]':
        """Flip Left and Right types."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    # ========================================
    # SCALA API
    # ========================================
    # NOTE: These methods favor the right part (success case) following Scala conventions.
    # They operate on the Right value and ignore/pass through Left values.

    def swap(self) -> 'Either[R, L]':
        """Swap Left and Right types."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def fold(self, if_left: Callable[[L], U], if_right: Callable[[R], U]) -> U:
        """Apply if_left to Left value or if_right to Right value."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def foreach(self, func: Callable[[R], Any]) -> None:
        """Execute function on Right value, do nothing for Left (Scala-style)."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def get(self) -> R:
        """Get the Right value. Raises exception if this is a Left (Scala-style)."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def get_or_else(self, default: Union[R, Callable[[], R]]) -> R:
        """Get the Right value or return default if this is a Left (Scala-style)."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def to_option(self) -> 'Any':  # Returns Option[R]
        """Convert Either to Option, keeping Right value and losing Left information (Scala-style)."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def contains(self, value: Any) -> bool:
        """Returns True if this is a Right containing the given value (Scala-style)."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def exists(self, predicate: Callable[[R], bool]) -> bool:
        """Returns True if this is a Right and the predicate holds for the Right value (Scala-style)."""
        raise NotImplementedError("Use Left or Right, not Either directly")

    def or_else(self, other: Union['Either[L, U]', Callable[[], 'Either[L, U]']]) -> 'Either[L, Union[R, U]]':
        """Return this Either if it's a Right, otherwise return other (Scala-style)."""
        raise NotImplementedError("Use Left or Right, not Either directly")
