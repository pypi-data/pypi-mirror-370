"""
Tests for Try class constructor and base functionality.
"""
import pytest
from monadc import Try, Success, Failure


class TestTryConstructor:
    """Test Try() constructor behavior."""

    def test_try_with_successful_function_creates_success(self):
        """Try(func) should create Success when function succeeds."""
        result = Try(lambda: "hello")
        assert isinstance(result, Success)
        assert result.get() == "hello"

    def test_try_with_failing_function_creates_failure(self):
        """Try(func) should create Failure when function raises exception."""
        result = Try(lambda: 1 / 0)
        assert isinstance(result, Failure)
        assert isinstance(result.exception(), ZeroDivisionError)

    def test_try_with_no_function_raises_error(self):
        """Try() without function should raise TypeError."""
        with pytest.raises(TypeError):
            Try()  # type: ignore[call-arg]

    def test_try_with_various_return_types(self):
        """Try should work with different return types."""
        # String
        str_try = Try(lambda: "test")
        assert isinstance(str_try, Success)
        assert str_try.get() == "test"

        # Integer
        int_try = Try(lambda: 42)
        assert isinstance(int_try, Success)
        assert int_try.get() == 42

        # None
        none_try = Try(lambda: None)
        assert isinstance(none_try, Success)
        assert none_try.get() is None

        # List
        list_try = Try(lambda: [1, 2, 3])
        assert isinstance(list_try, Success)
        assert list_try.get() == [1, 2, 3]

    def test_try_with_various_exceptions(self):
        """Try should catch different exception types."""
        # ZeroDivisionError
        div_try = Try(lambda: 1 / 0)
        assert isinstance(div_try, Failure)
        assert isinstance(div_try.exception(), ZeroDivisionError)

        # ValueError
        val_try = Try(lambda: int("not a number"))
        assert isinstance(val_try, Failure)
        assert isinstance(val_try.exception(), ValueError)

        # KeyError
        key_try = Try(lambda: {}["missing"])
        assert isinstance(key_try, Failure)
        assert isinstance(key_try.exception(), KeyError)

        # AttributeError
        attr_try = Try(lambda: getattr(object(), "missing"))
        assert isinstance(attr_try, Failure)
        assert isinstance(attr_try.exception(), AttributeError)


class TestTryBaseClass:
    """Test that Try base class prevents direct usage."""

    def test_try_base_class_prevents_direct_usage(self):
        """Try base class methods should raise NotImplementedError."""
        # Create a Try instance bypassing __new__
        try_obj = object.__new__(Try)

        with pytest.raises(NotImplementedError, match="Use Success or Failure, not Try directly"):
            try_obj.is_success()

        with pytest.raises(NotImplementedError, match="Use Success or Failure, not Try directly"):
            try_obj.is_failure()

        with pytest.raises(NotImplementedError, match="Use Success or Failure, not Try directly"):
            try_obj.get()

        with pytest.raises(NotImplementedError, match="Use Success or Failure, not Try directly"):
            try_obj.map(lambda x: x)


class TestTypeAnnotations:
    """Test type annotation compatibility."""

    def test_isinstance_checks(self):
        """Test isinstance works correctly."""
        success_val = Try(lambda: "hello")
        failure_val = Try(lambda: 1 / 0)
        direct_success = Success("world")
        direct_failure = Failure(ValueError("error"))

        # All should be instances of Try
        assert isinstance(success_val, Try)
        assert isinstance(failure_val, Try)
        assert isinstance(direct_success, Try)
        assert isinstance(direct_failure, Try)

        # Specific type checks
        assert isinstance(success_val, Success)
        assert isinstance(failure_val, Failure)
        assert not isinstance(success_val, Failure)
        assert not isinstance(failure_val, Success)

    def test_try_as_type_annotation(self):
        """Test Try can be used in type annotations."""
        def process_try(t: Try[int]) -> Try[str]:
            return t.map(str)

        # Should work with Try constructor
        result1 = process_try(Try(lambda: 42))
        assert isinstance(result1, Success)
        assert result1.get() == "42"

        # Should work with direct Success
        result2 = process_try(Success(100))
        assert isinstance(result2, Success)
        assert result2.get() == "100"

        # Should work with Failure
        result3 = process_try(Failure(ValueError("error")))
        assert isinstance(result3, Failure)
        assert isinstance(result3.exception(), ValueError)


