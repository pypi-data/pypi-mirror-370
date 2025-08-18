# Contributing to Ties 🔗

Thank you for your interest in contributing to Ties!
This document provides guidelines and information for contributors.

## 🤝 How to Contribute

There are many ways to contribute to Ties:

- **Report bugs** - Use the [issue tracker](https://github.com/AlonKellner/ties/issues)
- **Suggest features** - Open a feature request issue
- **Improve documentation** - Help make our docs clearer and more comprehensive
- **Submit code** - Fix bugs, add features, or improve existing code
- **Review pull requests** - Help review and test changes
  from other contributors

## 🚀 Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Git

### Getting Started

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/ties.git
   cd ties
   ```

2. **Create a virtual environment**

   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   uv pip install -e ".\\(dev\\]"
   ```

4. **Install pre-commit hooks**

   ```bash
   pre-commit install
   ```

5. **Verify setup**

   ```bash
   pytest
   ```

## 📝 Code Style

We use several tools to maintain code quality:

- **Ruff** - Fast Python linter and formatter
- **Black** - Code formatting (via Ruff)
- **isort** - Import sorting (via Ruff)
- **mypy** - Static type checking
- **Pre-commit** - Git hooks for quality checks

### Running Quality Checks

```bash
# Format code
ruff format

# Lint code
ruff check

# Type check
mypy src/

# Run all pre-commit checks
pre-commit run --all-files
```

### Code Style Guidelines

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints for all function parameters and return values
- Write docstrings in [NumPy format](https://numpydoc.readthedocs.io/en/latest/format.html)
- Keep functions focused and under 50 lines when possible
- Use meaningful variable and function names

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=ties

# Run specific test file
pytest tests/test_file.py

# Run tests in parallel
pytest -n auto
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names that explain what is being tested
- Follow the AAA pattern: Arrange, Act, Assert
- Use fixtures for common test data
- Aim for high test coverage (target: >90%)

### Test Structure

```text
tests/
├── test_module.py          # Tests for specific module
├── test_integration.py     # Integration tests
└── data/                   # Test data files
    ├── sample_config.toml
    └── expected_output.txt
```

## 📚 Documentation

### Documentation Standards

- Write clear, concise documentation
- Include examples for all major features
- Keep documentation up-to-date with code changes
- Use consistent formatting and structure

### Building Documentation

```bash
# Install documentation dependencies
uv pip install sphinx sphinx-rtd-theme

# Build docs
cd docs
make html
```

## 🔄 Pull Request Process

1. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Commit your changes**

   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a pull request**
   - Use the PR template
   - Describe your changes clearly
   - Link any related issues
   - Request reviews from maintainers

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## 🐛 Issue Reporting

When reporting issues, please include:

- **Clear description** of the problem
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Code examples** if applicable

## 📋 Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Other (please describe)

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] All existing tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Changes documented in CHANGELOG.md

## Related Issues
Closes #(issue number)
```

## 🏷️ Release Process

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with new changes
3. **Create a release tag**

   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

4. **GitHub Actions** will automatically build and publish to PyPI

## 🆘 Getting Help

- **GitHub Issues** - For bugs and feature requests
- **GitHub Discussions** - For questions and general discussion
- **Email** - Contact maintainers directly at <me@alonkellner.com>

## 📜 Code of Conduct

Please note that this project is released with a
[Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this
project you agree to abide by its terms.

## 🙏 Recognition

All contributors will be recognized in:
- The project README
- Release notes
- The contributors section on GitHub

Thank you for contributing to Ties! 🎉
