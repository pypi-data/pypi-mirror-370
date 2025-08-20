from typing import TypeVar, Generic, Callable, Union, Any, Optional, Type

T = TypeVar('T')  # Success type
U = TypeVar('U')  # Result type
E = TypeVar('E', bound=Exception)  # Exception type


class Try(Generic[T]):
    """
    Scala inspired Try monad for representing computations that may throw exceptions.

    Try[T] represents a computation that either:
    - Success[T]: A successful computation with result of type T
    - Failure: A failed computation that caught an exception

    Try automatically catches exceptions and wraps them in Failure.
    """

    def __new__(cls, func: Callable[[], T]) -> 'Try[T]':
        """Factory constructor that executes function and catches exceptions."""
        if cls is not Try:
            # Direct subclass instantiation (Success, Failure)
            return super().__new__(cls)

        try:
            result = func()
            from .success import Success
            return Success(result)
        except Exception as e:
            from .failure import Failure
            return Failure(e)

    @classmethod
    def of_value(cls, value: T) -> 'Try[T]':
        """Create a Success directly from a value without function execution."""
        from .success import Success
        return Success(value)

    # Type checking methods
    def is_success(self) -> bool:
        """Returns True if this Try is a Success, False otherwise."""
        raise NotImplementedError("Use Success or Failure, not Try directly")

    def is_failure(self) -> bool:
        """Returns True if this Try is a Failure, False otherwise."""
        raise NotImplementedError("Use Success or Failure, not Try directly")

    # Value extraction
    def get(self) -> T:
        """Get the value. Raises the original exception if this is a Failure."""
        raise NotImplementedError("Use Success or Failure, not Try directly")

    def get_or_else(self, default: Union[T, Callable[[], T]]) -> T:
        """Get the value or return default if this is a Failure."""
        raise NotImplementedError("Use Success or Failure, not Try directly")

    # Exception access
    def exception(self) -> Optional[Exception]:
        """Get the exception if this is a Failure, None otherwise."""
        raise NotImplementedError("Use Success or Failure, not Try directly")

    # Transformations
    def map(self, func: Callable[[T], U]) -> 'Try[U]':
        """Transform the Success value if present, otherwise return unchanged Failure."""
        raise NotImplementedError("Use Success or Failure, not Try directly")

    def flat_map(self, func: Callable[[T], 'Try[U]']) -> 'Try[U]':
        """Transform Success value to Try if present, otherwise return unchanged Failure."""
        raise NotImplementedError("Use Success or Failure, not Try directly")

    def filter(self, predicate: Callable[[T], bool]) -> 'Try[T]':
        """Keep Success if predicate matches, otherwise return Failure."""
        raise NotImplementedError("Use Success or Failure, not Try directly")

    # Recovery operations
    def recover(self, func: Callable[[Exception], T]) -> 'Try[T]':
        """Recover from Failure by applying function to exception."""
        raise NotImplementedError("Use Success or Failure, not Try directly")

    def recover_with(self, func: Callable[[Exception], 'Try[T]']) -> 'Try[T]':
        """Recover from Failure by applying function that returns Try."""
        raise NotImplementedError("Use Success or Failure, not Try directly")

    def or_else(self, alternative: Union['Try[T]', Callable[[], 'Try[T]']]) -> 'Try[T]':
        """Return self if Success, otherwise return alternative Try."""
        raise NotImplementedError("Use Success or Failure, not Try directly")

    def flatten(self) -> 'Try[Any]':
        """Flatten nested Try[Try[T]] to Try[T]. Raises TypeError if not nested."""
        raise NotImplementedError("Use Success or Failure, not Try directly")

    def flatten_safe(self) -> 'Try[Any]':
        """Safe flatten that returns self if not nested (idempotent behavior)."""
        raise NotImplementedError("Use Success or Failure, not Try directly")

    # Folding
    def fold(self, if_failure: Callable[[Exception], U], if_success: Callable[[T], U]) -> U:
        """Apply if_failure to exception or if_success to value."""
        raise NotImplementedError("Use Success or Failure, not Try directly")

    def transform(self, success_func: Callable[[T], 'Try[U]'],
                  failure_func: Callable[[Exception], 'Try[U]']) -> 'Try[U]':
        """Transform both Success and Failure cases."""
        raise NotImplementedError("Use Success or Failure, not Try directly")

    # Side effects
    def foreach(self, func: Callable[[T], Any]) -> None:
        """Execute function on Success value, do nothing for Failure."""
        raise NotImplementedError("Use Success or Failure, not Try directly")

    # Conversions
    def to_option(self) -> Any:  # Returns Option[T]
        """Convert Try to Option, losing exception information."""
        raise NotImplementedError("Use Success or Failure, not Try directly")

    def to_either(self) -> Any:  # Returns Either[Exception, T]
        """Convert Try to Either with exception as Left value."""
        raise NotImplementedError("Use Success or Failure, not Try directly")
