"""
Option monad for safe handling of nullable values.

Scala-inspired Option type providing Some and Nil for functional programming patterns.
"""

from .option import Option
from .some import Some
from .nil import Nil

__all__ = ["Option", "Some", "Nil"]