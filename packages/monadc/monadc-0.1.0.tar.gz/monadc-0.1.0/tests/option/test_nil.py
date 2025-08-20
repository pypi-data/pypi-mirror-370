"""
Tests for Nil class functionality.
"""
import pytest
from monadc import Option, Some, Nil


class TestNilConstruction:
    """Test Nil construction and singleton behavior."""

    def test_nil_creation(self):
        """Test Nil can be created."""
        nil = Nil()
        assert not nil.is_defined()
        assert nil.is_empty()

    def test_nil_is_singleton(self):
        """All Nil instances should be the same object."""
        nil1 = Nil()
        nil2 = Nil()
        assert nil1 is nil2

    def test_nil_boolean_conversion(self):
        """Nil should be falsy."""
        assert not bool(Nil())


class TestNilGetOperations:
    """Test Nil get operations."""

    def test_get_raises_error(self):
        """Nil.get() should raise ValueError."""
        nil = Nil()
        with pytest.raises(ValueError, match="Cannot get value from empty Option"):
            nil.get()

    def test_get_or_else_with_value(self):
        """get_or_else() should return default value."""
        nil = Nil()
        assert nil.get_or_else("default") == "default"
        assert nil.get_or_else(42) == 42

    def test_get_or_else_with_callable(self):
        """get_or_else() should call default function."""
        nil = Nil()
        assert nil.get_or_else(lambda: "computed") == "computed"

        counter = [0]
        def increment():
            counter[0] += 1
            return counter[0]

        result = nil.get_or_else(increment)
        assert result == 1
        assert counter[0] == 1

    def test_get_or_else_callable_exception(self):
        """get_or_else() should propagate callable exceptions."""
        nil = Nil()
        with pytest.raises(ValueError, match="Default function failed and Option is empty"):
            nil.get_or_else(lambda: 1 / 0)

    def test_or_else_with_option(self):
        """or_else() should return alternative Option."""
        nil = Nil()
        alternative = Some("alternative")
        result = nil.or_else(alternative)
        assert result is alternative

    def test_or_else_with_callable(self):
        """or_else() should call alternative function."""
        nil = Nil()
        alternative = Some("alternative")
        result = nil.or_else(lambda: alternative)
        assert result is alternative

    def test_or_else_callable_exception_returns_self(self):
        """or_else() should return self if callable fails."""
        nil = Nil()
        result = nil.or_else(lambda: 1 / 0)
        assert result is nil


class TestNilTransformations:
    """Test Nil transformation methods always return Nil."""

    def test_map_returns_nil(self):
        """Nil.map() should always return Nil regardless of function."""
        nil = Nil()
        result = nil.map(lambda x: x.upper())
        assert isinstance(result, type(nil))
        assert result is Nil()  # Should be singleton

    def test_flat_map_returns_nil(self):
        """Nil.flat_map() should always return Nil regardless of function."""
        nil = Nil()
        result = nil.flat_map(lambda x: Some(x.upper()))
        assert isinstance(result, type(nil))
        assert result is Nil()


class TestNilFiltering:
    """Test Nil filtering methods always return self."""

    def test_filter_returns_self(self):
        """Nil.filter() should always return self regardless of predicate."""
        nil = Nil()
        result = nil.filter(lambda x: True)
        assert result is nil

        result2 = nil.filter(lambda x: False)
        assert result2 is nil

    def test_filter_not_returns_self(self):
        """Nil.filter_not() should always return self regardless of predicate."""
        nil = Nil()
        result = nil.filter_not(lambda x: True)
        assert result is nil

        result2 = nil.filter_not(lambda x: False)
        assert result2 is nil


class TestNilFolding:
    """Test Nil folding and reduction methods."""

    def test_fold_returns_empty_value(self):
        """Nil.fold() should always return the if_empty value."""
        nil = Nil()
        result = nil.fold("empty", lambda x: x.upper())
        assert result == "empty"

        result2 = nil.fold(42, lambda x: x * 2)
        assert result2 == 42

    def test_exists_returns_false(self):
        """Nil.exists() should always return False."""
        nil = Nil()
        assert not nil.exists(lambda x: True)
        assert not nil.exists(lambda x: False)
        assert not nil.exists(lambda x: x > 0)

    def test_forall_returns_true(self):
        """Nil.forall() should always return True (vacuous truth)."""
        nil = Nil()
        assert nil.forall(lambda x: True)
        assert nil.forall(lambda x: False)
        assert nil.forall(lambda x: x > 1000)


class TestNilUtilityMethods:
    """Test Nil utility methods."""

    def test_foreach_does_nothing(self):
        """Nil.foreach() should do nothing."""
        nil = Nil()
        called = [False]
        nil.foreach(lambda x: called.__setitem__(0, True))
        assert not called[0]


    def test_to_list_returns_empty_list(self):
        """Nil.to_list() should return empty list."""
        nil = Nil()
        assert nil.to_list() == []

    def test_to_optional_returns_none(self):
        """Nil.to_optional() should return None."""
        nil = Nil()
        assert nil.to_optional() is None

    def test_iteration_yields_nothing(self):
        """Nil should be iterable but yield nothing."""
        nil = Nil()
        values = list(nil)
        assert values == []


class TestNilEquality:
    """Test Nil equality behavior."""

    def test_nil_equality_with_nil(self):
        """All Nil instances should be equal."""
        nil1 = Nil()
        nil2 = Nil()
        assert nil1 == nil2
        assert nil1 is nil2  # Should be same singleton

    def test_nil_not_equal_to_some(self):
        """Nil should never equal Some."""
        nil = Nil()
        some = Some("hello")
        assert nil != some
        assert some != nil

    def test_nil_not_equal_to_other_types(self):
        """Nil should not equal non-Option types."""
        nil = Nil()
        assert nil != None  # Important: Nil() != None
        assert nil != ""
        assert nil != 0
        assert nil != False
        assert nil != []


class TestNilStringRepresentation:
    """Test Nil string representation."""

    def test_repr(self):
        """Test Nil.__repr__()."""
        nil = Nil()
        assert repr(nil) == "Nil()"

    def test_str(self):
        """Test Nil.__str__()."""
        nil = Nil()
        assert str(nil) == "Nil()"


class TestNilSingleton:
    """Test Nil singleton pattern implementation."""

    def test_multiple_constructions_same_object(self):
        """Multiple Nil() calls should return same object."""
        instances = [Nil() for _ in range(10)]
        first = instances[0]
        assert all(instance is first for instance in instances)

    def test_option_none_returns_same_nil(self):
        """Option(None) should return the same Nil singleton."""
        nil1 = Nil()
        nil2 = Option(None)
        nil3 = Option()
        assert nil1 is nil2
        assert nil2 is nil3

    def test_singleton_memory_efficiency(self):
        """Test that singleton pattern saves memory."""
        # All these should reference the same object
        refs = [Nil(), Option(None), Option(), Nil()]
        unique_ids = set(id(ref) for ref in refs)
        assert len(unique_ids) == 1  # Only one unique object