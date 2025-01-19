# Contributing to OmniStack

First off, thank you for considering contributing to OmniStack! It's people like you that make OmniStack such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](../CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots and animated GIFs if possible**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please provide the following information:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and explain the behavior you expected to see instead**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Follow the style guides
* Include appropriate test cases
* Update documentation for significant changes

## Style Guides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* Consider starting the commit message with an applicable emoji:
    * 🎨 `:art:` when improving the format/structure of the code
    * 🐎 `:racehorse:` when improving performance
    * 📝 `:memo:` when writing docs
    * 🐛 `:bug:` when fixing a bug
    * 🔥 `:fire:` when removing code or files
    * 💚 `:green_heart:` when fixing the CI build
    * ✅ `:white_check_mark:` when adding tests
    * 🔒 `:lock:` when dealing with security
    * ⬆️ `:arrow_up:` when upgrading dependencies
    * ⬇️ `:arrow_down:` when downgrading dependencies

### Python Style Guide

We use:
* [Black](https://black.readthedocs.io/) for code formatting
* [isort](https://pycqa.github.io/isort/) for import sorting
* [flake8](https://flake8.pycqa.org/) for style guide enforcement
* [mypy](http://mypy-lang.org/) for static type checking

Example:
```python
from typing import Dict, Optional

import numpy as np
import torch
from pydantic import BaseModel

class AnalysisResult(BaseModel):
    """Result of code analysis."""
    
    quality_score: float
    suggestions: list[Dict[str, str]]
    context: Optional[Dict[str, str]] = None

def analyze_code(
    code: str,
    context: Optional[Dict[str, str]] = None
) -> AnalysisResult:
    """
    Analyze code quality and provide suggestions.
    
    Args:
        code: Source code to analyze
        context: Additional context for analysis
    
    Returns:
        AnalysisResult with quality score and suggestions
    
    Raises:
        ValueError: If code is empty or invalid
    """
    if not code.strip():
        raise ValueError("Code cannot be empty")
        
    # Analysis logic here
    return AnalysisResult(
        quality_score=0.85,
        suggestions=[
            {
                "type": "style",
                "message": "Add function docstring"
            }
        ],
        context=context
    )
```

### Documentation Style Guide

* Use [Google style](https://google.github.io/styleguide/pyguide.html) for docstrings
* Write documentation in Markdown
* Include code examples when relevant
* Keep line length to 80 characters
* Use proper heading hierarchy

Example:
```python
def process_data(
    data: np.ndarray,
    window_size: int = 10
) -> np.ndarray:
    """
    Process time series data using sliding window.
    
    Args:
        data: Input time series data
        window_size: Size of sliding window
    
    Returns:
        Processed data array
    
    Raises:
        ValueError: If window_size is larger than data length
    
    Example:
        >>> data = np.array([1, 2, 3, 4, 5])
        >>> process_data(data, window_size=2)
        array([1.5, 2.5, 3.5, 4.5])
    """
```

## Development Process

1. Fork the repository from [github.com/jvrsoftware/omnistack](https://github.com/jvrsoftware/omnistack)
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes following our guidelines
4. Run tests and ensure they pass
5. Update documentation if needed
6. Commit your changes (`git commit -m 'feat: add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request to the `main` branch

### Setting Up Development Environment

1. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

3. Run tests:
```bash
pytest
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=omnistack tests/

# Run specific test
pytest tests/test_context_analyzer.py -k "test_analyze"
```

### Code Quality Checks

```bash
# Format code
black .

# Sort imports
isort .

# Run linter
flake8 .

# Type checking
mypy .
```

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the documentation with details of changes if needed
3. The PR will be merged once you have the sign-off of two other developers
4. If you can't merge the PR due to lack of permissions, request a reviewer to merge it for you

## Community

* GitHub: [github.com/jvrsoftware/omnistack](https://github.com/jvrsoftware/omnistack)
* Website: [jvrsoftware.co.za](https://jvrsoftware.co.za)
* Email: jvrsoftware@gmail.com or jan@jvrsoftware.co.za

## Recognition

Contributors will be added to our [Contributors](../CONTRIBUTORS.md) list.

## Questions?

* Website: [jvrsoftware.co.za](https://jvrsoftware.co.za)
* Email: jvrsoftware@gmail.com or jan@jvrsoftware.co.za

## License

By contributing, you agree that your contributions will be licensed under the same [MIT License](../LICENSE) that covers the project.
