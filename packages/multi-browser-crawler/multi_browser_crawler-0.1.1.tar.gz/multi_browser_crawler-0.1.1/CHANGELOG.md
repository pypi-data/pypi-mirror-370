# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of multi-browser-crawler package
- Comprehensive browser automation with Playwright
- Advanced session management with isolation
- Proxy rotation and management
- API discovery and network monitoring
- JavaScript execution capabilities
- Image download and processing
- Concurrent crawling support
- Spider-MCP compatibility adapter
- Comprehensive test suite
- Type hints and py.typed support

### Features
- **BrowserCrawler**: Main API for browser automation
- **SessionManager**: Browser session lifecycle management
- **ProxyManager**: File-based proxy rotation with health monitoring
- **API Discovery**: Network sniffing and API call capture
- **Image Processing**: Bulk image download with format conversion
- **Error Handling**: Robust error recovery and fallback mechanisms
- **Caching**: HTML content caching with configurable TTL
- **Stealth Mode**: Anti-detection techniques for bot avoidance

### Technical
- Modern Python packaging with pyproject.toml
- Comprehensive type annotations
- Async/await throughout
- Configurable logging
- Memory-efficient resource management
- Cross-platform compatibility (Windows, macOS, Linux)

## [0.1.0] - 2024-01-XX

### Added
- Initial package structure
- Core browser automation functionality
- Session management system
- Proxy rotation capabilities
- API discovery features
- Comprehensive test suite
- Documentation and examples
- Spider-MCP adapter for backward compatibility

### Dependencies
- playwright>=1.40.0
- aiohttp>=3.8.0
- beautifulsoup4>=4.12.0
- psutil>=5.9.0
- lxml>=4.9.0
- html5lib>=1.1

### Development
- pytest test suite with integration tests
- Black code formatting
- MyPy type checking
- Pre-commit hooks
- GitHub Actions CI/CD (planned)
- Documentation with Sphinx (planned)
