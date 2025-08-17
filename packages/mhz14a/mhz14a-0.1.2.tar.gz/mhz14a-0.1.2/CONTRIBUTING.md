# Contributing to mhz14a

Thank you for your interest in contributing to the mhz14a project!

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- MH-Z14A sensor (for hardware testing)

### Setting Up Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/oaslananka/mhz14a.git
   cd mhz14a
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode with dev dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks (optional but recommended):**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Development Workflow

### Code Quality Tools

The project uses several tools to maintain code quality:

- **ruff**: Linting and code style
- **mypy**: Static type checking
- **pytest**: Testing framework

### Running Tests and Checks

1. **Run linting:**
   ```bash
   ruff check .
   ```

2. **Run type checking:**
   ```bash
   mypy src
   ```

3. **Run tests:**
   ```bash
   pytest -v
   ```

4. **Run all checks together:**
   ```bash
   ruff check . && mypy src && pytest -v
   ```

### Testing

#### Unit Tests

The project includes comprehensive unit tests:

- `tests/test_checksum.py`: Checksum calculation tests
- `tests/test_protocol.py`: Protocol communication tests (mocked)
- `tests/test_cli.py`: Command-line interface tests

#### Hardware Testing

For testing with real hardware:

1. Connect MH-Z14A sensor to your development machine
2. Set up udev rules (see README.md)
3. Run manual tests:
   ```bash
   mhz14a --port /dev/mhz14a read
   mhz14a --port /dev/mhz14a sample --interval 5 --count 3
   ```

### Building and Distribution

1. **Build the package:**
   ```bash
   python -m build
   ```

2. **Check build artifacts:**
   ```bash
   ls dist/
   # Should contain: mhz14a-X.Y.Z-py3-none-any.whl and mhz14a-X.Y.Z.tar.gz
   ```

## Code Style Guidelines

### Python Code Style

- Follow PEP 8 (enforced by ruff)
- Use type annotations for all functions and methods
- Write descriptive docstrings with examples
- Keep functions focused and testable

### Type Annotations

The project uses strict mypy configuration:

```python
# Good
def read_co2(self) -> int:
    """Read CO₂ concentration in ppm."""
    # implementation

# Bad
def read_co2(self):  # Missing return type
    # implementation
```

### Documentation

- All public methods must have docstrings with examples
- Use Google-style docstrings
- Include type information in docstrings when helpful

## Release Process

### Versioning

The project uses semantic versioning (semver) with automatic version management via git tags:

- Major version: Breaking changes
- Minor version: New features, backward compatible
- Patch version: Bug fixes, backward compatible

### Creating a Release

1. **Ensure all tests pass:**
   ```bash
   ruff check . && mypy src && pytest -v
   ```

2. **Update CHANGELOG.md:**
   - Move unreleased changes to new version section
   - Follow [Keep a Changelog](https://keepachangelog.com/) format

3. **Commit changes:**
   ```bash
   git add CHANGELOG.md
   git commit -m "Prepare release vX.Y.Z"
   ```

4. **Create and push tag:**
   ```bash
   git tag vX.Y.Z
   git push origin main
   git push origin vX.Y.Z
   ```

5. **GitHub Actions will automatically:**
   - Run CI tests
   - Build packages
   - Publish to TestPyPI (for verification)
   - Publish to PyPI (after manual approval)

### PyPI Publishing

The project uses GitHub Actions with Trusted Publishing:

1. **TestPyPI**: Automatic publication for all tagged releases
2. **PyPI**: Manual approval required in GitHub Actions

## Submitting Changes

### Pull Request Process

1. **Fork the repository** on GitHub
2. **Create a feature branch** from main:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the code style guidelines
4. **Add tests** for new functionality
5. **Run all checks** locally:
   ```bash
   ruff check . && mypy src && pytest -v
   ```
6. **Commit your changes** with descriptive messages
7. **Push to your fork** and submit a pull request

### Pull Request Guidelines

- Include a clear description of the problem and solution
- Reference any related issues
- Ensure all CI checks pass
- Update documentation if needed
- Add changelog entry for user-facing changes

## Getting Help

### Communication

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Email**: Contact maintainer at admin@oaslananka.me

### Common Development Tasks

#### Adding a New Feature

1. Create tests first (TDD approach)
2. Implement the feature
3. Update documentation
4. Add changelog entry

#### Fixing a Bug

1. Write a test that reproduces the bug
2. Fix the bug
3. Ensure the test passes
4. Add changelog entry

#### Updating Dependencies

1. Update version in pyproject.toml
2. Test thoroughly
3. Update documentation if needed

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

Thank you for contributing to mhz14a!
