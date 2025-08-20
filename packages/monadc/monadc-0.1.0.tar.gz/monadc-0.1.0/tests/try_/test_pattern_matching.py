"""
Tests for Try pattern matching support (Python 3.10+).
"""
import pytest
from monadc import Try, Success, Failure


class TestTryPatternMatching:
    """Test pattern matching support for Try types."""

    def test_success_pattern_matching(self):
        """Success should support pattern matching to extract value."""
        success_value = Success("hello")
        
        match success_value:
            case Success(value):
                result = f"Success: {value}"
            case Failure(exception):
                result = f"Failure: {exception}"
        
        assert result == "Success: hello"
    
    def test_failure_pattern_matching(self):
        """Failure should support pattern matching to extract exception."""
        failure_value = Failure(ValueError("test error"))
        
        match failure_value:
            case Success(value):
                result = f"Success: {value}"
            case Failure(exception):
                result = f"Failure: {type(exception).__name__}: {exception}"
        
        assert result == "Failure: ValueError: test error"
    
    def test_pattern_matching_with_guards(self):
        """Pattern matching should work with guards."""
        def process_try(try_val: Try[int]) -> str:
            match try_val:
                case Success(value) if value > 100:
                    return f"Large success: {value}"
                case Success(value) if value > 0:
                    return f"Small success: {value}"
                case Success(value):
                    return f"Non-positive success: {value}"
                case Failure(exception) if isinstance(exception, ValueError):
                    return f"ValueError: {exception}"
                case Failure(exception):
                    return f"Other error: {type(exception).__name__}"
        
        assert process_try(Success(150)) == "Large success: 150"
        assert process_try(Success(50)) == "Small success: 50"
        assert process_try(Success(-10)) == "Non-positive success: -10"
        assert process_try(Failure(ValueError("bad value"))) == "ValueError: bad value"
        assert process_try(Failure(RuntimeError("runtime issue"))) == "Other error: RuntimeError"
    
    def test_pattern_matching_with_exception_types(self):
        """Pattern matching should work with specific exception types."""
        def handle_error(try_val: Try[str]) -> str:
            match try_val:
                case Success(value):
                    return f"Got: {value}"
                case Failure(ValueError() as e):
                    return f"Value error: {e}"
                case Failure(TypeError() as e):
                    return f"Type error: {e}"
                case Failure(exception):
                    return f"Other error: {exception}"
        
        assert handle_error(Success("data")) == "Got: data"
        assert handle_error(Failure(ValueError("invalid"))) == "Value error: invalid"
        assert handle_error(Failure(TypeError("wrong type"))) == "Type error: wrong type"
        assert handle_error(Failure(RuntimeError("runtime"))) == "Other error: runtime"
    
    def test_pattern_matching_with_complex_values(self):
        """Pattern matching should work with complex data types."""
        success_dict = Success({"name": "Alice", "score": 95})
        
        match success_dict:
            case Success(data) if isinstance(data, dict) and data.get("score", 0) >= 90:
                result = f"High scorer: {data['name']}"
            case Success(data) if isinstance(data, dict):
                result = f"Low scorer: {data['name']}"
            case Success(value):
                result = f"Non-dict: {value}"
            case Failure(exception):
                result = f"Error: {exception}"
        
        assert result == "High scorer: Alice"
    
    def test_exhaustive_pattern_matching(self):
        """Pattern matching should be exhaustive without catch-all case."""
        tries = [Success(42), Failure(ValueError("error"))]
        results = []
        
        for try_val in tries:
            match try_val:
                case Success(value):
                    results.append(f"Success: {value}")
                case Failure(exception):
                    results.append(f"Failure: {exception}")
            # No case _ needed - Success/Failure cases are exhaustive for Try
        
        assert results == ["Success: 42", "Failure: error"]
    
    def test_pattern_matching_with_nested_tries(self):
        """Pattern matching should work with nested Try structures."""
        nested_success = Success(Success("nested"))
        
        match nested_success:
            case Success(Success(inner_value)):
                result = f"Nested success: {inner_value}"
            case Success(Failure(inner_exception)):
                result = f"Success wrapping failure: {inner_exception}"
            case Success(value):
                result = f"Success: {value}"
            case Failure(exception):
                result = f"Failure: {exception}"
        
        assert result == "Nested success: nested"
    
    def test_pattern_matching_with_factory_constructed_tries(self):
        """Pattern matching should work with factory-constructed Tries."""
        def safe_divide(a: int, b: int) -> Try[float]:
            return Try(lambda: a / b)
        
        def safe_int_parse(s: str) -> Try[int]:
            return Try(lambda: int(s))
        
        success_try = safe_divide(10, 2)
        failure_try = safe_divide(10, 0)
        parse_success = safe_int_parse("42")
        parse_failure = safe_int_parse("abc")
        
        results = []
        for try_val in [success_try, failure_try, parse_success, parse_failure]:
            match try_val:
                case Success(value) if isinstance(value, float):
                    results.append(f"Float: {value}")
                case Success(value) if isinstance(value, int):
                    results.append(f"Int: {value}")
                case Success(value):
                    results.append(f"Other: {value}")
                case Failure(ZeroDivisionError()):
                    results.append("Division by zero")
                case Failure(ValueError()):
                    results.append("Invalid value")
                case Failure(exception):
                    results.append(f"Other error: {exception}")
        
        assert results == ["Float: 5.0", "Division by zero", "Int: 42", "Invalid value"]
    
    def test_pattern_matching_with_chained_operations(self):
        """Pattern matching should work with results of chained operations."""
        def process_string(s: str) -> Try[int]:
            return (Try(lambda: s.strip())
                   .map(lambda stripped: int(stripped))
                   .filter(lambda n: n > 0))
        
        result1 = process_string("  42  ")
        result2 = process_string("abc")
        result3 = process_string("-5")
        
        results = []
        for result in [result1, result2, result3]:
            match result:
                case Success(num) if num > 10:
                    results.append(f"Large: {num}")
                case Success(num):
                    results.append(f"Small: {num}")
                case Failure(ValueError()):
                    results.append("Parse error")
                case Failure(exception):
                    results.append(f"Other error: {exception}")
        
        assert results == ["Large: 42", "Parse error", "Parse error"]
    
    def test_pattern_matching_variable_binding(self):
        """Pattern matching should properly bind variables."""
        success_list = Success([1, 2, 3, 4, 5])
        
        match success_list:
            case Success([first, *rest]) if len(rest) > 2:
                result = f"First: {first}, Rest count: {len(rest)}"
            case Success([single]):
                result = f"Single: {single}"
            case Success(lst) if isinstance(lst, list):
                result = f"List: {lst}"
            case Success(value):
                result = f"Non-list: {value}"
            case Failure(exception):
                result = f"Error: {exception}"
        
        assert result == "First: 1, Rest count: 4"
    
    def test_pattern_matching_with_exception_messages(self):
        """Pattern matching should work with exception message patterns."""
        def classify_error(try_val: Try[str]) -> str:
            match try_val:
                case Success(value):
                    return f"Success: {value}"
                case Failure(exception) if "network" in str(exception).lower():
                    return "Network error"
                case Failure(exception) if "timeout" in str(exception).lower():
                    return "Timeout error"
                case Failure(exception):
                    return f"Other error: {type(exception).__name__}"
        
        assert classify_error(Success("data")) == "Success: data"
        assert classify_error(Failure(RuntimeError("Network connection failed"))) == "Network error"
        assert classify_error(Failure(TimeoutError("Request timeout occurred"))) == "Timeout error"
        assert classify_error(Failure(ValueError("Invalid input"))) == "Other error: ValueError"