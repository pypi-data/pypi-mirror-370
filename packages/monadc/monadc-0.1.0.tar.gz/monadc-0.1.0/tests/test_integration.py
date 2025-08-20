"""
Integration tests showing how different monads work together.

These tests demonstrate real-world usage patterns combining Option, Either,
Try, and utility functions in complex scenarios.
"""
import pytest
from monadc import (Option, Some, Nil, Either, Left, Right, Try, Success, Failure,
                    Result, Ok, Err, option, try_)


class TestMonadConversions:
    """Test converting between different monad types."""

    def test_option_to_either_conversion(self):
        """Test converting Option to Either."""
        # Some to Right
        some_val = Some("success")
        either_val = some_val.map(Right).get_or_else(Left("empty"))
        assert isinstance(either_val, Right)
        assert either_val.unwrap_right() == "success"

        # Nil to Left
        nil_val = Nil()
        either_val2 = nil_val.map(Right).get_or_else(Left("empty"))
        assert isinstance(either_val2, Left)
        assert either_val2.unwrap_left() == "empty"

    def test_try_to_option_conversion(self):
        """Test converting Try to Option."""
        # Success to Some
        success_val = Success("result")
        option_val = success_val.to_option()
        assert isinstance(option_val, Some)
        assert option_val.get() == "result"

        # Failure to Nil
        failure_val = Failure(ValueError("error"))
        option_val2 = failure_val.to_option()
        assert isinstance(option_val2, type(Nil()))
        assert option_val2.is_empty()

    def test_try_to_either_conversion(self):
        """Test converting Try to Either."""
        # Success to Right
        success_val = Success("result")
        either_val = success_val.to_either()
        assert isinstance(either_val, Right)
        assert either_val.unwrap_right() == "result"

        # Failure to Left
        error = ValueError("error")
        failure_val = Failure(error)
        either_val2 = failure_val.to_either()
        assert isinstance(either_val2, Left)
        assert either_val2.unwrap_left() is error

    def test_either_to_option_conversion(self):
        """Test converting Either to Option."""
        # Right to Some
        right_val = Right("success")
        option_val = right_val.to_option()
        assert isinstance(option_val, Some)
        assert option_val.get() == "success"

        # Left to Nil
        left_val = Left("error")
        option_val2 = left_val.to_option()
        assert isinstance(option_val2, type(Nil()))
        assert option_val2.is_empty()


class TestRealWorldScenarios:
    """Test complex real-world scenarios using multiple monads."""

    def test_user_profile_processing(self):
        """Test processing user profile data with multiple validation steps."""

        @try_
        def validate_email(email: str) -> str:
            if "@" not in email or "." not in email:
                raise ValueError("Invalid email format")
            return email.lower()

        @try_
        def validate_age(age_str: str) -> int:
            age = int(age_str)
            if age < 0 or age > 150:
                raise ValueError("Invalid age range")
            return age

        def process_user_data(user_data: dict) -> Either[str, dict]:
            """Process user data returning Either[error_message, processed_data]."""
            result = {}

            # Extract and validate email
            email_option = Option(user_data.get("email"))
            if email_option.is_empty():
                return Left("Missing email")
            email_try = validate_email(email_option.get())
            if email_try.is_failure():
                return Left("Invalid email")
            result["email"] = email_try.get()

            # Extract and validate age
            age_option = Option(user_data.get("age"))
            if age_option.is_empty():
                return Left("Missing age")
            age_try = validate_age(age_option.get())
            if age_try.is_failure():
                return Left("Invalid age")
            result["age"] = age_try.get()

            # Optional name processing
            name_result = Option(user_data.get("name"))
            result["name"] = name_result.get_or_else("Anonymous")

            return Right(result)

        # Valid user data
        valid_user = {
            "email": "ALICE@EXAMPLE.COM",
            "age": "25",
            "name": "Alice Smith"
        }

        result1 = process_user_data(valid_user)
        assert isinstance(result1, Right)
        processed = result1.unwrap_right()
        assert processed["email"] == "alice@example.com"
        assert processed["age"] == 25
        assert processed["name"] == "Alice Smith"

        # Invalid email
        invalid_user = {
            "email": "invalid-email",
            "age": "25"
        }

        result2 = process_user_data(invalid_user)
        assert isinstance(result2, Left)
        assert "email" in result2.unwrap_left()

        # Missing age
        missing_age_user = {
            "email": "bob@example.com"
        }

        result3 = process_user_data(missing_age_user)
        assert isinstance(result3, Left)
        assert "age" in result3.unwrap_left()

    def test_safe_file_processing(self):
        """Test safe file processing with Try and Option monads."""

        def safe_read_config(filename: str) -> Try[dict]:
            """Safely read and parse a config file."""
            return Try(lambda: {
                "database_url": "postgres://localhost:5432/mydb",
                "redis_url": "redis://localhost:6379/0",
                "api_key": "secret123"
            })

        def extract_database_config(config: dict) -> Option[dict]:
            """Extract database configuration."""
            return (Option(config.get("database_url"))
                   .map(lambda url: {"url": url, "type": "postgresql"}))

        def process_config_file(filename: str) -> Either[str, dict]:
            """Process config file returning Either[error, config]."""
            # Try to read the file
            config_try = safe_read_config(filename)

            if config_try.is_failure():
                return Left(f"Failed to read config: {config_try.exception()}")

            config = config_try.get()

            # Extract database config
            db_config = extract_database_config(config)
            if db_config.is_empty():
                return Left("Missing database configuration")

            # Build final config
            final_config = {
                "database": db_config.get(),
                "api_key": Option(config.get("api_key")).get_or_else("default_key")
            }

            return Right(final_config)

        # Test successful processing
        result = process_config_file("config.json")
        assert isinstance(result, Right)
        final_config = result.unwrap_right()
        assert "database" in final_config
        assert final_config["database"]["type"] == "postgresql"
        assert final_config["api_key"] == "secret123"

    def test_api_request_processing(self):
        """Test API request processing with error handling."""

        def parse_request_params(params: dict) -> Either[str, dict]:
            """Parse and validate API request parameters."""
            parsed = {}

            # Required user_id
            user_id_opt = Option(params.get("user_id"))
            if user_id_opt.is_empty():
                return Left("Missing required parameter: user_id")

            # Validate user_id is numeric
            user_id_try = Try(lambda: int(user_id_opt.get()))
            if user_id_try.is_failure():
                return Left("Invalid user_id: must be numeric")

            parsed["user_id"] = user_id_try.get()

            # Optional limit with default
            limit_opt = (Option(params.get("limit"))
                        .map(lambda x: Try(lambda: int(x)))
                        .filter(lambda t: t.is_success())
                        .map(lambda t: t.get())
                        .filter(lambda x: 1 <= x <= 100))

            parsed["limit"] = limit_opt.get_or_else(10)

            return Right(parsed)

        def mock_api_call(params: dict) -> Try[list]:
            """Mock API call that might fail."""
            return Try(lambda: [f"item_{i}" for i in range(params["limit"])])

        def handle_api_request(raw_params: dict) -> Either[str, list]:
            """Handle complete API request."""
            return (parse_request_params(raw_params)
                   .right_and_then(lambda params:
                            mock_api_call(params).fold(
                                if_failure=lambda ex: Left(f"API error: {ex}"),
                                if_success=lambda data: Right(data)
                            )))

        # Valid request
        valid_params = {"user_id": "123", "limit": "5"}
        result1 = handle_api_request(valid_params)
        assert isinstance(result1, Right)
        assert len(result1.unwrap_right()) == 5

        # Missing required param
        invalid_params1 = {"limit": "5"}
        result2 = handle_api_request(invalid_params1)
        assert isinstance(result2, Left)
        assert "user_id" in result2.unwrap_left()

        # Invalid user_id
        invalid_params2 = {"user_id": "not_a_number", "limit": "5"}
        result3 = handle_api_request(invalid_params2)
        assert isinstance(result3, Left)
        assert "user_id" in result3.unwrap_left()

        # Default limit
        minimal_params = {"user_id": "123"}
        result4 = handle_api_request(minimal_params)
        assert isinstance(result4, Right)
        assert len(result4.unwrap_right()) == 10  # default limit


