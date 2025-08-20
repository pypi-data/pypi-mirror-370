"""
Tests for Rust-style Either methods.
"""
import pytest
from monadc import Either, Left, Right


class TestEitherMap:
    """Test Either.map() method."""

    def test_left_map_applies_function_to_value(self):
        """Left.map() should apply function to left value."""
        left = Left("error")
        result = left.map(lambda x: f"Processed: {x}")
        assert result == "Processed: error"

    def test_right_map_applies_function_to_value(self):
        """Right.map() should apply function to right value."""
        right = Right("success")
        result = right.map(lambda x: f"Processed: {x}")
        assert result == "Processed: success"

    def test_map_either_dual_function(self):
        """map_either() should use separate functions for left and right values."""
        left = Left("error")
        right = Right("success")
        
        assert left.map_either(str.upper, str.lower) == "ERROR"
        assert right.map_either(str.upper, str.lower) == "success"


class TestEitherAlias:
    """Test Either.either() method."""

    def test_either_is_alias_for_fold(self):
        """either() should work identically to fold()."""
        left = Left("error")
        right = Right("success")
        
        left_func = lambda x: f"Error: {x}"
        right_func = lambda x: f"Success: {x}"
        
        assert left.either(left_func, right_func) == left.fold(left_func, right_func)
        assert right.either(left_func, right_func) == right.fold(left_func, right_func)


class TestLeftAndThen:
    """Test left_and_then method."""

    def test_left_and_then_on_left(self):
        """Left.left_and_then() should apply function."""
        left = Left("error")
        result = left.left_and_then(lambda x: Left(x.upper()))
        assert isinstance(result, Left)
        assert result.unwrap_left() == "ERROR"

    def test_left_and_then_can_return_right(self):
        """Left.left_and_then() can return Right."""
        left = Left("error")
        result = left.left_and_then(lambda x: Right("converted"))
        assert isinstance(result, Right)
        assert result.unwrap_right() == "converted"

    def test_left_and_then_on_right(self):
        """Right.left_and_then() should pass through unchanged."""
        right = Right("success")
        result = right.left_and_then(lambda x: Left("should not be called"))
        assert result is right


class TestRightAndThen:
    """Test right_and_then method."""

    def test_right_and_then_on_right(self):
        """Right.right_and_then() should apply function."""
        right = Right("success")
        result = right.right_and_then(lambda x: Right(x.upper()))
        assert isinstance(result, Right)
        assert result.unwrap_right() == "SUCCESS"

    def test_right_and_then_can_return_left(self):
        """Right.right_and_then() can return Left."""
        right = Right("success")
        result = right.right_and_then(lambda x: Left("error"))
        assert isinstance(result, Left)
        assert result.unwrap_left() == "error"

    def test_right_and_then_on_left(self):
        """Left.right_and_then() should pass through unchanged."""
        left = Left("error")
        result = left.right_and_then(lambda x: Right("should not be called"))
        assert result is left


class TestLeftOr:
    """Test left_or method."""

    def test_left_or_on_left(self):
        """Left.left_or() should return self."""
        left = Left("original")
        other = Left("other")
        result = left.left_or(other)
        assert result is left

    def test_left_or_on_right(self):
        """Right.left_or() should return other."""
        right = Right("success")
        other = Left("fallback")
        result = right.left_or(other)
        assert result is other


class TestRightOr:
    """Test right_or method."""

    def test_right_or_on_right(self):
        """Right.right_or() should return self."""
        right = Right("original")
        other = Right("other")
        result = right.right_or(other)
        assert result is right

    def test_right_or_on_left(self):
        """Left.right_or() should return other."""
        left = Left("error")
        other = Right("fallback")
        result = left.right_or(other)
        assert result is other


class TestLeftOrElse:
    """Test left_or_else method."""

    def test_left_or_else_on_left(self):
        """Left.left_or_else() should return self without calling function."""
        left = Left("original")
        called = [False]
        result = left.left_or_else(lambda: (called.__setitem__(0, True), Left("fallback"))[1])
        assert result is left
        assert not called[0]

    def test_left_or_else_on_right(self):
        """Right.left_or_else() should call function and return result."""
        right = Right("success")
        result = right.left_or_else(lambda: Left("fallback"))
        assert isinstance(result, Left)
        assert result.unwrap_left() == "fallback"


