# Contributing to Toronto Open Data

Thank you for your interest in contributing to the Toronto Open Data package! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip
- git

### Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/alexwolson/toronto-open-data.git
   cd toronto-open-data
   ```

2. Install the package in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks:
   ```bash
   make pre-commit
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test file
pytest tests/test_core.py -v
```

### Code Quality Checks

```bash
# Run all linting checks
make lint

# Format code automatically
make format

# Run security checks
make security

# Run all quality checks
make check-all
```

### Building Documentation

```bash
# Build HTML documentation
make docs

# View documentation (open docs/_build/html/index.html in browser)
```

## Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pre-commit**: Automated checks

### Pre-commit Hooks

Pre-commit hooks will automatically run on staged files. To run them manually:

```bash
# Run on all files
make pre-commit-run

# Run on specific files
pre-commit run --files path/to/file.py
```

## Pull Request Process

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and ensure they pass all tests:
   ```bash
   make check-all
   ```

3. **Commit your changes** with clear commit messages:
   ```bash
   git commit -m "Add new feature: description"
   ```

4. **Push your branch** and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Ensure CI passes** - all GitHub Actions must pass before merging.

## Testing Guidelines

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Group related tests in classes
- Use fixtures for common setup
- Mock external dependencies

### Test Structure

```python
def test_functionality_description(self):
    """Test description of what is being tested."""
    # Arrange
    # Act
    # Assert
```

### Running Tests

```bash
# Run specific test
pytest tests/test_core.py::TestTorontoOpenData::test_initialization

# Run tests with markers
pytest -m "not slow"

# Run tests with coverage
pytest --cov=toronto_open_data --cov-report=html
```

## Documentation

### Docstring Style

We use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Short description of function.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When something goes wrong
    """
    pass
```

### Building Docs

```bash
cd docs
make html
```

## Release Process

1. **Update version** in `pyproject.toml` and `__init__.py`
2. **Update CHANGELOG.md** with new version
3. **Create release branch** and merge to main
4. **Build package**: `make build`
5. **Publish to PyPI**: `make publish`

## Getting Help

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and general discussion
- **Code of Conduct**: Please be respectful and inclusive

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
