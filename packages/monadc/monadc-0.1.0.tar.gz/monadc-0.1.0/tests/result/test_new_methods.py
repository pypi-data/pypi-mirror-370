"""
Tests for new Result methods: map_or, map_or_else, flatten, transpose.
"""
import pytest
from monadc import Result, Ok, Err, Option, Some, Nil


class TestMapOr:
    """Test map_or method."""
    
    def test_ok_map_or_applies_function(self):
        """map_or should apply function to Ok value."""
        ok = Ok(10)
        result = ok.map_or(0, lambda x: x * 2)
        assert result == 20
    
    def test_err_map_or_returns_default(self):
        """map_or should return default for Err."""
        err = Err("error")
        result = err.map_or(0, lambda x: x * 2)
        assert result == 0
    
    def test_map_or_with_different_types(self):
        """map_or should handle type transformations."""
        ok = Ok("hello")
        result = ok.map_or(0, len)
        assert result == 5
        
        err = Err("error")
        result = err.map_or(0, len)
        assert result == 0


class TestMapOrElse:
    """Test map_or_else method."""
    
    def test_ok_map_or_else_applies_function(self):
        """map_or_else should apply function to Ok value."""
        ok = Ok(10)
        result = ok.map_or_else(lambda e: 0, lambda x: x * 2)
        assert result == 20
    
    def test_err_map_or_else_calls_default_func(self):
        """map_or_else should call default function with Err value."""
        err = Err("error")
        result = err.map_or_else(lambda e: f"handled: {e}", lambda x: x * 2)
        assert result == "handled: error"
    
    def test_map_or_else_with_error_transformation(self):
        """map_or_else should allow error value transformation."""
        err = Err(404)
        result = err.map_or_else(lambda code: f"HTTP {code}", lambda x: x)
        assert result == "HTTP 404"


class TestFlatten:
    """Test flatten method."""
    
    def test_ok_with_ok_inner_flattens(self):
        """flatten should unwrap Ok(Ok(value)) to Ok(value)."""
        inner_ok = Ok("success")
        outer_ok = Ok(inner_ok)
        result = outer_ok.flatten()
        assert isinstance(result, Ok)
        assert result.unwrap() == "success"
    
    def test_ok_with_err_inner_flattens(self):
        """flatten should unwrap Ok(Err(error)) to Err(error)."""
        inner_err = Err("error")
        outer_ok = Ok(inner_err)
        result = outer_ok.flatten()
        assert isinstance(result, Err)
        assert result.unwrap_err() == "error"
    
    def test_ok_with_non_result_unchanged(self):
        """flatten should leave Ok(non-result) unchanged."""
        ok = Ok("plain value")
        result = ok.flatten()
        assert isinstance(result, Ok)
        assert result.unwrap() == "plain value"
    
    def test_err_flatten_unchanged(self):
        """flatten should leave Err unchanged."""
        err = Err("error")
        result = err.flatten()
        assert isinstance(result, Err)
        assert result.unwrap_err() == "error"


class TestTranspose:
    """Test transpose method."""
    
    def test_ok_with_some_transposes(self):
        """transpose should convert Ok(Some(value)) to Some(Ok(value))."""
        some_value = Some("success")
        ok = Ok(some_value)
        result = ok.transpose()
        assert isinstance(result, Some)
        inner = result.unwrap()
        assert isinstance(inner, Ok)
        assert inner.unwrap() == "success"
    
    def test_ok_with_nil_transposes(self):
        """transpose should convert Ok(Nil) to Nil."""
        nil_value = Nil()
        ok = Ok(nil_value)
        result = ok.transpose()
        assert isinstance(result, Nil)
        assert result.is_empty()
    
    def test_ok_with_non_option_wraps_in_some(self):
        """transpose should wrap Ok(non-option) in Some."""
        ok = Ok("plain value")
        result = ok.transpose()
        assert isinstance(result, Some)
        inner = result.unwrap()
        assert isinstance(inner, Ok)
        assert inner.unwrap() == "plain value"
    
    def test_err_transpose_wraps_in_some(self):
        """transpose should wrap Err in Some."""
        err = Err("error")
        result = err.transpose()
        assert isinstance(result, Some)
        inner = result.unwrap()
        assert isinstance(inner, Err)
        assert inner.unwrap_err() == "error"


class TestPatternMatching:
    """Test pattern matching support."""
    
    def test_ok_pattern_matching(self):
        """Ok should support pattern matching."""
        ok = Ok("success")
        
        match ok:
            case Ok(value):
                result = f"Ok: {value}"
            case Err(error):
                result = f"Err: {error}"
        
        assert result == "Ok: success"
    
    def test_err_pattern_matching(self):
        """Err should support pattern matching."""
        err = Err("failure")
        
        match err:
            case Ok(value):
                result = f"Ok: {value}"
            case Err(error):
                result = f"Err: {error}"
        
        assert result == "Err: failure"
    
    def test_pattern_matching_with_guards(self):
        """Pattern matching should work with guards."""
        def process_result(result: Result[int, str]) -> str:
            match result:
                case Ok(value) if value > 100:
                    return f"Large: {value}"
                case Ok(value):
                    return f"Small: {value}"
                case Err(error):
                    return f"Error: {error}"
        
        assert process_result(Ok(150)) == "Large: 150"
        assert process_result(Ok(50)) == "Small: 50"
        assert process_result(Err("failed")) == "Error: failed"