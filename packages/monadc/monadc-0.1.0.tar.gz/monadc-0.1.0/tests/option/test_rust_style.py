"""
Tests for Rust-style methods in Option monad.
"""
import pytest
from monadc import Option, Some, Nil


class TestRustStyleAliases:
    """Test Rust-style aliases for existing methods."""

    def test_unwrap_alias_for_get(self):
        """unwrap() should work like get()."""
        some = Some("value")
        assert some.unwrap() == "value"

        nil = Nil()
        with pytest.raises(ValueError):
            nil.unwrap()

    def test_unwrap_or_alias_for_get_or_else(self):
        """unwrap_or() should work like get_or_else() with value."""
        some = Some("value")
        assert some.unwrap_or("default") == "value"

        nil = Nil()
        assert nil.unwrap_or("default") == "default"

    def test_unwrap_or_else_with_function(self):
        """unwrap_or_else() should work like get_or_else() with function."""
        some = Some("value")
        assert some.unwrap_or_else(lambda: "default") == "value"

        nil = Nil()
        assert nil.unwrap_or_else(lambda: "default") == "default"

    def test_is_some_alias_for_is_defined(self):
        """is_some() should work like is_defined()."""
        some = Some("value")
        assert some.is_some() == True
        assert some.is_defined() == True  # Original method still works

        nil = Nil()
        assert nil.is_some() == False
        assert nil.is_defined() == False

    def test_is_none_alias_for_is_empty(self):
        """is_none() should work like is_empty()."""
        some = Some("value")
        assert some.is_none() == False
        assert some.is_empty() == False  # Original method still works

        nil = Nil()
        assert nil.is_none() == True
        assert nil.is_empty() == True

    def test_and_then_alias_for_flat_map(self):
        """and_then() should work like flat_map()."""
        some = Some("hello")
        result = some.and_then(lambda x: Some(x.upper()))
        assert result == Some("HELLO")

        nil = Nil()
        result = nil.and_then(lambda x: Some(x.upper()))
        assert result.is_none()


class TestRustStyleExpect:
    """Test expect() method."""

    def test_expect_returns_value_for_some(self):
        """expect() should return value for Some."""
        some = Some("value")
        assert some.expect("custom error") == "value"

    def test_expect_raises_custom_error_for_nil(self):
        """expect() should raise ValueError with custom message for Nil."""
        nil = Nil()
        with pytest.raises(ValueError, match="custom error message"):
            nil.expect("custom error message")


class TestRustStyleOrElseWith:
    """Test or_else_with() method."""

    def test_or_else_with_returns_self_for_some(self):
        """or_else_with() should return self for Some."""
        some = Some("value")
        result = some.or_else_with(lambda: Some("alternative"))
        assert result is some

    def test_or_else_with_calls_function_for_nil(self):
        """or_else_with() should call function for Nil."""
        nil = Nil()
        result = nil.or_else_with(lambda: Some("alternative"))
        assert result == Some("alternative")

    def test_or_else_with_can_return_nil(self):
        """or_else_with() can return Nil from function."""
        nil = Nil()
        result = nil.or_else_with(lambda: Nil())
        assert result.is_none()


class TestRustStyleLogicalOperations:
    """Test and_(), or_(), xor() methods."""

    def test_and_returns_other_for_some(self):
        """and_() should return other when self is Some."""
        some1 = Some("first")
        some2 = Some("second")
        nil = Nil()

        assert some1.and_(some2) == some2
        assert some1.and_(nil).is_none()

    def test_and_returns_nil_for_nil(self):
        """and_() should return Nil when self is Nil."""
        nil = Nil()
        some = Some("value")
        other_nil = Nil()

        result1 = nil.and_(some)
        assert result1.is_none()

        result2 = nil.and_(other_nil)
        assert result2.is_none()

    def test_or_returns_self_for_some(self):
        """or_() should return self when self is Some."""
        some = Some("value")
        other = Some("other")
        nil = Nil()

        assert some.or_(other) == some
        assert some.or_(nil) == some

    def test_or_returns_other_for_nil(self):
        """or_() should return other when self is Nil."""
        nil = Nil()
        some = Some("value")
        other_nil = Nil()

        assert nil.or_(some) == some
        assert nil.or_(other_nil).is_none()

    def test_xor_exclusive_or_behavior(self):
        """xor() should return Some only when exactly one is Some."""
        some1 = Some("first")
        some2 = Some("second")
        nil = Nil()

        # Some XOR Nil = Some
        assert some1.xor(nil) == some1
        assert nil.xor(some1) == some1

        # Some XOR Some = Nil
        assert some1.xor(some2).is_none()

        # Nil XOR Nil = Nil
        assert nil.xor(Nil()).is_none()




