"""Behaviour of the `failable` decorator."""

import asyncio

import pytest

from failable import Err, Ok, failable


class TestSync:
    def test_success_is_wrapped_in_ok(self):
        @failable()
        def add(a: int, b: int) -> int:
            return a + b

        assert add(1, 2) == Ok(3)

    def test_listed_exception_becomes_err(self):
        @failable(ZeroDivisionError)
        def divide(a: int, b: int) -> float:
            return a / b

        result = divide(1, 0)
        assert isinstance(result, Err)
        assert isinstance(result.error, ZeroDivisionError)

    def test_unlisted_exception_propagates(self):
        @failable(ZeroDivisionError)
        def fail() -> None:
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            fail()

    def test_bare_decorator_catches_every_exception(self):
        @failable()
        def fail() -> None:
            raise ValueError("boom")

        assert isinstance(fail(), Err)

    def test_subclasses_of_listed_exceptions_are_caught(self):
        class SpecificError(ValueError):
            pass

        @failable(ValueError)
        def fail() -> None:
            raise SpecificError

        result = fail()
        assert isinstance(result, Err)
        assert isinstance(result.error, SpecificError)

    def test_multiple_exception_types(self):
        @failable(KeyError, IndexError)
        def lookup(data: dict[str, list[int]], key: str, index: int) -> int:
            return data[key][index]

        data = {"a": [1]}
        assert lookup(data, "a", 0) == Ok(1)
        assert isinstance(lookup(data, "b", 0).error_or_none(), KeyError)
        assert isinstance(lookup(data, "a", 9).error_or_none(), IndexError)

    def test_base_exceptions_are_never_caught(self):
        @failable()
        def interrupt() -> None:
            raise KeyboardInterrupt

        with pytest.raises(KeyboardInterrupt):
            interrupt()

    def test_metadata_is_preserved(self):
        @failable()
        def documented(a: int) -> int:
            """Add one."""
            return a + 1

        assert documented.__name__ == "documented"
        assert documented.__doc__ == "Add one."

    def test_keyword_arguments_are_forwarded(self):
        @failable()
        def greet(name: str, *, greeting: str = "hi") -> str:
            return f"{greeting} {name}"

        assert greet("ada", greeting="hello") == Ok("hello ada")


class TestAsync:
    async def test_success_is_wrapped_in_ok(self):
        @failable()
        async def add(a: int, b: int) -> int:
            return a + b

        assert await add(1, 2) == Ok(3)

    async def test_listed_exception_becomes_err(self):
        @failable(ValueError)
        async def fail() -> None:
            raise ValueError("boom")

        result = await fail()
        assert isinstance(result, Err)
        assert str(result.error) == "boom"

    async def test_unlisted_exception_propagates(self):
        @failable(KeyError)
        async def fail() -> None:
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            await fail()

    async def test_cancellation_is_not_caught(self):
        started = asyncio.Event()

        @failable()
        async def forever() -> None:
            started.set()
            await asyncio.sleep(3600)

        task = asyncio.create_task(forever())
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    async def test_metadata_is_preserved(self):
        @failable()
        async def documented() -> None:
            """Do nothing."""

        assert documented.__name__ == "documented"
        assert documented.__doc__ == "Do nothing."


class TestCombinedWithVariants:
    def test_chaining_short_circuits_on_error(self):
        @failable(ValueError)
        def parse(raw: str) -> int:
            return int(raw)

        @failable(ZeroDivisionError)
        def reciprocal(value: int) -> float:
            return 1 / value

        assert parse("4").and_then(reciprocal) == Ok(0.25)
        assert parse("0").and_then(reciprocal).unwrap_or(0.0) == 0.0
        assert parse("x").and_then(reciprocal).unwrap_or(0.0) == 0.0
