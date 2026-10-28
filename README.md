<p align="center">
  <img src="assets/logo.png" alt="failable logo" width="240">
</p>


# failable

[![CI](https://github.com/TimCares/py-failable/actions/workflows/ci.yml/badge.svg)](https://github.com/TimCares/py-failable/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/failable.svg)](https://pypi.org/project/failable/)
[![Python versions](https://img.shields.io/pypi/pyversions/failable.svg)](https://pypi.org/project/failable/)
[![License](https://img.shields.io/pypi/l/failable.svg)](LICENSE)

Rust-like error handling for Python. Decorate a function and the exceptions it
raises come back as values your type checker can see.

No dependencies. Fully typed.

## Install

```sh
pip install failable
```

Requires Python 3.12 or newer.

## Usage

`failable` takes the exception types to catch and returns a decorator. The
wrapped function returns `Ok(value)` on success and `Err(exception)` on failure:

```python
from failable import failable


@failable(ZeroDivisionError)
def divide(a: float, b: float) -> float:
    return a / b


divide(1, 2)  # Ok(value=0.5)
divide(1, 0)  # Err(error=ZeroDivisionError('division by zero'))
```

Exceptions you did not list keep propagating, so unexpected bugs still fail.
Call `failable()` with no arguments to catch every `Exception`.

### Handling a result

A `Result` is the union `Ok[T] | Err[E]`. Match on it or use `isinstance`, and
the type checker knows which payload is available:

```python
result = divide(1, 0)

match result:
    case Ok(value):
        print(value)
    case Err(error):
        print(f"failed: {error}")

if isinstance(result, Err):
    print(result.error)
```

Or skip the branching and supply a fallback:

```python
result.unwrap_or(0.0)  # 0.0
result.unwrap_or_none()  # None
result.unwrap_or_raise()  # re-raises the ZeroDivisionError
```

### Chaining

`map` transforms a success, `map_err` transforms a failure, and `and_then`
chains another failable call. All three skip the work when the variant does not
carry what they need:

```python
@failable(ValueError)
def parse(raw: str) -> int:
    return int(raw)


parse("4").map(lambda n: n * 2)  # Ok(value=8)
parse("x").map(lambda n: n * 2)  # Err(error=ValueError(...))
parse("x").map_err(lambda e: KeyError(str(e)))  # Err(error=KeyError(...))
parse("4").and_then(lambda n: divide(1, n))  # Ok(value=0.25)
parse("0").and_then(lambda n: divide(1, n))  # Err(error=ZeroDivisionError(...))
```

### Async

Async functions work the same way. Await the wrapper and you get a `Result`:

```python
@failable(TimeoutError)
async def fetch(url: str) -> str: ...


result = await fetch("https://example.com")
```

## API

| | |
|---|---|
| `failable(*exceptions)` | Decorator factory. Converts the listed exceptions to `Err`; defaults to `Exception`. |
| `Ok(value)` | Success variant. `.value` holds the result. |
| `Err(error)` | Failure variant. `.error` holds the exception. |
| `Result[T, E]` | Alias for `Ok[T] \| Err[E]`. |

Both variants are frozen dataclasses and support these methods:

| Method | On `Ok[T]` | On `Err[E]` |
|---|---|---|
| `is_ok()` / `is_err()` | `True` / `False` | `False` / `True` |
| `unwrap_or_raise()` | the value | raises the error |
| `unwrap_or_none()` | the value | `None` |
| `unwrap_or(default)` | the value | `default` |
| `error_or_none()` | `None` | the error |
| `map(fn)` | `Ok(fn(value))` | unchanged |
| `map_err(fn)` | unchanged | `Err(fn(error))` |
| `and_then(fn)` | `fn(value)` | unchanged |

## Nice to know

- **The parentheses are required.** `@failable()`, not `@failable`. An exception
  class is callable itself, so a bare form could not be told apart from
  `@failable(ValueError)`.
- **`BaseException` is never caught.** `KeyboardInterrupt`, `SystemExit` and
  `asyncio.CancelledError` pass, which is what we want.
- **Both variants are truthy.** `if result:` is always true, use `isinstance` instead.
- **`is_ok()` / `is_err()` do not narrow the type.** They are predicates,
  useful for asserts and filters. To reach `.value` or `.error`, branch with
  `isinstance` or `match` (closer to Rust).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT, see [LICENSE](LICENSE).
