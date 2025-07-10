#!/usr/bin/env just --justfile

# Default recipe to display help
default:
    @just --list

# Install project dependencies with uv
install:
    uv pip install -e ".[dev]"

# Run all tests
test:
    python -m pytest tests/ -v

# Run tests with coverage
test-cov:
    python -m pytest tests/ --cov=minimidl --cov-report=term-missing --cov-report=html

# Format code with black and isort
format:
    black minimidl/ tests/
    isort minimidl/ tests/

# Check code formatting without modifying
format-check:
    black --check minimidl/ tests/
    isort --check-only minimidl/ tests/

# Run linting with ruff and pylint
lint:
    ruff check minimidl/ tests/
    pylint minimidl/ tests/

# Run type checking with mypy
type-check:
    mypy minimidl/ tests/

# Run all quality checks (format-check, lint, type-check)
check: format-check lint type-check

# Build documentation
docs:
    mkdocs build

# Serve documentation locally
docs-serve:
    mkdocs serve

# Build the package
build:
    uv build

# Clean build artifacts
clean:
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info
    rm -rf .coverage
    rm -rf htmlcov/
    rm -rf .pytest_cache/
    rm -rf .mypy_cache/
    rm -rf .ruff_cache/
    rm -rf site/
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Run the CLI
run *ARGS:
    python -m minimidl {{ARGS}}

# Development workflow: format, check, test
dev: format check test

# Pre-commit checks
pre-commit: format check test

# Create a new release
release VERSION:
    git tag -a v{{VERSION}} -m "Release v{{VERSION}}"
    git push origin v{{VERSION}}
    uv build
    @echo "Ready to upload to PyPI with: uv publish"