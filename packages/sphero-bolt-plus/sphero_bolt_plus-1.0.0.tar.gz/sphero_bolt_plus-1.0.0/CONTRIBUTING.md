# Contributing to Sphero BOLT+ Python Library

Thank you for your interest in contributing to the Sphero BOLT+ Python Library! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/assistant/sphero-bolt-plus
   cd sphero-bolt-plus
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   make install-dev
   # or manually:
   pip install -e .[dev]
   ```

4. **Verify installation:**
   ```bash
   make test
   ```

## Code Quality

This project maintains high code quality standards:

### Code Formatting
- We use [Black](https://black.readthedocs.io/) for code formatting
- Line length: 88 characters
- Run: `make format`

### Linting
- We use [Ruff](https://ruff.rs/) for fast Python linting
- Run: `make lint`

### Type Checking
- We use [mypy](http://mypy-lang.org/) for static type checking
- All public APIs must have type annotations
- Run: `make typecheck`

### Testing
- We use [pytest](https://pytest.org/) for testing
- Aim for >90% code coverage
- Run: `make test` or `make test-coverage`

## Development Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks:**
   ```bash
   make check  # lint + typecheck
   make test
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and create a pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `style:` - Code style changes (formatting, etc.)
- `chore:` - Maintenance tasks

Examples:
```
feat: add LED matrix scrolling text support
fix: resolve Bluetooth connection timeout issue
docs: update README with new examples
test: add unit tests for scanner module
```

## Code Style Guidelines

### Python Code
- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for all public APIs
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Use descriptive variable and function names

### Async/Await
- Use `async`/`await` for all I/O operations
- Provide both sync and async APIs where appropriate
- Handle `asyncio.TimeoutError` and other async exceptions

### Error Handling
- Create specific exception classes for different error types
- Provide clear, actionable error messages
- Log errors at appropriate levels
- Don't catch and ignore exceptions without good reason

### Documentation
- Write clear, concise docstrings
- Include examples in docstrings where helpful
- Update README.md for significant changes
- Add new features to the API reference

## Testing Guidelines

### Unit Tests
- Test all public APIs
- Test error conditions and edge cases
- Use mocks for external dependencies (Bluetooth, etc.)
- Keep tests fast and reliable

### Integration Tests
- Test with actual hardware when possible
- Provide instructions for manual testing
- Document hardware requirements

### Test Structure
```python
class TestClassName:
    """Test class description."""
    
    @pytest.fixture
    def setup_data(self):
        """Fixture for test data."""
        return SomeTestData()
    
    def test_specific_behavior(self, setup_data):
        """Test specific behavior with descriptive name."""
        # Arrange
        expected = "expected_result"
        
        # Act
        result = function_under_test(setup_data)
        
        # Assert
        assert result == expected
```

## Documentation

- Keep README.md up to date
- Update docstrings for any API changes
- Add examples for new features
- Update type hints and annotations

## Hardware Testing

If you have access to Sphero robots:

1. **Test on actual hardware** when making robot communication changes
2. **Document which models** you've tested with
3. **Include hardware requirements** in PR description
4. **Test Bluetooth connectivity** on different platforms

## Pull Request Process

1. **Ensure all checks pass:**
   - Code formatting (`make format`)
   - Linting (`make lint`)
   - Type checking (`make typecheck`)
   - Tests (`make test`)

2. **Write clear PR description:**
   - What problem does this solve?
   - What changes were made?
   - How was it tested?
   - Any breaking changes?

3. **Update documentation** as needed

4. **Be responsive** to review feedback

5. **Keep commits clean** - squash if necessary

## Release Process

(For maintainers)

1. Update version in `sphero_bolt_plus/__init__.py`
2. Update CHANGELOG.md
3. Create release PR
4. After merge, tag release: `git tag v1.x.x`
5. Build and upload: `make upload`

## Getting Help

- **Issues:** Use GitHub issues for bugs and feature requests
- **Discussions:** Use GitHub discussions for questions
- **Documentation:** Check README.md and docstrings

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn and contribute
- Follow the Golden Rule

Thank you for contributing to make Sphero BOLT+ programming more accessible and enjoyable!