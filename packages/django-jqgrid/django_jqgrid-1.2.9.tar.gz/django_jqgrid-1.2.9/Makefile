.PHONY: help install install-dev test test-cov lint format clean build upload docs

help:
	@echo "Available commands:"
	@echo "  install      Install package for development"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build package"
	@echo "  upload       Upload to PyPI"
	@echo "  docs         Build documentation"

install:
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

test:
	pytest

test-cov:
	pytest --cov=django_jqgrid --cov-report=html --cov-report=term-missing

lint:
	flake8 django_jqgrid
	black --check django_jqgrid
	isort --check-only django_jqgrid
	mypy django_jqgrid

format:
	black django_jqgrid
	isort django_jqgrid

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	twine upload dist/*

docs:
	cd docs && make html