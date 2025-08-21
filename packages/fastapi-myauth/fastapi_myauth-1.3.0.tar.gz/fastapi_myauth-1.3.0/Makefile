# Define the Python interpreter to use within the virtual environment
PYTHON = .venv/bin/python3

# Define commonly used tools
UV = $(PYTHON) -m uv
RUFF = $(PYTHON) -m ruff
PYTEST = $(PYTHON) -m pytest

.PHONY: help env install format lint test clean ci docs build publish

help:
	@echo "Common development tasks:"
	@echo "  help      - Display this help message."
	@echo "  install   - Install project dependencies from pyproject.toml using uv."
	@echo "  format    - Automatically format code using ruff."
	@echo "  lint      - Check code for style and errors using ruff."
	@echo "  test      - Run tests using pytest."
	@echo "  clean     - Remove build artifacts, cache files, and virtual environment."
	@echo "  ci        - Run formatting, linting, and tests (for CI/pre-commit checks)."
	@echo "  docs      - (Placeholder) Build documentation."
	@echo "  build     - (Placeholder) Build the package distribution."
	@echo "  publish   - (Placeholder) Publish the package to a repository."

install:
	@echo "Creating or updating virtual environment..."
	@uv sync

format: install
	@echo "Formatting code with ruff..."
	@$(RUFF) format

lint: install
	@echo "Linting code with ruff..."
	@$(RUFF) check

test: install
	@echo "Running tests with pytest..."
	@rm -f database.db
	@$(PYTEST) tests/

dev: install
	@echo "Running development server..."
	@uv run fastapi dev fastapi_myauth/test_main.py

clean:
	@echo "Cleaning up..."
	@rm -rf .venv
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@rm -rf build dist *.egg-info .ruff_cache htmlcov .pytest_cache

ci: format lint test
	@echo "CI checks passed."

# Placeholder rules for future functionality
docs:
	@echo "Building documentation (implement this later)."
	@echo "Sphinx or other documentation build tools go here."

build:
	@echo "Building package distribution (implement this later)."
	@echo "uv or build tool commands go here."

publish:
	@echo "Publishing package (implement this later)."
	@echo "uv or twine commands go here."
