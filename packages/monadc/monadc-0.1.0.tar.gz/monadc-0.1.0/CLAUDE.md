# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with coverage report
uv run pytest --cov=monadc --cov-report=html

# Run a specific test file
uv run pytest tests/test_option.py

# Run a specific test function
uv run pytest tests/test_option.py::test_option_creation
```

### Package Management
```bash
# Install dependencies including dev dependencies
uv sync --dev

# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name
```

### Type Checking and Linting
```bash
# Run type checking
uv run mypy src/monadc

# Type check specific module
uv run mypy src/monadc/option/

# Check all Python files in project
uv run mypy .
```

### Build and Distribution
```bash
# Build the package
uv build

# Install the package locally for development
uv pip install -e .
```

## Code Architecture

This is a comprehensive functional programming library implementing Rust and Scala inspired monad primitives for Python. The library provides four core monads with full interoperability and dual API support.

### Core Monad Types

#### Option Monad (Scala-inspired with Rust API)
- **Option[T]**: Abstract base class that serves as both a type annotation and factory constructor
- **Some[T]**: Concrete implementation for values that exist
- **Nil**: Singleton implementation for missing/null values (uses NilType internally)

#### Either Monad (Scala-inspired)
- **Either[L, R]**: Abstract base class for values that can be one of two types
- **Left[L]**: Represents error/failure values 
- **Right[R]**: Represents success values

#### Try Monad (Scala-inspired)
- **Try[T]**: Abstract base class for computations that may throw exceptions
- **Success[T]**: Wraps successful computation results
- **Failure**: Wraps exceptions from failed computations

#### Result Monad (Rust-inspired)
- **Result[T, E]**: Abstract base class for operations that can succeed or fail
- **Ok[T]**: Wraps successful operation results
- **Err[E]**: Wraps error information

### Key Design Patterns

**Factory Constructor Pattern**: `Option(value)`, `Try(lambda: computation())` automatically create the appropriate concrete type, mimicking Scala's companion objects.

**Singleton Pattern**: Nil uses a singleton pattern to ensure only one empty instance exists across the application.

**Monadic Operations**: All transformations (map, flat_map, filter) follow monadic laws and return new instances rather than mutating existing ones.

**Dual API Support**: Many types provide both Scala-style (`get_or_else`, `flat_map`) and Rust-style (`unwrap_or`, `and_then`) methods for maximum flexibility.

### Module Structure
- `src/monadc/option/` - Option/Some/Nil (Scala-inspired with Rust methods)
- `src/monadc/either/` - Either/Left/Right (Scala-inspired)
- `src/monadc/try_/` - Try/Success/Failure (Scala-inspired)
- `src/monadc/result/` - Result/Ok/Err (Rust-inspired)
- `src/monadc/decorators.py` - Function decorators for automatic monad wrapping


### Testing Strategy
Tests are organized by module with comprehensive coverage of:
- Type system correctness (factory constructor behavior)
- Monadic law compliance for all monad types
- Exception handling in both safe and unsafe variants
- Edge cases and error conditions
- Decorator functionality for all supported decorators
- Interoperability between different monad types
- Pattern matching support (where applicable)
- Dual API compatibility (Scala/Rust style methods)

## Important Implementation Details

When working with the codebase, be aware that:

1. **Circular Import Handling**: The modules use lazy imports within methods to avoid circular dependencies between related types (Option/Some/Nil, Either/Left/Right, etc.).

2. **Type Safety**: The library uses generic types throughout. When adding new methods, maintain the TypeVar pattern with T, U, E for input/output/error types.

3. **API Consistency**: Each monad follows its source inspiration (Scala for Option/Either/Try, Rust for Result) while maintaining consistency across the library.

4. **Exception Handling Philosophy**: The library provides both safe and unsafe variants of methods. Safe methods (`*_safe`) catch exceptions and return appropriate empty/error types, while regular methods allow exceptions to propagate.

5. **Dual API Support**: Option and Result types provide both Scala-style and Rust-style methods. When adding new functionality, consider whether both styles are appropriate.

6. **Interoperability**: Types can convert between each other using methods like `to_result()`, `to_either()`, etc. Maintain these conversion methods when adding new types.
