"""
Tests for Right class functionality.
"""
import pytest
from monadc import Either, Left, Right


class TestRightConstruction:
    """Test Right construction and basic properties."""

    def test_right_creation(self):
        """Test Right can be created with any value."""
        right = Right("success")
        assert right.unwrap_right() == "success"
        assert right.is_right()
        assert not right.is_left()

    def test_right_with_none(self):
        """Right can contain None value."""
        right = Right(None)
        assert right.unwrap_right() is None
        assert right.is_right()

    def test_right_boolean_conversion(self):
        """Right should be truthy (following Scala convention)."""
        assert bool(Right("success"))
        assert bool(Right(0))  # Even falsy values make Right truthy
        assert bool(Right(""))
        assert bool(Right(None))


class TestRightValueAccess:
    """Test Right value access methods."""

    def test_unwrap_right_returns_value(self):
        """unwrap_right() should return the wrapped value."""
        right = Right("success")
        assert right.unwrap_right() == "success"

    def test_unwrap_left_raises_error(self):
        """unwrap_left() should raise ValueError."""
        right = Right("success")
        with pytest.raises(ValueError, match="Cannot unwrap left value from Right"):
            right.unwrap_left()

    def test_right_returns_option_some(self):
        """right() should return Some with the value."""
        right = Right("success")
        option = right.right()
        from monadc import Some
        assert isinstance(option, Some)
        assert option.get() == "success"

    def test_left_returns_option_nil(self):
        """left() should return Nil."""
        right = Right("success")
        option = right.left()
        from monadc import Nil
        assert isinstance(option, type(Nil()))
        assert option.is_empty()

    def test_expect_right_returns_value(self):
        """expect_right() should return the wrapped value."""
        right = Right("success message")
        assert right.expect_right("Should be right") == "success message"

    def test_expect_left_raises_error(self):
        """expect_left() should raise ValueError with custom message."""
        right = Right("success")
        with pytest.raises(ValueError, match="Custom error message"):
            right.expect_left("Custom error message")


class TestRightTransformations:
    """Test Right transformation methods."""

    def test_map_right(self):
        """Test Right.map_right() transformation."""
        right = Right("hello")
        result = right.map_right(str.upper)
        assert isinstance(result, Right)
        assert result.unwrap_right() == "HELLO"

    def test_map_with_none_result_creates_right_with_none(self):
        """map() returning None should create Right(None)."""
        right = Right("hello")
        result = right.map_right(lambda x: None)
        assert isinstance(result, Right)
        assert result.unwrap_right() is None

    def test_map_exception_propagates(self):
        """map() should let exceptions bubble up."""
        right = Right(10)
        with pytest.raises(ZeroDivisionError):
            right.map_right(lambda x: x / 0)

    def test_map_left_returns_self(self):
        """Right.map_left() should return self unchanged."""
        right = Right("success")
        result = right.map_left(lambda x: x.upper())
        assert result is right


class TestRightFolding:
    """Test Right folding methods."""

    def test_fold_calls_right_function(self):
        """Right.fold() should call if_right function."""
        right = Right("success")
        result = right.fold(
            if_left=lambda x: f"Error: {x}",
            if_right=lambda x: f"Success: {x}"
        )
        assert result == "Success: success"

    def test_fold_with_exception_in_right_function(self):
        """fold() should propagate exceptions from if_right."""
        right = Right("success")
        with pytest.raises(ValueError):
            right.fold(
                if_left=lambda x: x,
                if_right=lambda x: (_ for _ in ()).throw(ValueError("fold error"))
            )


class TestRightSideEffects:
    """Test Right side effect methods."""

    def test_foreach(self):
        """foreach() should apply function to value."""
        right = Right(10)
        result = []
        right.foreach(lambda x: result.append(x * 2))
        assert result == [20]

    def test_foreach_exception_propagates(self):
        """foreach() should let exceptions bubble up."""
        right = Right(10)
        with pytest.raises(ZeroDivisionError):
            right.foreach(lambda x: x / 0)



class TestRightUtilityMethods:
    """Test Right utility methods."""

    def test_swap(self):
        """Right.swap() should return Left with same value."""
        right = Right("success")
        swapped = right.swap()
        assert isinstance(swapped, Left)
        assert swapped.unwrap_left() == "success"

    def test_to_option(self):
        """Right.to_option() should return Some with the value."""
        right = Right("success")
        option = right.to_option()
        # Import here to avoid circular imports in test
        from monadc import Some
        assert isinstance(option, Some)
        assert option.get() == "success"


class TestRightEquality:
    """Test Right equality behavior."""

    def test_right_equality_same_value(self):
        """Right instances with same value should be equal."""
        right1 = Right("success")
        right2 = Right("success")
        assert right1 == right2

    def test_right_equality_different_value(self):
        """Right instances with different values should not be equal."""
        right1 = Right("success1")
        right2 = Right("success2")
        assert right1 != right2

    def test_right_not_equal_to_left(self):
        """Right should never equal Left, even with same value."""
        right = Right("value")
        left = Left("value")
        assert right != left
        assert left != right

    def test_right_not_equal_to_other_types(self):
        """Right should not equal non-Either types."""
        right = Right("success")
        assert right != "success"
        assert right != None
        assert right != 42


class TestRightStringRepresentation:
    """Test Right string representation."""

    def test_repr(self):
        """Test Right.__repr__()."""
        right = Right("success")
        assert repr(right) == "Right('success')"

        right_int = Right(42)
        assert repr(right_int) == "Right(42)"

    def test_str(self):
        """Test Right.__str__()."""
        right = Right("success")
        assert str(right) == "Right('success')"