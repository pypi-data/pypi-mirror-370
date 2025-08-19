# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-20

### Added
- Initial release of Dolfi Python SDK
- Synchronous client (`DolfiClient`) for Dolfi API
- Asynchronous client (`AsyncDolfiClient`) for Dolfi API
- Complete type hints using dataclass models
- Support for search endpoint with AI-powered answers
- Support for scrape endpoint with content extraction
- Comprehensive error handling with custom exceptions
- Multi-language support (20+ languages)
- Context manager support for both clients
- Environment variable support for API key configuration
- Configurable base URL and timeout settings
- Full documentation and examples

### Features
- **Search API**: Natural language web search with AI-generated summaries
- **Scrape API**: Extract content from web pages in markdown or text format
- **Type Safety**: Full type hints and validation
- **Error Handling**: Structured exceptions for different error scenarios
- **Async Support**: Both sync and async implementations
- **Multi-language**: Support for search and answers in 20+ languages

### Dependencies
- `requests >= 2.25.0` for synchronous HTTP requests
- `aiohttp >= 3.8.0` for asynchronous HTTP requests
- `pydantic >= 2.0.0` for data validation
- Python 3.8+ support

### Documentation
- Comprehensive README with examples
- API reference documentation
- Usage examples for both sync and async clients
- Error handling examples