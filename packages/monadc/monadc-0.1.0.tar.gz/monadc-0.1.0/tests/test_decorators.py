"""
Tests for monad decorators.
"""
import pytest
from monadc import Option, Some, Nil, option, try_decorator, try_, result
from monadc import Try, Success, Failure, Result, Ok, Err, Either, Left, Right


class TestOptionDecorator:
    """Test @option decorator."""

    def test_option_with_non_none_return(self):
        """@option should wrap non-None returns in Some."""
        @option
        def get_value() -> str:
            return "hello"

        result = get_value()
        assert isinstance(result, Some)
        assert result.get() == "hello"

    def test_option_with_none_return(self):
        """@option should wrap None returns in Nil."""
        @option
        def get_none() -> str:
            return None

        result = get_none()
        assert isinstance(result, Nil)

    def test_option_with_parameters(self):
        """@option should work with parameterized functions."""
        @option
        def add(a: int, b: int) -> int:
            return a + b

        result = add(2, 3)
        assert isinstance(result, Some)
        assert result.get() == 5

    def test_option_exception_propagates(self):
        """@option should let exceptions propagate normally."""
        @option
        def raises_error() -> str:
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            raises_error()

    def test_option_preserves_function_metadata(self):
        """@option should preserve original function metadata."""
        @option
        def documented_func() -> str:
            """This function has documentation."""
            return "result"

        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "This function has documentation."

    def test_option_with_various_types(self):
        """@option should work with different return types."""
        @option
        def get_int() -> int:
            return 42

        @option
        def get_list() -> list:
            return [1, 2, 3]

        @option
        def get_dict() -> dict:
            return {"key": "value"}

        assert get_int().get() == 42
        assert get_list().get() == [1, 2, 3]
        assert get_dict().get() == {"key": "value"}

    def test_option_with_empty_collections(self):
        """@option should wrap empty collections as Some (not Nil)."""
        @option
        def get_empty_list() -> list:
            return []

        @option
        def get_empty_dict() -> dict:
            return {}

        @option
        def get_empty_string() -> str:
            return ""

        assert isinstance(get_empty_list(), Some)
        assert isinstance(get_empty_dict(), Some)
        assert isinstance(get_empty_string(), Some)


class TestDecoratorIntegration:
    """Test decorators working with Option methods."""

    def test_decorated_function_chaining(self):
        """Test chaining methods on decorated function results."""
        @try_
        def parse_email(s: str) -> str:
            if "@" not in s:
                raise ValueError("Invalid email")
            return s.lower()

        @try_
        def extract_domain(email: str) -> str:
            return email.split("@")[1]

        # Chain operations
        result = (parse_email("ALICE@EXAMPLE.COM")
                 .flat_map(lambda email: extract_domain(email))
                 .map(lambda domain: domain.upper())
                 .filter(lambda domain: len(domain) > 3))

        assert isinstance(result, Success)
        assert result.get() == "EXAMPLE.COM"

        # Test failure case
        result2 = (parse_email("invalid-email")
                  .flat_map(lambda email: extract_domain(email)))
        assert isinstance(result2, Failure)

    def test_decorated_functions_with_utilities(self):
        """Test decorated functions working with utility functions."""
        from monadc import Option

        @try_
        def process_user_age(age_str: str) -> int:
            age = int(age_str)
            if age < 0 or age > 150:
                raise ValueError("Invalid age")
            return age

        user_data = {"age": "25", "name": "Alice"}

        # Using idiomatic Option pattern instead of utility function
        age_option = Option(user_data.get("age"))
        if age_option.is_defined():
            result = (process_user_age(age_option.get())
                     .map(lambda age: f"Age: {age}"))
            assert isinstance(result, Success)
            assert result.get() == "Age: 25"
        else:
            assert False, "Should have found age in user_data"

        # Test with invalid age
        invalid_data = {"age": "invalid", "name": "Bob"}
        age_option2 = Option(invalid_data.get("age"))
        if age_option2.is_defined():
            result2 = process_user_age(age_option2.get())
            assert isinstance(result2, Failure)
        else:
            assert False, "Should have found age in invalid_data"


