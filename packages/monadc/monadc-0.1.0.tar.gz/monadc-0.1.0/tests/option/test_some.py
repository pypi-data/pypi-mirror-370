"""
Tests for Some class functionality.
"""
import pytest
from monadc import Option, Some, Nil


class TestSomeConstruction:
    """Test Some construction and basic properties."""

    def test_some_creation(self):
        """Test Some can be created with any non-None value."""
        some = Some("hello")
        assert some.get() == "hello"
        assert some.is_defined()
        assert not some.is_empty()

    def test_some_with_none_raises_error(self):
        """Some(None) should raise ValueError."""
        with pytest.raises(ValueError, match="Cannot create Some with None value"):
            Some(None)

    def test_some_boolean_conversion(self):
        """Some should be truthy."""
        assert bool(Some("hello"))
        assert bool(Some(0))  # Even falsy values make Some truthy
        assert bool(Some(""))
        assert bool(Some(False))


class TestSomeTransformations:
    """Test Some transformation methods."""

    def test_map(self):
        """Test Some.map() transformation."""
        some = Some("hello")
        result = some.map(str.upper)
        assert isinstance(result, Some)
        assert result.get() == "HELLO"

    def test_map_with_none_result_creates_nil(self):
        """map() returning None should create Nil."""
        some = Some("hello")
        result = some.map(lambda x: None)
        assert isinstance(result, Nil)

    def test_map_exception_propagates(self):
        """map() should let exceptions bubble up."""
        some = Some(10)
        with pytest.raises(ZeroDivisionError):
            some.map(lambda x: x / 0)

    def test_flat_map(self):
        """Test Some.flat_map() transformation."""
        some = Some("hello")
        result = some.flat_map(lambda x: Some(x.upper()))
        assert isinstance(result, Some)
        assert result.get() == "HELLO"

    def test_flat_map_to_nil(self):
        """flat_map() can return Nil."""
        some = Some("hello")
        result = some.flat_map(lambda x: Nil())
        assert isinstance(result, Nil)

    def test_flat_map_exception_propagates(self):
        """flat_map() should let exceptions bubble up."""
        some = Some(10)
        with pytest.raises(ZeroDivisionError):
            some.flat_map(lambda x: Some(x / 0))


class TestSomeFiltering:
    """Test Some filtering methods."""

    def test_filter_true_returns_self(self):
        """filter() with true predicate returns self."""
        some = Some(10)
        result = some.filter(lambda x: x > 5)
        assert result is some

    def test_filter_false_returns_nil(self):
        """filter() with false predicate returns Nil."""
        some = Some(10)
        result = some.filter(lambda x: x > 15)
        assert isinstance(result, Nil)

    def test_filter_exception_propagates(self):
        """filter() should let exceptions bubble up."""
        some = Some(10)
        with pytest.raises(ZeroDivisionError):
            some.filter(lambda x: x / 0 > 5)

    def test_filter_not(self):
        """Test filter_not() inverts the predicate."""
        some = Some(10)
        result1 = some.filter_not(lambda x: x > 15)  # True (10 is not > 15)
        assert result1 is some

        result2 = some.filter_not(lambda x: x > 5)   # False (10 is > 5)
        assert isinstance(result2, Nil)


class TestSomeFolding:
    """Test Some folding and reduction methods."""

    def test_fold(self):
        """Test Some.fold() applies function to value."""
        some = Some(10)
        result = some.fold(0, lambda x: x * 2)
        assert result == 20

    def test_fold_exception_propagates(self):
        """fold() should let exceptions bubble up."""
        some = Some(10)
        with pytest.raises(ZeroDivisionError):
            some.fold(99, lambda x: x / 0)

    def test_exists_true(self):
        """exists() should return True when predicate matches."""
        some = Some(10)
        assert some.exists(lambda x: x > 5)
        assert some.exists(lambda x: x == 10)

    def test_exists_false(self):
        """exists() should return False when predicate doesn't match."""
        some = Some(10)
        assert not some.exists(lambda x: x > 15)
        assert not some.exists(lambda x: x < 0)

    def test_exists_exception_propagates(self):
        """exists() should let exceptions bubble up."""
        some = Some(10)
        with pytest.raises(ZeroDivisionError):
            some.exists(lambda x: x / 0 > 5)

    def test_forall_true(self):
        """forall() should return True when predicate matches."""
        some = Some(10)
        assert some.forall(lambda x: x > 5)
        assert some.forall(lambda x: x == 10)

    def test_forall_false(self):
        """forall() should return False when predicate doesn't match."""
        some = Some(10)
        assert not some.forall(lambda x: x > 15)
        assert not some.forall(lambda x: x < 0)

    def test_forall_exception_propagates(self):
        """forall() should let exceptions bubble up."""
        some = Some(10)
        with pytest.raises(ZeroDivisionError):
            some.forall(lambda x: x / 0 > 5)


class TestSomeUtilityMethods:
    """Test Some utility methods."""

    def test_get_returns_value(self):
        """get() should return the wrapped value."""
        some = Some("hello")
        assert some.get() == "hello"

    def test_get_or_else_returns_value(self):
        """get_or_else() should return the value, ignoring default."""
        some = Some("hello")
        assert some.get_or_else("default") == "hello"
        assert some.get_or_else(lambda: "default") == "hello"

    def test_or_else_returns_self(self):
        """or_else() should return self, ignoring alternative."""
        some = Some("hello")
        alternative = Some("world")
        result = some.or_else(alternative)
        assert result is some

    def test_foreach(self):
        """foreach() should apply function to value."""
        some = Some(10)
        result = []
        some.foreach(lambda x: result.append(x * 2))
        assert result == [20]

    def test_foreach_exception_propagates(self):
        """foreach() should let exceptions bubble up."""
        some = Some(10)
        with pytest.raises(ZeroDivisionError):
            some.foreach(lambda x: x / 0)

    def test_to_list(self):
        """to_list() should return single-item list."""
        some = Some("hello")
        assert some.to_list() == ["hello"]

    def test_to_optional(self):
        """to_optional() should return the value."""
        some = Some("hello")
        assert some.to_optional() == "hello"

    def test_iteration(self):
        """Some should be iterable with single value."""
        some = Some("hello")
        values = list(some)
        assert values == ["hello"]


class TestSomeEquality:
    """Test Some equality behavior."""

    def test_some_equality_same_value(self):
        """Some instances with same value should be equal."""
        some1 = Some("hello")
        some2 = Some("hello")
        assert some1 == some2

    def test_some_equality_different_value(self):
        """Some instances with different values should not be equal."""
        some1 = Some("hello")
        some2 = Some("world")
        assert some1 != some2

    def test_some_not_equal_to_nil(self):
        """Some should never equal Nil."""
        some = Some("hello")
        nil = Nil()
        assert some != nil
        assert nil != some

    def test_some_not_equal_to_other_types(self):
        """Some should not equal non-Option types."""
        some = Some("hello")
        assert some != "hello"
        assert some != None
        assert some != 42


class TestSomeStringRepresentation:
    """Test Some string representation."""

    def test_repr(self):
        """Test Some.__repr__()."""
        some = Some("hello")
        assert repr(some) == "Some('hello')"

        some_int = Some(42)
        assert repr(some_int) == "Some(42)"

    def test_str(self):
        """Test Some.__str__()."""
        some = Some("hello")
        assert str(some) == "Some('hello')"