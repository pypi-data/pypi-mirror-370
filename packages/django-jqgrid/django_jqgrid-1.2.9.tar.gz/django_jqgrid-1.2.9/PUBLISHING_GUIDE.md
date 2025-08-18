# Django-jqGrid Package Publishing Guide

This guide covers how to publish the `django-jqgrid` package to PyPI and TestPyPI using the included publishing scripts.

## 📋 Overview

The publishing system includes three main scripts:

1. **`publish_package.py`** - Main Python publishing script with full functionality
2. **`bump_version.py`** - Standalone version management utility
3. **`publish.sh`** - Shell wrapper for easy command-line usage

## 🚀 Quick Start

### 1. First-Time Setup

```bash
# Make scripts executable
chmod +x publish_package.py bump_version.py publish.sh

# Set up token configuration
cp .pypi_tokens.conf.template .pypi_tokens.conf

# Edit the config file with your actual tokens
nano .pypi_tokens.conf
```

### 2. Get PyPI Tokens

- **PyPI**: https://pypi.org/manage/account/token/
- **TestPyPI**: https://test.pypi.org/manage/account/token/

Create API tokens with "Entire account" scope and copy them to `.pypi_tokens.conf`.

### 3. Basic Publishing

```bash
# Interactive mode (recommended for first-time users)
./publish.sh

# Quick publish to TestPyPI
./publish.sh -q testpypi

# Bump patch version and publish to PyPI
./publish.sh -b patch -t pypi
```

## 📖 Detailed Usage

### Interactive Mode

The interactive mode provides a user-friendly menu:

```bash
./publish.sh
# or
python3 publish_package.py
```

Menu options:
1. Quick publish to PyPI (current version)
2. Quick publish to TestPyPI (current version)
3. Bump version and publish
4. Build only (no upload)
5. Check package
6. Clean build artifacts
7. Show version history
8. Exit

### Command Line Usage

#### Shell Script (`publish.sh`)

```bash
# Show help
./publish.sh --help

# Show current version
./publish.sh --show-version

# Quick publish
./publish.sh -q testpypi          # Test environment
./publish.sh -q pypi              # Production

# Version management
./publish.sh -b patch             # Bump patch (1.0.3 → 1.0.4)
./publish.sh -b minor             # Bump minor (1.0.3 → 1.1.0)
./publish.sh -b major             # Bump major (1.0.3 → 2.0.0)
./publish.sh -v 2.1.0             # Set custom version

# Combined operations
./publish.sh -b patch -t pypi     # Bump patch and publish to PyPI
./publish.sh -v 2.0.0 -t both     # Set version and publish to both

# Build operations
./publish.sh --build-only         # Build without uploading
./publish.sh --check-only         # Check existing package
./publish.sh --clean              # Clean build artifacts

# Dry run (show what would happen)
./publish.sh --dry-run -b minor -t pypi
```

#### Python Script (`publish_package.py`)

```bash
# Interactive mode
python3 publish_package.py

# Non-interactive mode
python3 publish_package.py --non-interactive --target pypi --bump patch

# Build operations
python3 publish_package.py --build-only
python3 publish_package.py --check-only
python3 publish_package.py --clean
```

#### Version Utility (`bump_version.py`)

```bash
# Show current version
python3 bump_version.py --show

# Bump version
python3 bump_version.py patch     # 1.0.3 → 1.0.4
python3 bump_version.py minor     # 1.0.3 → 1.1.0
python3 bump_version.py major     # 1.0.3 → 2.0.0

# Set custom version
python3 bump_version.py --custom 2.1.0
python3 bump_version.py 2.1.0     # Alternative syntax

# Dry run
python3 bump_version.py --dry-run patch
```

## 🔧 Configuration

### Token Configuration (`.pypi_tokens.conf`)

```ini
[tokens]
PYPI_TOKEN = pypi-AgENdGVzdC5weXBpLm9yZwIkYjQyN...
TESTPYPI_TOKEN = pypi-AgENdGVzdC5weXBpLm9yZwIkYjQyN...
```

**Security Notes:**
- Never commit `.pypi_tokens.conf` to version control
- Use tokens with limited scope when possible
- Rotate tokens regularly

### Package Metadata

Version is managed in `django_jqgrid/__init__.py`:

```python
__version__ = '1.0.0'
```

Package metadata is defined in:
- `setup.py` (legacy)
- `pyproject.toml` (modern)

## 📦 Publishing Workflow

