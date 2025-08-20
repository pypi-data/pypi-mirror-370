# Contributing to iamx

Thank you for your interest in contributing to iamx! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- pip (Python package manager)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/iamx.git
   cd iamx
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=iamx

# Run specific test file
pytest tests/test_analyzer.py

# Run tests with verbose output
pytest -v
```

## 📝 Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **flake8** for linting
- **mypy** for type checking
- **isort** for import sorting

```bash
# Format code
black .

# Check linting
flake8

# Type checking
mypy iamx/

# Sort imports
isort .
```

## 🔧 Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests and checks**
   ```bash
   pytest
   black .
   flake8
   mypy iamx/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new analysis rule for X"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📋 Pull Request Guidelines

### Before submitting a PR:

- [ ] All tests pass
- [ ] Code is formatted with Black
- [ ] Linting passes (flake8)
- [ ] Type checking passes (mypy)
- [ ] Documentation is updated
- [ ] New features have tests
- [ ] Commit messages follow conventional commits

### PR Title Format

Use conventional commit format:
- `feat: add new analysis rule`
- `fix: resolve parsing issue with wildcards`
- `docs: update README with new examples`
- `test: add tests for resource rules`
- `refactor: improve risk score calculation`

## 🏗️ Project Structure

```
iamx/
├── core/           # Core analysis engine
│   ├── analyzer.py # Main analyzer
│   ├── models.py   # Data models
│   └── parser.py   # Policy parser
├── rules/          # Analysis rules
│   ├── base.py     # Base rule class
│   ├── permissions.py # Permission rules
│   └── resources.py   # Resource rules
├── reports/        # Report generators
│   ├── markdown.py # Markdown reporter
│   └── json.py     # JSON reporter
├── cli.py          # Command-line interface
├── web/            # Web interface
└── tests/          # Test suite
```

## 🧩 Adding New Analysis Rules

To add a new analysis rule:

1. **Create a new rule class** in `iamx/rules/`
   ```python
   from .base import BaseRule
   from ..core.models import Finding, Severity
   
   class MyNewRule(BaseRule):
       title = "My New Rule"
       description = "Description of what this rule detects"
       severity = Severity.MEDIUM
       category = "my-category"
       
       def analyze_statement(self, statement, statement_index):
           # Your analysis logic here
           findings = []
           # ... analysis code ...
           return findings
   ```

2. **Register the rule** in `iamx/rules/__init__.py`
   ```python
   from .my_new_rule import MyNewRule
   
   __all__ = [
       # ... existing rules ...
       "MyNewRule",
   ]
   ```

3. **Add the rule** to the analyzer in `iamx/core/analyzer.py`
   ```python
   from ..rules import (
       # ... existing imports ...
       MyNewRule,
   )
   
   def _load_rules(self):
       return [
           # ... existing rules ...
           MyNewRule(),
       ]
   ```

4. **Add tests** in `tests/test_rules.py`
   ```python
   def test_my_new_rule():
       rule = MyNewRule()
       # Test your rule logic
   ```

## 🐛 Reporting Bugs

When reporting bugs, please include:

- **Description** of the issue
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Sample policy** that triggers the issue (if applicable)

## 💡 Feature Requests

When requesting features, please include:

- **Description** of the feature
- **Use case** and motivation
- **Proposed implementation** (if you have ideas)
- **Examples** of how it would be used

## 📚 Documentation

When updating documentation:

- Keep it clear and concise
- Include examples where helpful
- Update both README.md and docstrings
- Test any code examples

## 🤝 Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and constructive in all interactions.

## 📄 License

By contributing to iamx, you agree that your contributions will be licensed under the MIT License.

## 🆘 Getting Help

If you need help with contributing:

- Check existing issues and PRs
- Ask questions in GitHub Discussions
- Join our community chat (if available)

Thank you for contributing to iamx! 🎉
