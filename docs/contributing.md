# Contributing to Incident Helper

Thank you for your interest in contributing to Incident Helper! This guide will help you get started with development and contributions.

## Development Setup

### Prerequisites
- Python 3.8+
- Git
- Ollama (for testing local LLM integration)

### Setup Development Environment

1. **Fork and clone the repository**
```bash
git clone https://github.com/malikyawar/incident-helper.git
cd incident-helper
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

5. **Run tests to verify setup**
```bash
pytest
```

## Project Structure

```
incident_helper/
├── __init__.py
├── cli.py              # Main CLI interface
├── context.py          # Incident context management
├── agents.py           # LLM provider integration
├── prompts.py          # AI prompt templates
├── utils.py            # Utility functions
└── resolvers/          # Diagnostic modules
    ├── system.py       # System diagnostics
    ├── services.py     # Service management
    ├── logs.py         # Log analysis
    ├── network.py      # Network diagnostics
    └── ssh.py          # SSH operations

tests/                  # Test suite
docs/                   # Documentation
```

## Development Guidelines

### Code Style
We use Black for code formatting and follow PEP 8:

```bash
# Format code
black incident_helper/

# Check formatting
black --check incident_helper/

# Lint code
flake8 incident_helper/

# Type checking
mypy incident_helper/
```

### Testing
- Write tests for all new functionality
- Maintain test coverage above 80%
- Use pytest for testing framework
- Mock external dependencies

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=incident_helper

# Run specific test file
pytest tests/test_cli.py

# Run specific test
pytest tests/test_cli.py::test_quick_check_command
```

### Documentation
- Update README.md for user-facing changes
- Add docstrings to all functions and classes
- Update architecture.md for structural changes
- Include examples in docstrings

## Contributing Process

### 1. Choose an Issue
- Look for issues labeled `good first issue` for beginners
- Check existing issues before creating new ones
- Comment on issues you want to work on

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number
```

### 3. Make Changes
- Follow the coding standards
- Write tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 4. Test Your Changes
```bash
# Run tests
pytest

# Test CLI manually
incident-helper start
incident-helper quick-check
```

### 5. Submit a Pull Request
- Push your branch to your fork
- Create a pull request with clear description
- Link to related issues
- Ensure CI passes

## Types of Contributions

### 🐛 Bug Fixes
- Fix existing functionality
- Add regression tests
- Update documentation if needed

### ✨ New Features
- Add new resolver modules
- Enhance existing functionality
- Improve user experience

### 📚 Documentation
- Improve README and guides
- Add code examples
- Fix typos and clarity issues

### 🧪 Testing
- Add missing test coverage
- Improve test quality
- Add integration tests

## Adding New Resolvers

Resolvers are the core diagnostic modules. Here's how to add a new one:

### 1. Create Resolver Class
```python
# incident_helper/resolvers/my_resolver.py
from typing import Dict, Any

class MyResolver:
    """Handles my specific diagnostic area"""
    
    def diagnose_issue(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main diagnostic method"""
        try:
            # Your diagnostic logic here
            return {
                "status": "success",
                "findings": [],
                "recommendations": []
            }
        except Exception as e:
            return {"error": f"Diagnostic failed: {e}"}
```

### 2. Add Tests
```python
# tests/test_my_resolver.py
import pytest
from incident_helper.resolvers.my_resolver import MyResolver

class TestMyResolver:
    def test_diagnose_issue(self):
        resolver = MyResolver()
        result = resolver.diagnose_issue({})
        assert "status" in result
```

### 3. Integrate with CLI
```python
# In cli.py
from incident_helper.resolvers.my_resolver import MyResolver

my_resolver = MyResolver()

# Add commands or integrate with existing flows
```

### 4. Add Documentation
- Update README.md with new capabilities
- Add resolver documentation
- Include usage examples

## Adding LLM Providers

To add support for a new LLM provider:

### 1. Implement Provider Class
```python
# In agents.py
class MyLLMProvider(LLMProvider):
    def __init__(self, model: str = "default-model"):
        self.model = model
    
    def ask(self, prompt: str, context: Dict[str, Any] = None) -> str:
        # Implement your provider's API call
        pass
```

### 2. Register Provider
```python
# In LLMEngine.__init__
elif provider == "myprovider":
    self.provider = MyLLMProvider(model or "default-model")
```

### 3. Add Tests and Documentation

## Code Review Process

### What We Look For
- **Functionality**: Does it work as intended?
- **Tests**: Are there adequate tests?
- **Documentation**: Is it well documented?
- **Style**: Does it follow our coding standards?
- **Performance**: Is it efficient?
- **Security**: Are there any security concerns?

### Review Timeline
- Initial review within 2-3 days
- Follow-up reviews within 1-2 days
- Merge after approval and CI passes

## Release Process

### Versioning
We follow semantic versioning (SemVer):
- **Major**: Breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, backward compatible

### Release Steps
1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release PR
4. Tag release after merge
5. Publish to PyPI

## Getting Help

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Request Comments**: Code-specific discussions

### Mentorship
- New contributors are welcome
- Maintainers provide guidance and feedback
- Don't hesitate to ask questions

## Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

## Code of Conduct

We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Please be respectful and inclusive in all interactions.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Incident Helper! Your efforts help make incident response better for everyone. 🚀