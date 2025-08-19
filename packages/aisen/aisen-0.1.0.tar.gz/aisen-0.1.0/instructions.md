# Development Instructions for aisen Python SDK

## Project Overview

This is a Python SDK for the aisen.vn API - Vietnam's AI platform. The SDK allows developers to easily integrate aisen.vn's AI capabilities into their Python applications, with special optimization for Vietnamese language processing.

## Current Status

✅ **Completed:**
- Basic project structure with `pyproject.toml`
- Core package structure (`aisen/`)
- Main client class (`AisenClient`)
- Custom exceptions
- Basic README with usage examples and Vietnamese language support

## Next Steps for Development

### Phase 1: Core Functionality
1. **API Endpoint Implementation**
   - Implement all available aisen.vn API endpoints
   - Add proper request/response models
   - Implement streaming responses for real-time chat
   - Add support for file uploads (images, documents)
   - Implement Vietnamese-specific model parameters

2. **Enhanced Client Features**
   - Add async client support (`aiohttp`)
   - Implement retry logic with exponential backoff
   - Add request/response logging
   - Implement rate limiting
   - Add support for Vietnamese tokenization

3. **Data Models**
   - Create Pydantic models for API responses
   - Add type hints throughout the codebase
   - Implement proper serialization/deserialization
   - Add Vietnamese text preprocessing utilities

### Phase 2: Vietnamese Language Features
1. **Language-Specific Features**
   - Vietnamese text preprocessing utilities
   - Support for Vietnamese diacritics handling
   - Vietnamese language detection
   - Vietnamese-specific prompt templates

2. **Cultural Context**
   - Vietnamese holiday and cultural context awareness
   - Vietnamese name and address handling
   - Support for Vietnamese date/time formats

### Phase 3: Testing & Quality
1. **Testing Framework**
   - Set up pytest with fixtures
   - Add unit tests for all client methods
   - Add integration tests (with API mocking)
   - Add Vietnamese language-specific tests
   - Set up test coverage reporting

2. **Code Quality**
   - Set up pre-commit hooks
   - Configure Black for code formatting
   - Set up flake8/ruff for linting
   - Add mypy for type checking
   - Set up GitHub Actions CI/CD

### Phase 4: Documentation & Examples
1. **Documentation**
   - Set up Sphinx documentation
   - Add API reference documentation
   - Create user guide with Vietnamese examples
   - Add troubleshooting guide

2. **Examples**
   - Create example scripts for Vietnamese NLP tasks
   - Add Jupyter notebook examples
   - Create CLI tool examples
   - Vietnamese chatbot example
   - Vietnamese text summarization example

### Phase 5: Advanced Features
1. **Advanced Client Features**
   - Implement caching mechanisms
   - Add bulk operations support
   - Implement streaming responses
   - Add webhook support if available

2. **Integration Features**
   - Create Django integration package
   - Create Flask integration package
   - Add FastAPI examples
   - Vietnamese web framework examples

## Development Setup

### Prerequisites
- Python 3.8+
- pip or poetry/uv for dependency management

### Local Development
```bash
# Clone the repository
git clone <repository-url>
cd aisen

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 aisen/
black --check aisen/
mypy aisen/
```

### Publishing to PyPI

#### Test PyPI (for testing)
```bash
# Build the package
uv build

# Upload to Test PyPI
uv publish --publish-url https://test.pypi.org/legacy/

# Test installation
pip install --index-url https://test.pypi.org/simple/ aisen
```

#### Production PyPI
```bash
# Build the package
uv build

# Upload to PyPI
uv publish
```

## File Structure
```
aisen/
├── aisen/
│   ├── __init__.py
│   ├── client.py
│   ├── exceptions.py
│   ├── models.py          # (to be created)
│   ├── async_client.py    # (to be created)
│   ├── utils.py           # (to be created)
│   └── vietnamese/        # (to be created)
│       ├── __init__.py
│       ├── preprocessor.py
│       └── templates.py
├── tests/
│   ├── __init__.py        # (to be created)
│   ├── test_client.py     # (to be created)
│   ├── test_models.py     # (to be created)
│   └── test_vietnamese.py # (to be created)
├── examples/
│   ├── basic_usage.py     # (to be created)
│   ├── vietnamese_chat.py # (to be created)
│   └── vietnamese_nlp.py  # (to be created)
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
5. **Vietnamese Support**: Ensure proper handling of Vietnamese text
6. **Commit Messages**: Use conventional commit format

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

## Vietnamese Language Considerations

1. **Text Encoding**: Ensure proper UTF-8 handling for Vietnamese characters
2. **Diacritics**: Handle Vietnamese tone marks correctly
3. **Tokenization**: Consider Vietnamese word segmentation
4. **Cultural Context**: Be aware of Vietnamese cultural nuances in AI responses

## Known Issues & TODOs

- [ ] Need to verify actual aisen.vn API endpoints
- [ ] Add proper error handling for network timeouts
- [ ] Implement proper logging configuration
- [ ] Add configuration file support
- [ ] Add CLI interface for common operations
- [ ] Implement Vietnamese text preprocessing
- [ ] Add support for Vietnamese-specific models
- [ ] Create Vietnamese prompt templates