### Recommended Publishing Flow

1. **Development**
   ```bash
   # Test your changes locally
   python -m pytest
   
   # Check package structure
   ./publish.sh --build-only
   ./publish.sh --check-only
   ```

2. **Test Release**
   ```bash
   # Bump version and publish to TestPyPI
   ./publish.sh -b patch -t testpypi
   
   # Test installation
   pip install -i https://test.pypi.org/simple/ django-jqgrid==1.0.4
   ```

3. **Production Release**
   ```bash
   # Publish same version to PyPI
   ./publish.sh -t pypi
   
   # Test installation
   pip install django-jqgrid==1.0.4
   ```

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (`2.0.0`): Breaking changes
- **MINOR** (`1.1.0`): New features, backwards compatible
- **PATCH** (`1.0.1`): Bug fixes, backwards compatible

Examples:
```bash
# Bug fix release
./publish.sh -b patch -t pypi     # 1.0.3 → 1.0.4

# New feature release
./publish.sh -b minor -t pypi     # 1.0.4 → 1.1.0

# Major rewrite/breaking changes
./publish.sh -b major -t pypi     # 1.1.0 → 2.0.0
```

## 🔍 Package Validation

The scripts perform several validation checks:

### Build Checks
- ✅ Clean build artifacts
- ✅ Build wheel and source distribution
- ✅ Validate package metadata
- ✅ Check file structure

### Content Checks
- ✅ README.md exists and is valid
- ✅ LICENSE file included
- ✅ Static files and templates included
- ✅ Dependencies properly listed

### Quality Checks
- ✅ Version format validation
- ✅ Package structure validation
- ✅ Metadata completeness

## 🔨 Build Process

The build process follows these steps:

1. **Clean**: Remove old build artifacts
2. **Build**: Create wheel and source distributions using `python -m build`
3. **Check**: Validate packages using `twine check`
4. **Upload**: Upload to PyPI/TestPyPI using `twine upload`

### Generated Files

```
dist/
├── django_jqgrid-1.0.0-py3-none-any.whl    # Wheel distribution
└── django-jqgrid-1.0.0.tar.gz              # Source distribution
```

## 🚨 Troubleshooting

### Common Issues

#### 1. "Version already exists"
```bash
# Solution: Bump version first
./publish.sh -b patch -t pypi
```

#### 2. "Invalid token"
```bash
# Check token format in .pypi_tokens.conf
# Tokens should start with 'pypi-'
```

#### 3. "Package check failed"
```bash
# Check build artifacts
./publish.sh --build-only
./publish.sh --check-only

# Common issues:
# - Missing README.md
# - Invalid package metadata
# - Missing required files
```

#### 4. "Build tools not found"
```bash
# Install build dependencies
pip install build twine

# Or use requirements
pip install -r requirements-dev.txt
```

### Debug Mode

For detailed error information:

```bash
# Python script with verbose output
python3 publish_package.py --non-interactive --target testpypi --bump patch

# Manual twine upload with verbose output
python -m twine upload --repository testpypi dist/* --verbose
```

## 🔐 Security Best Practices

1. **Token Management**
   - Use scoped tokens (project-specific)
   - Store tokens securely
   - Rotate tokens regularly
   - Never commit tokens to version control

2. **Build Security**
   - Review package contents before publishing
   - Use virtual environments for building
   - Verify checksums of dependencies

3. **Version Control**
   - Tag releases in git
   - Create release notes
   - Sign releases (optional)

## 🌐 CI/CD Integration

### GitHub Actions Example

```yaml
name: Publish Package

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      run: |
        python -m twine upload dist/* -u __token__ -p ${{ secrets.PYPI_TOKEN }}
```

### Local Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run package checks before commit
cd django-jqgrid-package
./publish.sh --build-only
./publish.sh --check-only
```

## 📊 Monitoring

### Check Package Status

```bash
# Show version history
./publish.sh --show-version

# Check PyPI listing
pip index versions django-jqgrid

# Check download stats (external tools)
# - pypistats
# - pypi-stats
```

### Package Analytics

Monitor your package using:
- [PyPI Stats](https://pypistats.org/)
- [Libraries.io](https://libraries.io/)
- [Snyk](https://snyk.io/) (security)

## 📚 Additional Resources

- [PyPI Help](https://pypi.org/help/)
- [TestPyPI](https://test.pypi.org/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)
- [Twine Documentation](https://twine.readthedocs.io/)

---

**Happy Publishing! 🚀**