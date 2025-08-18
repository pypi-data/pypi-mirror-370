# Dependency Architecture

## Overview

The AnyRFC library uses a clean dependency architecture that separates core library requirements from development tooling, following best practices for Python library distribution.

## Architecture Principles

### 1. Minimal Core Dependencies ✅
The published library has only essential runtime dependencies:
```toml
dependencies = [
    "anyio>=4.0.0",         # Async I/O framework
    "httpx>=0.25.0",        # HTTP client
    "typing-extensions>=4.0.0",  # Type hints backport
]
```

### 2. Reserved Optional Dependencies 🎯
The `[project.optional-dependencies]` section is kept **completely empty** and reserved for future library features that clients might want to install:
```toml
# Reserved for future library features like:
# [project.optional-dependencies]
# cli = ["click>=8.0.0", "rich>=12.0.0"]  # Future CLI client
# gui = ["tkinter-extras>=1.0.0"]         # Future GUI client
# crypto = ["cryptography>=40.0.0"]       # Future encryption features
```

This keeps the client-facing API clean and prevents development tooling from cluttering the namespace.

### 3. Development Dependencies via UV Groups 🛠️
All development, testing, and example dependencies are organized in UV dependency groups:

```toml
[dependency-groups]
dev = [
    "pytest>=7.0.0",           # Testing framework
    "mypy>=1.0.0",             # Type checking
    "ruff>=0.1.0",             # Linting and formatting
    "coverage>=7.0.0",         # Test coverage
    "autobahntestsuite>=0.8.2", # WebSocket compliance
    "commitizen>=4.8.3",       # Conventional commits
    "twine>=6.1.0",            # Package publishing
]
notebook = [
    "jupyter>=1.0.0",          # Interactive notebooks
    "ipykernel>=6.0.0",        # Jupyter kernel
    "matplotlib>=3.7.0",       # Plotting
    "pandas>=2.0.0",           # Data analysis
]
examples = [
    "python-dotenv>=1.1.1",    # Environment variables
]
```

## Usage Patterns

### Library Users (Minimal Install)
```bash
pip install anyrfc
# Only installs: anyio, httpx, typing-extensions
```

### Developers (Testing & Development)
```bash
uv sync --group dev
# Installs: pytest, mypy, ruff, coverage, testing tools
```

### Example Users (Running Examples)
```bash
uv sync --group examples
# Installs: python-dotenv for .env file support
```

### Data Scientists (Analysis)
```bash
uv sync --group notebook
# Installs: jupyter, pandas, matplotlib for analysis
```

### Full Development Setup
```bash
uv sync --group dev --group examples --group notebook
# Installs everything for comprehensive development
```

## Benefits

### For Library Users 📦
- **Minimal dependencies**: Only 3 essential packages
- **Fast installation**: No unnecessary development tools
- **Clean namespace**: Optional dependencies reserved for actual features
- **Future-proof**: Can add features without breaking existing installs

### For Developers 🚀
- **Organized tooling**: Clear separation of development tools
- **Flexible setup**: Install only what you need
- **No pollution**: Dev tools don't affect library API
- **Standard compliance**: Uses Python packaging standards

### For Future Features 🔮
- **Reserved namespace**: Optional dependencies available for new features
- **Clean API**: Clients can opt into features cleanly
- **No confusion**: Dev tools won't appear as installable features

## Examples

### Core Library Only
```python
# Works with just: pip install anyrfc
from anyrfc.email.imap import IMAPClient
from anyrfc.websocket import WebSocketClient
from anyrfc.parsing import IMAPParser

# All core functionality available
parser = IMAPParser()
# ... use the library
```

### Example with Environment Variables
```bash
# Needs: uv sync --group examples
# Or add python-dotenv manually for examples
```

### Future CLI Tool (Hypothetical)
```bash
# Future: pip install anyrfc[cli]
# Would install click, rich, etc. for CLI features
```

This architecture ensures the library remains lightweight for users while providing comprehensive tooling for developers and clear pathways for future enhancements.