class TestDecoratorEdgeCases:
    """Test edge cases for decorators."""

    def test_decorated_methods(self):
        """Test decorators on class methods."""
        class Calculator:
            @try_
            def divide(self, a: int, b: int) -> float:
                return a / b

            @option
            def multiply(self, a: int, b: int) -> int:
                return a * b

        calc = Calculator()

        # Try method
        assert calc.divide(10, 2).get() == 5.0
        assert isinstance(calc.divide(10, 0), Failure)

        # Option method
        assert calc.multiply(3, 4).get() == 12

    def test_decorated_functions_with_default_args(self):
        """Test decorators with functions that have default arguments."""
        @try_
        def greet(name: str, greeting: str = "Hello") -> str:
            if not name.strip():
                raise ValueError("Name cannot be empty")
            return f"{greeting}, {name}!"

        assert greet("Alice").get() == "Hello, Alice!"
        assert greet("Bob", "Hi").get() == "Hi, Bob!"
        assert isinstance(greet(""), Failure)

    def test_decorated_generator_functions(self):
        """Test decorators with generator functions."""
        @option
        def get_range(n: int) -> range:
            return range(n)

        result = get_range(5)
        assert isinstance(result, Some)
        assert list(result.get()) == [0, 1, 2, 3, 4]


class TestDecoratorCompatibilityWithOtherMonads:
    """Test decorators working with other monad types."""

    def test_option_decorator_with_either_conversion(self):
        """Test @try_ decorator results can be converted to Either."""
        from monadc import Right, Left

        @try_
        def safe_parse(s: str) -> int:
            return int(s)

        # Success case
        result1 = safe_parse("42").to_either()
        assert isinstance(result1, Right)
        assert result1.unwrap_right() == 42

        # Failure case
        result2 = safe_parse("invalid").to_either()
        assert isinstance(result2, Left)
        assert isinstance(result2.unwrap_left(), ValueError)

    def test_try_decorator_with_try_integration(self):
        """Test @try_ decorator working with Try monad."""
        from monadc import Try

        @try_
        def get_config_value(config: dict, key: str) -> str:
            return config[key]

        def safe_config_processing(config: dict, key: str) -> str:
            # Use Try for robust error handling
            try_result = get_config_value(config, key)
            if try_result.is_success():
                return try_result.get().upper()
            else:
                return "MISSING"

        # Test with valid config
        config1 = {"database_url": "postgres://localhost"}
        result1 = safe_config_processing(config1, "database_url")
        assert result1 == "POSTGRES://LOCALHOST"

        # Test with missing key
        config2 = {}
        result2 = safe_config_processing(config2, "database_url")
        assert result2 == "MISSING"


class TestTryDecorator:
    """Test @try_decorator and @try_ decorators."""

    def test_try_decorator_with_success(self):
        """@try_decorator should wrap successful returns in Success."""
        @try_decorator
        def parse_int(s: str) -> int:
            return int(s)

        result = parse_int("42")
        assert isinstance(result, Success)
        assert result.get() == 42

    def test_try_decorator_with_exception(self):
        """@try_decorator should wrap exceptions in Failure."""
        @try_decorator
        def parse_int(s: str) -> int:
            return int(s)

        result = parse_int("invalid")
        assert isinstance(result, Failure)
        assert isinstance(result.exception(), ValueError)

    def test_try_alias_works(self):
        """@try_ should work as alias for @try_decorator."""
        @try_
        def divide(a: float, b: float) -> float:
            return a / b

        # Success case
        success = divide(10.0, 2.0)
        assert isinstance(success, Success)
        assert success.get() == 5.0

        # Failure case
        failure = divide(10.0, 0.0)
        assert isinstance(failure, Failure)
        assert isinstance(failure.exception(), ZeroDivisionError)
        
    def test_try_decorator_preserves_metadata(self):
        """@try_decorator should preserve function metadata."""
        @try_decorator
        def documented_function() -> str:
            """This is a documented function."""
            return "result"

        assert documented_function.__name__ == "documented_function"
        assert "documented function" in documented_function.__doc__


