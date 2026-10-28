# Contributing

Issues and pull requests are welcome. For anything larger than a bug fix, open
an issue first so we agree on the direction before you write code.

## Setup

The project uses [uv](https://docs.astral.sh/uv/).

```sh
make install
```

That installs the dev dependencies and the commit hooks. `make help` lists
every target.

## Checks

Run the suite before pushing; CI runs the same thing, plus the tests on Python
3.12, 3.13 and 3.14:

```sh
make check
```

`make fix` applies the formatter and the lint auto-fixes.

## Commit messages

Commits follow [Conventional Commits](https://www.conventionalcommits.org/).
The version number and changelog are derived from them, so the prefix decides
what gets released:

| Prefix | Release |
|---|---|
| `fix:` | patch |
| `feat:` | minor |
| any type with `!` or a `BREAKING CHANGE:` footer | major |
| `chore:`, `docs:`, `test:`, `refactor:`, `ci:` | none |

```
feat: add Result.inspect for side-effecting on success
fix: stop catching BaseException in the async wrapper
```

The `commit-msg` hook rejects messages that do not parse. `uv run cz commit`
walks you through the format if you prefer a prompt.

## Conventions

- Public API lives in `src/failable/__init__.py`; implementation in the
  underscore-prefixed modules.
- Everything public needs a Google-style docstring and full annotations.
- Behaviour changes need a test. `tests/test_typing.py` holds the static typing
  contract via `assert_type` — add a case there when you change a signature.
- Coverage must stay at 100%.
- Do not edit `CHANGELOG.md` or `__version__` by hand; both are generated.

## Releasing

There is no manual release step. Every push to `main` runs semantic-release,
which reads the commits since the last tag and, if any of them warrant a
release, bumps `__version__`, writes `CHANGELOG.md`, commits, tags, builds, and
publishes to PyPI via trusted publishing. Commits that warrant nothing produce
no release.
