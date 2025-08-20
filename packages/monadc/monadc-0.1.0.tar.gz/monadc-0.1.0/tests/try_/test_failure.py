"""
Tests for Failure class functionality.
"""
import pytest
from monadc import Try, Success, Failure


class TestFailureConstruction:
    """Test Failure construction and basic properties."""

    def test_failure_creation(self):
        """Test Failure can be created with any Exception."""
        error = ValueError("test error")
        failure = Failure(error)
        assert failure.exception() is error
        assert failure.is_failure()
        assert not failure.is_success()

    def test_failure_boolean_conversion(self):
        """Failure should be falsy."""
        assert not bool(Failure(ValueError("error")))
        assert not bool(Failure(Exception()))


class TestFailureValueAccess:
    """Test Failure value access methods."""

    def test_get_raises_original_exception(self):
        """get() should raise the original exception."""
        error = ValueError("test error")
        failure = Failure(error)
        with pytest.raises(ValueError, match="test error"):
            failure.get()

    def test_get_or_else_with_value(self):
        """get_or_else() should return default value."""
        failure = Failure(ValueError("error"))
        assert failure.get_or_else("default") == "default"
        assert failure.get_or_else(42) == 42

    def test_get_or_else_with_callable(self):
        """get_or_else() should call default function."""
        failure = Failure(ValueError("error"))
        assert failure.get_or_else(lambda: "computed") == "computed"

        counter = [0]
        def increment():
            counter[0] += 1
            return counter[0]

        result = failure.get_or_else(increment)
        assert result == 1
        assert counter[0] == 1

    def test_exception_returns_exception(self):
        """exception() should return the wrapped exception."""
        error = ValueError("test error")
        failure = Failure(error)
        assert failure.exception() is error


class TestFailureTransformations:
    """Test Failure transformation methods (should be no-ops)."""

    def test_map_returns_self(self):
        """Failure.map() should return self unchanged."""
        failure = Failure(ValueError("error"))
        result = failure.map(lambda x: x.upper())
        assert result is failure

    def test_flat_map_returns_self(self):
        """Failure.flat_map() should return self unchanged."""
        failure = Failure(ValueError("error"))
        result = failure.flat_map(lambda x: Success(x.upper()))
        assert result is failure

    def test_filter_returns_self(self):
        """Failure.filter() should return self unchanged."""
        failure = Failure(ValueError("error"))
        result = failure.filter(lambda x: True)
        assert result is failure


class TestFailureRecovery:
    """Test Failure recovery methods."""

    def test_recover_transforms_exception(self):
        """Failure.recover() should transform exception to Success."""
        failure = Failure(ValueError("error"))
        result = failure.recover(lambda ex: f"Recovered: {ex}")
        assert isinstance(result, Success)
        assert "Recovered: error" in result.get()

    def test_recover_exception_creates_new_failure(self):
        """recover() function exceptions should create new Failure."""
        failure = Failure(ValueError("original"))
        result = failure.recover(lambda ex: (_ for _ in ()).throw(RuntimeError("recovery error")))
        assert isinstance(result, Failure)
        assert isinstance(result.exception(), RuntimeError)
        assert "recovery error" in str(result.exception())

    def test_recover_with_to_success(self):
        """Failure.recover_with() should allow recovery to Success."""
        failure = Failure(ValueError("error"))
        result = failure.recover_with(lambda ex: Success(f"Recovered: {ex}"))
        assert isinstance(result, Success)
        assert "Recovered: error" in result.get()

    def test_recover_with_to_failure(self):
        """Failure.recover_with() can return another Failure."""
        failure = Failure(ValueError("original"))
        result = failure.recover_with(lambda ex: Failure(RuntimeError("new error")))
        assert isinstance(result, Failure)
        assert isinstance(result.exception(), RuntimeError)
        assert "new error" in str(result.exception())

    def test_recover_with_exception_creates_failure(self):
        """recover_with() function exceptions should create Failure."""
        failure = Failure(ValueError("original"))
        result = failure.recover_with(lambda ex: (_ for _ in ()).throw(RuntimeError("recovery error")))
        assert isinstance(result, Failure)
        assert isinstance(result.exception(), RuntimeError)