class TestTryEquality:
    """Test Try equality behavior."""

    def test_try_constructed_values_equal_direct_construction(self):
        """Try(func) should equal Success(result) for successful functions."""
        # Success equality
        result1 = Try(lambda: "hello")
        result2 = Success("hello")
        assert result1 == result2
        assert result2 == result1

        # Failure equality (same exception type and message)
        error = ValueError("test error")
        result3 = Failure(error)
        # Try constructor creates new exception, so compare types and messages
        result4 = Try(lambda: (_ for _ in ()).throw(ValueError("test error")))
        assert isinstance(result4, Failure)
        assert type(result3.exception()) == type(result4.exception())
        assert str(result3.exception()) == str(result4.exception())

    def test_different_values_not_equal(self):
        """Try instances with different results should not be equal."""
        assert Try(lambda: "hello") != Try(lambda: "world")
        assert Try(lambda: 42) != Try(lambda: 24)


class TestTryWithSideEffects:
    """Test Try with functions that have side effects."""

    def test_try_executes_side_effects(self):
        """Try should execute side effects even if they don't affect return value."""
        side_effect = []

        def func_with_side_effect():
            side_effect.append("executed")
            return "result"

        result = Try(func_with_side_effect)
        assert isinstance(result, Success)
        assert result.get() == "result"
        assert side_effect == ["executed"]

    def test_try_executes_side_effects_before_exception(self):
        """Try should execute side effects before exception occurs."""
        side_effect = []

        def func_with_side_effect_and_exception():
            side_effect.append("executed")
            raise ValueError("error after side effect")

        result = Try(func_with_side_effect_and_exception)
        assert isinstance(result, Failure)
        assert "error after side effect" in str(result.exception())
        assert side_effect == ["executed"]


class TestTryWithComplexComputations:
    """Test Try with complex computational scenarios."""

    def test_try_with_nested_function_calls(self):
        """Try should handle nested function calls."""
        def complex_computation():
            data = {"user": {"profile": {"email": "test@example.com"}}}
            return data["user"]["profile"]["email"].split("@")[1].upper()

        result = Try(complex_computation)
        assert isinstance(result, Success)
        assert result.get() == "EXAMPLE.COM"

    def test_try_with_failing_nested_function_calls(self):
        """Try should catch exceptions in nested function calls."""
        def failing_computation():
            data = {"user": {}}  # Missing profile
            return data["user"]["profile"]["email"]

        result = Try(failing_computation)
        assert isinstance(result, Failure)
        assert isinstance(result.exception(), KeyError)

    def test_try_with_parameterized_function(self):
        """Try should work with functions that capture parameters."""
        def safe_divide(a, b):
            return Try(lambda: a / b)

        # Successful division
        result1 = safe_divide(10, 2)
        assert isinstance(result1, Success)
        assert result1.get() == 5.0

        # Division by zero
        result2 = safe_divide(10, 0)
        assert isinstance(result2, Failure)
        assert isinstance(result2.exception(), ZeroDivisionError)


