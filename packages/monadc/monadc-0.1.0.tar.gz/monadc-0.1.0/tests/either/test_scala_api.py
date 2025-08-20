"""
Tests for Scala-style Either methods.
"""
import pytest
from monadc import Either, Left, Right


class TestScalaGet:
    """Test Scala-style get() method."""

    def test_right_get_returns_value(self):
        """Right.get() should return the Right value."""
        right = Right("success")
        assert right.get() == "success"

    def test_left_get_raises_error(self):
        """Left.get() should raise ValueError."""
        left = Left("error")
        with pytest.raises(ValueError, match="Cannot get Right value from Left"):
            left.get()


class TestScalaGetOrElse:
    """Test Scala-style get_or_else() method."""

    def test_right_get_or_else_returns_value(self):
        """Right.get_or_else() should return Right value, ignoring default."""
        right = Right("success")
        assert right.get_or_else("default") == "success"
        assert right.get_or_else(lambda: "default") == "success"

    def test_left_get_or_else_returns_default_value(self):
        """Left.get_or_else() should return default value."""
        left = Left("error")
        assert left.get_or_else("default") == "default"

    def test_left_get_or_else_calls_default_function(self):
        """Left.get_or_else() should call default function."""
        left = Left("error")
        assert left.get_or_else(lambda: "computed") == "computed"


class TestScalaContains:
    """Test Scala-style contains() method."""

    def test_right_contains_matching_value(self):
        """Right.contains() should return True for matching value."""
        right = Right("success")
        assert right.contains("success") is True

    def test_right_contains_non_matching_value(self):
        """Right.contains() should return False for non-matching value."""
        right = Right("success")
        assert right.contains("different") is False

    def test_left_contains_always_false(self):
        """Left.contains() should always return False."""
        left = Left("error")
        assert left.contains("success") is False
        assert left.contains("error") is False


class TestScalaExists:
    """Test Scala-style exists() method."""

    def test_right_exists_predicate_true(self):
        """Right.exists() should return True when predicate holds."""
        right = Right("success")
        assert right.exists(lambda x: len(x) > 5) is True

    def test_right_exists_predicate_false(self):
        """Right.exists() should return False when predicate doesn't hold."""
        right = Right("hi")
        assert right.exists(lambda x: len(x) > 5) is False

    def test_left_exists_always_false(self):
        """Left.exists() should always return False."""
        left = Left("error")
        assert left.exists(lambda x: True) is False
        assert left.exists(lambda x: False) is False


class TestScalaOrElse:
    """Test Scala-style or_else() method."""

    def test_right_or_else_returns_self(self):
        """Right.or_else() should return self, ignoring other."""
        right = Right("success")
        other = Right("other")
        result = right.or_else(other)
        assert result is right

    def test_right_or_else_ignores_function(self):
        """Right.or_else() should return self, not calling function."""
        right = Right("success")
        called = [False]
        result = right.or_else(lambda: (called.__setitem__(0, True), Right("other"))[1])
        assert result is right
        assert not called[0]

    def test_left_or_else_returns_other_value(self):
        """Left.or_else() should return other Either."""
        left = Left("error")
        other = Right("fallback")
        result = left.or_else(other)
        assert result is other

    def test_left_or_else_calls_function(self):
        """Left.or_else() should call function and return result."""
        left = Left("error")
        result = left.or_else(lambda: Right("computed"))
        assert isinstance(result, Right)
        assert result.get() == "computed"


class TestScalaToOption:
    """Test Scala-style to_option() method."""

    def test_right_to_option_returns_some(self):
        """Right.to_option() should return Some with Right value."""
        right = Right("success")
        option = right.to_option()
        assert option.is_some()
        assert option.get() == "success"

    def test_left_to_option_returns_nil(self):
        """Left.to_option() should return Nil."""
        left = Left("error")
        option = left.to_option()
        assert option.is_empty()


class TestScalaForeach:
    """Test Scala-style foreach() method."""

    def test_right_foreach_executes_function(self):
        """Right.foreach() should execute function on Right value."""
        right = Right(10)
        results = []
        right.foreach(lambda x: results.append(x * 2))
        assert results == [20]

    def test_left_foreach_does_nothing(self):
        """Left.foreach() should do nothing."""
        left = Left("error")
        results = []
        left.foreach(lambda x: results.append(x))
        assert results == []

    def test_right_foreach_exception_propagates(self):
        """Right.foreach() should let exceptions propagate."""
        right = Right(10)
        with pytest.raises(ZeroDivisionError):
            right.foreach(lambda x: x / 0)

    def test_left_foreach_with_exception_does_nothing(self):
        """Left.foreach() should do nothing even with exception-raising function."""
        left = Left("error")
        # Should not raise
        left.foreach(lambda x: x / 0)


class TestScalaMethodChaining:
    """Test chaining Scala-style methods."""

    def test_right_chain_get_or_else_with_contains(self):
        """Test chaining get_or_else with contains on Right."""
        right = Right("hello")
        result = right.get_or_else("default")
        assert result == "hello"
        assert right.contains("hello")

    def test_left_chain_get_or_else_with_or_else(self):
        """Test chaining get_or_else with or_else on Left."""
        left = Left("error")
        fallback_value = left.get_or_else("fallback")
        assert fallback_value == "fallback"
        
        fallback_either = left.or_else(Right("recovered"))
        assert isinstance(fallback_either, Right)
        assert fallback_either.get() == "recovered"

    def test_complex_scala_chain(self):
        """Test complex chain of Scala methods."""
        def process_either(either: Either[str, str]) -> str:
            return (either
                   .or_else(Right("fallback"))
                   .get_or_else("ultimate_default"))
        
        # Right case
        right_result = process_either(Right("success"))
        assert right_result == "success"
        
        # Left case
        left_result = process_either(Left("error"))
        assert left_result == "fallback"


class TestScalaExceptionHandling:
    """Test exception handling in Scala methods."""

    def test_exists_predicate_exception_propagates(self):
        """Exceptions in exists predicate should propagate."""
        right = Right(10)
        with pytest.raises(ZeroDivisionError):
            right.exists(lambda x: x / 0 > 5)

    def test_get_or_else_function_exception_propagates(self):
        """Exceptions in get_or_else function should propagate."""
        left = Left("error")
        with pytest.raises(ValueError):
            left.get_or_else(lambda: (_ for _ in ()).throw(ValueError("test error")))

    def test_or_else_function_exception_propagates(self):
        """Exceptions in or_else function should propagate."""
        left = Left("error")
        with pytest.raises(RuntimeError):
            left.or_else(lambda: (_ for _ in ()).throw(RuntimeError("test error")))


class TestScalaTypeCompatibility:
    """Test type compatibility for Scala methods."""

    def test_get_or_else_with_different_types(self):
        """get_or_else should work with compatible types."""
        left_str = Left("error")
        result = left_str.get_or_else(42)  # String -> Int fallback
        assert result == 42

    def test_or_else_with_different_left_types(self):
        """or_else should work with different Left types."""
        left_str = Left("string_error")
        result = left_str.or_else(Left(404))  # str -> int Left type
        assert isinstance(result, Left)
        assert result.unwrap_left() == 404

    def test_contains_with_different_types(self):
        """contains should work with different value types."""
        right_int = Right(42)
        assert right_int.contains(42) is True
        assert right_int.contains("42") is False  # Different type