"""
Tests for exception handling edge cases in Either monad.
"""
import pytest
from monadc import Either, Left, Right


class TestEitherFactoryExceptionHandling:
    """Test Either factory constructor edge cases."""

    def test_either_factory_with_kwargs_construction(self):
        """Test that Either can handle keyword construction for Left."""
        # This tests the line in left.py where kwargs['left'] is accessed
        left = Left.__new__(Left, "dummy")
        left.__init__(None, left="test_value")
        assert left._value == "test_value"

    def test_either_factory_with_kwargs_construction_right(self):
        """Test that Either can handle keyword construction for Right."""
        # This tests the line in right.py where kwargs['right'] is accessed
        right = Right.__new__(Right, "dummy")
        right.__init__(None, right="test_value")
        assert right._value == "test_value"


class TestRightExceptionHandling:
    """Test Right exception handling edge cases."""

    def test_right_foreach_with_exception(self):
        """Test foreach allows exceptions to propagate."""
        def failing_func(x):
            raise TypeError("Side effect failed")

        right = Right("value")
        # Should raise exception
        with pytest.raises(TypeError, match="Side effect failed"):
            right.foreach(failing_func)