class TestTryOfValue:
    """Test Try.of_value factory method."""

    def test_of_value_creates_success(self):
        """Try.of_value should create Success with given value."""
        result = Try.of_value("hello")
        assert isinstance(result, Success)
        assert result.get() == "hello"

    def test_of_value_with_none(self):
        """Try.of_value should create Success even with None value."""
        result = Try.of_value(None)
        assert isinstance(result, Success)
        assert result.get() is None

    def test_of_value_with_various_types(self):
        """Try.of_value should work with different value types."""
        # Integer
        int_result = Try.of_value(42)
        assert isinstance(int_result, Success)
        assert int_result.get() == 42

        # List
        list_result = Try.of_value([1, 2, 3])
        assert isinstance(list_result, Success)
        assert list_result.get() == [1, 2, 3]

        # Dict
        dict_result = Try.of_value({"key": "value"})
        assert isinstance(dict_result, Success)
        assert dict_result.get() == {"key": "value"}

    def test_of_value_with_callable(self):
        """Try.of_value should wrap callable without executing it."""
        func = lambda: "hello"
        result = Try.of_value(func)
        assert isinstance(result, Success)
        assert result.get() is func  # The function itself, not its result
        assert result.get()() == "hello"  # We can still call it

    def test_of_value_vs_try_constructor(self):
        """Compare Try.of_value vs Try() constructor behavior."""
        def get_value():
            return "computed"
        
        # Try() executes the function
        try_result = Try(get_value)
        assert isinstance(try_result, Success)
        assert try_result.get() == "computed"
        
        # Try.of_value wraps the function without executing
        of_value_result = Try.of_value(get_value)
        assert isinstance(of_value_result, Success)
        assert of_value_result.get() is get_value


class TestTryOrElse:
    """Test Try.or_else method for providing alternatives."""

    def test_success_or_else_returns_self(self):
        """Success.or_else should return self, ignoring alternative."""
        success = Success("original")
        alternative = Success("alternative")
        
        result = success.or_else(alternative)
        assert result is success
        assert result.get() == "original"

    def test_success_or_else_with_callable_returns_self(self):
        """Success.or_else with callable should return self without calling function."""
        success = Success("original")
        call_count = 0
        
        def get_alternative():
            nonlocal call_count
            call_count += 1
            return Success("alternative")
        
        result = success.or_else(get_alternative)
        assert result is success
        assert result.get() == "original"
        assert call_count == 0  # Function should not be called

    def test_failure_or_else_returns_alternative(self):
        """Failure.or_else should return the alternative Try."""
        failure = Failure(ValueError("original error"))
        alternative = Success("alternative")
        
        result = failure.or_else(alternative)
        assert result is alternative
        assert result.get() == "alternative"

    def test_failure_or_else_with_callable(self):
        """Failure.or_else with callable should call function and return result."""
        failure = Failure(ValueError("original error"))
        call_count = 0
        
        def get_alternative():
            nonlocal call_count
            call_count += 1
            return Success("alternative")
        
        result = failure.or_else(get_alternative)
        assert isinstance(result, Success)
        assert result.get() == "alternative"
        assert call_count == 1  # Function should be called

    def test_failure_or_else_with_failing_callable(self):
        """Failure.or_else with failing callable should return Failure."""
        failure = Failure(ValueError("original error"))
        
        def failing_alternative():
            raise RuntimeError("alternative failed")
        
        result = failure.or_else(failing_alternative)
        assert isinstance(result, Failure)
        assert isinstance(result.exception(), RuntimeError)
        assert "alternative failed" in str(result.exception())

    def test_failure_or_else_with_failure_alternative(self):
        """Failure.or_else can return another Failure."""
        original_failure = Failure(ValueError("original error"))
        alternative_failure = Failure(RuntimeError("alternative error"))
        
        result = original_failure.or_else(alternative_failure)
        assert result is alternative_failure
        assert isinstance(result.exception(), RuntimeError)

    def test_or_else_chaining(self):
        """Test chaining multiple or_else calls."""
        failure1 = Failure(ValueError("error1"))
        failure2 = Failure(RuntimeError("error2"))
        success = Success("final")
        
        result = failure1.or_else(failure2).or_else(success)
        assert result is success
        assert result.get() == "final"

    def test_or_else_with_complex_types(self):
        """Test or_else with complex value types."""
        failure = Failure(ValueError("error"))
        alternative_data = {"key": "value", "list": [1, 2, 3]}
        alternative = Success(alternative_data)
        
        result = failure.or_else(alternative)
        assert isinstance(result, Success)
        assert result.get() == alternative_data
        assert result.get()["key"] == "value"

    def test_or_else_functional_composition(self):
        """Test or_else in functional composition patterns."""
        def safe_divide(a: float, b: float) -> Try[float]:
            return Try(lambda: a / b)
        
        def default_value() -> Try[float]:
            return Success(0.0)
        
        # Successful division
        result1 = safe_divide(10, 2).or_else(default_value)
        assert isinstance(result1, Success)
        assert result1.get() == 5.0
        
        # Division by zero with fallback
        result2 = safe_divide(10, 0).or_else(default_value)
        assert isinstance(result2, Success)
        assert result2.get() == 0.0

    def test_or_else_with_lazy_evaluation(self):
        """Test that or_else properly handles lazy evaluation."""
        expensive_call_count = 0
        
        def expensive_alternative():
            nonlocal expensive_call_count
            expensive_call_count += 1
            return Success("expensive result")
        
        # Success case - should not call expensive function
        success = Success("cheap")
        result1 = success.or_else(expensive_alternative)
        assert expensive_call_count == 0
        assert result1.get() == "cheap"
        
        # Failure case - should call expensive function
        failure = Failure(ValueError("error"))
        result2 = failure.or_else(expensive_alternative)
        assert expensive_call_count == 1
        assert result2.get() == "expensive result"


