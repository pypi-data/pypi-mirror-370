"""
Decorators for automatic monad wrapping of function returns.
"""
from functools import wraps
from typing import Callable, TypeVar, Any, TYPE_CHECKING
from .option import Option

if TYPE_CHECKING:
    from .try_ import Try
    from .result import Result

T = TypeVar('T')


def option(func: Callable[..., T]) -> Callable[..., 'Option[T]']:
    """
    Decorator that wraps function return values in Option.

    - Returns Some(result) for non-None values
    - Returns Nil() for None values
    - Exceptions propagate normally (not caught)

    Example:
        @option
        def find_user(user_id: str) -> User:
            return database.get(user_id)  # Returns Option[User]
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> 'Option[T]':
        result = func(*args, **kwargs)
        return Option(result)

    return wrapper


def try_decorator(func: Callable[..., T]) -> Callable[..., 'Try[T]']:
    """
    Decorator that wraps function return values in Try monad.

    - Returns Success(result) for successful execution
    - Returns Failure(exception) if function raises any exception

    Example:
        @try_decorator
        def parse_int(s: str) -> int:
            return int(s)  # Returns Success(42) or Failure(ValueError)
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> 'Try[T]':
        try:
            result = func(*args, **kwargs)
            from .try_ import Success
            return Success(result)
        except Exception as e:
            from .try_ import Failure
            return Failure(e)

    return wrapper


# Alias for more natural usage
try_ = try_decorator


def result(func: Callable[..., T]) -> Callable[..., 'Result[T, Exception]']:
    """
    Decorator that wraps function return values in Result monad.

    - Returns Ok(result) for successful execution  
    - Returns Err(exception) if function raises any exception

    Example:
        @result
        def divide(a: float, b: float) -> float:
            return a / b  # Returns Ok(2.0) or Err(ZeroDivisionError)
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> 'Result[T, Exception]':
        try:
            result = func(*args, **kwargs)
            from .result import Ok
            return Ok(result)
        except Exception as e:
            from .result import Err
            return Err(e)

    return wrapper
