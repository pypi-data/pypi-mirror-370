# monadc

Functional programming monads for Python with first-class pattern matching support.

## Installation

```bash
pip install monadc
```

## Option - Handle Missing Data Safely

**Example**: Extracting nested data from API responses without crashes.

```python
from monadc import Option, Some, Nil

# Instead of this brittle code:
def get_user_avatar(api_response):
    if (api_response and "data" in api_response and 
        api_response["data"] and "user" in api_response["data"] and
        api_response["data"]["user"] and "profile" in api_response["data"]["user"]):
        profile = api_response["data"]["user"]["profile"]
        return profile.get("avatar_url", "/default.png")
    return "/default.png"

# Write this:
def get_user_avatar(api_response):
    return (Option(api_response.get("data"))
            .flat_map(lambda data: Option(data.get("user")))
            .flat_map(lambda user: Option(user.get("profile")))
            .flat_map(lambda profile: Option(profile.get("avatar_url")))
            .unwrap_or("/default.png"))

# Pattern matching for different cases
def handle_user_data(api_response):
    user_profile = (Option(api_response.get("data"))
                   .flat_map(lambda data: Option(data.get("user")))
                   .flat_map(lambda user: Option(user.get("profile"))))
    
    match user_profile:
        case Some(profile) if profile.get("verified"):
            return f"✓ Verified user: {profile['name']}"
        case Some(profile):
            return f"User: {profile.get('name', 'Anonymous')}"
        case Nil():
            return "Please log in"
```

## Try - Exception-Safe Operations

**Example**: File I/O and parsing operations that can fail in multiple ways.

*Note: You can also use `Result/Ok/Err` for Rust-style syntax with identical functionality.*

```python
from monadc import Try, Success, Failure, try_
import json

@try_
def load_user_config(username: str):
    with open(f"users/{username}/config.json") as f:
        return json.load(f)

@try_
def validate_theme(config: dict):
    theme = config["ui"]["theme"]
    if theme not in ["light", "dark", "auto"]:
        raise ValueError(f"Invalid theme: {theme}")
    return theme

# Chain operations that can each fail
def get_user_theme(username: str):
    return (load_user_config(username)
            .and_then(validate_theme)
            .unwrap_or("light"))

# Pattern matching handles different failure types
def load_config_with_feedback(username: str):
    result = load_user_config(username).and_then(validate_theme)
    
    match result:
        case Success(theme):
            return f"Loaded theme: {theme}"
        case Failure(FileNotFoundError()):
            return "No config found, using defaults"
        case Failure(json.JSONDecodeError()):
            return "Config file corrupted, using defaults" 
        case Failure(KeyError()):
            return "Config missing theme setting"
        case Failure(ValueError() as e):
            return f"Invalid config: {e}"
```

## Either - Validation with Error Messages

**Example**: Form validation that collects specific error messages.

```python
from monadc import Either, Left, Right

def validate_email(email: str) -> Either[str, str]:
    if not email:
        return Left("Email is required")
    if "@" not in email or "." not in email:
        return Left("Please enter a valid email address")
    return Right(email.lower())

def validate_age(age_str: str) -> Either[str, int]:
    try:
        age = int(age_str)
        if age < 13:
            return Left("Must be at least 13 years old")
        if age > 120:
            return Left("Please enter a valid age")
        return Right(age)
    except ValueError:
        return Left("Age must be a number")

# Pattern matching for comprehensive error handling
def create_user_account(form_data):
    email_result = validate_email(form_data.get("email", ""))
    age_result = validate_age(form_data.get("age", ""))
    
    match (email_result, age_result):
        case (Right(email), Right(age)):
            return create_account(email, age)
        case (Left(email_error), Right(_)):
            return {"error": f"Email: {email_error}"}
        case (Right(_), Left(age_error)):
            return {"error": f"Age: {age_error}"}
        case (Left(email_error), Left(age_error)):
            return {"error": f"Email: {email_error}; Age: {age_error}"}
```


## Key Benefits

**Four functional primitives for safer code:**
- `Option/Some/Nil` - Handle missing data without None checks
- `Result/Ok/Err` and `Try/Success/Failure` - Exception handling with explicit error types  
- `Either/Left/Right` - Type-safe unions for validation and error messaging

**Enhanced Python integration:**
- Function decorators (`@try_`, `@option`, `@result`) for automatic wrapping
- First-class support for `match/case` pattern matching (Python 3.10+)
- Full MyPy compatibility with generic type annotations

## Contributing

See [CLAUDE.md](CLAUDE.md) for development setup.
