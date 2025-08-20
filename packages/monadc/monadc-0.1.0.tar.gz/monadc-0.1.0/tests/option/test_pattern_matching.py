"""
Tests for Option pattern matching support (Python 3.10+).
"""
import pytest
from monadc import Option, Some, Nil


class TestOptionPatternMatching:
    """Test pattern matching support for Option types."""

    def test_some_pattern_matching(self):
        """Some should support pattern matching to extract value."""
        some_value = Some("hello")
        
        match some_value:
            case Some(value):
                result = f"Some: {value}"
            case Nil():
                result = "Nil"
        
        assert result == "Some: hello"
    
    def test_nil_pattern_matching(self):
        """Nil should support pattern matching."""
        nil_value = Nil()
        
        match nil_value:
            case Some(value):
                result = f"Some: {value}"
            case Nil():
                result = "Nil"
        
        assert result == "Nil"
    
    def test_pattern_matching_with_guards(self):
        """Pattern matching should work with guards."""
        def process_option(opt: Option[int]) -> str:
            match opt:
                case Some(value) if value > 100:
                    return f"Large: {value}"
                case Some(value) if value > 0:
                    return f"Positive: {value}"
                case Some(value):
                    return f"Non-positive: {value}"
                case Nil():
                    return "Empty"
        
        assert process_option(Some(150)) == "Large: 150"
        assert process_option(Some(50)) == "Positive: 50"
        assert process_option(Some(-10)) == "Non-positive: -10"
        assert process_option(Nil()) == "Empty"
    
    def test_pattern_matching_with_string_values(self):
        """Pattern matching should work with different value types."""
        def classify_string(opt: Option[str]) -> str:
            match opt:
                case Some(value) if len(value) > 10:
                    return "Long string"
                case Some(value) if value.startswith("test"):
                    return "Test string"
                case Some(value):
                    return f"String: {value}"
                case Nil():
                    return "No string"
        
        assert classify_string(Some("this is a very long string")) == "Long string"
        assert classify_string(Some("test_value")) == "Test string"
        assert classify_string(Some("hello")) == "String: hello"
        assert classify_string(Nil()) == "No string"
    
    def test_nested_pattern_matching(self):
        """Pattern matching should work with nested structures."""
        nested_option = Some(Some("nested"))
        
        match nested_option:
            case Some(Some(inner_value)):
                result = f"Nested: {inner_value}"
            case Some(Nil()):
                result = "Some(Nil)"
            case Some(value):
                result = f"Some: {value}"
            case Nil():
                result = "Nil"
        
        assert result == "Nested: nested"
    
    def test_pattern_matching_with_complex_types(self):
        """Pattern matching should work with complex data types."""
        data_option = Some({"name": "Alice", "age": 30})
        
        match data_option:
            case Some(data) if isinstance(data, dict) and data.get("age", 0) >= 18:
                result = f"Adult: {data['name']}"
            case Some(data) if isinstance(data, dict):
                result = f"Minor: {data['name']}"
            case Some(value):
                result = f"Non-dict: {value}"
            case Nil():
                result = "No data"
        
        assert result == "Adult: Alice"
    
    def test_exhaustive_pattern_matching(self):
        """Pattern matching should be exhaustive without catch-all case."""
        options = [Some(42), Nil()]
        results = []
        
        for opt in options:
            match opt:
                case Some(value):
                    results.append(f"Value: {value}")
                case Nil():
                    results.append("Empty")
            # No case _ needed - Some/Nil cases are exhaustive for Option
        
        assert results == ["Value: 42", "Empty"]
    
    def test_pattern_matching_variable_binding(self):
        """Pattern matching should properly bind variables."""
        some_list = Some([1, 2, 3, 4, 5])
        
        match some_list:
            case Some([first, *rest]) if len(rest) > 2:
                result = f"First: {first}, Rest count: {len(rest)}"
            case Some([single]):
                result = f"Single: {single}"
            case Some(lst) if isinstance(lst, list):
                result = f"List: {lst}"
            case Some(value):
                result = f"Non-list: {value}"
            case Nil():
                result = "Empty"
        
        assert result == "First: 1, Rest count: 4"
    
    def test_pattern_matching_with_factory_constructed_options(self):
        """Pattern matching should work with factory-constructed Options."""
        factory_some = Option("factory_value")
        factory_nil = Option(None)
        
        match factory_some:
            case Some(value):
                result1 = f"Some: {value}"
            case Nil():
                result1 = "Nil"
        
        match factory_nil:
            case Some(value):
                result2 = f"Some: {value}"
            case Nil():
                result2 = "Nil"
        
        assert result1 == "Some: factory_value"
        assert result2 == "Nil"
    
    def test_pattern_matching_with_chained_operations(self):
        """Pattern matching should work with results of chained operations."""
        def process_chain(value: str) -> Option[int]:
            return (Option(value)
                   .filter(lambda s: s.isdigit())
                   .map(int)
                   .filter(lambda n: n > 0))
        
        result1 = process_chain("42")
        result2 = process_chain("abc")
        result3 = process_chain("-5")
        
        results = []
        for result in [result1, result2, result3]:
            match result:
                case Some(num) if num > 10:
                    results.append(f"Large: {num}")
                case Some(num):
                    results.append(f"Small: {num}")
                case Nil():
                    results.append("Invalid")
        
        assert results == ["Large: 42", "Invalid", "Invalid"]