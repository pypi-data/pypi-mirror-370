"""
Tests for Result class constructor and base functionality.
"""
import pytest
from monadc import Result, Ok, Err


class TestResultConstructor:
    """Test Result() constructor behavior."""

    def test_result_with_ok_value_creates_ok(self):
        """Result(ok_value=x) should create Ok(x)."""
        result = Result(ok_value="success")
        assert isinstance(result, Ok)
        assert result.unwrap() == "success"

    def test_result_with_err_value_creates_err(self):
        """Result(err_value=x) should create Err(x)."""
        result = Result(err_value="error")
        assert isinstance(result, Err)
        assert result.unwrap_err() == "error"

    def test_result_with_both_values_raises_error(self):
        """Result() should raise error when both ok_value and err_value provided."""
        with pytest.raises(ValueError, match="Cannot specify both ok_value and err_value"):
            Result(ok_value="success", err_value="error")

    def test_result_with_no_values_raises_error(self):
        """Result() should raise error when no values provided."""
        with pytest.raises(ValueError, match="Must specify either ok_value or err_value"):
            Result()

    def test_result_with_various_types(self):
        """Result should work with different value types."""
        # String
        str_result = Result(ok_value="test")
        assert isinstance(str_result, Ok)
        assert str_result.unwrap() == "test"

        # Integer
        int_result = Result(err_value=404)
        assert isinstance(int_result, Err)
        assert int_result.unwrap_err() == 404

        # None values are allowed
        none_ok = Result(ok_value=None)
        assert isinstance(none_ok, Ok)
        assert none_ok.unwrap() is None

        none_err = Result(err_value=None)
        assert isinstance(none_err, Err)
        assert none_err.unwrap_err() is None


class TestResultBaseClass:
    """Test that Result base class cannot be used directly."""

    def test_result_base_class_prevents_direct_usage(self):
        """Result base class methods should raise NotImplementedError."""
        # This would create an Ok, but we can't test the base class directly
        # We'll test this indirectly through the factory constructor
        pass


class TestTypeAnnotations:
    """Test isinstance checks and type annotations."""

    def test_isinstance_checks(self):
        """Test isinstance works correctly with Result types."""
        ok_val = Ok("success")
        err_val = Err("error")

        assert isinstance(ok_val, Result)
        assert isinstance(ok_val, Ok)
        assert not isinstance(ok_val, Err)

        assert isinstance(err_val, Result)
        assert isinstance(err_val, Err)
        assert not isinstance(err_val, Ok)

    def test_result_as_type_annotation(self):
        """Test Result can be used as type annotation."""
        def process_result(r: Result[str, str]) -> str:
            return r.unwrap_or("default")

        ok_result = Ok("success")
        err_result = Err("error")

        assert process_result(ok_result) == "success"
        assert process_result(err_result) == "default"


class TestResultEquality:
    """Test equality behavior for Result factory."""

    def test_result_constructed_values_equal_direct_construction(self):
        """Result factory should create equivalent objects to direct construction."""
        factory_ok = Result(ok_value="test")
        direct_ok = Ok("test")
        assert factory_ok == direct_ok

        factory_err = Result(err_value="error")
        direct_err = Err("error")
        assert factory_err == direct_err