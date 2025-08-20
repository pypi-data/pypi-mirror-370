"""
Tests for idiomatic monad usage patterns.

This file demonstrates the recommended ways to use monads for common scenarios,
replacing the old utility functions with more composable monad operations.
"""

import os
from unittest import TestCase

from monadc import Option, Some, Nil, Try, Success, Failure, Result, Ok, Err


class TestIdiomaticPatterns(TestCase):
    """Test idiomatic patterns for creating and using monads."""

    def test_safe_function_calls(self):
        """Demonstrate safe function calls using Try monad."""
        
        # Safe computation that succeeds
        safe_result = Try(lambda: 10 / 2).to_option()
        assert safe_result == Some(5.0)
        
        # Safe computation that fails
        unsafe_result = Try(lambda: 10 / 0).to_option()
        assert unsafe_result == Nil()
        
        # Keep exception context with Try
        division_result = Try(lambda: 10 / 0)
        assert division_result.is_failure()
        # Can inspect the actual exception in Try
        assert isinstance(division_result.exception(), ZeroDivisionError)

    def test_safe_dictionary_access(self):
        """Demonstrate safe dictionary access using Option."""
        
        data = {"name": "Alice", "age": 30}
        
        # Basic access
        name = Option(data.get("name"))
        assert name == Some("Alice")
        
        # Missing key
        email = Option(data.get("email"))
        assert email == Nil()
        
        # With default values
        country = Option(data.get("country") or "Unknown")
        assert country == Some("Unknown")
        
        # Chaining nested dictionary access
        nested_data = {
            "user": {
                "profile": {
                    "email": "alice@example.com"
                }
            }
        }
        
        email = (Option(nested_data.get("user"))
                .flat_map(lambda user: Option(user.get("profile")))
                .flat_map(lambda profile: Option(profile.get("email"))))
        
        assert email == Some("alice@example.com")

    def test_safe_attribute_access(self):
        """Demonstrate safe attribute access using Try monad."""
        
        class User:
            def __init__(self, name: str):
                self.name = name
            
            @property
            def computed_value(self) -> str:
                if self.name == "error":
                    raise ValueError("Computed property error")
                return f"computed_{self.name}"
        
        user = User("Alice")
        error_user = User("error")
        
        # Safe attribute access
        name = Try(lambda: user.name).to_option()
        assert name == Some("Alice")
        
        # Safe property access that succeeds
        computed = Try(lambda: user.computed_value).to_option()
        assert computed == Some("computed_Alice")
        
        # Safe property access that fails
        error_computed = Try(lambda: error_user.computed_value).to_option()
        assert error_computed == Nil()
        
        # Missing attribute
        missing = Try(lambda: user.nonexistent).to_option()
        assert missing == Nil()

    def test_chained_operations(self):
        """Demonstrate chaining operations across different monads."""
        
        # Option chaining with filtering
        result = (Some("hello@example.com")
                 .filter(lambda email: "@" in email)
                 .map(str.upper))
        
        assert result == Some("HELLO@EXAMPLE.COM")
        
        # Failed case - filtering removes invalid emails
        failed_result = (Some("invalid-email")
                        .filter(lambda email: "@" in email)
                        .map(str.upper))
        
        assert failed_result == Nil()
        
        # Try -> Option chaining
        try_result = Try(lambda: "hello@example.com".upper()).to_option()
        assert try_result == Some("HELLO@EXAMPLE.COM")

    def test_real_world_config_loading(self):
        """Demonstrate real-world config loading pattern."""
        
        def load_config():
            """Simulated config loading that might fail."""
            
            # Try to load from environment variable
            config_path = Try(lambda: os.environ["CONFIG_FILE"]).to_option()
            
            if config_path.is_defined():
                # Simulate loading config file
                return Try(lambda: f"config from {config_path.get()}").to_option()
            else:
                # Use default config
                return Some("default config")
        
        # Test with no environment variable (uses default)
        if "CONFIG_FILE" in os.environ:
            del os.environ["CONFIG_FILE"]
        
        config = load_config()
        assert config == Some("default config")
        
        # Test with environment variable
        os.environ["CONFIG_FILE"] = "/etc/myapp.conf"
        config = load_config()
        assert config == Some("config from /etc/myapp.conf")
        
        # Clean up
        del os.environ["CONFIG_FILE"]

    def test_data_validation_pipeline(self):
        """Demonstrate data validation using monads."""
        
        def validate_user_data(data: dict) -> Option[dict]:
            """Validate user data returning Option."""
            
            # Extract and validate required fields using Option
            name_opt = Option(data.get("name"))
            email_opt = (Option(data.get("email"))
                        .filter(lambda e: "@" in e))
            age_opt = (Option(data.get("age"))
                      .filter(lambda a: isinstance(a, int) and a >= 0))
            
            # Combine using flat_map - all must be present
            return (name_opt
                   .flat_map(lambda n: 
                       email_opt.flat_map(lambda e:
                           age_opt.map(lambda a: {"name": n, "email": e, "age": a}))))
        
        # Valid data
        valid_data = {"name": "Alice", "email": "alice@example.com", "age": 25}
        result = validate_user_data(valid_data)
        assert result.is_defined()
        assert result.get() == {"name": "Alice", "email": "alice@example.com", "age": 25}
        
        # Invalid email
        invalid_email_data = {"name": "Alice", "email": "invalid", "age": 25}
        result = validate_user_data(invalid_email_data)
        assert result.is_empty()
        
        # Missing name
        missing_name_data = {"email": "alice@example.com", "age": 25}
        result = validate_user_data(missing_name_data)
        assert result.is_empty()

    def test_interoperability_showcase(self):
        """Demonstrate interoperability between monads."""
        
        def process_data(input_str: str) -> str:
            """Complex processing pipeline using multiple monads."""
            
            # Start with Option, use Try for processing, back to Option
            option_result = Option(input_str).filter(lambda s: len(s) > 0)
            
            if option_result.is_defined():
                try_result = Try(lambda: option_result.get().upper().strip())
                final_option = try_result.to_option()
                return final_option.map(lambda s: f"Processed: {s}").get_or_else("Failed to process")
            else:
                return "Failed to process"
        
        # Success case
        assert process_data("  hello  ") == "Processed: HELLO"
        
        # Empty input case
        assert process_data("") == "Failed to process"
        
        # None input case
        assert process_data(None) == "Failed to process"

    def test_exception_context_preservation(self):
        """Show how Try preserves exception context better than old utils."""
        
        def risky_operation(x: int) -> int:
            if x == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            elif x < 0:
                raise ValueError("Negative values not allowed")
            return 100 // x
        
        # Success case
        success = Try(lambda: risky_operation(10))
        assert success == Success(10)
        assert success.to_option() == Some(10)
        
        # ZeroDivisionError case - we can inspect the actual exception
        zero_error = Try(lambda: risky_operation(0))
        assert zero_error.is_failure()
        assert isinstance(zero_error.exception(), ZeroDivisionError)
        assert "Cannot divide by zero" in str(zero_error.exception())
        
        # ValueError case - different exception type preserved
        value_error = Try(lambda: risky_operation(-1))
        assert value_error.is_failure()
        assert isinstance(value_error.exception(), ValueError)
        assert "Negative values not allowed" in str(value_error.exception())
        
        # Can still convert to Option when you don't need exception details
        as_option = zero_error.to_option()
        assert as_option == Nil()


