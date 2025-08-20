from typing import Callable, Union, Any, Optional
from .try_ import Try, T, U


class Success(Try[T]):
    """
    Represents a successful computation in a Try monad.

    Success contains the result of a computation that completed without throwing an exception.
    """
    
    __match_args__ = ("_value",)

    def __new__(cls, value: T) -> 'Success[T]':
        """Create a new Success instance directly, bypassing Try.__new__."""
        return object.__new__(cls)

    def __init__(self, value: T) -> None:
        # If _value already exists, this is a second call from Python's object creation process
        # We should ignore it since the object has already been properly initialized
        if hasattr(self, '_value'):
            return

        self._value = value

    def is_success(self) -> bool:
        return True

    def is_failure(self) -> bool:
        return False

    def get(self) -> T:
        return self._value

    def get_or_else(self, default: Union[T, Callable[[], T]]) -> T:
        return self._value

    def exception(self) -> Optional[Exception]:
        return None

    def map(self, func: Callable[[T], U]) -> Try[U]:
        try:
            result = func(self._value)
            return Success(result)
        except Exception as e:
            from .failure import Failure
            return Failure(e)

    def flat_map(self, func: Callable[[T], Try[U]]) -> Try[U]:
        try:
            return func(self._value)
        except Exception as e:
            from .failure import Failure
            return Failure(e)

    def filter(self, predicate: Callable[[T], bool]) -> Try[T]:
        try:
            if predicate(self._value):
                return self
            else:
                from .failure import Failure
                return Failure(ValueError("Predicate does not hold"))
        except Exception as e:
            from .failure import Failure
            return Failure(e)

    def recover(self, func: Callable[[Exception], T]) -> Try[T]:
        # Success doesn't need recovery
        return self

    def recover_with(self, func: Callable[[Exception], Try[T]]) -> Try[T]:
        # Success doesn't need recovery
        return self

    def fold(self, if_failure: Callable[[Exception], U], if_success: Callable[[T], U]) -> U:
        return if_success(self._value)

    def transform(self, success_func: Callable[[T], Try[U]],
                  failure_func: Callable[[Exception], Try[U]]) -> Try[U]:
        try:
            return success_func(self._value)
        except Exception as e:
            from .failure import Failure
            return Failure(e)

    def foreach(self, func: Callable[[T], Any]) -> None:
        func(self._value)

    def or_else(self, alternative: Union[Try[T], Callable[[], Try[T]]]) -> Try[T]:
        """Return self since Success doesn't need alternative."""
        return self

    def flatten(self) -> Any:  # Returns Try[U] where T = Try[U]
        """Flatten Success[Try[U]] to Try[U]. Raises TypeError if T is not Try[U]."""
        if isinstance(self._value, Try):
            return self._value
        else:
            # Following Scala's behavior: throw if trying to flatten non-nested Try
            raise TypeError(f"Cannot flatten Success[{type(self._value).__name__}] - value must be a Try instance")

    def flatten_safe(self) -> Any:  # Returns Try[U]
        """Safe flatten that returns self if not nested (idempotent behavior)."""
        if isinstance(self._value, Try):
            return self._value
        else:
            return self

    def to_option(self) -> Any:  # Returns Option[T]
        from ..option import Option
        return Option(self._value)

    def to_either(self) -> Any:  # Returns Either[Exception, T]
        from ..either import Right
        return Right(self._value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Success):
            return self._value == other._value  # type: ignore[no-any-return]
        return False

    def __repr__(self) -> str:
        return f"Success({self._value!r})"

    def __str__(self) -> str:
        return self.__repr__()