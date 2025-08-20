"""
Try monad for representing computations that may throw exceptions.

Scala-inspired Try type providing Success and Failure for exception handling.
"""

from .try_ import Try
from .success import Success
from .failure import Failure

__all__ = ["Try", "Success", "Failure"]