class TestRightOrElse:
    """Test right_or_else method."""

    def test_right_or_else_on_right(self):
        """Right.right_or_else() should return self without calling function."""
        right = Right("original")
        called = [False]
        result = right.right_or_else(lambda: (called.__setitem__(0, True), Right("fallback"))[1])
        assert result is right
        assert not called[0]

    def test_right_or_else_on_left(self):
        """Left.right_or_else() should call function and return result."""
        left = Left("error")
        result = left.right_or_else(lambda: Right("fallback"))
        assert isinstance(result, Right)
        assert result.unwrap_right() == "fallback"


class TestMethodChaining:
    """Test chaining the new methods together."""

    def test_chaining_and_then_methods(self):
        """Test chaining and_then methods."""
        # Right -> Right -> Left chain
        result = (Right("start")
                 .right_and_then(lambda x: Right(x.upper()))
                 .right_and_then(lambda x: Left(f"Failed: {x}")))
        
        assert isinstance(result, Left)
        assert result.unwrap_left() == "Failed: START"

    def test_chaining_or_methods(self):
        """Test chaining or methods."""
        # Start with Left, use right_or to get Right
        result = (Left("error")
                 .right_or(Right("fallback"))
                 .map_right(str.upper))
        
        assert isinstance(result, Right)
        assert result.unwrap_right() == "FALLBACK"

    def test_complex_chain(self):
        """Test complex method chaining."""
        def validate_positive(x: int) -> Either[str, int]:
            return Right(x) if x > 0 else Left("Must be positive")
        
        def validate_even(x: int) -> Either[str, int]:
            return Right(x) if x % 2 == 0 else Left("Must be even")
        
        # Valid case
        result = (Right(4)
                 .right_and_then(validate_positive)
                 .right_and_then(validate_even)
                 .map_right(lambda x: x * 2))
        
        assert isinstance(result, Right)
        assert result.unwrap_right() == 8
        
        # Invalid case (odd number)
        result2 = (Right(3)
                  .right_and_then(validate_positive)
                  .right_and_then(validate_even)
                  .map_right(lambda x: x * 2))
        
        assert isinstance(result2, Left)
        assert "even" in result2.unwrap_left()


class TestExceptionHandling:
    """Test exception handling in new methods."""

    def test_and_then_exception_propagates(self):
        """Exceptions in and_then should propagate."""
        right = Right(10)
        with pytest.raises(ZeroDivisionError):
            right.right_and_then(lambda x: Right(x / 0))

    def test_map_exception_propagates(self):
        """Exceptions in map should propagate."""
        left = Left(10)
        with pytest.raises(ZeroDivisionError):
            left.map(lambda x: x / 0)

    def test_or_else_exception_propagates(self):
        """Exceptions in or_else function should propagate."""
        left = Left("error")
        with pytest.raises(ValueError):
            left.right_or_else(lambda: (_ for _ in ()).throw(ValueError("test error")))


class TestFlipMethod:
    """Test flip method."""

    def test_left_flip(self):
        """Left.flip() should return Right with same value."""
        left = Left("error")
        result = left.flip()
        assert isinstance(result, Right)
        assert result.unwrap_right() == "error"

    def test_right_flip(self):
        """Right.flip() should return Left with same value."""
        right = Right("success")
        result = right.flip()
        assert isinstance(result, Left)
        assert result.unwrap_left() == "success"

    def test_flip_is_alias_for_swap(self):
        """flip() should work identically to swap()."""
        left = Left("error")
        right = Right("success")
        
        assert left.flip() == left.swap()
        assert right.flip() == right.swap()

    def test_flip_twice_returns_original(self):
        """Calling flip twice should return original Either."""
        left = Left("error")
        right = Right("success")
        
        assert left.flip().flip() == left
        assert right.flip().flip() == right


class TestTypeConsistency:
    """Test type consistency of new methods."""

    def test_and_then_preserves_type_structure(self):
        """and_then methods should preserve Either type structure."""
        left = Left("error")
        right = Right("success")
        
        # Type transformations should work correctly
        left_result = left.left_and_then(lambda x: Right(len(x)))
        assert isinstance(left_result, Right)
        assert left_result.unwrap_right() == 5
        
        right_result = right.right_and_then(lambda x: Left(len(x)))
        assert isinstance(right_result, Left)
        assert right_result.unwrap_left() == 7

    def test_or_methods_maintain_alternative_types(self):
        """or methods should correctly handle type alternatives."""
        left_str = Left("error")
        right_int = Right(42)
        
        # left_or should work with different Left types
        result = right_int.left_or(Left(404))
        assert isinstance(result, Left)
        assert result.unwrap_left() == 404
        
        # right_or should work with different Right types  
        result2 = left_str.right_or(Right("fallback"))
        assert isinstance(result2, Right)
        assert result2.unwrap_right() == "fallback"