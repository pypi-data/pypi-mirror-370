# Async Support

## Overview
Add async/await support for Option operations that need to work with asynchronous functions.

## Implementation Plan

### 1. AsyncOption Class
```python
class AsyncOption[T]:
    def __init__(self, option: Option[T]):
        self._option = option

    async def map_async(self, func: Callable[[T], Awaitable[U]]) -> 'AsyncOption[U]':
        if self._option.is_empty():
            return AsyncOption(Nil())

        try:
            result = await func(self._option.get())
            return AsyncOption(Option(result))
        except Exception:
            return AsyncOption(Nil())

    async def flat_map_async(self, func: Callable[[T], Awaitable[Option[U]]]) -> 'AsyncOption[U]':
        if self._option.is_empty():
            return AsyncOption(Nil())

        try:
            result = await func(self._option.get())
            return AsyncOption(result)
        except Exception:
            return AsyncOption(Nil())

    async def to_option(self) -> Option[T]:
        return self._option
```

### 2. Async Decorators
```python
def async_option(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[Option[T]]]:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Option[T]:
        result = await func(*args, **kwargs)
        return Option(result)
    return wrapper

def async_option_safe(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[Option[T]]]:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Option[T]:
        try:
            result = await func(*args, **kwargs)
            return Option(result)
        except Exception:
            return Nil()
    return wrapper
```

### 3. Usage Examples
```python
@async_option_safe
async def fetch_user(user_id: str) -> User:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/users/{user_id}")
        return User.from_dict(response.json())

@async_option_safe
async def fetch_profile(user: User) -> UserProfile:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/profiles/{user.id}")
        return UserProfile.from_dict(response.json())

# Usage
async def get_user_email():
    return await (AsyncOption(await fetch_user("123"))
                 .flat_map_async(fetch_profile)
                 .map_async(lambda profile: profile.email)
                 .to_option())
```

## Files to Create
- `src/optionc/async_option.py`
- `src/optionc/async_decorators.py`
- `tests/test_async_option.py`
- `tests/test_async_decorators.py`

## Dependencies
- Add `httpx` to dev dependencies for testing
- Requires Python 3.10+ for proper async generic typing

## Priority
**Medium** - Useful for modern async Python applications, but not critical for core functionality.