"""
Tests for new Option methods: flatten, unzip, and Rust/Scala additions.
"""
import pytest
from monadc import Option, Some, Nil


class TestFlatten:
    """Test flatten method."""
    
    def test_some_with_some_inner_flattens(self):
        """flatten should unwrap Some(Some(value)) to Some(value)."""
        inner_some = Some("nested")
        outer_some = Some(inner_some)
        result = outer_some.flatten()
        assert isinstance(result, Some)
        assert result.unwrap() == "nested"
    
    def test_some_with_nil_inner_flattens(self):
        """flatten should unwrap Some(Nil()) to Nil()."""
        inner_nil = Nil()
        outer_some = Some(inner_nil)
        result = outer_some.flatten()
        assert isinstance(result, Nil)
    
    def test_some_with_non_option_unchanged(self):
        """flatten should leave Some(non-option) unchanged."""
        some = Some("plain value")
        result = some.flatten()
        assert isinstance(result, Some)
        assert result.unwrap() == "plain value"
    
    def test_nil_flatten_unchanged(self):
        """flatten should leave Nil unchanged."""
        nil = Nil()
        result = nil.flatten()
        assert isinstance(result, Nil)


class TestUnzip:
    """Test unzip method."""
    
    def test_some_with_tuple_unzips(self):
        """unzip should convert Some((a, b)) to (Some(a), Some(b))."""
        some_tuple = Some(("hello", 42))
        first, second = some_tuple.unzip()
        assert isinstance(first, Some)
        assert isinstance(second, Some)
        assert first.unwrap() == "hello"
        assert second.unwrap() == 42
    
    def test_some_with_non_tuple_returns_nils(self):
        """unzip should return (Nil, Nil) for Some(non-tuple)."""
        some_non_tuple = Some("not a tuple")
        first, second = some_non_tuple.unzip()
        assert isinstance(first, Nil)
        assert isinstance(second, Nil)
    
    def test_nil_unzip_returns_nils(self):
        """unzip should return (Nil, Nil) for Nil."""
        nil = Nil()
        first, second = nil.unzip()
        assert isinstance(first, Nil)
        assert isinstance(second, Nil)


class TestRustMethods:
    """Test new Rust-style methods."""
    
    def test_map_or_some(self):
        """map_or should apply function to Some value."""
        some = Some(10)
        result = some.map_or(0, lambda x: x * 2)
        assert result == 20
    
    def test_map_or_nil(self):
        """map_or should return default for Nil."""
        nil = Nil()
        result = nil.map_or(0, lambda x: x * 2)
        assert result == 0
    
    def test_map_or_else_some(self):
        """map_or_else should apply function to Some value."""
        some = Some(10)
        result = some.map_or_else(lambda: 0, lambda x: x * 2)
        assert result == 20
    
    def test_map_or_else_nil(self):
        """map_or_else should call default function for Nil."""
        nil = Nil()
        result = nil.map_or_else(lambda: 42, lambda x: x * 2)
        assert result == 42
    
    def test_get_or_insert_some(self):
        """get_or_insert should return existing value for Some."""
        some = Some("existing")
        result = some.get_or_insert("new")
        assert result == "existing"
    
    def test_get_or_insert_nil(self):
        """get_or_insert should return inserted value for Nil."""
        nil = Nil()
        result = nil.get_or_insert("inserted")
        assert result == "inserted"
    
    def test_get_or_insert_with_some(self):
        """get_or_insert_with should return existing value for Some."""
        some = Some("existing")
        result = some.get_or_insert_with(lambda: "new")
        assert result == "existing"
    
    def test_get_or_insert_with_nil(self):
        """get_or_insert_with should call function for Nil."""
        nil = Nil()
        result = nil.get_or_insert_with(lambda: "computed")
        assert result == "computed"
    
    def test_ok_or_some(self):
        """ok_or should convert Some to Ok."""
        some = Some("value")
        result = some.ok_or("error")
        # Should return Ok("value")
        assert hasattr(result, 'is_ok')
        assert result.is_ok()
        assert result.unwrap() == "value"
    
    def test_ok_or_nil(self):
        """ok_or should convert Nil to Err."""
        nil = Nil()
        result = nil.ok_or("error")
        # Should return Err("error")
        assert hasattr(result, 'is_err')
        assert result.is_err()
        assert result.unwrap_err() == "error"
    
    def test_transpose_some_with_ok(self):
        """transpose should handle Some(Ok(value))."""
        from monadc.result import Ok
        ok_value = Ok("success")
        some = Some(ok_value)
        result = some.transpose()
        # Should return Ok(Some("success"))
        assert hasattr(result, 'is_ok')
        assert result.is_ok()
        inner = result.unwrap()
        assert isinstance(inner, Some)
        assert inner.unwrap() == "success"
    
    def test_transpose_nil(self):
        """transpose should convert Nil to Ok(Nil)."""
        nil = Nil()
        result = nil.transpose()
        # Should return Ok(Nil)
        assert hasattr(result, 'is_ok')
        assert result.is_ok()
        inner = result.unwrap()
        assert isinstance(inner, Nil)


class TestScalaMethods:
    """Test new Scala-style methods."""
    
    def test_foreach_some(self):
        """foreach should execute function on Some value."""
        some = Some(42)
        result = []
        some.foreach(lambda x: result.append(x * 2))
        assert result == [84]
    
    def test_foreach_nil(self):
        """foreach should do nothing on Nil."""
        nil = Nil()
        result = []
        nil.foreach(lambda x: result.append(x))
        assert result == []
    
    def test_forall_some_true(self):
        """forall should return True if Some value satisfies predicate."""
        some = Some(10)
        assert some.forall(lambda x: x > 5)
    
    def test_forall_some_false(self):
        """forall should return False if Some value doesn't satisfy predicate."""
        some = Some(3)
        assert not some.forall(lambda x: x > 5)
    
    def test_forall_nil(self):
        """forall should return True for Nil (vacuous truth)."""
        nil = Nil()
        assert nil.forall(lambda x: x > 1000)  # Any predicate
    
    def test_contains_some_match(self):
        """contains should return True if Some contains the value."""
        some = Some("hello")
        assert some.contains("hello")
    
    def test_contains_some_no_match(self):
        """contains should return False if Some doesn't contain the value."""
        some = Some("hello")
        assert not some.contains("world")
    
    def test_contains_nil(self):
        """contains should return False for Nil."""
        nil = Nil()
        assert not nil.contains("anything")
    
    def test_non_empty_some(self):
        """non_empty should return True for Some."""
        some = Some("value")
        assert some.non_empty()
    
    def test_non_empty_nil(self):
        """non_empty should return False for Nil."""
        nil = Nil()
        assert not nil.non_empty()
    
    def test_or_null_some(self):
        """or_null should return value for Some."""
        some = Some("value")
        assert some.or_null() == "value"
    
    def test_or_null_nil(self):
        """or_null should return None for Nil."""
        nil = Nil()
        assert nil.or_null() is None
    
    def test_or_none_some(self):
        """or_none should return value for Some."""
        some = Some("value")
        assert some.or_none() == "value"
    
    def test_or_none_nil(self):
        """or_none should return None for Nil."""
        nil = Nil()
        assert nil.or_none() is None