class TestResultDecorator:
    """Test @result decorator."""

    def test_result_with_success(self):
        """@result should wrap successful returns in Ok."""
        @result
        def add(a: int, b: int) -> int:
            return a + b

        res = add(2, 3)
        assert isinstance(res, Ok)
        assert res.unwrap() == 5

    def test_result_with_exception(self):
        """@result should wrap exceptions in Err."""
        @result
        def divide(a: float, b: float) -> float:
            if b == 0:
                raise ZeroDivisionError("Division by zero")
            return a / b

        # Success case
        success = divide(10.0, 2.0)
        assert isinstance(success, Ok)
        assert success.unwrap() == 5.0

        # Error case
        error = divide(10.0, 0.0)
        assert isinstance(error, Err)
        assert isinstance(error.unwrap_err(), ZeroDivisionError)

    def test_result_with_various_exception_types(self):
        """@result should handle different exception types."""
        @result
        def risky_operation(action: str) -> str:
            if action == "key_error":
                raise KeyError("Missing key")
            elif action == "value_error":
                raise ValueError("Invalid value")
            elif action == "type_error":
                raise TypeError("Wrong type")
            return f"Success: {action}"

        # Success
        success = risky_operation("success")
        assert isinstance(success, Ok)
        assert success.unwrap() == "Success: success"

        # Different error types
        key_err = risky_operation("key_error")
        assert isinstance(key_err, Err)
        assert isinstance(key_err.unwrap_err(), KeyError)

        val_err = risky_operation("value_error")  
        assert isinstance(val_err, Err)
        assert isinstance(val_err.unwrap_err(), ValueError)

    def test_result_preserves_metadata(self):
        """@result should preserve function metadata."""
        @result
        def calculate(x: int) -> int:
            """Calculate something important."""
            return x * 2

        assert calculate.__name__ == "calculate"
        assert "important" in calculate.__doc__


class TestDecoratorInteroperability:
    """Test that different decorators work well together."""

    def test_monad_conversion_compatibility(self):
        """Test that decorated functions work with monad conversions."""
        @try_decorator
        def parse_number(s: str) -> float:
            return float(s)

        @result
        def divide_by_two(x: float) -> float:
            return x / 2

        # Chain Try -> Either -> Option conversion
        try_result = parse_number("10.0")
        either_from_try = try_result.to_either()
        option_from_either = either_from_try.to_option()
        
        assert isinstance(either_from_try, Right)
        assert either_from_try.unwrap_right() == 10.0
        assert isinstance(option_from_either, Some)
        assert option_from_either.get() == 10.0

    def test_decorator_functional_composition(self):
        """Test functional composition with different decorators."""
        @try_
        def safe_parse(s: str) -> int:
            return int(s)

        @result  
        def safe_divide(a: int, b: int) -> float:
            return a / b

        # Compose operations
        def safe_parse_and_divide(s: str, divisor: int) -> str:
            parsed = safe_parse(s)
            if parsed.is_success():
                divided = safe_divide(parsed.get(), divisor)
                if divided.is_ok():
                    return f"Result: {divided.unwrap()}"
                else:
                    return f"Division error: {divided.unwrap_err()}"
            else:
                return f"Parse error: {parsed.exception()}"

        # Test successful composition
        result1 = safe_parse_and_divide("20", 4)
        assert result1 == "Result: 5.0"

        # Test parse failure
        result2 = safe_parse_and_divide("invalid", 4)
        assert "Parse error" in result2

        # Test division failure  
        result3 = safe_parse_and_divide("20", 0)
        assert "Division error" in result3