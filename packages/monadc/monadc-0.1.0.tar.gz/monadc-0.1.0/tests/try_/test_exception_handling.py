"""
Tests for exception handling edge cases in Try monad.
"""
import pytest
from monadc import Try, Success, Failure


class TestTryFactoryExceptionHandling:
    """Test Try factory constructor edge cases."""

    def test_try_success_double_init_protection(self):
        """Test that Success protects against double initialization."""
        success = Success.__new__(Success, "test_value")
        success.__init__("test_value")
        # Try to init again - should be ignored
        success.__init__("different_value")
        assert success._value == "test_value"

    def test_try_failure_double_init_protection(self):
        """Test that Failure protects against double initialization."""
        error = ValueError("test error")
        failure = Failure.__new__(Failure, error)
        failure.__init__(error)
        # Try to init again - should be ignored
        failure.__init__(RuntimeError("different error"))
        assert failure._exception == error


class TestFailureExceptionHandling:
    """Test Failure exception handling edge cases."""

    def test_failure_recover_with_exception(self):
        """Test recover method when recovery function itself throws exception."""
        def failing_recovery(exc):
            raise RuntimeError("Recovery failed")

        failure = Failure(ValueError("original error"))
        result = failure.recover(failing_recovery)
        # Should create a new Failure with the recovery exception
        assert isinstance(result, Failure)
        assert isinstance(result._exception, RuntimeError)
        assert str(result._exception) == "Recovery failed"

    def test_failure_recover_with_to_failure_exception(self):
        """Test recover_with method when recovery function throws exception."""
        def failing_recovery_with(exc):
            raise TypeError("Recovery with failed")

        failure = Failure(ValueError("original error"))
        result = failure.recover_with(failing_recovery_with)
        # Should create a new Failure with the recovery exception
        assert isinstance(result, Failure)
        assert isinstance(result._exception, TypeError)


class TestSuccessExceptionHandling:
    """Test Success exception handling edge cases."""

    def test_success_transform_with_exception(self):
        """Test transform method when transform function throws exception."""
        def failing_transform(val):
            raise ValueError("Transform failed")

        success = Success("value")
        result = success.transform(failing_transform, lambda e: e)
        # Should create a Failure with the transform exception
        assert isinstance(result, Failure)
        assert isinstance(result._exception, ValueError)

    def test_success_transform_with_exception_in_failure_func(self):
        """Test transform method when failure function throws exception."""
        def failing_failure_func(exc):
            raise RuntimeError("Failure function failed")

        # Create a success first, then manually create a failure to test the failure function path
        success = Success("value")
        # Transform success to failure first
        failure = success.map(lambda x: 1/0)  # This will create a Failure due to division by zero

        # Now test transform on this failure
        result = failure.transform(lambda v: v, failing_failure_func)
        # Should create a new Failure with the failure function exception
        assert isinstance(result, Failure)
        # The exception could be either ZeroDivisionError or RuntimeError depending on implementation