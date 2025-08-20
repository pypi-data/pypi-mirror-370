"""
Tests for Either class constructor and base functionality.
"""
import pytest
from monadc import Either, Left, Right


class TestEitherConstructor:
    """Test Either() constructor behavior."""

    def test_either_with_right_value_creates_right(self):
        """Either(right=x) should create Right(x)."""
        result = Either(right="success")
        assert isinstance(result, Right)
        assert result.unwrap_right() == "success"

    def test_either_with_left_value_creates_left(self):
        """Either(left=x) should create Left(x)."""
        result = Either(left="error")
        assert isinstance(result, Left)
        assert result.unwrap_left() == "error"

    def test_either_with_both_values_raises_error(self):
        """Either with both values should raise ValueError."""
        with pytest.raises(ValueError, match="Cannot specify both left and right"):
            Either(right="success", left="error")

    def test_either_with_no_values_raises_error(self):
        """Either with no values should raise ValueError."""
        with pytest.raises(ValueError, match="Must specify either left or right"):
            Either()

    def test_either_with_various_types(self):
        """Either should work with different value types."""
        # String
        str_either = Either(right="test")
        assert isinstance(str_either, Right)
        assert str_either.unwrap_right() == "test"

        # Integer
        int_either = Either(left=404)
        assert isinstance(int_either, Left)
        assert int_either.unwrap_left() == 404

        # None values are allowed
        none_right = Either(right=None)
        assert isinstance(none_right, Right)
        assert none_right.unwrap_right() is None

        none_left = Either(left=None)
        assert isinstance(none_left, Left)
        assert none_left.unwrap_left() is None


class TestEitherBaseClass:
    """Test that Either base class prevents direct usage."""

    def test_either_base_class_prevents_direct_usage(self):
        """Either base class methods should raise NotImplementedError."""
        # Create an Either instance bypassing __new__
        either = object.__new__(Either)

        with pytest.raises(NotImplementedError, match="Use Left or Right, not Either directly"):
            either.is_left()

        with pytest.raises(NotImplementedError, match="Use Left or Right, not Either directly"):
            either.is_right()

        with pytest.raises(NotImplementedError, match="Use Left or Right, not Either directly"):
            either.unwrap_left()

        with pytest.raises(NotImplementedError, match="Use Left or Right, not Either directly"):
            either.unwrap_right()

        with pytest.raises(NotImplementedError, match="Use Left or Right, not Either directly"):
            either.map_right(lambda x: x)


class TestTypeAnnotations:
    """Test type annotation compatibility."""

    def test_isinstance_checks(self):
        """Test isinstance works correctly."""
        right_val = Either(right="hello")
        left_val = Either(left="error")
        direct_right = Right("world")
        direct_left = Left("fail")

        # All should be instances of Either
        assert isinstance(right_val, Either)
        assert isinstance(left_val, Either)
        assert isinstance(direct_right, Either)
        assert isinstance(direct_left, Either)

        # Specific type checks
        assert isinstance(right_val, Right)
        assert isinstance(left_val, Left)
        assert not isinstance(right_val, Left)
        assert not isinstance(left_val, Right)

    def test_either_as_type_annotation(self):
        """Test Either can be used in type annotations."""
        def process_either(e: Either[str, int]) -> Either[str, str]:
            return e.map_right(str)

        # Should work with Either constructor
        result1 = process_either(Either(right=42))
        assert isinstance(result1, Right)
        assert result1.unwrap_right() == "42"

        # Should work with direct Right
        result2 = process_either(Right(100))
        assert isinstance(result2, Right)
        assert result2.unwrap_right() == "100"

        # Should work with Left
        result3 = process_either(Left("error"))
        assert isinstance(result3, Left)
        assert result3.unwrap_left() == "error"


class TestEitherEquality:
    """Test Either equality behavior."""

    def test_either_constructed_values_equal_direct_construction(self):
        """Either(right=x) should equal Right(x) and Either(left=x) should equal Left(x)."""
        # Right equality
        assert Either(right="hello") == Right("hello")
        assert Right("hello") == Either(right="hello")

        # Left equality
        assert Either(left="error") == Left("error")
        assert Left("error") == Either(left="error")

        # Different values not equal
        assert Either(right="hello") != Either(right="world")
        assert Either(left="error1") != Either(left="error2")
        assert Either(right="hello") != Either(left="hello")