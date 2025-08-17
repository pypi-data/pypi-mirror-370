# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet

### Changed
- Nothing yet

### Deprecated
- Nothing yet

### Removed
- Nothing yet

### Fixed
- Nothing yet

### Security
- Nothing yet

## [0.1.0] - 2025-08-17

### Added
- Initial release of mhz14a library
- MHZ14A sensor class with full protocol support
- Command-line interface with all sensor operations
- Support for CO₂ reading, calibration, ABC, and range setting
- Comprehensive error handling with retry logic
- Type annotations and mypy strict compliance
- Extensive test suite with mocked hardware tests
- Documentation and usage examples
- GitHub Actions CI/CD pipeline
- PyPI Trusted Publishing setup
- udev rules for Raspberry Pi integration

### Features
- **Sensor Operations**: read_co2(), zero_calibrate(), span_calibrate(), set_abc(), set_range()
- **CLI Commands**: read, sample, zero, span, abc, range
- **Robust Communication**: Automatic retry, checksum validation, timeout handling
- **Multiple Ranges**: Support for 2000, 5000, and 10000 ppm ranges
- **JSON Output**: Machine-readable sample output format
- **Context Manager**: Safe resource management with automatic cleanup
- **Pure Python**: Universal wheel compatibility, minimal dependencies

[Unreleased]: https://github.com/oaslananka/mhz14a/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/oaslananka/mhz14a/releases/tag/v0.1.0