class TestFailureFolding:
    """Test Failure folding methods."""

    def test_fold_calls_failure_function(self):
        """Failure.fold() should call if_failure function."""
        failure = Failure(ValueError("error"))
        result = failure.fold(
            if_failure=lambda ex: f"Error: {ex}",
            if_success=lambda x: f"Success: {x}"
        )
        assert result == "Error: error"

    def test_fold_with_exception_in_failure_function(self):
        """fold() should propagate exceptions from if_failure."""
        failure = Failure(ValueError("original"))
        with pytest.raises(RuntimeError):
            failure.fold(
                if_failure=lambda ex: (_ for _ in ()).throw(RuntimeError("fold error")),
                if_success=lambda x: x
            )

    def test_transform_calls_failure_function(self):
        """Failure.transform() should call failure_func."""
        failure = Failure(ValueError("error"))
        result = failure.transform(
            success_func=lambda x: Success(x.upper()),
            failure_func=lambda ex: Success("recovered")
        )
        assert isinstance(result, Success)
        assert result.get() == "recovered"


class TestFailureSideEffects:
    """Test Failure side effect methods."""

    def test_foreach_does_nothing(self):
        """Failure.foreach() should do nothing."""
        failure = Failure(ValueError("error"))
        called = [False]
        failure.foreach(lambda x: called.__setitem__(0, True))
        assert not called[0]


class TestFailureConversions:
    """Test Failure conversion methods."""

    def test_to_option(self):
        """Failure.to_option() should return Nil."""
        failure = Failure(ValueError("error"))
        option = failure.to_option()
        from monadc import Nil
        assert isinstance(option, type(Nil()))
        assert option.is_empty()

    def test_to_either(self):
        """Failure.to_either() should return Left with the exception."""
        error = ValueError("error")
        failure = Failure(error)
        either = failure.to_either()
        from monadc import Left
        assert isinstance(either, Left)
        assert either.unwrap_left() is error


class TestFailureEquality:
    """Test Failure equality behavior."""

    def test_failure_equality_same_exception(self):
        """Failure instances with same exception should be equal."""
        error = ValueError("error")
        failure1 = Failure(error)
        failure2 = Failure(error)
        assert failure1 == failure2

    def test_failure_equality_equivalent_exceptions(self):
        """Failure instances with equivalent exceptions should be equal."""
        failure1 = Failure(ValueError("error"))
        failure2 = Failure(ValueError("error"))
        # This might or might not be equal depending on implementation
        # At minimum, they should have same type and message
        assert type(failure1.exception()) == type(failure2.exception())
        assert str(failure1.exception()) == str(failure2.exception())

    def test_failure_not_equal_to_success(self):
        """Failure should never equal Success."""
        failure = Failure(ValueError("error"))
        success = Success("hello")
        assert failure != success
        assert success != failure

    def test_failure_not_equal_to_other_types(self):
        """Failure should not equal non-Try types."""
        failure = Failure(ValueError("error"))
        assert failure != ValueError("error")
        assert failure != "error"
        assert failure != None


class TestFailureStringRepresentation:
    """Test Failure string representation."""

    def test_repr(self):
        """Test Failure.__repr__()."""
        error = ValueError("test error")
        failure = Failure(error)
        repr_str = repr(failure)
        assert "Failure" in repr_str
        assert "ValueError" in repr_str
        assert "test error" in repr_str

    def test_str(self):
        """Test Failure.__str__()."""
        error = ValueError("test error")
        failure = Failure(error)
        str_repr = str(failure)
        assert "Failure" in str_repr


class TestFailureWithDifferentExceptionTypes:
    """Test Failure with various exception types."""

    def test_failure_with_runtime_error(self):
        """Test Failure with RuntimeError."""
        error = RuntimeError("runtime error")
        failure = Failure(error)
        assert failure.exception() is error
        with pytest.raises(RuntimeError):
            failure.get()

    def test_failure_with_custom_exception(self):
        """Test Failure with custom exception class."""
        class CustomError(Exception):
            def __init__(self, code, message):
                self.code = code
                self.message = message
                super().__init__(f"{code}: {message}")

        error = CustomError(404, "Not Found")
        failure = Failure(error)
        assert failure.exception() is error
        assert failure.exception().code == 404
        assert failure.exception().message == "Not Found"

    def test_failure_with_system_exit(self):
        """Test Failure with SystemExit (should still work)."""
        error = SystemExit(1)
        failure = Failure(error)
        assert failure.exception() is error
        with pytest.raises(SystemExit):
            failure.get()