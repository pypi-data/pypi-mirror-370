"""
Tests for Left class functionality.
"""
import pytest
from monadc import Either, Left, Right


class TestLeftConstruction:
    """Test Left construction and basic properties."""

    def test_left_creation(self):
        """Test Left can be created with any value."""
        left = Left("error")
        assert left.unwrap_left() == "error"
        assert left.is_left()
        assert not left.is_right()

    def test_left_with_none(self):
        """Left can contain None value."""
        left = Left(None)
        assert left.unwrap_left() is None
        assert left.is_left()

    def test_left_boolean_conversion(self):
        """Left should be truthy (like any object instance in Python)."""
        assert bool(Left("error"))
        assert bool(Left(0))
        assert bool(Left(""))
        assert bool(Left(None))


class TestLeftValueAccess:
    """Test Left value access methods."""

    def test_unwrap_left_returns_value(self):
        """unwrap_left() should return the wrapped value."""
        left = Left("error message")
        assert left.unwrap_left() == "error message"

    def test_unwrap_right_raises_error(self):
        """unwrap_right() should raise ValueError."""
        left = Left("error")
        with pytest.raises(ValueError, match="Cannot unwrap right value from Left"):
            left.unwrap_right()

    def test_left_returns_option_some(self):
        """left() should return Some with the value."""
        left = Left("error")
        option = left.left()
        from monadc import Some
        assert isinstance(option, Some)
        assert option.get() == "error"

    def test_right_returns_option_nil(self):
        """right() should return Nil."""
        left = Left("error")
        option = left.right()
        from monadc import Nil
        assert isinstance(option, type(Nil()))
        assert option.is_empty()

    def test_expect_left_returns_value(self):
        """expect_left() should return the wrapped value."""
        left = Left("error message")
        assert left.expect_left("Should be left") == "error message"

    def test_expect_right_raises_error(self):
        """expect_right() should raise ValueError with custom message."""
        left = Left("error")
        with pytest.raises(ValueError, match="Custom error message"):
            left.expect_right("Custom error message")


class TestLeftTransformations:
    """Test Left transformation methods (should be no-ops for Right-biased operations)."""

    def test_map_right_returns_self(self):
        """Left.map_right() should return self unchanged."""
        left = Left("error")
        result = left.map_right(lambda x: x.upper())
        assert result is left
        assert result.unwrap_left() == "error"

    def test_map_left_transforms_value(self):
        """Left.map_left() should transform the left value."""
        left = Left("error")
        result = left.map_left(lambda x: x.upper())
        assert isinstance(result, Left)
        assert result.unwrap_left() == "ERROR"


class TestLeftFolding:
    """Test Left folding methods."""

    def test_fold_calls_left_function(self):
        """Left.fold() should call if_left function."""
        left = Left("error")
        result = left.fold(
            if_left=lambda x: f"Error: {x}",
            if_right=lambda x: f"Success: {x}"
        )
        assert result == "Error: error"

    def test_fold_with_exception_in_left_function(self):
        """fold() should propagate exceptions from if_left."""
        left = Left("error")
        with pytest.raises(ValueError):
            left.fold(
                if_left=lambda x: (_ for _ in ()).throw(ValueError("fold error")),
                if_right=lambda x: x
            )


class TestLeftSideEffects:
    """Test Left side effect methods."""

    def test_foreach_does_nothing(self):
        """Left.foreach() should do nothing."""
        left = Left("error")
        called = [False]
        left.foreach(lambda x: called.__setitem__(0, True))
        assert not called[0]



class TestLeftUtilityMethods:
    """Test Left utility methods."""

    def test_swap(self):
        """Left.swap() should return Right with same value."""
        left = Left("error")
        swapped = left.swap()
        assert isinstance(swapped, Right)
        assert swapped.unwrap_right() == "error"

    def test_to_option(self):
        """Left.to_option() should return Nil."""
        left = Left("error")
        option = left.to_option()
        # Import here to avoid circular imports in test
        from monadc import Nil
        assert isinstance(option, type(Nil()))
        assert option.is_empty()


class TestLeftEquality:
    """Test Left equality behavior."""

    def test_left_equality_same_value(self):
        """Left instances with same value should be equal."""
        left1 = Left("error")
        left2 = Left("error")
        assert left1 == left2

    def test_left_equality_different_value(self):
        """Left instances with different values should not be equal."""
        left1 = Left("error1")
        left2 = Left("error2")
        assert left1 != left2

    def test_left_not_equal_to_right(self):
        """Left should never equal Right, even with same value."""
        left = Left("value")
        right = Right("value")
        assert left != right
        assert right != left

    def test_left_not_equal_to_other_types(self):
        """Left should not equal non-Either types."""
        left = Left("error")
        assert left != "error"
        assert left != None
        assert left != 42


class TestLeftStringRepresentation:
    """Test Left string representation."""

    def test_repr(self):
        """Test Left.__repr__()."""
        left = Left("error")
        assert repr(left) == "Left('error')"

        left_int = Left(404)
        assert repr(left_int) == "Left(404)"

    def test_str(self):
        """Test Left.__str__()."""
        left = Left("error")
        assert str(left) == "Left('error')"