class TestTryFlatten:
    """Test Try.flatten method for flattening nested Try instances."""

    def test_success_flatten_success(self):
        """Success[Success[T]] should flatten to Success[T]."""
        inner_success = Success("inner_value")
        outer_success = Success(inner_success)
        
        result = outer_success.flatten()
        assert result is inner_success
        assert isinstance(result, Success)
        assert result.get() == "inner_value"

    def test_success_flatten_failure(self):
        """Success[Failure] should flatten to Failure."""
        inner_failure = Failure(ValueError("inner error"))
        outer_success = Success(inner_failure)
        
        result = outer_success.flatten()
        assert result is inner_failure
        assert isinstance(result, Failure)
        assert isinstance(result.exception(), ValueError)

    def test_success_flatten_non_try_raises_error(self):
        """Success[T] where T is not Try should raise TypeError."""
        success = Success("regular_value")
        
        with pytest.raises(TypeError, match="Cannot flatten Success\\[str\\] - value must be a Try instance"):
            success.flatten()

    def test_failure_flatten_returns_self(self):
        """Failure.flatten() should return self."""
        failure = Failure(ValueError("error"))
        
        result = failure.flatten()
        assert result is failure
        assert isinstance(result, Failure)
        assert isinstance(result.exception(), ValueError)

    def test_flatten_deeply_nested(self):
        """Test flattening deeply nested Try instances."""
        # Create Success[Success[Success[T]]]
        innermost = Success("deep_value")
        middle = Success(innermost)
        outer = Success(middle)
        
        # First flatten: Success[Success[Success[T]]] -> Success[Success[T]]
        result1 = outer.flatten()
        assert result1 is middle
        assert isinstance(result1, Success)
        
        # Second flatten: Success[Success[T]] -> Success[T]
        result2 = result1.flatten()
        assert result2 is innermost
        assert isinstance(result2, Success)
        assert result2.get() == "deep_value"

    def test_flatten_mixed_nested_types(self):
        """Test flattening with mixed Success/Failure nesting."""
        # Success[Failure[Success[T]]] - only flattens one level
        innermost = Success("value")
        middle = Failure(ValueError("middle error"))  # This breaks the chain
        outer = Success(middle)
        
        result = outer.flatten()
        assert result is middle
        assert isinstance(result, Failure)
        assert isinstance(result.exception(), ValueError)

    def test_flatten_with_complex_types(self):
        """Test flatten with complex nested types."""
        complex_data = {"key": "value", "list": [1, 2, 3]}
        inner_success = Success(complex_data)
        outer_success = Success(inner_success)
        
        result = outer_success.flatten()
        assert result is inner_success
        assert isinstance(result, Success)
        assert result.get() == complex_data
        assert result.get()["key"] == "value"

    def test_flatten_safe_idempotent(self):
        """Test that flatten_safe is idempotent for non-nested Try."""
        success = Success("value")
        failure = Failure(ValueError("error"))
        
        # Multiple flatten_safe calls should not change anything
        assert success.flatten_safe() is success
        assert success.flatten_safe().flatten_safe() is success
        
        assert failure.flatten_safe() is failure
        assert failure.flatten_safe().flatten_safe() is failure

    def test_flatten_vs_flatten_safe(self):
        """Test difference between flatten and flatten_safe."""
        # Nested Try - both should work the same
        nested_success = Success(Success("value"))
        nested_failure = Success(Failure(ValueError("error")))
        
        assert nested_success.flatten().get() == "value"
        assert nested_success.flatten_safe().get() == "value"
        
        assert isinstance(nested_failure.flatten(), Failure)
        assert isinstance(nested_failure.flatten_safe(), Failure)
        
        # Non-nested Try - flatten throws, flatten_safe returns self
        regular_success = Success("value")
        
        with pytest.raises(TypeError):
            regular_success.flatten()
            
        assert regular_success.flatten_safe() is regular_success

    def test_flatten_error_messages_for_different_types(self):
        """Test that flatten provides helpful error messages for different types."""
        # String
        with pytest.raises(TypeError, match="Cannot flatten Success\\[str\\]"):
            Success("text").flatten()
            
        # Integer  
        with pytest.raises(TypeError, match="Cannot flatten Success\\[int\\]"):
            Success(42).flatten()
            
        # List
        with pytest.raises(TypeError, match="Cannot flatten Success\\[list\\]"):
            Success([1, 2, 3]).flatten()
            
        # Dict
        with pytest.raises(TypeError, match="Cannot flatten Success\\[dict\\]"):
            Success({"key": "value"}).flatten()

    def test_flatten_with_functional_composition(self):
        """Test flatten in functional composition patterns."""
        def create_nested_try(value: str) -> Try[Try[str]]:
            if value == "error":
                return Success(Failure(ValueError("nested error")))
            else:
                return Success(Success(value.upper()))
        
        # Success case
        result1 = create_nested_try("hello").flatten()
        assert isinstance(result1, Success)
        assert result1.get() == "HELLO"
        
        # Failure case (nested)
        result2 = create_nested_try("error").flatten()
        assert isinstance(result2, Failure)
        assert isinstance(result2.exception(), ValueError)
        assert "nested error" in str(result2.exception())

    def test_flatten_chaining_with_flat_map(self):
        """Test that flatten can replace some flat_map usage."""
        def create_nested(x: int) -> Try[int]:
            return Success(x * 2)
        
        # Create a nested Try manually
        nested = Success(Success(10))
        
        # Using flat_map approach
        result1 = nested.flat_map(lambda inner_try: inner_try)
        
        # Using flatten approach  
        result2 = nested.flatten()
        
        # Both should produce the same result
        assert isinstance(result1, Success)
        assert isinstance(result2, Success)
        assert result1.get() == 10
        assert result2.get() == 10
        
        # Verify they're equivalent
        assert result1.get() == result2.get()

    def test_flatten_vs_flat_map_equivalence(self):
        """Test that map + flatten can replace flat_map in some cases."""
        def wrap_double(x: int) -> Try[int]:
            return Success(x * 2)
        
        value = Success(5)
        
        # Traditional flat_map
        result1 = value.flat_map(wrap_double)
        
        # Using map + flatten (though unnecessary here since wrap_double doesn't return Try[Try[T]])
        # This example shows the concept
        result2 = value.map(lambda x: wrap_double(x)).flatten()
        
        assert isinstance(result1, Success)
        assert isinstance(result2, Success)
        assert result1.get() == 10
        assert result2.get() == 10