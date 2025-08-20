"""
Tests for exception handling edge cases in Result monad.
"""
import pytest
from monadc import Result, Ok, Err


class TestResultFactoryExceptionHandling:
    """Test Result factory constructor edge cases."""

    def test_result_factory_with_kwargs_construction_ok(self):
        """Test that Ok can handle keyword construction."""
        ok = Ok.__new__(Ok, "dummy")
        ok.__init__(None, ok_value="test_value")
        assert ok._value == "test_value"

    def test_result_factory_with_kwargs_construction_err(self):
        """Test that Err can handle keyword construction."""
        err = Err.__new__(Err, "dummy")
        err.__init__(None, err_value="test_error")
        assert err._value == "test_error"


class TestResultEdgeCases:
    """Test Result edge cases and error scenarios."""

    def test_ok_with_none_value(self):
        """Test Ok can contain None value."""
        ok = Ok(None)
        assert ok.is_ok()
        assert ok.unwrap() is None

    def test_err_with_none_error(self):
        """Test Err can contain None error."""
        err = Err(None)
        assert err.is_err()
        assert err.unwrap_err() is None

    def test_result_conversions_with_complex_types(self):
        """Test Result conversions work with complex types."""
        # Test with dictionary
        ok_dict = Ok({"key": "value"})
        option = ok_dict.to_option()
        assert option.is_some()
        assert option.unwrap() == {"key": "value"}

        # Test with list
        err_list = Err(["error1", "error2"])
        option = err_list.to_option()
        assert option.is_none()

    def test_result_chaining_complex_scenario(self):
        """Test complex Result chaining scenario."""
        def divide(a, b):
            if b == 0:
                return Err("Division by zero")
            return Ok(a / b)

        def sqrt(x):
            if x < 0:
                return Err("Negative square root")
            return Ok(x ** 0.5)

        # Test successful chain
        result = (Ok(16)
                 .and_then(lambda x: divide(x, 2))  # 16/2 = 8
                 .and_then(lambda x: sqrt(x)))       # sqrt(8) ≈ 2.83

        assert result.is_ok()
        assert abs(result.unwrap() - 2.8284271247461903) < 0.0001

        # Test failed chain (division by zero)
        result = (Ok(16)
                 .and_then(lambda x: divide(x, 0))
                 .and_then(lambda x: sqrt(x)))

        assert result.is_err()
        assert result.unwrap_err() == "Division by zero"

        # Test failed chain (negative sqrt)
        result = (Ok(-4)
                 .and_then(lambda x: divide(x, 2))  # -4/2 = -2
                 .and_then(lambda x: sqrt(x)))       # sqrt(-2) fails

        assert result.is_err()
        assert result.unwrap_err() == "Negative square root"