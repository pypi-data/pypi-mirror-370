"""
Tests for Err class functionality.
"""
import pytest
from monadc import Result, Ok, Err, Option, Some, Nil, Either, Left, Try, Failure


class TestErrConstruction:
    """Test Err creation and basic properties."""

    def test_err_creation(self):
        """Err should be created with any error value."""
        err = Err("error")
        assert not err.is_ok()
        assert err.is_err()
        assert err.unwrap_err() == "error"

    def test_err_with_none(self):
        """Err should accept None as a valid error value."""
        err = Err(None)
        assert err.is_err()
        assert err.unwrap_err() is None

    def test_err_boolean_conversion(self):
        """Err should be falsy (following Rust convention)."""
        assert not bool(Err("error"))
        assert not bool(Err(404))
        assert not bool(Err(""))
        assert not bool(Err(None))


class TestErrValueAccess:
    """Test Err value access methods."""

    def test_unwrap_raises_error(self):
        """unwrap() should raise error with err value."""
        err = Err("error message")
        with pytest.raises(ValueError, match="Called unwrap\\(\\) on an Err value: error message"):
            err.unwrap()

    def test_unwrap_err_returns_value(self):
        """unwrap_err() should return the err value."""
        err = Err("error")
        assert err.unwrap_err() == "error"

    def test_ok_returns_none(self):
        """ok() should return Nil() for Err."""
        err = Err("error")
        result = err.ok()
        assert isinstance(result, Nil)
        assert result.is_empty()

    def test_err_returns_value(self):
        """err() should return Some(error)."""
        err = Err("error")
        result = err.err()
        assert isinstance(result, Some)
        assert result.unwrap() == "error"

    def test_unwrap_or_returns_default(self):
        """unwrap_or() should return default value for Err."""
        err = Err("error")
        assert err.unwrap_or("default") == "default"

    def test_unwrap_or_else_calls_function(self):
        """unwrap_or_else() should call function with error value."""
        err = Err("error")
        result = err.unwrap_or_else(lambda e: f"handled: {e}")
        assert result == "handled: error"


class TestErrTransformations:
    """Test Err transformation methods."""

    def test_map_returns_self(self):
        """map() should return self unchanged for Err."""
        err = Err("error")
        result = err.map(lambda x: x.upper())
        assert result is err

    def test_map_err_transforms_error(self):
        """map_err() should transform the error value."""
        err = Err("error")
        result = err.map_err(lambda e: e.upper())
        assert isinstance(result, Err)
        assert result.unwrap_err() == "ERROR"

    def test_and_then_returns_self(self):
        """and_then() should return self unchanged for Err."""
        err = Err("error")
        result = err.and_then(lambda x: Ok(x.upper()))
        assert result is err

    def test_or_else_transforms_error(self):
        """or_else() should apply function to error value."""
        err = Err("error")
        result = err.or_else(lambda e: Ok(f"recovered from {e}"))
        assert isinstance(result, Ok)
        assert result.unwrap() == "recovered from error"

    def test_or_else_can_return_err(self):
        """or_else() can return another Err."""
        err = Err("original")
        result = err.or_else(lambda e: Err(f"new error: {e}"))
        assert isinstance(result, Err)
        assert result.unwrap_err() == "new error: original"


class TestErrLogicalOperations:
    """Test Err logical operations."""

    def test_and_returns_self(self):
        """and_() should return self when self is Err."""
        err = Err("error")
        ok = Ok("success")
        other_err = Err("other")

        assert err.and_(ok) is err
        assert err.and_(other_err) is err

    def test_or_returns_other(self):
        """or_() should return other when self is Err."""
        err = Err("error")
        ok = Ok("success")
        other_err = Err("other")

        assert err.or_(ok) == ok
        assert err.or_(other_err) == other_err


class TestErrInspection:
    """Test Err inspection methods."""

    def test_inspect_does_nothing(self):
        """inspect() should do nothing for Err."""
        err = Err("error")
        called = []

        result = err.inspect(lambda x: called.append(x))
        assert result is err
        assert called == []

    def test_inspect_err(self):
        """inspect_err() should call function with err value and return self."""
        err = Err("error")
        called_with = []

        result = err.inspect_err(lambda e: called_with.append(e))
        assert result is err
        assert called_with == ["error"]


class TestErrConversions:
    """Test Err conversion methods."""

    def test_to_option(self):
        """to_option() should convert Err to Nil."""
        err = Err("error")
        option = err.to_option()
        assert isinstance(option, Nil)


    def test_to_try_with_exception(self):
        """to_try() should convert Err with Exception to Failure."""
        exception = ValueError("test error")
        err = Err(exception)
        try_result = err.to_try()
        assert isinstance(try_result, Failure)
        assert try_result.exception() is exception

    def test_to_try_with_non_exception(self):
        """to_try() should wrap non-Exception errors in RuntimeError."""
        err = Err("string error")
        try_result = err.to_try()
        assert isinstance(try_result, Failure)
        exception = try_result.exception()
        assert isinstance(exception, RuntimeError)
        assert str(exception) == "string error"


class TestErrEquality:
    """Test Err equality behavior."""

    def test_err_equality_same_value(self):
        """Err values with same content should be equal."""
        err1 = Err("error")
        err2 = Err("error")
        assert err1 == err2

    def test_err_equality_different_value(self):
        """Err values with different content should not be equal."""
        err1 = Err("error1")
        err2 = Err("error2")
        assert err1 != err2

    def test_err_not_equal_to_ok(self):
        """Err should not equal Ok even with same value."""
        err = Err("value")
        ok = Ok("value")
        assert err != ok

    def test_err_not_equal_to_other_types(self):
        """Err should not equal other types."""
        err = Err("error")
        assert err != "error"
        assert err != ["error"]
        assert err != {"error": "error"}


class TestErrStringRepresentation:
    """Test Err string representation."""

    def test_repr(self):
        """repr() should show Err with error value."""
        err = Err("error")
        assert repr(err) == "Err('error')"

        err_int = Err(404)
        assert repr(err_int) == "Err(404)"

    def test_str(self):
        """str() should be same as repr."""
        err = Err("error")
        assert str(err) == "Err('error')"


class TestErrWithDifferentErrorTypes:
    """Test Err with various error types."""

    def test_err_with_exception(self):
        """Err should work with Exception objects."""
        exception = ValueError("test error")
        err = Err(exception)
        assert err.unwrap_err() is exception

    def test_err_with_custom_error_type(self):
        """Err should work with custom error types."""
        class CustomError:
            def __init__(self, message):
                self.message = message
            def __str__(self):
                return self.message

        custom_err = CustomError("custom error")
        err = Err(custom_err)
        assert err.unwrap_err() is custom_err