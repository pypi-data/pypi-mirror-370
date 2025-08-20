"""
Either monad for representing computations that can succeed or fail.

Scala-inspired Either type providing Left and Right for error handling patterns.
"""

from .either import Either
from .left import Left
from .right import Right

__all__ = ["Either", "Left", "Right"]