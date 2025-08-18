# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Additional browser support
- Enhanced detection methods
- Performance improvements

## [1.0.0] - 2025-06-22

### Added
- **Initial Release**: First public release of browseversa package
- **Multi-Browser Support**: Detect Chrome, Firefox, Edge, and Internet Explorer versions
- **Windows Optimized**: Specifically designed for Windows systems
- **Multiple Detection Methods**:
  - Registry-based detection for Windows
  - Executable-based detection for Windows
  - Folder-based detection for Chrome and Edge
- **Enterprise Support**: Enhanced Windows Server 2019/2022 and enterprise deployment detection
- **Command-Line Interface**: User-friendly CLI with multiple output formats
  - Standard output with detection status
  - Version-only output for scripting/automation
  - Verbose logging option
- **Python API**: Comprehensive class-based API with convenience functions
- **Robust Error Handling**: Comprehensive fallback mechanisms and logging
- **Zero Dependencies**: Uses only Python standard library modules
- **Package Structure**: Complete Python package setup for PyPI publication
  - setup.py and pyproject.toml configuration
  - Comprehensive documentation and README
  - MIT License
  - Development tools configuration
  - Test suite with pytest

### Supported Browsers
- **Google Chrome**: Including Chromium variants
- **Mozilla Firefox**: Including Firefox ESR (Extended Support Release)
- **Microsoft Edge**: Including Beta, Dev, and Enterprise versions
- **Internet Explorer**: Windows only (deprecated by Microsoft)

### Supported Platforms
- **Windows**: 7, 8, 10, 11, Server 2019/2022

**Note**: This package is designed specifically for Windows systems and will not work on macOS or Linux.

### Features
- Native Windows detection without requiring Selenium or WebDrivers
- Multiple detection strategies for maximum Windows compatibility
- Clean and maintainable code structure with comprehensive documentation
- Type hints and proper error handling
- Suitable for automation scripts, system administration, and CI/CD pipelines on Windows

### Changed
- Improved registry detection methods
- Enhanced folder-based version detection
- Better executable path handling
- More robust version extraction patterns
- Refactored code structure for better maintainability
- Enhanced documentation and type hints

### Fixed
- Fixed version detection on Windows Server environments
- Improved handling of user vs system installations
- Better fallback mechanisms for detection failures 