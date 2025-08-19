# Development Instructions for llama-search Python SDK

## Project Overview

This is a Python SDK for the llama-search.com API that allows developers to easily integrate llama-search functionality into their Python applications.

## Current Status

✅ **Completed:**
- Basic project structure with `pyproject.toml`
- Core package structure (`llama_search/`)
- Main client class (`LlamaSearchClient`)
- Custom exceptions
- Basic README with usage examples

## Next Steps for Development

### Phase 1: Core Functionality
1. **API Endpoint Implementation**
   - Implement all available llama-search.com API endpoints
   - Add proper request/response models
   - Implement pagination support
   - Add filtering and sorting options

2. **Enhanced Client Features**
   - Add async client support (`aiohttp`)
   - Implement retry logic with exponential backoff
   - Add request/response logging
   - Implement rate limiting

3. **Data Models**
   - Create Pydantic models for API responses
   - Add type hints throughout the codebase
   - Implement proper serialization/deserialization

### Phase 2: Testing & Quality
1. **Testing Framework**
   - Set up pytest with fixtures
   - Add unit tests for all client methods
   - Add integration tests (with API mocking)
   - Add property-based testing with Hypothesis
   - Set up test coverage reporting

2. **Code Quality**
   - Set up pre-commit hooks
   - Configure Black for code formatting
   - Set up flake8/ruff for linting
   - Add mypy for type checking
   - Set up GitHub Actions CI/CD

### Phase 3: Documentation & Examples
1. **Documentation**
   - Set up Sphinx documentation
   - Add API reference documentation
   - Create user guide with examples
   - Add troubleshooting guide

2. **Examples**
   - Create example scripts for common use cases
   - Add Jupyter notebook examples
   - Create CLI tool examples

### Phase 4: Advanced Features
1. **Advanced Client Features**
   - Implement caching mechanisms
   - Add bulk operations support
   - Implement streaming responses
   - Add webhook support if available

2. **Integration Features**
   - Create Django integration package
   - Create Flask integration package
   - Add FastAPI examples

## Development Setup

### Prerequisites
- Python 3.8+
- pip or poetry for dependency management

### Local Development
```bash
# Clone the repository
git clone <repository-url>
cd llama-search

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 llama_search/
black --check llama_search/
mypy llama_search/
```

### Publishing to PyPI

#### Test PyPI (for testing)
```bash
# Build the package
python -m build

# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ llama-search
```

#### Production PyPI
```bash
# Build the package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## File Structure
```
llama-search/
├── llama_search/
│   ├── __init__.py
│   ├── client.py
│   ├── exceptions.py
│   ├── models.py          # (to be created)
│   ├── async_client.py    # (to be created)
│   └── utils.py           # (to be created)
├── tests/
│   ├── __init__.py        # (to be created)
│   ├── test_client.py     # (to be created)
│   └── test_models.py     # (to be created)
├── examples/
│   ├── basic_usage.py     # (to be created)
│   └── advanced_usage.py  # (to be created)
├── docs/                  # (to be created)
├── pyproject.toml
├── README.md
├── LICENSE
└── instructions.md
```

## Contributing Guidelines

1. **Code Style**: Follow PEP 8, use Black for formatting
2. **Type Hints**: Add type hints to all public APIs
3. **Documentation**: Document all public methods and classes
4. **Testing**: Write tests for all new functionality
5. **Commit Messages**: Use conventional commit format

## API Key Management

For development and testing:
- Store API keys in environment variables
- Never commit API keys to version control
- Use `.env` files for local development (add to `.gitignore`)

## Release Process

1. Update version in `pyproject.toml` and `__init__.py`
2. Update CHANGELOG.md
3. Create a git tag for the version
4. Build and upload to PyPI
5. Create GitHub release with release notes

## Known Issues & TODOs

- [ ] Need to verify actual llama-search.com API endpoints
- [ ] Add proper error handling for network timeouts
- [ ] Implement proper logging configuration
- [ ] Add configuration file support
- [ ] Add CLI interface for common operations