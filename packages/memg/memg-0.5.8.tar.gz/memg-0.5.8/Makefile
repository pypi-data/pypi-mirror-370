# MEMG Development Makefile
# Provides convenient commands for development tasks

.PHONY: test test-unit test-integration test-fast test-all test-coverage clean lint format lint-fix type-check security-check quality-check quality install-dev help

# Default target
help:
	@echo "MEMG Development Commands"
	@echo "========================"
	@echo ""
	@echo "Testing:"
	@echo "  test-unit       Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-fast       Run fast tests (exclude slow ones)"
	@echo "  test-all        Run all tests with coverage"
	@echo "  test-coverage   Generate detailed coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint            Run linting with Ruff"
	@echo "  format          Format code with Ruff"
	@echo "  lint-fix        Auto-fix linting issues and format"
	@echo "  type-check      Run type checking with MyPy"
	@echo "  security-check  Run security analysis with Bandit"
	@echo "  quality-check   Run all quality checks"
	@echo "  quality         Run all quality checks and tests"
	@echo ""
	@echo "Development:"
	@echo "  install-dev     Install development dependencies"
	@echo "  clean           Clean build artifacts and cache"
	@echo ""

# Testing targets
test: test-fast

test-unit:
	python tests/test_runner.py unit

test-integration:
	python tests/test_runner.py integration

test-fast:
	python tests/test_runner.py fast

test-all:
	python tests/test_runner.py all

test-coverage:
	python -m pytest tests/ --cov=memg --cov-report=html --cov-report=term-missing --cov-report=xml

# Code quality targets
lint:
	@echo "Running Ruff linter..."
	ruff check src/

format:
	@echo "Formatting code with Ruff..."
	ruff format src/

lint-fix:
	@echo "Auto-fixing Ruff issues..."
	ruff check src/ --fix
	ruff format src/

type-check:
	@echo "Running MyPy type checker..."
	mypy src/memg/

security-check:
	@echo "Running Bandit security scanner..."
	bandit -r src/ -q

quality-check: lint type-check security-check
	@echo "All quality checks completed"

quality: quality-check test
	@echo "All quality checks and tests passed!"

# Development targets
install-dev:
	pip install -e ".[dev]"

install-pre-commit:
	@echo "Installing pre-commit hooks..."
	pre-commit install
	pre-commit install --hook-type pre-push
	@echo "Pre-commit hooks installed successfully!"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