class TestMonadComposition:
    """Test composing monads in functional programming patterns."""

    def test_railway_oriented_programming(self):
        """Test railway-oriented programming pattern with Either."""

        def validate_positive(x: int) -> Either[str, int]:
            return Right(x) if x > 0 else Left("Must be positive")

        def validate_even(x: int) -> Either[str, int]:
            return Right(x) if x % 2 == 0 else Left("Must be even")

        def double_value(x: int) -> Either[str, int]:
            return Right(x * 2)

        def process_number(x: int) -> Either[str, int]:
            """Process number through validation pipeline."""
            return (validate_positive(x)
                   .right_and_then(validate_even)
                   .right_and_then(double_value))

        # Valid case
        result1 = process_number(4)
        assert isinstance(result1, Right)
        assert result1.unwrap_right() == 8

        # Fails at first validation
        result2 = process_number(-2)
        assert isinstance(result2, Left)
        assert "positive" in result2.unwrap_left()

        # Fails at second validation
        result3 = process_number(3)
        assert isinstance(result3, Left)
        assert "even" in result3.unwrap_left()

    def test_option_chaining_with_early_termination(self):
        """Test Option chaining that terminates early on Nil."""

        def safe_divide(a: float, b: float) -> Option[float]:
            return Option(a / b if b != 0 else None)

        def safe_sqrt(x: float) -> Option[float]:
            return Option(x ** 0.5 if x >= 0 else None)

        def safe_log(x: float) -> Option[float]:
            import math
            return Option(math.log(x) if x > 0 else None)

        def complex_calculation(a: float, b: float) -> Option[float]:
            """Perform complex calculation that can fail at any step."""
            return (safe_divide(a, b)
                   .flat_map(safe_sqrt)
                   .flat_map(safe_log))

        # Successful calculation
        result1 = complex_calculation(16, 4)  # 16/4 = 4, sqrt(4) = 2, log(2) ≈ 0.693
        assert isinstance(result1, Some)
        assert abs(result1.get() - 0.693) < 0.01

        # Division by zero
        result2 = complex_calculation(16, 0)
        assert isinstance(result2, Nil)

        # Negative result after division
        result3 = complex_calculation(-16, 4)  # -16/4 = -4, sqrt(-4) fails
        assert isinstance(result3, Nil)

        # Zero result for log
        result4 = complex_calculation(0, 4)  # 0/4 = 0, sqrt(0) = 0, log(0) fails
        assert isinstance(result4, Nil)