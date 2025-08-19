# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is an open-source Python SDK for the Dolfi API, designed to simplify integration with Dolfi's search and web scraping services. The SDK will be distributed on PyPI as `dolfi-python-sdk`.

## Development Commands

### Package Installation & Setup
```bash
# Install package in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Install from requirements.txt (for current environment)
pip install -r requirements.txt
```

### Testing
```bash
# Run basic test
python tests/basic.py

# Run tests with pytest (if available)
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/basic.py -v
```

### Code Quality & Formatting
```bash
# Format code with black (if installed)
python -m black dolfi_sdk/ tests/ examples/

# Sort imports with isort (if installed)  
python -m isort dolfi_sdk/ tests/ examples/

# Type checking with mypy (if installed)
python -m mypy dolfi_sdk/

# Linting with flake8 (if installed)
python -m flake8 dolfi_sdk/ tests/ examples/
```

### Examples & Testing
```bash
# Run basic usage example
python examples/basic_usage.py

# Run async example
python examples/async_usage.py

# Quick test with basic.py
python tests/basic.py
```

### Package Building & Distribution
```bash
# Build package
python setup.py sdist bdist_wheel

# Upload to PyPI (requires twine)
python -m twine upload dist/*
```

## Architecture Overview

### Core SDK Structure
The SDK follows a dual-client pattern with both synchronous and asynchronous implementations:

- **`DolfiClient`** (`client.py`): Synchronous client using `requests`
- **`AsyncDolfiClient`** (`async_client.py`): Asynchronous client using `aiohttp`
- **Data Models** (`models.py`): Dataclass-based request/response models with type validation
- **Exception Hierarchy** (`exceptions.py`): Structured error handling for different failure modes

### API Integration Pattern
Both clients implement the same interface:
1. **Authentication**: API key via `x-api-key` header or `DOLFI_API_KEY` environment variable
2. **Request Validation**: Dataclass models validate parameters before API calls
3. **Response Building**: Raw API responses are converted to structured dataclass objects
4. **Error Mapping**: HTTP status codes map to specific exception types

### Data Flow
```
User Input → Request Model → HTTP Client → API Response → Response Model → User
```

### Key Components

#### Authentication & Configuration
- API key can be passed directly or via `DOLFI_API_KEY` environment variable
- Base URL configurable (default: production API endpoint in `constants.py`)
- Timeout configurable per client instance

#### Request/Response Models (`models.py`)
- Uses dataclasses with type hints for validation
- Automatic UUID generation for response IDs
- Language code constants for supported languages (20+ languages)
- Separate models for search and scrape operations

#### Error Handling Strategy
- **`DolfiAuthenticationError`**: 401 Unauthorized (invalid API key)
- **`DolfiValidationError`**: 422 Validation Error (invalid request parameters)  
- **`DolfiAPIError`**: Other HTTP errors from API
- **`DolfiConnectionError`**: Network connection failures
- **`DolfiTimeoutError`**: Request timeout failures

### Context Managers
Both clients support context manager pattern for proper resource cleanup:
```python
with DolfiClient(api_key="...") as client:
    # Use client
# Session automatically closed
```

## Development Notes

### API Endpoint Configuration
- Production API endpoint defined in `dolfi_sdk/constants.py`
- Base URL is configurable per client instance for testing/enterprise deployments

### Model Validation
- Request models use dataclass validation (not Pydantic despite setup.py dependency)
- Response models are built manually from API responses for flexibility
- Language codes are strictly typed using Literal types

### Async Implementation
- AsyncDolfiClient mirrors DolfiClient interface but with async/await
- Uses aiohttp for HTTP requests
- Supports context manager for proper session cleanup

### Testing Strategy
- `tests/basic.py` provides simple integration testing
- Examples in `examples/` directory demonstrate real usage patterns
- Development dependencies in setup.py include pytest, coverage, and linting tools