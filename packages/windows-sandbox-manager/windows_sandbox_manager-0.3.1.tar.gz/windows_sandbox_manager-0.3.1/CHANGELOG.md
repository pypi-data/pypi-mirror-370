# Changelog

All notable changes to Windows Sandbox Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-07-18

### Added
- Initial release of Windows Sandbox Manager
- Async sandbox lifecycle management with state tracking
- Type-safe configuration system using Pydantic
- Comprehensive security validation framework
- Resource monitoring and metrics collection
- CLI interface with rich formatting
- Multi-sandbox management capabilities
- Plugin system foundation
- Comprehensive test suite
- Modern Python packaging with pyproject.toml

### Features
- **Core Engine**: Async sandbox creation, management, and cleanup
- **Configuration**: YAML/JSON configuration with validation
- **Security**: Input validation, path traversal prevention, command injection protection
- **Monitoring**: Resource tracking and health checks
- **CLI**: Rich terminal interface with progress bars and tables
- **Registry**: Persistent sandbox state tracking

### Security
- Zero command injection vulnerabilities through strict validation
- Path traversal prevention for all file operations
- Privilege separation and least access principles
- Comprehensive input sanitization

### Performance
- Async operations for non-blocking sandbox management
- Concurrent sandbox creation with configurable limits
- Resource pooling and efficient cleanup
- Optimized WSB file generation