"""The `Ok` / `Err` result variants and the `Result` alias."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, Never

__all__ = ["Err", "Ok", "Result"]


@dataclass(frozen=True, slots=True)
class Ok[T]:
    """Successful result variant.

    Attributes:
        value: The successfully computed value.
    """

    value: T

    def is_ok(self) -> Literal[True]:
        """Return `True`, because this variant is a success."""
        return True

    def is_err(self) -> Literal[False]:
        """Return `False`, because this variant is a success."""
        return False

    def unwrap_or_raise(self) -> T:
        """Return the value."""
        return self.value

    def unwrap_or_none(self) -> T:
        """Return the value."""
        return self.value

    def unwrap_or[U](self, default: U) -> T | U:
        """Return the value, ignoring `default`."""
        return self.value

    def error_or_none(self) -> None:
        """Return `None`, because a success has no error."""

    def map[U](self, fn: Callable[[T], U]) -> "Ok[U]":
        """Return `Ok(fn(value))`. Exceptions raised by `fn` are not caught."""
        return Ok(fn(self.value))

    def map_err[F: Exception](self, fn: Callable[[Never], F]) -> "Ok[T]":
        """Return `self`, because a success has no error."""
        return self

    def and_then[U](self, fn: Callable[[T], U]) -> U:
        """Return `fn(value)`, usually another `Result`."""
        return fn(self.value)


@dataclass(frozen=True, slots=True)
class Err[E: Exception]:
    """Failed result variant.

    Attributes:
        error: The caught exception value.
    """

    error: E

    def is_ok(self) -> Literal[False]:
        """Return `False`, because this variant is a failure."""
        return False

    def is_err(self) -> Literal[True]:
        """Return `True`, because this variant is a failure."""
        return True

    def unwrap_or_raise(self) -> Never:
        """Raise the exception."""
        raise self.error

    def unwrap_or_none(self) -> None:
        """Return `None`, because an error carries no value."""

    def unwrap_or[U](self, default: U) -> U:
        """Return `default`, because an error carries no value."""
        return default

    def error_or_none(self) -> E:
        """Return the error."""
        return self.error

    def map[U](self, fn: Callable[[Never], U]) -> "Err[E]":
        """Return `self`, because an error carries no value."""
        return self

    def map_err[F: Exception](self, fn: Callable[[E], F]) -> "Err[F]":
        """Return `Err(fn(error))`, to translate one exception into another."""
        return Err(fn(self.error))

    def and_then[U](self, fn: Callable[[Never], U]) -> "Err[E]":
        """Return `self`, because an error has no value."""
        return self


type Result[T, E: Exception] = Ok[T] | Err[E]
"""Either a success has a `T` or a failure carrying an `E`."""
