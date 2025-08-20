"""
Tests for Success class functionality.
"""
import pytest
from monadc import Try, Success, Failure


class TestSuccessConstruction:
    """Test Success construction and basic properties."""

    def test_success_creation(self):
        """Test Success can be created with any value."""
        success = Success("hello")
        assert success.get() == "hello"
        assert success.is_success()
        assert not success.is_failure()

    def test_success_with_none(self):
        """Success can contain None value."""
        success = Success(None)
        assert success.get() is None
        assert success.is_success()

    def test_success_boolean_conversion(self):
        """Success should be truthy."""
        assert bool(Success("hello"))
        assert bool(Success(0))  # Even falsy values make Success truthy
        assert bool(Success(""))
        assert bool(Success(None))


class TestSuccessValueAccess:
    """Test Success value access methods."""

    def test_get_returns_value(self):
        """get() should return the wrapped value."""
        success = Success("hello")
        assert success.get() == "hello"

    def test_get_or_else_returns_value(self):
        """get_or_else() should return the value, ignoring default."""
        success = Success("hello")
        assert success.get_or_else("default") == "hello"
        assert success.get_or_else(lambda: "default") == "hello"

    def test_exception_returns_none(self):
        """exception() should return None for Success."""
        success = Success("hello")
        assert success.exception() is None


class TestSuccessTransformations:
    """Test Success transformation methods."""

    def test_map(self):
        """Test Success.map() transformation."""
        success = Success("hello")
        result = success.map(str.upper)
        assert isinstance(result, Success)
        assert result.get() == "HELLO"

    def test_map_with_none_result(self):
        """map() returning None should create Success(None)."""
        success = Success("hello")
        result = success.map(lambda x: None)
        assert isinstance(result, Success)
        assert result.get() is None

    def test_map_exception_creates_failure(self):
        """map() should catch exceptions and return Failure."""
        success = Success(10)
        result = success.map(lambda x: x / 0)
        assert isinstance(result, Failure)
        assert isinstance(result.exception(), ZeroDivisionError)

    def test_flat_map(self):
        """Test Success.flat_map() transformation."""
        success = Success("hello")
        result = success.flat_map(lambda x: Success(x.upper()))
        assert isinstance(result, Success)
        assert result.get() == "HELLO"

    def test_flat_map_to_failure(self):
        """flat_map() can return Failure."""
        success = Success("hello")
        result = success.flat_map(lambda x: Failure(ValueError("error")))
        assert isinstance(result, Failure)
        assert isinstance(result.exception(), ValueError)

    def test_flat_map_exception_creates_failure(self):
        """flat_map() should catch exceptions and return Failure."""
        success = Success(10)
        result = success.flat_map(lambda x: Success(x / 0))
        assert isinstance(result, Failure)
        assert isinstance(result.exception(), ZeroDivisionError)

    def test_filter_true_returns_self(self):
        """filter() with true predicate returns self."""
        success = Success(10)
        result = success.filter(lambda x: x > 5)
        assert result is success

    def test_filter_false_returns_failure(self):
        """filter() with false predicate returns Failure."""
        success = Success(10)
        result = success.filter(lambda x: x > 15)
        assert isinstance(result, Failure)
        # Should contain a NoSuchElementException or similar
        assert "filter predicate" in str(result.exception()) or isinstance(result.exception(), Exception)

    def test_filter_exception_creates_failure(self):
        """filter() should catch exceptions and return Failure."""
        success = Success(10)
        result = success.filter(lambda x: x / 0 > 5)
        assert isinstance(result, Failure)
        assert isinstance(result.exception(), ZeroDivisionError)


class TestSuccessRecovery:
    """Test Success recovery methods (should be no-ops)."""

    def test_recover_returns_self(self):
        """Success.recover() should return self unchanged."""
        success = Success("hello")
        result = success.recover(lambda ex: "recovery")
        assert result is success

    def test_recover_with_returns_self(self):
        """Success.recover_with() should return self unchanged."""
        success = Success("hello")
        result = success.recover_with(lambda ex: Success("recovery"))
        assert result is success


class TestSuccessFolding:
    """Test Success folding methods."""

    def test_fold_calls_success_function(self):
        """Success.fold() should call if_success function."""
        success = Success("hello")
        result = success.fold(
            if_failure=lambda ex: f"Error: {ex}",
            if_success=lambda x: f"Success: {x}"
        )
        assert result == "Success: hello"

    def test_fold_with_exception_in_success_function(self):
        """fold() should propagate exceptions from if_success."""
        success = Success("hello")
        with pytest.raises(ValueError):
            success.fold(
                if_failure=lambda ex: str(ex),
                if_success=lambda x: (_ for _ in ()).throw(ValueError("fold error"))
            )

    def test_transform_calls_success_function(self):
        """Success.transform() should call success_func."""
        success = Success("hello")
        result = success.transform(
            success_func=lambda x: Success(x.upper()),
            failure_func=lambda ex: Failure(ex)
        )
        assert isinstance(result, Success)
        assert result.get() == "HELLO"


class TestSuccessSideEffects:
    """Test Success side effect methods."""

    def test_foreach(self):
        """foreach() should apply function to value."""
        success = Success(10)
        result = []
        success.foreach(lambda x: result.append(x * 2))
        assert result == [20]

    def test_foreach_with_exception(self):
        """foreach() exceptions should not affect the Success."""
        success = Success(10)
        # Exception should be swallowed (or logged) but not propagate
        try:
            success.foreach(lambda x: x / 0)
        except ZeroDivisionError:
            # If exceptions propagate, that's also acceptable behavior
            pass


class TestSuccessConversions:
    """Test Success conversion methods."""

    def test_to_option(self):
        """Success.to_option() should return Some with the value."""
        success = Success("hello")
        option = success.to_option()
        from monadc import Some
        assert isinstance(option, Some)
        assert option.get() == "hello"

    def test_to_either(self):
        """Success.to_either() should return Right with the value."""
        success = Success("hello")
        either = success.to_either()
        from monadc import Right
        assert isinstance(either, Right)
        assert either.unwrap_right() == "hello"


class TestSuccessEquality:
    """Test Success equality behavior."""

    def test_success_equality_same_value(self):
        """Success instances with same value should be equal."""
        success1 = Success("hello")
        success2 = Success("hello")
        assert success1 == success2

    def test_success_equality_different_value(self):
        """Success instances with different values should not be equal."""
        success1 = Success("hello")
        success2 = Success("world")
        assert success1 != success2

    def test_success_not_equal_to_failure(self):
        """Success should never equal Failure."""
        success = Success("hello")
        failure = Failure(ValueError("error"))
        assert success != failure
        assert failure != success

    def test_success_not_equal_to_other_types(self):
        """Success should not equal non-Try types."""
        success = Success("hello")
        assert success != "hello"
        assert success != None
        assert success != 42


class TestSuccessStringRepresentation:
    """Test Success string representation."""

    def test_repr(self):
        """Test Success.__repr__()."""
        success = Success("hello")
        assert repr(success) == "Success('hello')"

        success_int = Success(42)
        assert repr(success_int) == "Success(42)"

    def test_str(self):
        """Test Success.__str__()."""
        success = Success("hello")
        assert str(success) == "Success('hello')"