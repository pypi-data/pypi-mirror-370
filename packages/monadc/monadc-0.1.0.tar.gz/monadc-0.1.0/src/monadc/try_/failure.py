from typing import Callable, Union, Any, Optional, cast
from .try_ import Try, T, U


class Failure(Try[T]):
    """
    Represents a failed computation in a Try monad.

    Failure contains the exception that was thrown during computation.
    """
    
    __match_args__ = ("_exception",)

    def __new__(cls, exception: Exception) -> 'Failure[T]':
        """Create a new Failure instance directly, bypassing Try.__new__."""
        return object.__new__(cls)

    def __init__(self, exception: Exception) -> None:
        # If _exception already exists, this is a second call from Python's object creation process
        # We should ignore it since the object has already been properly initialized
        if hasattr(self, '_exception'):
            return

        self._exception = exception

    def is_success(self) -> bool:
        return False

    def is_failure(self) -> bool:
        return True

    def __bool__(self) -> bool:
        """Failure is falsy."""
        return False

    def get(self) -> T:
        # Re-raise the original exception
        raise self._exception

    def get_or_else(self, default: Union[T, Callable[[], T]]) -> T:
        if callable(default):
            try:
                return default()
            except Exception:
                # If default function also fails, re-raise original exception
                raise self._exception
        return default

    def exception(self) -> Optional[Exception]:
        return self._exception

    def map(self, func: Callable[[T], U]) -> Try[U]:
        # Failure passes through unchanged
        return cast(Try[U], self)

    def flat_map(self, func: Callable[[T], Try[U]]) -> Try[U]:
        # Failure passes through unchanged
        return cast(Try[U], self)

    def filter(self, predicate: Callable[[T], bool]) -> Try[T]:
        # Failure passes through unchanged
        return self

    def recover(self, func: Callable[[Exception], T]) -> Try[T]:
        try:
            result = func(self._exception)
            from .success import Success
            return Success(result)
        except Exception as e:
            return Failure(e)

    def recover_with(self, func: Callable[[Exception], Try[T]]) -> Try[T]:
        try:
            return func(self._exception)
        except Exception as e:
            return Failure(e)

    def fold(self, if_failure: Callable[[Exception], U], if_success: Callable[[T], U]) -> U:
        return if_failure(self._exception)

    def transform(self, success_func: Callable[[T], Try[U]],
                  failure_func: Callable[[Exception], Try[U]]) -> Try[U]:
        try:
            return failure_func(self._exception)
        except Exception as e:
            return Failure(e)

    def foreach(self, func: Callable[[T], Any]) -> None:
        # Failure does nothing
        pass

    def or_else(self, alternative: Union[Try[T], Callable[[], Try[T]]]) -> Try[T]:
        """Return alternative since this is Failure."""
        if callable(alternative):
            try:
                return alternative()
            except Exception as e:
                return Failure(e)
        return alternative

    def flatten(self) -> Any:  # Returns Try[U]
        """Flatten Failure to itself since Failure has no inner Try to unwrap."""
        return self

    def flatten_safe(self) -> Any:  # Returns Try[U]
        """Safe flatten that returns self (same as flatten for Failure)."""
        return self

    def to_option(self) -> Any:  # Returns Option[T]
        from ..option import Nil
        return Nil()

    def to_either(self) -> Any:  # Returns Either[Exception, T]
        from ..either import Left
        return Left(self._exception)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Failure):
            # Compare exceptions by type and message
            return (type(self._exception) == type(other._exception) and
                    str(self._exception) == str(other._exception))
        return False

    def __repr__(self) -> str:
        return f"Failure({self._exception!r})"

    def __str__(self) -> str:
        return self.__repr__()