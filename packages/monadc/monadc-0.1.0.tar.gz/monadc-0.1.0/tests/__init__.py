"""
Test suite for monadc library.

This test suite is organized to match the modular structure of the monadc library:

- tests/option/ - Tests for Option monad (Some, Nil, Option constructor)
- tests/either/ - Tests for Either monad (Left, Right, Either constructor)
- tests/try_/    - Tests for Try monad (Success, Failure, Try constructor)
- tests/test_utils.py - Tests for utility functions
- tests/test_decorators.py - Tests for function decorators
- tests/test_integration.py - Integration tests showing monads working together

Each monad module contains comprehensive tests for:
- Construction and factory methods
- Type checking and value access
- Transformations (map, flat_map, filter, etc.)
- Folding and reduction operations
- Side effects and utility methods
- Equality and string representation
- Error handling and edge cases
"""