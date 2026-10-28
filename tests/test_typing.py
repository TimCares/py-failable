"""Static typing contract, checked by ty rather than at runtime.

`assert_type` is a no-op at runtime; these tests fail by failing the type
checkers in CI. Running them under pytest only proves the code still executes.
"""

from typing import Literal, assert_type

from failable import Err, Ok, Result, failable


class TestVariantMethods:
    # The type parameters are pinned explicitly because ty keeps literal
    # types: `Ok(1)` alone would infer `Ok[Literal[1]]`, not `Ok[int]`.
    def test_ok_narrows_to_value_type(self):
        assert_type(Ok[int](1).unwrap_or_raise(), int)
        assert_type(Ok[int](1).unwrap_or_none(), int)
        assert_type(Ok[int](1).error_or_none(), None)

    def test_err_narrows_to_error_type(self):
        assert_type(Err(ValueError()).unwrap_or_none(), None)
        assert_type(Err(ValueError()).error_or_none(), ValueError)

    def test_unwrap_or_unions_value_and_default(self):
        # Taken as a parameter so the fallback stays `str`; ty narrows a local
        # to `Literal["fallback"]` even when it is declared as `str`.
        def check(fallback: str) -> None:
            assert_type(Ok[int](1).unwrap_or(fallback), int | str)
            assert_type(Err(ValueError()).unwrap_or(fallback), str)

        check("fallback")

    def test_map_rewraps_in_same_variant(self):
        assert_type(Ok[int](1).map(str), Ok[str])
        assert_type(Err(ValueError()).map(str), Err[ValueError])

    def test_map_err_rewraps_in_same_variant(self):
        assert_type(Ok[int](1).map_err(RuntimeError), Ok[int])
        assert_type(
            Err(ValueError()).map_err(lambda exc: RuntimeError(str(exc))),
            Err[RuntimeError],
        )


class TestDecorator:
    def test_signature_is_preserved(self):
        @failable(ValueError)
        def parse(raw: str, *, base: int = 10) -> int:
            return int(raw, base)

        assert_type(parse("1", base=2), Result[int, ValueError])

    def test_bare_call_catches_exception(self):
        @failable()
        def identity(value: int) -> int:
            return value

        assert_type(identity(1), Result[int, Exception])

    def test_multiple_exceptions_union_the_error_type(self):
        @failable(KeyError, IndexError)
        def lookup(key: str) -> int:
            return {"a": 1}[key]

        assert_type(lookup("a"), Result[int, KeyError | IndexError])

    async def test_async_signature_is_preserved(self):
        @failable(ValueError)
        async def parse(raw: str) -> int:
            return int(raw)

        assert_type(await parse("1"), Result[int, ValueError])


class TestNarrowing:
    def test_isinstance_narrows_the_union(self):
        @failable(ValueError)
        def parse(raw: str) -> int:
            return int(raw)

        result = parse("1")
        if isinstance(result, Ok):
            assert_type(result.value, int)
        else:
            assert_type(result.error, ValueError)

    def test_match_narrows_the_union(self):
        @failable(ValueError)
        def parse(raw: str) -> int:
            return int(raw)

        match parse("1"):
            case Ok(value):
                assert_type(value, int)
            case Err(error):
                assert_type(error, ValueError)

    def test_predicates_do_not_narrow(self):
        """`is_ok` is a plain predicate; narrowing needs isinstance or match."""
        assert_type(Ok(1).is_ok(), Literal[True])
        assert_type(Err(ValueError()).is_ok(), Literal[False])


class TestChaining:
    def test_and_then_propagates_both_error_types(self):
        @failable(ValueError)
        def parse(raw: str) -> int:
            return int(raw)

        @failable(ZeroDivisionError)
        def reciprocal(value: int) -> float:
            return 1 / value

        # The success path carries `reciprocal`'s error, the failure path keeps
        # `parse`'s, so both show up in the union.
        assert_type(
            parse("1").and_then(reciprocal),
            Ok[float] | Err[ZeroDivisionError] | Err[ValueError],
        )

    def test_map_preserves_the_error_type(self):
        @failable(ValueError)
        def parse(raw: str) -> int:
            return int(raw)

        assert_type(parse("1").map(str), Ok[str] | Err[ValueError])
