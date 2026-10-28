"""Behaviour of the `Ok` and `Err` variants."""

import pytest

from failable import Err, Ok


class TestOk:
    def test_is_ok(self):
        assert Ok(1).is_ok() is True
        assert Ok(1).is_err() is False

    def test_unwrap_or_raise_returns_value(self):
        assert Ok(1).unwrap_or_raise() == 1

    def test_unwrap_or_none_returns_value(self):
        assert Ok(1).unwrap_or_none() == 1

    def test_unwrap_or_ignores_default(self):
        assert Ok(1).unwrap_or(2) == 1

    def test_error_or_none_is_none(self):
        assert Ok(1).error_or_none() is None

    def test_map_applies_function(self):
        assert Ok(2).map(lambda v: v * 3) == Ok(6)

    def test_map_does_not_catch_exceptions(self):
        with pytest.raises(ValueError, match="boom"):
            Ok(1).map(lambda _: (_ for _ in ()).throw(ValueError("boom")))

    def test_map_err_is_identity(self):
        ok = Ok(1)
        assert ok.map_err(lambda _: RuntimeError()) is ok

    def test_and_then_chains(self):
        assert Ok(2).and_then(lambda v: Ok(v + 1)) == Ok(3)

    def test_and_then_can_produce_err(self):
        error = ValueError("nope")
        assert Ok(2).and_then(lambda _: Err(error)) == Err(error)


class TestErr:
    def test_is_err(self):
        assert Err(ValueError()).is_ok() is False
        assert Err(ValueError()).is_err() is True

    def test_unwrap_or_raise_raises(self):
        error = ValueError("boom")
        with pytest.raises(ValueError, match="boom") as exc_info:
            Err(error).unwrap_or_raise()
        assert exc_info.value is error

    def test_unwrap_or_none_is_none(self):
        assert Err(ValueError()).unwrap_or_none() is None

    def test_unwrap_or_returns_default(self):
        assert Err(ValueError()).unwrap_or(2) == 2

    def test_error_or_none_returns_error(self):
        error = ValueError("boom")
        assert Err(error).error_or_none() is error

    def test_map_is_identity(self):
        err = Err(ValueError())
        assert err.map(lambda v: v) is err

    def test_map_err_applies_function(self):
        err = Err(ValueError("boom"))
        mapped = err.map_err(lambda exc: RuntimeError(str(exc)))
        assert isinstance(mapped.error, RuntimeError)
        assert str(mapped.error) == "boom"

    def test_and_then_is_identity(self):
        err = Err(ValueError())
        assert err.and_then(Ok) is err


class TestVariantSemantics:
    def test_equality_is_structural(self):
        assert Ok(1) == Ok(1)
        assert Ok(1) != Ok(2)
        assert Ok(1) != Err(ValueError())

    def test_variants_are_frozen(self):
        with pytest.raises(AttributeError):
            setattr(Ok(1), "value", 2)  # noqa: B010

    def test_ok_is_hashable_when_value_is(self):
        assert len({Ok(1), Ok(1), Ok(2)}) == 2

    def test_pattern_matching(self):
        error = ValueError("boom")
        results = [Ok(1), Err(error)]
        seen: list[object] = []
        for result in results:
            match result:
                case Ok(value):
                    seen.append(value)
                case Err(caught):
                    seen.append(caught)
        assert seen == [1, error]
