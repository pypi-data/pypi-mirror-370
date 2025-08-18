# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v0.3.1 (2025-08-17)

### Fix

- Support all AnyIO 4.5.1+

## v0.3.0 (2025-08-17)

### Feat

- increased compatibility to old AnyIO

### Fix

- Make some code a bit more ergonomic

## v0.2.13 (2025-08-16)

### Fix

- Less Claudified documentation

## v0.2.12 (2025-08-16)

### Fix

- Remove conventional commits from pre-commit hooks
- Update Readme
- preserve formatting
- Make markdownlint less aggressive about trailing whitespace (preserves formatting)
- formatting

## v0.2.11 (2025-08-16)

### Fix

- cleaned up changelog

## v0.2.10 (2025-08-16)

### Fix

- Added & cleaned up examples

## v0.2.9 (2025-08-16)

### Fix

- ruff reformatting

## v0.2.8 (2025-08-16)

### Fix

- Reorganize tests and the pyproject.toml
- Complete, correct grammar-based parsing

## v0.2.7 (2025-08-16)

### Fix

- Organize code a bit better
- IMAP able to retrieve messages

## v0.2.6 (2025-08-16)

### Fix

- Fix formatting on README

## v0.2.5 (2025-08-16)

### Fix

- Updated pytest plugins to include pytest-anyio

## v0.2.4 (2025-08-16)

### Fix

- Add deployments to makefile

## v0.2.3 (2025-08-16)

### Fix

- Proper link to changelog

## v0.2.2 (2025-08-16)

### Fix

- Added a Makefile

## v0.2.1 (2025-08-16)

### Fix

- Make uv.lock changes get captured before tagging

## v0.2.0 (2025-08-16)

### Feat

- Added complete IMAP implementation & tests

## v0.1.4 (2025-08-16)

### Fix

- Added some more tests

## v0.1.3 (2025-08-16)

### Fix

- Updates from cleaned up examples

## v0.1.2 (2025-08-15)

### Fix

- Add Commitizen & fix README.md

## [0.1.1] - 2024-08-16

### Added

- **WebSocket Client (RFC 6455)** - Complete implementation
  - Full RFC 6455 WebSocket client with all frame types
  - Proper handshake protocol with validation
  - Message fragmentation support
  - Client frame masking per RFC requirements
  - Ping/pong and close frame handling
  - Graceful connection management
  - Real-server interoperability testing

- **IMAP Client Foundation (RFC 9051)**
  - IMAP4rev2 client foundation with TLS support
  - Command construction for all major IMAP operations
  - Response parsing with RFC 9051 compliance
  - Authentication support (LOGIN, SASL preparation)
  - Mailbox operations (SELECT, LIST, STATUS)
  - Message operations (FETCH, SEARCH, STORE)

- **SMTP Client Foundation (RFC 5321)**
  - SMTP client with EHLO/HELO handshake
  - STARTTLS support for secure connections
  - Authentication (PLAIN, LOGIN methods)
  - Complete message sending with DATA handling
  - Transaction state management
  - Capability detection

- **Core Framework**
  - RFC compliance testing framework
  - Protocol state machines with AnyIO integration
  - Structured concurrency patterns
  - Type-safe interfaces for all protocols
  - URI parsing (RFC 3986)
  - TLS configuration helpers
  - AnyIO stream utilities

- **Testing Infrastructure**
  - Comprehensive interoperability tests
  - RFC compliance validation
  - Real-server testing against echo.websocket.org
  - Unit tests for frame parsing and validation
  - Integration tests for cross-component functionality

- **Documentation**
  - Complete README with usage examples
  - API documentation for all modules
  - Development setup instructions
  - Contributing guidelines

### Technical Details

- **AnyIO-Only Constraint**: All I/O operations use AnyIO exclusively (no asyncio imports)
- **RFC Compliance First**: Every implementation validates against RFC specifications
- **Type Safety**: Full mypy compliance with strict typing
- **Security by Default**: TLS by default, proper certificate validation
- **Production Ready**: Real-world testing and error handling

### Dependencies

- `anyio>=4.0.0` - Structured concurrency and I/O
- `httpx>=0.25.0` - HTTP client (when approved)
- `typing-extensions>=4.0.0` - Enhanced type hints

### Compatibility

- Python 3.11+
- Cross-platform (Windows, macOS, Linux)
- Works with all major WebSocket servers
- Compatible with major IMAP/SMTP servers

[0.1.1]: https://github.com/elgertam/anyrfc/releases/tag/v0.1.1

## v0.1.0 (2025-08-15)

- Initial Commit
