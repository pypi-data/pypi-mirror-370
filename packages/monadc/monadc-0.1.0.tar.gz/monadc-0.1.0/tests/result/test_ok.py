"""
Tests for Ok class functionality.
"""
import pytest
from monadc import Result, Ok, Err, Option, Some, Nil, Either, Right, Try, Success


class TestOkConstruction:
    """Test Ok creation and basic properties."""

    def test_ok_creation(self):
        """Ok should be created with any value."""
        ok = Ok("success")
        assert ok.is_ok()
        assert not ok.is_err()
        assert ok.unwrap() == "success"

    def test_ok_with_none(self):
        """Ok should accept None as a valid value."""
        ok = Ok(None)
        assert ok.is_ok()
        assert ok.unwrap() is None

    def test_ok_boolean_conversion(self):
        """Ok should be truthy (following Rust convention)."""
        assert bool(Ok("success"))
        assert bool(Ok(0))  # Even falsy values make Ok truthy
        assert bool(Ok(""))
        assert bool(Ok(None))


class TestOkValueAccess:
    """Test Ok value access methods."""

    def test_unwrap_returns_value(self):
        """unwrap() should return the ok value."""
        ok = Ok("success")
        assert ok.unwrap() == "success"

    def test_unwrap_err_raises_error(self):
        """unwrap_err() should raise error on Ok."""
        ok = Ok("success")
        with pytest.raises(ValueError, match="Called unwrap_err\\(\\) on an Ok value"):
            ok.unwrap_err()

    def test_ok_returns_value(self):
        """ok() should return Some(value)."""
        ok = Ok("success")
        result = ok.ok()
        assert isinstance(result, Some)
        assert result.unwrap() == "success"

    def test_err_returns_none(self):
        """err() should return Nil() for Ok."""
        ok = Ok("success")
        result = ok.err()
        assert isinstance(result, Nil)
        assert result.is_empty()

    def test_unwrap_or_returns_value(self):
        """unwrap_or() should return the ok value, ignoring default."""
        ok = Ok("success")
        assert ok.unwrap_or("default") == "success"

    def test_unwrap_or_else_returns_value(self):
        """unwrap_or_else() should return the ok value, not calling function."""
        ok = Ok("success")
        assert ok.unwrap_or_else(lambda e: "default") == "success"


class TestOkTransformations:
    """Test Ok transformation methods."""

    def test_map(self):
        """map() should transform the ok value."""
        ok = Ok("hello")
        result = ok.map(lambda x: x.upper())
        assert isinstance(result, Ok)
        assert result.unwrap() == "HELLO"

    def test_map_with_none_result_creates_ok_with_none(self):
        """map() returning None should create Ok(None)."""
        ok = Ok("hello")
        result = ok.map(lambda x: None)
        assert isinstance(result, Ok)
        assert result.unwrap() is None

    def test_map_err_returns_self(self):
        """map_err() should return self unchanged for Ok."""
        ok = Ok("success")
        result = ok.map_err(lambda e: e.upper())
        assert result is ok

    def test_and_then(self):
        """and_then() should chain ok values."""
        ok = Ok("hello")
        result = ok.and_then(lambda x: Ok(x.upper()))
        assert isinstance(result, Ok)
        assert result.unwrap() == "HELLO"

    def test_and_then_to_err(self):
        """and_then() should be able to chain to Err."""
        ok = Ok("hello")
        result = ok.and_then(lambda x: Err("error"))
        assert isinstance(result, Err)
        assert result.unwrap_err() == "error"

    def test_or_else_returns_self(self):
        """or_else() should return self for Ok."""
        ok = Ok("success")
        result = ok.or_else(lambda e: Ok("recovery"))
        assert result is ok


class TestOkLogicalOperations:
    """Test Ok logical operations."""

    def test_and_returns_other(self):
        """and_() should return other when self is Ok."""
        ok1 = Ok("first")
        ok2 = Ok("second")
        err = Err("error")

        assert ok1.and_(ok2) == ok2
        assert ok1.and_(err) == err

    def test_or_returns_self(self):
        """or_() should return self when self is Ok."""
        ok = Ok("success")
        other = Ok("other")
        err = Err("error")

        assert ok.or_(other) == ok
        assert ok.or_(err) == ok


class TestOkInspection:
    """Test Ok inspection methods."""

    def test_inspect(self):
        """inspect() should call function with ok value and return self."""
        ok = Ok("success")
        called_with = []

        result = ok.inspect(lambda x: called_with.append(x))
        assert result is ok
        assert called_with == ["success"]

    def test_inspect_err_does_nothing(self):
        """inspect_err() should do nothing for Ok."""
        ok = Ok("success")
        called = []

        result = ok.inspect_err(lambda e: called.append(e))
        assert result is ok
        assert called == []


class TestOkConversions:
    """Test Ok conversion methods."""

    def test_to_option(self):
        """to_option() should convert Ok to Some."""
        ok = Ok("success")
        option = ok.to_option()
        assert isinstance(option, Some)
        assert option.get() == "success"


    def test_to_try(self):
        """to_try() should convert Ok to Success."""
        ok = Ok("success")
        try_result = ok.to_try()
        assert isinstance(try_result, Success)
        assert try_result.get() == "success"


class TestOkEquality:
    """Test Ok equality behavior."""

    def test_ok_equality_same_value(self):
        """Ok values with same content should be equal."""
        ok1 = Ok("success")
        ok2 = Ok("success")
        assert ok1 == ok2

    def test_ok_equality_different_value(self):
        """Ok values with different content should not be equal."""
        ok1 = Ok("success")
        ok2 = Ok("failure")
        assert ok1 != ok2

    def test_ok_not_equal_to_err(self):
        """Ok should not equal Err even with same value."""
        ok = Ok("value")
        err = Err("value")
        assert ok != err

    def test_ok_not_equal_to_other_types(self):
        """Ok should not equal other types."""
        ok = Ok("success")
        assert ok != "success"
        assert ok != ["success"]
        assert ok != {"value": "success"}


class TestOkStringRepresentation:
    """Test Ok string representation."""

    def test_repr(self):
        """repr() should show Ok with value."""
        ok = Ok("hello")
        assert repr(ok) == "Ok('hello')"

        ok_int = Ok(42)
        assert repr(ok_int) == "Ok(42)"

    def test_str(self):
        """str() should be same as repr."""
        ok = Ok("hello")
        assert str(ok) == "Ok('hello')"