class TestMigrationPatterns(TestCase):
    """Test migration patterns from old utility functions to idiomatic monads."""
    
    def test_migration_from_callable(self):
        """Show migration from from_callable to Try().to_option()."""
        
        def might_fail():
            return "success"
        
        def will_fail():
            raise RuntimeError("Something went wrong")
        
        # Old pattern (if it existed): from_callable(might_fail)
        # New pattern:
        success = Try(lambda: might_fail()).to_option()
        assert success == Some("success")
        
        failure = Try(lambda: will_fail()).to_option()
        assert failure == Nil()
        
        # Advantage: Can keep exception info with Try
        failure_with_context = Try(lambda: will_fail())
        assert failure_with_context.is_failure()
        assert isinstance(failure_with_context.exception(), RuntimeError)
    
    def test_migration_from_dict_get(self):
        """Show migration from from_dict_get to Option(dict.get())."""
        
        data = {"key": "value", "number": 42}
        
        # Old pattern (if it existed): from_dict_get(data, "key")
        # New pattern:
        value = Option(data.get("key"))
        assert value == Some("value")
        
        missing = Option(data.get("missing"))
        assert missing == Nil()
        
        # With default
        with_default = Option(data.get("missing", "default"))
        assert with_default == Some("default")
        
        # More powerful: can chain operations
        number_doubled = (Option(data.get("number"))
                         .filter(lambda n: isinstance(n, int))
                         .map(lambda n: n * 2))
        assert number_doubled == Some(84)
    
    def test_migration_from_getattr(self):
        """Show migration from from_getattr to Try(lambda: obj.attr).to_option()."""
        
        class TestObj:
            def __init__(self):
                self.attr = "value"
            
            @property
            def prop(self):
                return "property_value"
            
            @property
            def error_prop(self):
                raise ValueError("Property error")
        
        obj = TestObj()
        
        # Old pattern (if it existed): from_getattr(obj, "attr")
        # New pattern:
        attr_value = Try(lambda: obj.attr).to_option()
        assert attr_value == Some("value")
        
        # Property access
        prop_value = Try(lambda: obj.prop).to_option()
        assert prop_value == Some("property_value")
        
        # Missing attribute
        missing = Try(lambda: obj.missing_attr).to_option()
        assert missing == Nil()
        
        # Property that raises exception
        error_prop = Try(lambda: obj.error_prop).to_option()
        assert error_prop == Nil()
        
        # Advantage: Can inspect the exception
        error_try = Try(lambda: obj.error_prop)
        assert error_try.is_failure()
        assert isinstance(error_try.exception(), ValueError)