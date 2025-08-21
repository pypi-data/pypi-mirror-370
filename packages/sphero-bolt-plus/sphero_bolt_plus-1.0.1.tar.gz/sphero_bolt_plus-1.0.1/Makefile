.PHONY: install install-dev test lint format typecheck clean build upload docs

# Python interpreter
PYTHON := python3

# Package name
PACKAGE := sphero_bolt_plus

# Install package
install:
	$(PYTHON) -m pip install .

# Install package in development mode
install-dev:
	$(PYTHON) -m pip install -e .[dev]

# Run tests
test:
	$(PYTHON) -m pytest tests/ -v

# Run tests with coverage
test-coverage:
	$(PYTHON) -m pytest tests/ --cov=$(PACKAGE) --cov-report=html --cov-report=term

# Lint code
lint:
	$(PYTHON) -m ruff check $(PACKAGE) tests examples

# Format code
format:
	$(PYTHON) -m black $(PACKAGE) tests examples
	$(PYTHON) -m ruff check --fix $(PACKAGE) tests examples

# Type check
typecheck:
	$(PYTHON) -m mypy $(PACKAGE)

# Check all (lint, format, typecheck)
check: lint typecheck

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Build package
build: clean
	$(PYTHON) -m build

# Upload to PyPI (requires twine)
upload: build
	$(PYTHON) -m twine upload dist/*

# Upload to PyPI test (requires twine)
upload-test: build
	$(PYTHON) -m twine upload --repository testpypi dist/*

# Generate documentation
docs:
	cd docs && $(PYTHON) -m sphinx -b html source build

# Run examples
example-basic:
	$(PYTHON) examples/basic_movement.py

example-matrix:
	$(PYTHON) examples/led_matrix_demo.py

example-sensors:
	$(PYTHON) examples/sensor_monitoring.py

# Development setup
dev-setup: install-dev
	pre-commit install

# Help
help:
	@echo "Available commands:"
	@echo "  install       Install package"
	@echo "  install-dev   Install package in development mode"
	@echo "  test          Run tests"
	@echo "  test-coverage Run tests with coverage report"
	@echo "  lint          Run linter"
	@echo "  format        Format code"
	@echo "  typecheck     Run type checker"
	@echo "  check         Run lint and typecheck"
	@echo "  clean         Clean build artifacts"
	@echo "  build         Build package"
	@echo "  upload        Upload to PyPI"
	@echo "  upload-test   Upload to PyPI test"
	@echo "  docs          Generate documentation"
	@echo "  example-*     Run example scripts"
	@echo "  dev-setup     Setup development environment"
	@echo "  help          Show this help message"