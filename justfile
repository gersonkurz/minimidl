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

# Generate C++ example project
example-cpp:
    python -m minimidl generate examples/task-manager/task_manager.idl --target cpp --output ./tmp/cpp-example
    @echo "C++ example generated in ./tmp/cpp-example"

# Generate Swift example project
example-swift:
    python -m minimidl generate examples/task-manager/task_manager.idl --target swift --output ./tmp/swift-example
    @echo "Swift example generated in ./tmp/swift-example"

# Generate all examples
examples: example-cpp example-swift

# Test fixture generation
generate-fixture NAME:
    python -m minimidl generate tests/fixtures/{{NAME}}.idl --target all --output ./tmp/{{NAME}}
    @echo "Generated test fixture in ./tmp/{{NAME}}"

# Parse IDL file and show AST
parse-debug FILE:
    python -m minimidl parse {{FILE}} --json | python -m json.tool

# Validate IDL file with verbose output
validate-debug FILE:
    python -m minimidl --verbose validate {{FILE}}

# Run specific test file
test-file FILE:
    python -m pytest {{FILE}} -v

# Run tests with specific marker
test-mark MARK:
    python -m pytest -m {{MARK}} -v

# Update test snapshots
test-update:
    python -m pytest tests/ --snapshot-update

# Watch mode for development
watch:
    watchmedo auto-restart --patterns="*.py" --recursive -- python -m minimidl

# Profile CLI performance
profile CMD:
    python -m cProfile -o profile.stats -m minimidl {{CMD}}
    python -m pstats profile.stats

# Check for security issues
security:
    pip-audit
    bandit -r minimidl/

# Generate requirements file
requirements:
    uv pip freeze > requirements.txt

# Install in editable mode with all extras
install-all:
    uv pip install -e ".[dev,docs]"

# Debug parser grammar
debug-parser:
    python -c "from minimidl.parser.grammar import get_parser; print(get_parser().pretty())"

# Run integration tests only
test-integration:
    python -m pytest tests/integration/ -v

# Run unit tests only
test-unit:
    python -m pytest tests/unit/ -v

# Generate test coverage badge
coverage-badge:
    coverage-badge -o assets/coverage.svg

# Serve documentation with auto-reload
docs-dev:
    mkdocs serve --dev-addr 0.0.0.0:8001

# Deploy documentation to GitHub Pages
docs-deploy:
    mkdocs gh-deploy

# Check for outdated dependencies
deps-outdated:
    pip list --outdated

# Update all dependencies
deps-update:
    uv pip install --upgrade -e ".[dev,docs]"

# Create source distribution
sdist:
    python -m build --sdist

# Create wheel distribution
wheel:
    python -m build --wheel

# Test installation in clean environment
test-install:
    uv venv tmp-env
    tmp-env/bin/pip install dist/*.whl
    tmp-env/bin/minimidl --help
    rm -rf tmp-env

# Run benchmarks
bench:
    python -m pytest tests/benchmarks/ -v --benchmark-only

# Generate API documentation
api-docs:
    pdoc --html --output-dir docs/api minimidl