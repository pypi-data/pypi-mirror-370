# BrowseVersa

[![PyPI version](https://badge.fury.io/py/browseversa.svg)](https://badge.fury.io/py/browseversa)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://github.com/pandiyarajk/browseversa)

A comprehensive Python package to programmatically detect web browser versions on Windows systems. This tool provides native Windows detection without requiring Selenium or WebDrivers, making it perfect for automation scripts, system administration, and CI/CD pipelines on Windows environments.

## Features

- 🔍 **Multi-Browser Support**: Detect Chrome, Firefox, Edge, and Internet Explorer versions
- 🖥️ **Windows Optimized**: Specifically designed for Windows systems
- 🏢 **Enterprise Ready**: Enhanced support for Windows Server 2019/2022 and enterprise deployments
- 🛠️ **Multiple Detection Methods**: Registry queries, executable commands, and folder-based detection
- 📝 **Robust Error Handling**: Comprehensive fallback mechanisms and logging
- 🚀 **Zero Dependencies**: Uses only Python standard library
- 💻 **CLI Interface**: Command-line tool for automation and scripting
- 📦 **Easy Integration**: Simple API for use in Python applications

## Supported Browsers

| Browser | Windows | Notes |
|---------|---------|-------|
| Google Chrome | ✅ | Includes Chromium |
| Mozilla Firefox | ✅ | Includes Firefox ESR |
| Microsoft Edge | ✅ | Includes Beta/Dev/Enterprise |
| Internet Explorer | ✅ | Windows only, deprecated |

## Supported Platforms

- **Windows**: 7, 8, 10, 11, Server 2019/2022

**Note**: This package is designed specifically for Windows systems and will not work on macOS or Linux.

## Installation

### From PyPI (Recommended)

```bash
pip install browseversa
```

### From Source

```bash
git clone https://github.com/pandiyarajk/browseversa.git
cd browseversa
pip install -e .
```

## Quick Start

### Command Line Usage

```bash
# Detect all browsers
browseversa

# Detect specific browser
browseversa --browser chrome

# Get version only (for scripting)
browseversa --browser firefox --version-only

# Check script version
browseversa --script-version

# Enable verbose logging
browseversa --browser all --verbose
```

### Python API Usage

```python
from browseversa import BrowserVersionDetector

# Create detector instance
detector = BrowserVersionDetector()

# Detect specific browser
chrome_version = detector.detect_chrome_version()
print(f"Chrome version: {chrome_version}")

# Detect all browsers
all_browsers = detector.detect_all_browsers()
for browser, info in all_browsers.items():
    if browser != 'platform':
        status = info['version'] if info['detected'] else 'Not found'
        print(f"{browser}: {status}")
```

### Convenience Functions

```python
from browseversa import (
    get_chrome_version,
    get_firefox_version,
    get_edge_version,
    get_ie_version,
    get_all_browser_versions
)

# Quick version checks
chrome_ver = get_chrome_version()
firefox_ver = get_firefox_version()
edge_ver = get_edge_version()
ie_ver = get_ie_version()

# Get all versions at once
all_versions = get_all_browser_versions()
```

## Output Examples

### Standard Output
```
Browser Version Detection Results:
========================================
✓ Chrome: 120.0.6099.109
✓ Firefox: 120.0
✗ Edge: Not found
✗ Ie: Not found

Platform: win32
```

### Version-Only Output (for scripting)
```
chrome: 120.0.6099.109
firefox: 120.0
edge: Not found
ie: Not found
```

## API Reference

### BrowserVersionDetector Class

The main class for browser version detection.

#### Methods

- `detect_chrome_version()` → `Optional[str]`
- `detect_firefox_version()` → `Optional[str]`
- `detect_edge_version()` → `Optional[str]`
- `detect_ie_version()` → `Optional[str]`
- `detect_all_browsers()` → `Dict[str, Any]`

#### Example

```python
detector = BrowserVersionDetector()

# Individual browser detection
chrome_ver = detector.detect_chrome_version()
if chrome_ver:
    print(f"Chrome {chrome_ver} detected")
else:
    print("Chrome not found")

# All browsers detection
results = detector.detect_all_browsers()
print(f"Platform: {results['platform']}")
for browser, info in results.items():
    if browser != 'platform':
        print(f"{browser}: {info['version'] if info['detected'] else 'Not found'}")
```

### Convenience Functions

- `get_chrome_version()` → `Optional[str]`
- `get_firefox_version()` → `Optional[str]`
- `get_edge_version()` → `Optional[str]`
- `get_ie_version()` → `Optional[str]`
- `get_all_browser_versions()` → `Dict[str, Any]`

## Use Cases

### System Administration
```python
# Check browser versions across multiple systems
from browseversa import get_all_browser_versions

def check_system_browsers():
    browsers = get_all_browser_versions()
    detected = [b for b, info in browsers.items() 
                if b != 'platform' and info['detected']]
    return detected
```

### CI/CD Pipelines
```bash
# Check if required browser is available
if browseversa --browser chrome --version-only | grep -q "Not found"; then
    echo "Chrome not found, installing..."
    # Install Chrome
fi
```

### Automation Scripts
```python
# Ensure compatible browser versions
from browseversa import get_chrome_version

def check_chrome_compatibility():
    version = get_chrome_version()
    if not version:
        raise RuntimeError("Chrome not installed")
    
    major_version = int(version.split('.')[0])
    if major_version < 90:
        raise RuntimeError(f"Chrome version {version} is too old. Need 90+")
    
    return version
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/pandiyarajk/browseversa.git
cd browseversa
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black browseversa.py
flake8 browseversa.py
mypy browseversa.py
```

### Building Package

```bash
python -m build
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Pandiyaraj Karuppasamy** - [pandiyarajk@live.com](mailto:pandiyarajk@live.com)

## Acknowledgments

- Thanks to the Python community for excellent tooling
- Inspired by the need for reliable browser version detection in automation workflows
- Built with enterprise environments in mind

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

## Support

- 📧 Email: [pandiyarajk@live.com](mailto:pandiyarajk@live.com)
- 🐛 Issues: [GitHub Issues](https://github.com/pandiyarajk/browseversa/issues)
- 📖 Documentation: [GitHub README](https://github.com/pandiyarajk/browseversa#readme)

---

**Note**: Internet Explorer has been deprecated by Microsoft and may not be available on newer Windows versions. This tool includes IE detection for legacy system support.
