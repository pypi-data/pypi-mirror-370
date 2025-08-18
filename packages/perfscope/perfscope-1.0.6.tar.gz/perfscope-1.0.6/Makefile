.PHONY: help install install-dev test test-cov lint format typecheck clean build upload docs

help:
	@echo "Available commands:"
	@echo "  install       Install the package in production mode"
	@echo "  install-dev   Install the package in development mode with all dependencies"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage report"
	@echo "  lint          Run linting (ruff check)"
	@echo "  format        Format code (ruff format)"
	@echo "  typecheck     Run type checking (mypy)"
	@echo "  clean         Clean build artifacts"
	@echo "  build         Build distribution packages"
	@echo "  upload        Upload to PyPI"
	@echo "  docs          Build documentation"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest

test-cov:
	pytest --cov=perfscope --cov-report=term-missing --cov-report=html

lint:
	ruff check src tests

format:
	ruff format src tests

typecheck:
	mypy src/perfscope

clean:
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	rm -rf htmlcov .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	python -m twine upload dist/*

docs:
	cd docs && make html
