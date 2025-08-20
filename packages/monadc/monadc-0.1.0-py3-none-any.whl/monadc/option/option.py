from typing import TypeVar, Generic, Callable, Union, Any, Optional, Iterator

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')
E = TypeVar('E')


class Option(Generic[T]):
    """
    Rust and Scala inspired Option monad representing optional values with dual Scala/Rust API.

    Option[T] represents a value that may or may not exist:
    - Some[T]: Contains a value of type T
    - Nil: Represents no value (equivalent to None in Rust and Scala)
    """

    def __new__(cls, value: Optional[T] = None) -> 'Option[T]':
        """Factory constructor: Option(x) creates Some(x) or Nil()"""
        if cls is not Option:
            # Direct subclass instantiation (Some, Nil)
            return super().__new__(cls)

        # Option(x) factory behavior
        if value is None:
            from .nil import Nil
            return Nil()
        else:
            from .some import Some
            return Some(value)

    # ========================================
    # Rust / Scala Common API
    # ========================================

    def or_else(self, alternative: Union['Option[T]', Callable[[], 'Option[T]']]) -> 'Option[T]':
        """
        Return this Option if defined, otherwise use alternative.
        - Rust: the alternative is a callable.
        - Scala: the alternative is a value.
        """
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def filter(self, predicate: Callable[[T], bool]) -> 'Option[T]':
        """Keep value if predicate is true, otherwise return empty Option."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def map(self, func: Callable[[T], U]) -> 'Option[U]':
        """Transform the value if present, otherwise return empty Option."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def flatten(self) -> 'Option[Any]':
        """Flatten Option[Option[T]] to Option[T]."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def transpose(self) -> 'Any':  # Returns Result[Option[T], E] if self is Option[Result[T, E]]
        """Rust-style: Transpose Option[Result[T, E]] to Result[Option[T], E]."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def zip(self, other: 'Option[U]') -> 'Option[tuple[T, U]]':
        """Rust-style: Zip with another Option to create Option of tuple."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def unzip(self) -> 'tuple[Option[Any], Option[Any]]':
        """Unzip Option[tuple[A, B]] to tuple[Option[A], Option[B]]."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    # ========================================
    # RUST API
    # ========================================

    def is_some(self) -> bool:
        """Rust-style: True if this is Some."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def is_none(self) -> bool:
        """Rust-style: True if this is Nil."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def unwrap(self) -> T:
        """Rust-style: Get the value. Panics if this is Nil."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def unwrap_or(self, default: T) -> T:
        """Rust-style: Get the value or return default if Nil."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def unwrap_or_else(self, func: Callable[[], T]) -> T:
        """Rust-style: Get the value or compute default if Nil."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def expect(self, message: str) -> T:
        """Rust-style: Get the value or raise error with custom message."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def and_then(self, func: Callable[[T], 'Option[U]']) -> 'Option[U]':
        """Rust-style: Transform Some value to Option."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def or_else_with(self, func: Callable[[], 'Option[T]']) -> 'Option[T]':
        """Rust-style: Return self if Some, otherwise call func."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def and_(self, other: 'Option[U]') -> 'Option[U]':
        """Rust-style: Return other if self is Some, otherwise return Nil."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def or_(self, other: 'Option[T]') -> 'Option[T]':
        """Rust-style: Return self if Some, otherwise return other."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def xor(self, other: 'Option[T]') -> 'Option[T]':
        """Rust-style: Return Some if exactly one of self or other is Some."""
        raise NotImplementedError("Use Some or Nil, not Option directly")


    def zip_with(self, other: 'Option[U]', func: Callable[[T, U], V]) -> 'Option[V]':
        """Rust-style: Zip with another Option and apply function."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def inspect(self, func: Callable[[T], Any]) -> 'Option[T]':
        """Rust-style: Call function with value if Some, return self unchanged."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def get_or_insert(self, value: T) -> T:
        """Rust-style: Get the value or insert and return default if Nil."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def get_or_insert_with(self, func: Callable[[], T]) -> T:
        """Rust-style: Get the value or insert result of func and return it if Nil."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def insert(self, value: T) -> T:
        """Rust-style: Insert value and return it."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def map_or(self, default: U, func: Callable[[T], U]) -> U:
        """Rust-style: Apply func to Some value or return default if Nil."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def map_or_else(self, default_func: Callable[[], U], func: Callable[[T], U]) -> U:
        """Rust-style: Apply func to Some value or call default_func if Nil."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def ok_or(self, error: E) -> 'Any':  # Returns Result[T, E]
        """Rust-style: Convert Some(v) to Ok(v) or Nil to Err(error)."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def ok_or_else(self, func: Callable[[], E]) -> 'Any':  # Returns Result[T, E]
        """Rust-style: Convert Some(v) to Ok(v) or Nil to Err(func())."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    # ========================================
    # SCALA API
    # ========================================

    def is_defined(self) -> bool:
        """Returns True if this Option has a value, False otherwise."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def is_empty(self) -> bool:
        """Returns True if this Option is empty, False otherwise."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def get(self) -> T:
        """Get the value of this Option. Raises exception if empty."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def get_or_else(self, default: Union[T, Callable[[], T]]) -> T:
        """Get the value or return default if empty."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def filter_not(self, predicate: Callable[[T], bool]) -> 'Option[T]':
        """Keep value if predicate is false, otherwise return empty Option."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def flat_map(self, func: Callable[[T], 'Option[U]']) -> 'Option[U]':
        """Transform the value to Option if present, otherwise return empty Option."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def fold(self, if_empty: U, func: Callable[[T], U]) -> U:
        """Apply func to value if present, otherwise return if_empty."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def foreach(self, func: Callable[[T], Any]) -> None:
        """Scala-style: Apply func to value if present."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def exists(self, predicate: Callable[[T], bool]) -> bool:
        """True if value exists and satisfies predicate."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def forall(self, predicate: Callable[[T], bool]) -> bool:
        """Scala-style: True if empty or value satisfies predicate."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def contains(self, value: Any) -> bool:
        """Scala-style: True if Option contains the specified value."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def non_empty(self) -> bool:
        """Scala-style: True if this Option is not empty."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def or_null(self) -> Optional[T]:
        """Scala-style: Return value if defined, None if empty."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def or_none(self) -> Optional[T]:
        """Return value if defined, None if empty. Alias for or_null."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def to_list(self) -> list[T]:
        """Convert to list - empty list if empty, single-item list if defined."""
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def to_optional(self) -> Optional[T]:
        """Convert to Optional - None if empty, value if defined."""
        raise NotImplementedError("Use Some or Nil, not Option directly")


    # ========================================
    # PYTHON SPECIAL METHODS
    # ========================================

    def __bool__(self) -> bool:
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def __iter__(self) -> Iterator[T]:
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def __repr__(self) -> str:
        raise NotImplementedError("Use Some or Nil, not Option directly")

    def __str__(self) -> str:
        raise NotImplementedError("Use Some or Nil, not Option directly")
