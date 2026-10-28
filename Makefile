.DEFAULT_GOAL := help

.PHONY: help
help:  ## Show this help message
	@echo "Makefile Commands"
	@echo "================="
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# Setup
# =============================================================================

.PHONY: install
install:  ## Install the dev environment and the commit hooks
	uv sync --all-groups
	uv run pre-commit install --install-hooks --hook-type commit-msg

# =============================================================================
# Checks (read-only — what CI runs)
# =============================================================================

.PHONY: format-check
format-check:  ## Check formatting without changing files
	uv run ruff format --check .

.PHONY: lint-check
lint-check:  ## Lint without auto-fixing
	uv run ruff check .

.PHONY: type-check
type-check:  ## Type check with ty
	uv run ty check

.PHONY: test
test:  ## Run the tests (100% coverage required)
	uv run pytest

.PHONY: check
check: format-check lint-check type-check test  ## Run the full check suite

# =============================================================================
# Fixes (modify files)
# =============================================================================

.PHONY: format
format:  ## Format code
	uv run ruff format .

.PHONY: lint
lint:  ## Lint and auto-fix
	uv run ruff check --fix .

.PHONY: fix
fix: format lint  ## Run every auto-fixer

# =============================================================================
# Version
# =============================================================================

.PHONY: build
build:  ## Build the sdist and wheel into dist/
	uv build

.PHONY: version
version:  ## Show the current version
	@uv run python -c "import failable; print(failable.__version__)"

# =============================================================================
# Cleanup
# =============================================================================

.PHONY: clean
clean:  ## Remove build and cache artifacts
	rm -rf build dist htmlcov .coverage coverage.xml .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
