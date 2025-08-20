"""
Tests for Python 3.10+ pattern matching support in Either monad.
"""
import sys
import pytest
from monadc import Either, Left, Right


# Skip all tests if Python < 3.10 (pattern matching not available)
pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 10), 
    reason="Pattern matching requires Python 3.10+"
)


class TestBasicPatternMatching:
    """Test basic pattern matching with Left and Right."""

    def test_left_pattern_matching(self):
        """Test pattern matching on Left values."""
        left = Left("error")
        
        match left:
            case Left(value):
                result = f"Error: {value}"
            case Right(value):
                result = f"Success: {value}"
        
        assert result == "Error: error"

    def test_right_pattern_matching(self):
        """Test pattern matching on Right values."""
        right = Right("success")
        
        match right:
            case Left(value):
                result = f"Error: {value}"
            case Right(value):
                result = f"Success: {value}"
        
        assert result == "Success: success"

    def test_pattern_matching_without_catch_all(self):
        """Test that catch-all is not required when all Either cases are covered."""
        def process_either(either: Either[str, int]) -> str:
            match either:
                case Left(error):
                    return f"Failed with: {error}"
                case Right(value):
                    return f"Succeeded with: {value}"
            # No case _ needed since Left and Right are exhaustive for Either
        
        assert process_either(Left("boom")) == "Failed with: boom"
        assert process_either(Right(42)) == "Succeeded with: 42"


class TestPatternMatchingWithTypes:
    """Test pattern matching with different value types."""

    def test_string_values(self):
        """Test pattern matching with string values."""
        cases = [Left("error message"), Right("success message")]
        results = []
        
        for case in cases:
            match case:
                case Left(msg):
                    results.append(f"ERROR: {msg.upper()}")
                case Right(msg):
                    results.append(f"OK: {msg.upper()}")
        
        assert results == ["ERROR: ERROR MESSAGE", "OK: SUCCESS MESSAGE"]

    def test_numeric_values(self):
        """Test pattern matching with numeric values."""
        cases = [Left(404), Right(200)]
        results = []
        
        for case in cases:
            match case:
                case Left(code):
                    results.append(f"HTTP Error: {code}")
                case Right(code):
                    results.append(f"HTTP Success: {code}")
        
        assert results == ["HTTP Error: 404", "HTTP Success: 200"]

    def test_mixed_types(self):
        """Test pattern matching with mixed Left/Right types."""
        cases = [Left("string_error"), Right(123)]
        results = []
        
        for case in cases:
            match case:
                case Left(error_msg):
                    results.append(f"Error: {error_msg}")
                case Right(success_val):
                    results.append(f"Value: {success_val * 2}")
        
        assert results == ["Error: string_error", "Value: 246"]


class TestPatternMatchingWithGuards:
    """Test pattern matching with guard conditions."""

    def test_guards_on_values(self):
        """Test pattern matching with guards on the extracted values."""
        def categorize_result(either: Either[str, int]) -> str:
            match either:
                case Right(value) if value > 100:
                    return "large_success"
                case Right(value) if value > 0:
                    return "small_success"
                case Right(value):
                    return "zero_or_negative"
                case Left(error) if "critical" in error:
                    return "critical_error"
                case Left(error):
                    return "normal_error"
        
        assert categorize_result(Right(150)) == "large_success"
        assert categorize_result(Right(50)) == "small_success"
        assert categorize_result(Right(0)) == "zero_or_negative"
        assert categorize_result(Left("critical failure")) == "critical_error"
        assert categorize_result(Left("minor issue")) == "normal_error"

    def test_guards_on_either_type(self):
        """Test pattern matching with guards on Either instances."""
        def process_special_cases(either: Either[str, str]) -> str:
            match either:
                case Left(msg) if len(msg) > 10:
                    return "long_error"
                case Left(msg):
                    return "short_error"
                case Right(msg) if msg.startswith("URGENT"):
                    return "urgent_success"
                case Right(msg):
                    return "normal_success"
        
        assert process_special_cases(Left("very long error message")) == "long_error"
        assert process_special_cases(Left("short")) == "short_error"
        assert process_special_cases(Right("URGENT: fix this")) == "urgent_success"
        assert process_special_cases(Right("all good")) == "normal_success"


