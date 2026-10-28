"""The `failable` decorator, turning raised exceptions into `Err` values."""

from collections.abc import Callable, Coroutine
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Protocol, cast, overload

from ._result import Err, Ok, Result

__all__ = ["FailableDecorator", "failable"]


class FailableDecorator[E: Exception](Protocol):
    """Decorator type returned by `failable`."""

    @overload
    def __call__[**P, T](
        self,
        fn: Callable[P, Coroutine[Any, Any, T]],
    ) -> Callable[P, Coroutine[Any, Any, Result[T, E]]]: ...

    @overload
    def __call__[**P, T](self, fn: Callable[P, T]) -> Callable[P, Result[T, E]]: ...


@overload
def failable() -> FailableDecorator[Exception]: ...


@overload
def failable[E: Exception](*exceptions: type[E]) -> FailableDecorator[E]: ...


def failable[E: Exception](*exceptions: type[E]) -> FailableDecorator[E]:
    """Wrap a function so expected exceptions become explicit error results.

    Only the listed exceptions are converted to `Err`; anything else keeps
    propagating. Async functions work too: await the wrapper to get the result.
    The parentheses are required, even when catching everything.

    Args:
        *exceptions: Exception classes to catch. Defaults to `Exception`.

    Returns:
        A decorator turning a callable returning `T` into one returning
        `Result[T, E]`.
    """
    caught: tuple[type[Exception], ...] = exceptions or (Exception,)

    def decorator[**P](fn: Callable[P, Any]) -> Callable[P, Any]:
        if iscoroutinefunction(fn):

            @wraps(fn)
            async def async_wrapper(
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> Result[Any, E]:
                try:
                    return Ok(await fn(*args, **kwargs))
                except caught as exc:
                    return Err(cast("E", exc))

            return async_wrapper

        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[Any, E]:
            try:
                return Ok(fn(*args, **kwargs))
            except caught as exc:
                return Err(cast("E", exc))

        return wrapper

    return cast("FailableDecorator[E]", decorator)
