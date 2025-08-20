"""
Tests for Option class constructor and base functionality.
"""
import pytest
from monadc import Option, Some, Nil


class TestOptionConstructor:
    """Test Option() constructor behavior."""

    def test_option_with_value_creates_some(self):
        """Option(value) should create Some(value)."""
        result = Option("hello")
        assert isinstance(result, Some)
        assert result.get() == "hello"

    def test_option_with_none_creates_nil(self):
        """Option(None) should create Nil()."""
        result = Option(None)
        assert isinstance(result, Nil)
        assert result.is_empty()

    def test_option_with_no_args_creates_nil(self):
        """Option() should create Nil()."""
        result = Option()
        assert isinstance(result, Nil)
        assert result.is_empty()

    def test_option_with_various_types(self):
        """Option should work with different value types."""
        # String
        str_opt = Option("test")
        assert isinstance(str_opt, Some)
        assert str_opt.get() == "test"

        # Integer
        int_opt = Option(42)
        assert isinstance(int_opt, Some)
        assert int_opt.get() == 42

        # List
        list_opt = Option([1, 2, 3])
        assert isinstance(list_opt, Some)
        assert list_opt.get() == [1, 2, 3]

        # Empty string (not None!)
        empty_str_opt = Option("")
        assert isinstance(empty_str_opt, Some)
        assert empty_str_opt.get() == ""

        # Zero (not None!)
        zero_opt = Option(0)
        assert isinstance(zero_opt, Some)
        assert zero_opt.get() == 0

        # False (not None!)
        false_opt = Option(False)
        assert isinstance(false_opt, Some)
        assert false_opt.get() is False


class TestOptionBaseClass:
    """Test that Option base class prevents direct usage."""

    def test_option_base_class_prevents_direct_usage(self):
        """Option base class methods should raise NotImplementedError."""
        # Create an Option instance bypassing __new__
        opt = object.__new__(Option)

        with pytest.raises(NotImplementedError, match="Use Some or Nil, not Option directly"):
            opt.is_defined()

        with pytest.raises(NotImplementedError, match="Use Some or Nil, not Option directly"):
            opt.is_empty()

        with pytest.raises(NotImplementedError, match="Use Some or Nil, not Option directly"):
            opt.get()

        with pytest.raises(NotImplementedError, match="Use Some or Nil, not Option directly"):
            opt.map(lambda x: x)



class TestTypeAnnotations:
    """Test type annotation compatibility."""

    def test_isinstance_checks(self):
        """Test isinstance works correctly."""
        some_val = Option("hello")
        nil_val = Option(None)
        direct_some = Some("world")
        direct_nil = Nil()

        # All should be instances of Option
        assert isinstance(some_val, Option)
        assert isinstance(nil_val, Option)
        assert isinstance(direct_some, Option)
        assert isinstance(direct_nil, Option)

        # Specific type checks
        assert isinstance(some_val, Some)
        assert isinstance(nil_val, type(Nil()))
        assert not isinstance(some_val, type(Nil()))
        assert not isinstance(nil_val, Some)

    def test_option_as_type_annotation(self):
        """Test Option can be used in type annotations."""
        def process_option(opt: Option[str]) -> Option[int]:
            return opt.map(len)

        # Should work with Option constructor
        result1 = process_option(Option("hello"))
        assert isinstance(result1, Some)
        assert result1.get() == 5

        # Should work with direct Some
        result2 = process_option(Some("world"))
        assert isinstance(result2, Some)
        assert result2.get() == 5

        # Should work with Nil
        result3 = process_option(Nil())
        assert isinstance(result3, Nil)

        # Should work with Option(None)
        result4 = process_option(Option(None))
        assert isinstance(result4, Nil)


class TestOptionEquality:
    """Test Option equality behavior."""

    def test_option_constructed_values_equal_direct_construction(self):
        """Option(x) should equal Some(x) and Nil()."""
        # Some equality
        assert Option("hello") == Some("hello")
        assert Some("hello") == Option("hello")

        # Nil equality
        assert Option(None) == Nil()
        assert Nil() == Option(None)
        assert Option() == Nil()

        # Different values not equal
        assert Option("hello") != Option("world")
        assert Option("hello") != Option(None)
        assert Option(42) != Nil()