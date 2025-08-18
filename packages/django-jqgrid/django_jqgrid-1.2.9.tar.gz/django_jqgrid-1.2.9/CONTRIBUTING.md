# Contributing to Django jqGrid

Thank you for your interest in contributing to Django jqGrid! We welcome contributions from the community and are grateful for any help you can provide.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or bugfix
4. Make your changes
5. Submit a pull request

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, please include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Your environment details (Django version, Python version, OS)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- A clear and descriptive title
- A detailed description of the proposed enhancement
- Any possible drawbacks
- Examples of how the enhancement would be used

### Pull Requests

1. Ensure your code follows our coding standards
2. Include tests for new functionality
3. Update documentation as needed
4. Add an entry to CHANGELOG.md
5. Ensure all tests pass
6. Submit your pull request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, virtualenv, or poetry)

### Setting Up Your Development Environment

```bash
# Clone your fork
git clone https://github.com/coder-aniket/django-jqgrid.git
cd django-jqgrid

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running the Example Project

```bash
# Navigate to the example project
cd example_project

# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

## Coding Standards

### Python Style Guide

We follow PEP 8 with the following modifications:
- Line length: 88 characters (Black's default)
- Use double quotes for strings
- Use type hints where appropriate

### JavaScript Style Guide

- Use ES6+ features
- Use semicolons
- Use single quotes for strings
- 2 spaces for indentation

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build process or auxiliary tool changes

Example:
```
feat(grid): add column freezing support

Add ability to freeze columns in the grid to keep them visible
while scrolling horizontally.

Closes #123
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=django_jqgrid --cov-report=html

# Run specific test file
pytest tests/test_mixins.py

# Run specific test
pytest tests/test_mixins.py::TestJQGridMixin::test_get_model
```

### Writing Tests

- Write tests for all new functionality
- Maintain or improve code coverage
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Use fixtures for common test data

Example test:

```python
import pytest
from django.test import TestCase
from django_jqgrid import JQGridMixin


class TestJQGridMixin(TestCase):
    def test_get_grid_config_returns_dict(self):
        # Arrange
        mixin = JQGridMixin()
        mixin.grid_model = 'myapp.MyModel'
        
        # Act
        config = mixin.get_grid_config()
        
        # Assert
        assert isinstance(config, dict)
        assert 'colModel' in config
        assert 'options' in config
```

### Testing JavaScript

```bash
# Run JavaScript tests
npm test

# Run with coverage
npm run test:coverage
```

## Documentation

### Building Documentation

```bash
# Navigate to docs directory
cd docs

# Build HTML documentation
make html

# View documentation
open _build/html/index.html  # On macOS
# or
start _build/html/index.html  # On Windows
# or
xdg-open _build/html/index.html  # On Linux
```

### Writing Documentation

- Use clear and concise language
- Include code examples
- Update docstrings for all public APIs
- Add screenshots for UI features
- Keep the README.md up to date

## Submitting Changes

### Pull Request Process

1. Update your fork with the latest upstream changes:
   ```bash
   git remote add upstream https://github.com/originalowner/django-jqgrid.git
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Create a Pull Request on GitHub

### Pull Request Checklist

- [ ] Code follows the project's coding standards
- [ ] Tests have been added/updated
- [ ] Documentation has been updated
- [ ] CHANGELOG.md has been updated
- [ ] All tests pass
- [ ] Code has been reviewed by at least one maintainer

## Release Process

Releases are managed by project maintainers. The process is:

1. Update version in `setup.py` and `pyproject.toml`
2. Update CHANGELOG.md
3. Create a git tag: `git tag v1.0.0`
4. Push tag: `git push origin v1.0.0`
5. GitHub Actions will automatically publish to PyPI

## Getting Help

If you need help, you can:

- Open an issue on GitHub
- Join our Discord server (link in README)
- Post on Stack Overflow with tag `django-jqgrid`
- Email the maintainers (see AUTHORS.md)

## Recognition

Contributors will be recognized in:
- AUTHORS.md file
- Release notes
- Project documentation

Thank you for contributing to Django jqGrid!