class TestRustStyleZip:
    """Test zip() and zip_with() methods."""

    def test_zip_some_with_some(self):
        """zip() should create tuple when both are Some."""
        some1 = Some("hello")
        some2 = Some("world")
        result = some1.zip(some2)
        assert result == Some(("hello", "world"))

    def test_zip_some_with_nil(self):
        """zip() should return Nil when other is Nil."""
        some = Some("hello")
        nil = Nil()
        result = some.zip(nil)
        assert result.is_none()

    def test_zip_nil_with_some(self):
        """zip() should return Nil when self is Nil."""
        nil = Nil()
        some = Some("world")
        result = nil.zip(some)
        assert result.is_none()

    def test_zip_nil_with_nil(self):
        """zip() should return Nil when both are Nil."""
        nil1 = Nil()
        nil2 = Nil()
        result = nil1.zip(nil2)
        assert result.is_none()

    def test_zip_with_some_with_some(self):
        """zip_with() should apply function when both are Some."""
        some1 = Some(5)
        some2 = Some(3)
        result = some1.zip_with(some2, lambda a, b: a + b)
        assert result == Some(8)

    def test_zip_with_some_with_nil(self):
        """zip_with() should return Nil when other is Nil."""
        some = Some(5)
        nil = Nil()
        result = some.zip_with(nil, lambda a, b: a + b)
        assert result.is_none()

    def test_zip_with_nil_with_some(self):
        """zip_with() should return Nil when self is Nil."""
        nil = Nil()
        some = Some(3)
        result = nil.zip_with(some, lambda a, b: a + b)
        assert result.is_none()


class TestRustStyleInspect:
    """Test inspect() method."""

    def test_inspect_calls_function_for_some(self):
        """inspect() should call function with value and return self for Some."""
        some = Some("value")
        called_with = []

        result = some.inspect(lambda x: called_with.append(x))
        assert result is some
        assert called_with == ["value"]

    def test_inspect_does_nothing_for_nil(self):
        """inspect() should do nothing and return self for Nil."""
        nil = Nil()
        called = []

        result = nil.inspect(lambda x: called.append(x))
        assert result is nil
        assert called == []


class TestRustStyleCompatibility:
    """Test that Rust-style methods work alongside Scala-style methods."""

    def test_both_styles_work_together(self):
        """Both Rust and Scala style methods should work on same object."""
        some = Some("hello")

        # Scala style
        scala_result = some.map(str.upper).filter(lambda x: len(x) > 3)

        # Rust style
        rust_result = some.and_then(lambda x: Some(x.upper())).inspect(lambda x: None)

        assert scala_result == Some("HELLO")
        assert rust_result == Some("HELLO")

    def test_method_chaining_mixed_styles(self):
        """Should be able to chain mixed Rust and Scala style methods."""
        result = (Option("hello")
                  .map(str.upper)           # Scala style
                  .and_then(lambda x: Some(x + "!"))  # Rust style
                  .filter(lambda x: "!" in x)         # Scala style
                  .inspect(lambda x: None))           # Rust style

        assert result == Some("HELLO!")

    def test_error_handling_consistency(self):
        """Error handling should be consistent between styles."""
        nil = Nil()

        # Both should raise errors
        with pytest.raises(ValueError):
            nil.get()  # Scala style

        with pytest.raises(ValueError):
            nil.unwrap()  # Rust style

        # Both should provide defaults
        assert nil.get_or_else("default") == "default"  # Scala style
        assert nil.unwrap_or("default") == "default"    # Rust style