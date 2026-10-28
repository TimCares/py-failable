"""Rust-like error handling for Python.

Decorate a function with `failable` and the exceptions it raises come back as
`Err` values instead of unwinding the stack:

    >>> from failable import failable
    >>> @failable(ZeroDivisionError)
    ... def divide(a: int, b: int) -> float:
    ...     return a / b
    >>> divide(1, 2)
    Ok(value=0.5)
    >>> divide(1, 0).unwrap_or(float("inf"))
    inf
"""

from ._decorator import FailableDecorator, failable
from ._result import Err, Ok, Result

__all__ = ["Err", "FailableDecorator", "Ok", "Result", "failable"]

# Managed by semantic-release; 0.0.0 means nothing has been released yet.
__version__ = "0.0.0"
