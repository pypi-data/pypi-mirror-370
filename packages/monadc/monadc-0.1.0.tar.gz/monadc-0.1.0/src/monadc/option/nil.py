from typing import Optional, Callable, Union, Any, Iterator, cast
from .option import Option, T, U, V, E


class NilType(Option[T]):
    
    __match_args__ = ()

    _instance: Optional['NilType[Any]'] = None

    def __new__(cls) -> 'NilType[Any]':
        if cls._instance is None:
            cls._instance = cast('NilType[Any]', super().__new__(cls))
        return cls._instance

    # ========================================
    # Rust / Scala Common API
    # ========================================

    def is_defined(self) -> bool:
        return False

    def is_empty(self) -> bool:
        return True

    def map(self, func: Callable[[T], U]) -> Option[U]:
        # Nil maps to Nil regardless of function
        return Nil()

    def flatten(self) -> Option[Any]:
        """Flatten Nil to Nil."""
        return cast(Option[Any], self)

    def transpose(self) -> Any:  # Returns Result[Option[T], E]
        """Rust-style: Transpose Nil to Ok(Nil)."""
        from ..result import Ok
        return Ok(self)

    def zip(self, other: Option[U]) -> Option[tuple[T, U]]:
        """Rust-style: Return Nil since self is Nil."""
        return cast(Option[tuple[T, U]], self)

    def unzip(self) -> tuple[Option[Any], Option[Any]]:
        """Unzip Nil to tuple of Nils."""
        return cast(Option[Any], self), cast(Option[Any], self)

    def filter(self, predicate: Callable[[T], bool]) -> Option[T]:
        # Nil filters to Nil regardless of predicate
        return self

    # ========================================
    # RUST API
    # ========================================

    def is_some(self) -> bool:
        """Rust-style: Return False since this is Nil."""
        return False

    def is_none(self) -> bool:
        """Rust-style: Return True since this is Nil."""
        return True

    def unwrap(self) -> T:
        """Rust-style: Panic since this is Nil."""
        raise ValueError("Called unwrap() on a Nil value")

    def unwrap_or(self, default: T) -> T:
        """Rust-style: Return default since this is Nil."""
        return default

    def unwrap_or_else(self, func: Callable[[], T]) -> T:
        """Rust-style: Call func to compute default since this is Nil."""
        return func()

    def expect(self, message: str) -> T:
        """Rust-style: Panic with custom message for Nil."""
        raise ValueError(message)

    def and_then(self, func: Callable[[T], Option[U]]) -> Option[U]:
        """Rust-style: Return Nil since this is Nil."""
        return cast(Option[U], self)

    def or_else_with(self, func: Callable[[], Option[T]]) -> Option[T]:
        """Rust-style: Call func to get alternative since self is Nil."""
        return func()

    def and_(self, other: Option[U]) -> Option[U]:
        """Rust-style: Return Nil since self is Nil."""
        return cast(Option[U], self)

    def or_(self, other: Option[T]) -> Option[T]:
        """Rust-style: Return other since self is Nil."""
        return other

    def xor(self, other: Option[T]) -> Option[T]:
        """Rust-style: Return other since self is Nil."""
        return other


    def zip_with(self, other: Option[U], func: Callable[[T, U], V]) -> Option[V]:
        """Rust-style: Return Nil since self is Nil."""
        return cast(Option[V], self)

    def inspect(self, func: Callable[[T], Any]) -> Option[T]:
        """Rust-style: Do nothing since self is Nil, return self."""
        return self

    def get_or_insert(self, value: T) -> T:
        """Rust-style: Return the inserted value since Nil is empty."""
        return value

    def get_or_insert_with(self, func: Callable[[], T]) -> T:
        """Rust-style: Call func and return result since Nil is empty."""
        return func()

    def insert(self, value: T) -> T:
        """Rust-style: Return the inserted value."""
        return value

    def map_or(self, default: U, func: Callable[[T], U]) -> U:
        """Rust-style: Return default since Nil has no value."""
        return default

    def map_or_else(self, default_func: Callable[[], U], func: Callable[[T], U]) -> U:
        """Rust-style: Call default_func since Nil has no value."""
        return default_func()

    def ok_or(self, error: E) -> Any:  # Returns Result[T, E]
        """Rust-style: Convert Nil to Err(error)."""
        from ..result import Err
        return Err(error)

    def ok_or_else(self, func: Callable[[], E]) -> Any:  # Returns Result[T, E]
        """Rust-style: Convert Nil to Err(func())."""
        from ..result import Err
        return Err(func())

    # ========================================
    # SCALA API
    # ========================================

    def get(self) -> T:
        raise ValueError("Cannot get value from empty Option")

    def get_or_else(self, default: Union[T, Callable[[], T]]) -> T:
        if callable(default):
            try:
                return default()
            except Exception:
                raise ValueError("Default function failed and Option is empty")
        return default

    def or_else(self, alternative: Union[Option[T], Callable[[], Option[T]]]) -> Option[T]:
        if callable(alternative):
            try:
                return alternative()
            except Exception:
                return self
        return alternative

    def filter_not(self, predicate: Callable[[T], bool]) -> Option[T]:
        # Nil filters to Nil regardless of predicate
        return self

    def flat_map(self, func: Callable[[T], Option[U]]) -> Option[U]:
        # Nil flat_maps to Nil regardless of function
        return Nil()

    def fold(self, if_empty: U, func: Callable[[T], U]) -> U:
        # Nil always returns the empty value
        return if_empty

    def foreach(self, func: Callable[[T], Any]) -> None:
        """Scala-style: Nil does nothing."""
        pass

    def exists(self, predicate: Callable[[T], bool]) -> bool:
        # Nil never satisfies any predicate
        return False

    def forall(self, predicate: Callable[[T], bool]) -> bool:
        """Scala-style: Nil vacuously satisfies all predicates."""
        return True

    def contains(self, value: Any) -> bool:
        """Scala-style: Nil never contains any value."""
        return False

    def non_empty(self) -> bool:
        """Scala-style: False since Nil is empty."""
        return False

    def or_null(self) -> Optional[T]:
        """Scala-style: Return None since Nil is empty."""
        return None

    def or_none(self) -> Optional[T]:
        """Return None since Nil is empty. Alias for or_null."""
        return None

    def to_list(self) -> list[T]:
        # Nil converts to empty list
        return []

    def to_optional(self) -> Optional[T]:
        # Nil converts to None
        return None


    # ========================================
    # PYTHON SPECIAL METHODS
    # ========================================

    def __bool__(self) -> bool:
        return False

    def __iter__(self) -> Iterator[T]:
        # Nil yields nothing
        return iter([])

    def __eq__(self, other: object) -> bool:
        # Nil is equal to other Nil instances
        return isinstance(other, NilType)

    def __repr__(self) -> str:
        return "Nil()"

    def __str__(self) -> str:
        return self.__repr__()


# Export singleton class
Nil = NilType
