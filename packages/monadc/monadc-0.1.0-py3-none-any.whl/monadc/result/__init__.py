"""
Result monad for representing computations that can succeed or fail.

Rust-inspired Result type providing Ok and Err for error handling.
"""

from .result import Result
from .ok import Ok
from .err import Err

__all__ = ["Result", "Ok", "Err"]