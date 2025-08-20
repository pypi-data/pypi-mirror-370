from typing import Callable, Union, Any, Optional, Iterator, cast
from .option import Option, T, U, V, E
from .nil import Nil


class Some(Option[T]):
    
    __match_args__ = ("_value",)

    def __init__(self, value: T) -> None:
        if value is None:
            raise ValueError("Cannot create Some with None value")
        self._value = value

    # ========================================
    # Rust / Scala Common API
    # ========================================

    def is_defined(self) -> bool:
        return True

    def is_empty(self) -> bool:
        return False

    def map(self, func: Callable[[T], U]) -> Option[U]:
        result = func(self._value)
        return Option(result)

    def flatten(self) -> Option[Any]:
        """Flatten Option[Option[T]] to Option[T]."""
        if isinstance(self._value, Option):
            return self._value
        return self

    def transpose(self) -> Any:  # Returns Result[Option[T], E]
        """Rust-style: Transpose Option[Result[T, E]] to Result[Option[T], E]."""
        from ..result import Ok, Result
        # If the value is a Result, transpose it
        if isinstance(self._value, Result):
            if self._value.is_ok():
                return Ok(Some(self._value.unwrap()))
            else:
                return self._value  # Return the Err as-is
        # If not a Result, wrap in Ok(Some(...))
        return Ok(Some(self._value))

    def zip(self, other: Option[U]) -> Option[tuple[T, U]]:
        """Rust-style: Zip with another Option to create Option of tuple."""
        if other.is_some():
            from .some import Some
            return Some((self._value, other.get()))
        else:
            return Nil()

    def unzip(self) -> tuple[Option[Any], Option[Any]]:
        """Unzip Option[tuple[A, B]] to tuple[Option[A], Option[B]]."""
        if isinstance(self._value, tuple) and len(self._value) == 2:
            from .some import Some
            return Some(self._value[0]), Some(self._value[1])
        else:
            return Nil(), Nil()

    def filter(self, predicate: Callable[[T], bool]) -> Option[T]:
        if predicate(self._value):
            return self
        else:
            return Nil()

    # ========================================
    # RUST API
    # ========================================

    def is_some(self) -> bool:
        """Rust-style: Return True since this is Some."""
        return True

    def is_none(self) -> bool:
        """Rust-style: Return False since this is Some."""
        return False

    def unwrap(self) -> T:
        """Rust-style: Get the value."""
        return self._value

    def unwrap_or(self, default: T) -> T:
        """Rust-style: Get the value, ignoring default."""
        return self._value

    def unwrap_or_else(self, func: Callable[[], T]) -> T:
        """Rust-style: Get the value, not calling func."""
        return self._value

    def expect(self, message: str) -> T:
        """Rust-style: Get the value. For Some, message is ignored."""
        return self._value

    def and_then(self, func: Callable[[T], Option[U]]) -> Option[U]:
        """Rust-style: Transform Some value to Option."""
        return func(self._value)

    def or_else_with(self, func: Callable[[], Option[T]]) -> Option[T]:
        """Rust-style: Return self since Some doesn't need alternative."""
        return self

    def and_(self, other: Option[U]) -> Option[U]:
        """Rust-style: Return other since self is Some."""
        return other

    def or_(self, other: Option[T]) -> Option[T]:
        """Rust-style: Return self since self is Some."""
        return self

    def xor(self, other: Option[T]) -> Option[T]:
        """Rust-style: Return Nil if other is Some, self if other is Nil."""
        if other.is_some():
            return Nil()
        return self


    def get_or_insert(self, value: T) -> T:
        """Rust-style: Get the value (ignore insert since Some has value)."""
        return self._value

    def get_or_insert_with(self, func: Callable[[], T]) -> T:
        """Rust-style: Get the value (don't call func since Some has value)."""
        return self._value

    def insert(self, value: T) -> T:
        """Rust-style: Return the inserted value (for Some, return current value)."""
        return self._value

    def map_or(self, default: U, func: Callable[[T], U]) -> U:
        """Rust-style: Apply func to Some value."""
        return func(self._value)

    def map_or_else(self, default_func: Callable[[], U], func: Callable[[T], U]) -> U:
        """Rust-style: Apply func to Some value (ignore default_func)."""
        return func(self._value)

    def ok_or(self, error: E) -> Any:  # Returns Result[T, E]
        """Rust-style: Convert Some(v) to Ok(v)."""
        from ..result import Ok
        return Ok(self._value)

    def ok_or_else(self, func: Callable[[], E]) -> Any:  # Returns Result[T, E]
        """Rust-style: Convert Some(v) to Ok(v) (don't call func)."""
        from ..result import Ok
        return Ok(self._value)

    def zip_with(self, other: Option[U], func: Callable[[T, U], V]) -> Option[V]:
        """Rust-style: Zip with another Option and apply function."""
        if other.is_some():
            from .some import Some
            return Some(func(self._value, other.get()))
        else:
            return Nil()

    def inspect(self, func: Callable[[T], Any]) -> Option[T]:
        """Rust-style: Call function with value and return self unchanged."""
        func(self._value)
        return self

    # ========================================
    # SCALA API
    # ========================================

    def get(self) -> T:
        return self._value

    def get_or_else(self, default: Union[T, Callable[[], T]]) -> T:
        return self._value

    def or_else(self, alternative: Union[Option[T], Callable[[], Option[T]]]) -> Option[T]:
        return self

    def filter_not(self, predicate: Callable[[T], bool]) -> Option[T]:
        if not predicate(self._value):
            return self
        else:
            return Nil()

    def flat_map(self, func: Callable[[T], Option[U]]) -> Option[U]:
        return func(self._value)

    def fold(self, if_empty: U, func: Callable[[T], U]) -> U:
        return func(self._value)

    def foreach(self, func: Callable[[T], Any]) -> None:
        """Scala-style: Apply func to value."""
        func(self._value)

    def exists(self, predicate: Callable[[T], bool]) -> bool:
        return predicate(self._value)

    def forall(self, predicate: Callable[[T], bool]) -> bool:
        """Scala-style: True if value satisfies predicate."""
        return predicate(self._value)

    def contains(self, value: Any) -> bool:
        """Scala-style: True if Option contains the specified value."""
        return cast(bool, self._value == value)

    def non_empty(self) -> bool:
        """Scala-style: True since Some is not empty."""
        return True

    def or_null(self) -> Optional[T]:
        """Scala-style: Return value since Some is defined."""
        return self._value

    def or_none(self) -> Optional[T]:
        """Return value since Some is defined. Alias for or_null."""
        return self._value

    def to_list(self) -> list[T]:
        return [self._value]

    def to_optional(self) -> Optional[T]:
        return self._value


    # ========================================
    # PYTHON SPECIAL METHODS
    # ========================================

    def __bool__(self) -> bool:
        return True

    def __iter__(self) -> Iterator[T]:
        yield self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Some):
            return cast(bool, self._value == other._value)
        # Some is never equal to Nil or other types
        return False

    def __repr__(self) -> str:
        return f"Some({self._value!r})"

    def __str__(self) -> str:
        return self.__repr__()