class TestPatternMatchingInFunctions:
    """Test pattern matching used in various function contexts."""

    def test_either_processing_function(self):
        """Test a function that processes Either using pattern matching."""
        def handle_division(dividend: int, divisor: int) -> Either[str, float]:
            if divisor == 0:
                return Left("Division by zero")
            return Right(dividend / divisor)
        
        def process_division_result(result: Either[str, float]) -> str:
            match result:
                case Left(error):
                    return f"Cannot compute: {error}"
                case Right(value) if value > 1.0:
                    return f"Result is greater than 1: {value:.2f}"
                case Right(value):
                    return f"Result is less than or equal to 1: {value:.2f}"
        
        assert process_division_result(handle_division(10, 2)) == "Result is greater than 1: 5.00"
        assert process_division_result(handle_division(1, 2)) == "Result is less than or equal to 1: 0.50"
        assert process_division_result(handle_division(10, 0)) == "Cannot compute: Division by zero"

    def test_nested_pattern_matching(self):
        """Test pattern matching with nested structures."""
        def process_nested_either(either: Either[str, Either[str, int]]) -> str:
            match either:
                case Left(outer_error):
                    return f"Outer error: {outer_error}"
                case Right(inner_either):
                    match inner_either:
                        case Left(inner_error):
                            return f"Inner error: {inner_error}"
                        case Right(value):
                            return f"Final value: {value}"
        
        # Test cases
        outer_left = Left("outer failure")
        inner_left = Right(Left("inner failure"))
        inner_right = Right(Right(42))
        
        assert process_nested_either(outer_left) == "Outer error: outer failure"
        assert process_nested_either(inner_left) == "Inner error: inner failure"
        assert process_nested_either(inner_right) == "Final value: 42"


class TestPatternMatchingWithComplexValues:
    """Test pattern matching with complex value types."""

    def test_dict_values(self):
        """Test pattern matching with dictionary values."""
        left_dict = Left({"error": "not_found", "code": 404})
        right_dict = Right({"user": "alice", "id": 123})
        
        def process_dict_either(either: Either[dict, dict]) -> str:
            match either:
                case Left(error_dict):
                    return f"{error_dict['error']}: {error_dict['code']}"
                case Right(user_dict):
                    return f"User {user_dict['user']} (ID: {user_dict['id']})"
        
        assert process_dict_either(left_dict) == "not_found: 404"
        assert process_dict_either(right_dict) == "User alice (ID: 123)"

    def test_list_values(self):
        """Test pattern matching with list values."""
        left_list = Left(["error1", "error2"])
        right_list = Right([1, 2, 3, 4, 5])
        
        def process_list_either(either: Either[list, list]) -> str:
            match either:
                case Left(errors):
                    return f"Errors: {', '.join(errors)}"
                case Right(numbers) if len(numbers) > 3:
                    return f"Many numbers: {sum(numbers)}"
                case Right(numbers):
                    return f"Few numbers: {numbers}"
        
        assert process_list_either(left_list) == "Errors: error1, error2"
        assert process_list_either(right_list) == "Many numbers: 15"
        assert process_list_either(Right([1, 2])) == "Few numbers: [1, 2]"


class TestPatternMatchingExhaustiveness:
    """Test that pattern matching can be exhaustive without catch-all."""

    def test_exhaustive_matching_no_catch_all_needed(self):
        """Test that Left/Right cases are exhaustive for Either."""
        def is_exhaustive(either: Either[str, int]) -> bool:
            # This should be exhaustive - no case _ needed
            match either:
                case Left(_):
                    return False  # Error case
                case Right(_):
                    return True   # Success case
            # No unreachable code warning should occur
        
        assert is_exhaustive(Left("error")) is False
        assert is_exhaustive(Right(42)) is True

    def test_partial_matching_with_default(self):
        """Test pattern matching with a catch-all for incomplete patterns."""
        def classify_either(either: Either[str, int]) -> str:
            match either:
                case Right(value) if value > 0:
                    return "positive"
                case _:  # Catch-all for Left or Right(value <= 0)
                    return "other"
        
        assert classify_either(Right(5)) == "positive"
        assert classify_either(Right(0)) == "other"
        assert classify_either(Right(-1)) == "other"
        assert classify_either(Left("error")) == "other"


class TestPatternMatchingEdgeCases:
    """Test edge cases for pattern matching."""

    def test_none_values(self):
        """Test pattern matching with None values."""
        left_none = Left(None)
        right_none = Right(None)
        
        def handle_none_either(either: Either[None, None]) -> str:
            match either:
                case Left(None):
                    return "left_none"
                case Right(None):
                    return "right_none"
        
        assert handle_none_either(left_none) == "left_none"
        assert handle_none_either(right_none) == "right_none"

    def test_boolean_values(self):
        """Test pattern matching with boolean values."""
        cases = [Left(True), Left(False), Right(True), Right(False)]
        results = []
        
        for case in cases:
            match case:
                case Left(True):
                    results.append("error_true")
                case Left(False):
                    results.append("error_false")
                case Right(True):
                    results.append("success_true")
                case Right(False):
                    results.append("success_false")
        
        assert results == ["error_true", "error_false", "success_true", "success_false"]