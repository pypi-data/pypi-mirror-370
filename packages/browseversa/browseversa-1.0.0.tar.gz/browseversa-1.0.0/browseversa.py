#!/usr/bin/env python3
"""
BrowseVersa - A Comprehensive Web Browser Version Detection Tool for Windows

A robust Python package to programmatically detect the version of web browsers
(Chrome, Firefox, Edge, Internet Explorer) installed on Windows systems. 
Optimized for Windows, Windows Server 2019/2022, and enterprise deployments.

Features:
- Native Windows detection without requiring Selenium or WebDrivers
- Multiple detection methods (registry, executable, folder-based)
- Robust error handling and fallback mechanisms
- Support for various browser installation paths
- Windows Server 2019/2022 enterprise deployment support
- Clean and maintainable code structure
- Command-line interface for automation and scripting
- Windows-specific optimizations

Requirements:
- Python 3.6+
- Windows operating system
- No external dependencies (uses standard library only)

Author: Pandiyaraj Karuppasamy
License: MIT
Version: 1.0.0

Usage Examples:
    # As a Python module
    from browseversa import BrowserVersionDetector
    
    detector = BrowserVersionDetector()
    chrome_version = detector.detect_chrome_version()
    print(f"Chrome version: {chrome_version}")
    
    # Get all browser versions
    all_browsers = detector.detect_all_browsers()
    for browser, info in all_browsers.items():
        if browser != 'platform':
            print(f"{browser}: {info['version'] if info['detected'] else 'Not found'}")
    
    # Command-line usage
    # python browseversa.py --browser chrome
    # python browseversa.py --browser all --version-only
    # python browseversa.py --script-version

Output Formats:
    - Standard output: Shows browser names and versions with detection status
    - Version-only output: Simple "browser: version" format for scripting
    - All browsers: Lists all detected browsers with their versions

Supported Browsers:
    - Google Chrome (including Chromium)
    - Mozilla Firefox (including Firefox ESR)
    - Microsoft Edge (including Beta/Dev/Enterprise)
    - Internet Explorer (Windows only, deprecated)

Supported Platforms:
    - Windows (7, 8, 10, 11, Server 2019/2022)

Note: This package is designed specifically for Windows systems and will not work on macOS or Linux.
"""

__version__ = "1.0.0"
__author__ = "Pandiyaraj Karuppasamy"
__email__ = "pandiyarajk@live.com"
__license__ = "MIT"
__url__ = "https://github.com/pandiyarajk/browseversa"

import os
import re
import subprocess
import logging
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BrowserVersionDetector:
    """
    A comprehensive class to detect web browser versions across different operating systems.
    
    This class provides methods to detect the version of major web browsers
    (Chrome, Firefox, Edge, Internet Explorer) installed on the system.
    It uses multiple detection strategies including registry queries, executable
    version commands, and folder-based detection to ensure maximum compatibility.
    
    Attributes:
        platform (str): The current operating system platform
        browsers (dict): Dictionary to store detected browser information
        windows_version (str): Windows version information (Windows only)
    
    Example:
        >>> detector = BrowserVersionDetector()
        >>> chrome_version = detector.detect_chrome_version()
        >>> print(f"Chrome version: {chrome_version}")
        Chrome version: 120.0.6099.109
    """
    
    def __init__(self):
        """Initialize the BrowserVersionDetector with platform detection."""
        self.platform = sys.platform
        self.browsers = {}
        self.windows_version = self._get_windows_version()
        
    def _get_windows_version(self) -> Optional[str]:
        """
        Get Windows version information for enhanced detection.
        
        Returns:
            Optional[str]: Windows version string or None if not Windows
        """
        if self.platform != "win32":
            return None
            
        try:
            # Get Windows version using systeminfo
            result = subprocess.run(
                ['systeminfo', '/fo', 'csv'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Look for OS Name and Version
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'OS Name' in line or 'OS Version' in line:
                        logger.debug(f"Windows Info: {line.strip()}")
                        
            # Alternative method using registry
            result = subprocess.run(
                'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion" /v ProductName',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                if 'Windows Server' in result.stdout:
                    logger.info("Detected Windows Server environment")
                    return "Windows Server"
                    
        except Exception as e:
            logger.debug(f"Failed to get Windows version: {e}")
            
        return "Windows"
    
    def _extract_version_from_registry(self, output: str) -> Optional[str]:
        """
        Extract browser version from Windows registry output.
        
        Args:
            output: Registry query output string
            
        Returns:
            Browser version string or None if not found
        """
        try:
            # Look for DisplayVersion in registry output
            if 'DisplayVersion' in output:
                # Use regex to extract version more reliably
                version_pattern = r'DisplayVersion\s+REG_SZ\s+(\d+\.\d+(?:\.\d+)?(?:\.\d+)?)'
                match = re.search(version_pattern, output)
                if match:
                    return match.group(1)
                    
            # Fallback method for older registry formats
            if 'DisplayVersion    REG_SZ' in output:
                start_idx = output.rindex('DisplayVersion    REG_SZ') + 24
                version = ''
                for char in output[start_idx:]:
                    if char == '\n':
                        break
                    version += char
                return version.strip()
                
        except (TypeError, ValueError, IndexError) as e:
            logger.debug(f"Failed to extract version from registry: {e}")
            
        return None
    
    def _extract_ie_version_from_registry(self, output: str) -> Optional[str]:
        """
        Extract Internet Explorer version from Windows registry output.
        
        Args:
            output: Registry query output string
            
        Returns:
            IE version string or None if not found
        """
        try:
            # Try multiple IE version patterns
            version_patterns = [
                r'Version\s+REG_SZ\s+(\d+\.\d+\.\d+\.\d+)',
                r'Version\s+REG_SZ\s+(\d+\.\d+\.\d+)',
                r'svcVersion\s+REG_SZ\s+(\d+\.\d+\.\d+\.\d+)',
                r'svcVersion\s+REG_SZ\s+(\d+\.\d+\.\d+)',
                r'Version Vector\s+REG_SZ\s+(\d+\.\d+\.\d+\.\d+)',
                r'Version Vector\s+REG_SZ\s+(\d+\.\d+\.\d+)'
            ]
            
            for pattern in version_patterns:
                match = re.search(pattern, output)
                if match:
                    return match.group(1)
                    
        except (TypeError, ValueError, IndexError) as e:
            logger.debug(f"Failed to extract IE version from registry: {e}")
            
        return None
    
    def _get_chrome_paths(self) -> List[str]:
        """
        Get possible Chrome installation paths for the current platform.
        
        Chrome can be installed in various locations depending on the platform
        and installation method (user vs system installation).
        
        Returns:
            List[str]: List of possible Chrome installation paths
            
        Note:
            - Windows: Checks both Program Files and user AppData locations
            - macOS: Checks Applications folder
            - Linux: Checks common Linux installation paths
        """
        if self.platform == "win32":
            return [
                # Standard system installation paths (64-bit and 32-bit)
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                # User installation paths (per-user installations)
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
                os.path.expanduser(r"~\AppData\Local\Google\Chrome Beta\Application\chrome.exe"),
                # Windows Server specific paths (duplicate for clarity)
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                # Server user paths (additional user profile locations)
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
                os.path.expanduser(r"~\AppData\Roaming\Google\Chrome\Application\chrome.exe")
            ]
        elif self.platform == "darwin":
            return [
                # macOS Chrome installation paths
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium"
            ]
        elif self.platform in ["linux", "linux2"]:
            return [
                # Linux Chrome installation paths (various package managers)
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
                "/snap/bin/google-chrome",  # Snap package
                "/opt/google/chrome/chrome"  # Manual installation
            ]
        return []
    
    def _get_firefox_paths(self) -> List[str]:
        """
        Get possible Firefox installation paths for the current platform.
        
        Firefox can be installed in various locations including standard
        installations and enterprise deployments (ESR).
        
        Returns:
            List[str]: List of possible Firefox installation paths
            
        Note:
            - Windows: Includes both standard Firefox and Firefox ESR
            - macOS: Includes regular, Developer Edition, and Nightly builds
            - Linux: Includes both standard and ESR versions
        """
        if self.platform == "win32":
            return [
                # Standard Firefox installation paths
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                # User installation paths
                os.path.expanduser(r"~\AppData\Local\Mozilla Firefox\firefox.exe"),
                os.path.expanduser(r"~\AppData\Local\Programs\Mozilla Firefox\firefox.exe"),
                # Windows Server specific paths (duplicate for clarity)
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                # Server user paths (additional user profile locations)
                os.path.expanduser(r"~\AppData\Local\Mozilla Firefox\firefox.exe"),
                os.path.expanduser(r"~\AppData\Roaming\Mozilla Firefox\firefox.exe"),
                # Enterprise/Server installations (Firefox ESR)
                r"C:\Program Files\Mozilla Firefox ESR\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox ESR\firefox.exe"
            ]
        elif self.platform == "darwin":
            return [
                # macOS Firefox installation paths
                "/Applications/Firefox.app/Contents/MacOS/firefox",
                "/Applications/Firefox Developer Edition.app/Contents/MacOS/firefox",
                "/Applications/Firefox Nightly.app/Contents/MacOS/firefox"
            ]
        elif self.platform in ["linux", "linux2"]:
            return [
                # Linux Firefox installation paths
                "/usr/bin/firefox",
                "/usr/bin/firefox-esr",  # Extended Support Release
                "/snap/bin/firefox",     # Snap package
                "/opt/firefox/firefox",  # Manual installation
                "/usr/lib/firefox/firefox",
                "/usr/lib/firefox-esr/firefox"
            ]
        return []
    
    def _get_edge_paths(self) -> List[str]:
        """
        Get possible Edge installation paths for the current platform.
        
        Microsoft Edge can be installed in various locations including
        standard installations, beta/dev versions, and enterprise deployments.
        
        Returns:
            List[str]: List of possible Edge installation paths
            
        Note:
            - Windows: Includes standard, beta, dev, and enterprise versions
            - macOS: Standard macOS application path
            - Linux: Various Linux package manager paths
        """
        if self.platform == "win32":
            return [
                # Standard Edge installation paths
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                # User installation paths
                os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\Application\msedge.exe"),
                # Windows 11 specific paths (EdgeWebView)
                r"C:\Program Files\Microsoft\EdgeWebView\Application\msedge.exe",
                r"C:\Program Files (x86)\Microsoft\EdgeWebView\Application\msedge.exe",
                # Beta and Dev channel installations
                r"C:\Program Files\Microsoft\Edge Beta\Application\msedge.exe",
                r"C:\Program Files (x86)\Microsoft\Edge Beta\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge Dev\Application\msedge.exe",
                r"C:\Program Files (x86)\Microsoft\Edge Dev\Application\msedge.exe",
                # Windows Server specific paths (duplicate for clarity)
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                # Server user paths (additional user profile locations)
                os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\Application\msedge.exe"),
                os.path.expanduser(r"~\AppData\Roaming\Microsoft\Edge\Application\msedge.exe"),
                # Enterprise/Server installations (Edge Enterprise)
                r"C:\Program Files\Microsoft\Edge Enterprise\Application\msedge.exe",
                r"C:\Program Files (x86)\Microsoft\Edge Enterprise\Application\msedge.exe"
            ]
        elif self.platform == "darwin":
            return [
                # macOS Edge installation path
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
            ]
        elif self.platform in ["linux", "linux2"]:
            return [
                # Linux Edge installation paths
                "/usr/bin/microsoft-edge",
                "/usr/bin/microsoft-edge-stable",
                "/opt/microsoft/msedge/microsoft-edge"
            ]
        return []
    
    def _get_ie_paths(self) -> List[str]:
        """
        Get possible Internet Explorer installation paths for the current platform.
        
        Internet Explorer is primarily a Windows browser and has been deprecated
        by Microsoft. This method includes paths for legacy installations.
        
        Returns:
            List[str]: List of possible IE installation paths
            
        Note:
            - Windows only: IE is not available on other platforms
            - Includes legacy Windows NT paths for older installations
            - Duplicate paths for clarity in server environments
        """
        if self.platform == "win32":
            return [
                # Standard IE installation paths
                r"C:\Program Files\Internet Explorer\iexplore.exe",
                r"C:\Program Files (x86)\Internet Explorer\iexplore.exe",
                # Windows 10/11 IE paths (if still available)
                r"C:\Program Files\Windows NT\Accessories\iexplore.exe",
                r"C:\Program Files (x86)\Windows NT\Accessories\iexplore.exe",
                # Windows Server specific paths (duplicate for clarity)
                r"C:\Program Files\Internet Explorer\iexplore.exe",
                r"C:\Program Files (x86)\Internet Explorer\iexplore.exe",
                # Server-specific locations
                r"C:\Program Files\Windows NT\Accessories\iexplore.exe",
                r"C:\Program Files (x86)\Windows NT\Accessories\iexplore.exe",
                # Enterprise/Server installations (duplicate for clarity)
                r"C:\Program Files\Internet Explorer\iexplore.exe",
                r"C:\Program Files (x86)\Internet Explorer\iexplore.exe"
            ]
        # IE is primarily a Windows browser, not available on other platforms
        return []
    
    def _try_executable_version(self, path: str, browser_type: str) -> Optional[str]:
        """
        Try to get browser version by executing the binary.
        
        This method attempts to run the browser executable with the --version flag
        and parses the output to extract version information. It handles different
        output formats for each browser type.
        
        Args:
            path (str): Path to browser executable
            browser_type (str): Type of browser (chrome, firefox, edge, ie)
            
        Returns:
            Optional[str]: Browser version string or None if failed
            
        Note:
            This method uses subprocess.run for security and timeout handling.
            It includes multiple regex patterns to handle various output formats.
        """
        try:
            # Check if file exists and is executable
            if os.path.exists(path) and os.access(path, os.X_OK):
                # Use subprocess instead of os.popen for better security and timeout handling
                result = subprocess.run(
                    [path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10  # 10 second timeout to prevent hanging
                )
                
                if result.returncode == 0:
                    output = result.stdout.strip()
                    
                    if browser_type == "chrome":
                        # Extract Chrome version - try multiple patterns
                        version_patterns = [
                            r'Google Chrome\s+(\d+\.\d+\.\d+\.\d+)',  # Standard format
                            r'Chromium\s+(\d+\.\d+\.\d+\.\d+)'        # Chromium format
                        ]
                        
                        for pattern in version_patterns:
                            match = re.search(pattern, output)
                            if match:
                                return match.group(1)
                            
                    elif browser_type == "firefox":
                        # Extract Firefox version - try multiple patterns
                        version_patterns = [
                            r'Mozilla Firefox\s+(\d+\.\d+(?:\.\d+)?)',  # Standard format
                            r'Firefox\s+(\d+\.\d+(?:\.\d+)?)'           # Short format
                        ]
                        
                        for pattern in version_patterns:
                            match = re.search(pattern, output)
                            if match:
                                return match.group(1)
                            
                    elif browser_type == "edge":
                        # Extract Edge version - try multiple patterns
                        version_patterns = [
                            r'Microsoft Edge\s+(\d+\.\d+\.\d+\.\d+)',  # Standard format
                            r'Microsoft Edge\s+(\d+\.\d+\.\d+)',       # 3-part version
                            r'Edge\s+(\d+\.\d+\.\d+\.\d+)',            # Short format
                            r'Edge\s+(\d+\.\d+\.\d+)',                 # Short 3-part
                            r'(\d+\.\d+\.\d+\.\d+)',                   # Fallback: just version number
                        ]
                        
                        for pattern in version_patterns:
                            match = re.search(pattern, output)
                            if match:
                                return match.group(1)
                        
                    elif browser_type == "ie":
                        # Extract Internet Explorer version - try multiple patterns
                        version_patterns = [
                            r'Internet Explorer\s+(\d+\.\d+\.\d+\.\d+)',  # Standard format
                            r'Internet Explorer\s+(\d+\.\d+\.\d+)',       # 3-part version
                            r'IE\s+(\d+\.\d+\.\d+\.\d+)',                # Short format
                            r'IE\s+(\d+\.\d+\.\d+)',                     # Short 3-part
                            r'(\d+\.\d+\.\d+\.\d+)',                     # Fallback: just version number
                        ]
                        
                        for pattern in version_patterns:
                            match = re.search(pattern, output)
                            if match:
                                return match.group(1)
                            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
            logger.debug(f"Failed to execute {path}: {e}")
            
        return None
    
    def _detect_chrome_windows(self) -> Optional[str]:
        """
        Detect Chrome version on Windows using multiple detection methods.
        
        This method tries several approaches to find Chrome version:
        1. Registry queries for installation information
        2. Folder detection in Program Files
        3. Executable version command
        
        Returns:
            Optional[str]: Chrome version string or None if not found
            
        Note:
            Chrome can be installed via various methods including:
            - Standard installer (Program Files)
            - Per-user installation (AppData)
            - Enterprise deployment (Group Policy)
        """
        # Method 1: Try registry queries for Chrome installation information
        try:
            registry_commands = [
                # Standard uninstall registry keys
                'reg query "HKLM\\SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Google Chrome"',
                'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Google Chrome"',
                # Chrome beacon registry (contains version info)
                'reg query "HKCU\\SOFTWARE\\Google\\Chrome\\BLBeacon"',
                # Windows Server specific keys
                'reg query "HKLM\\SOFTWARE\\Google\\Chrome\\BLBeacon"',
                # Group Policy managed installations
                'reg query "HKLM\\SOFTWARE\\Policies\\Google\\Chrome"',
                # Chrome update client state
                'reg query "HKLM\\SOFTWARE\\Google\\Chrome\\UpdateClientState"',
                # Enterprise deployment keys (specific GUID)
                'reg query "HKLM\\SOFTWARE\\Google\\Chrome\\UpdateClientState\\{8A69D345-D564-463C-AFF1-A69D9E530F96}"',
                'reg query "HKLM\\SOFTWARE\\Wow6432Node\\Google\\Chrome\\UpdateClientState\\{8A69D345-D564-463C-AFF1-A69D9E530F96}"'
            ]
            
            for cmd in registry_commands:
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        version = self._extract_version_from_registry(result.stdout)
                        if version:
                            return version
                except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
                    logger.debug(f"Registry command failed: {e}")
                    
        except Exception as e:
            logger.debug(f"Registry detection failed: {e}")
        
        # Method 2: Try folder detection in Program Files
        try:
            for i in range(2):  # Check both 64-bit and 32-bit Program Files
                base_path = Path('C:\\Program Files' + (' (x86)' if i else '') + '\\Google\\Chrome\\Application')
                if base_path.exists():
                    for item in base_path.iterdir():
                        if item.is_dir():
                            folder_name = item.name
                            # Chrome version folders follow pattern: 120.0.6099.109
                            version_pattern = r'^\d+\.\d+\.\d+\.\d+$'
                            if re.match(version_pattern, folder_name):
                                return folder_name
        except Exception as e:
            logger.debug(f"Folder detection failed: {e}")
        
        # Method 3: Try executable paths and run --version command
        for path in self._get_chrome_paths():
            version = self._try_executable_version(path, "chrome")
            if version:
                return version
                
        return None
    
    def _detect_firefox_windows(self) -> Optional[str]:
        """Detect Firefox version on Windows."""
        # Try registry
        try:
            registry_commands = [
                'reg query "HKLM\\SOFTWARE\\Mozilla\\Mozilla Firefox"',
                'reg query "HKLM\\SOFTWARE\\Wow6432Node\\Mozilla\\Mozilla Firefox"',
                'reg query "HKCU\\SOFTWARE\\Mozilla\\Mozilla Firefox"',
                # Windows Server specific keys
                'reg query "HKLM\\SOFTWARE\\Mozilla\\Mozilla Firefox ESR"',
                'reg query "HKLM\\SOFTWARE\\Wow6432Node\\Mozilla\\Mozilla Firefox ESR"',
                'reg query "HKLM\\SOFTWARE\\Policies\\Mozilla\\Firefox"',
                # Enterprise deployment keys
                'reg query "HKLM\\SOFTWARE\\Mozilla\\Mozilla Firefox\\CurrentVersion"',
                'reg query "HKLM\\SOFTWARE\\Wow6432Node\\Mozilla\\Mozilla Firefox\\CurrentVersion"'
            ]
            
            for cmd in registry_commands:
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        version = self._extract_version_from_registry(result.stdout)
                        if version:
                            return version
                except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
                    logger.debug(f"Registry command failed: {e}")
                    
        except Exception as e:
            logger.debug(f"Registry detection failed: {e}")
        
        # Try folder detection (application.ini)
        try:
            firefox_paths = [
                r"C:\Program Files\Mozilla Firefox",
                r"C:\Program Files (x86)\Mozilla Firefox",
                r"C:\Program Files\Mozilla Firefox ESR",
                r"C:\Program Files (x86)\Mozilla Firefox ESR"
            ]
            
            for base_path_str in firefox_paths:
                base_path = Path(base_path_str)
                app_ini_path = base_path / "application.ini"
                if app_ini_path.exists():
                    with open(app_ini_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        version_match = re.search(r'Version=(\d+\.\d+(?:\.\d+)?)', content)
                        if version_match:
                            return version_match.group(1)
        except Exception as e:
            logger.debug(f"Folder detection failed: {e}")
        
        # Try executable paths
        for path in self._get_firefox_paths():
            version = self._try_executable_version(path, "firefox")
            if version:
                return version
                
        return None
    
    def _detect_edge_windows(self) -> Optional[str]:
        """
        Detect Edge version on Windows using multiple detection methods.
        
        This method tries several approaches to find Edge version:
        1. Registry queries for EdgeUpdate client information
        2. Folder detection in Program Files
        3. Executable version command
        
        Returns:
            Optional[str]: Edge version string or None if not found
            
        Note:
            Edge can be installed as:
            - Standard Edge (regular releases)
            - Edge Beta/Dev (preview versions)
            - Edge Enterprise (enterprise deployments)
            - EdgeWebView (embedded component)
        """
        # Method 1: Try registry queries for Edge installation information
        try:
            registry_commands = [
                # Standard Edge registry keys (EdgeUpdate clients)
                'reg query "HKLM\\SOFTWARE\\Microsoft\\EdgeUpdate\\Clients\\{56EB18F8-B008-4CBD-B6D2-8C97FE7E9062}"',
                'reg query "HKLM\\SOFTWARE\\Wow6432Node\\Microsoft\\EdgeUpdate\\Clients\\{56EB18F8-B008-4CBD-B6D2-8C97FE7E9062}"',
                # Alternative registry keys (different GUIDs)
                'reg query "HKLM\\SOFTWARE\\Microsoft\\EdgeUpdate\\Clients\\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"',
                'reg query "HKLM\\SOFTWARE\\Wow6432Node\\Microsoft\\EdgeUpdate\\Clients\\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"',
                # Windows 11 specific keys
                'reg query "HKLM\\SOFTWARE\\Microsoft\\EdgeUpdate\\Clients\\{2CD8A007-E189-409D-A2C8-9AF4EF3C72AA}"',
                'reg query "HKLM\\SOFTWARE\\Wow6432Node\\Microsoft\\EdgeUpdate\\Clients\\{2CD8A007-E189-409D-A2C8-9AF4EF3C72AA}"',
                # Uninstall registry keys
                'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Microsoft Edge"',
                'reg query "HKLM\\SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Microsoft Edge"',
                # User-specific keys
                'reg query "HKCU\\SOFTWARE\\Microsoft\\EdgeUpdate\\Clients\\{56EB18F8-B008-4CBD-B6D2-8C97FE7E9062}"',
                # Windows Server specific keys
                'reg query "HKLM\\SOFTWARE\\Microsoft\\EdgeUpdate\\Clients\\{56EB18F8-B008-4CBD-B6D2-8C97FE7E9062}"',
                # Group Policy managed installations
                'reg query "HKLM\\SOFTWARE\\Policies\\Microsoft\\EdgeUpdate"',
                # Enterprise deployment keys
                'reg query "HKLM\\SOFTWARE\\Microsoft\\EdgeUpdate\\Clients\\{56EB18F8-B008-4CBD-B6D2-8C97FE7E9062}\\Commands\\regedit"',
                'reg query "HKLM\\SOFTWARE\\Wow6432Node\\Microsoft\\EdgeUpdate\\Clients\\{56EB18F8-B008-4CBD-B6D2-8C97FE7E9062}\\Commands\\regedit"'
            ]
            
            for cmd in registry_commands:
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        version = self._extract_version_from_registry(result.stdout)
                        if version:
                            return version
                except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
                    logger.debug(f"Registry command failed: {e}")
                    
        except Exception as e:
            logger.debug(f"Registry detection failed: {e}")
        
        # Method 2: Try folder detection in Program Files
        try:
            edge_paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application",
                r"C:\Program Files\Microsoft\Edge\Application",
                r"C:\Program Files\Microsoft\EdgeWebView\Application",
                r"C:\Program Files (x86)\Microsoft\EdgeWebView\Application",
                # Windows Server specific paths
                r"C:\Program Files\Microsoft\Edge\Application",
                r"C:\Program Files (x86)\Microsoft\Edge\Application",
                r"C:\Program Files\Microsoft\Edge Enterprise\Application",
                r"C:\Program Files (x86)\Microsoft\Edge Enterprise\Application"
            ]
            
            for base_path_str in edge_paths:
                base_path = Path(base_path_str)
                if base_path.exists():
                    # Look for version directories (Edge uses version folders like Chrome)
                    for item in base_path.iterdir():
                        if item.is_dir():
                            folder_name = item.name
                            # Edge version folders follow pattern: 120.0.6099.109
                            version_pattern = r'^\d+\.\d+\.\d+\.\d+$'
                            if re.match(version_pattern, folder_name):
                                return folder_name
                                
        except Exception as e:
            logger.debug(f"Folder detection failed: {e}")
        
        # Method 3: Try executable paths and run --version command
        for path in self._get_edge_paths():
            version = self._try_executable_version(path, "edge")
            if version:
                return version
                
        return None
    
    def _detect_ie_windows(self) -> Optional[str]:
        """Detect Internet Explorer version on Windows."""
        # Try registry - multiple possible keys for IE
        try:
            registry_commands = [
                # Standard IE registry keys
                'reg query "HKLM\\SOFTWARE\\Microsoft\\Internet Explorer"',
                'reg query "HKCU\\SOFTWARE\\Microsoft\\Internet Explorer"',
                # Version-specific keys
                'reg query "HKLM\\SOFTWARE\\Microsoft\\Internet Explorer\\Version Vector"',
                'reg query "HKLM\\SOFTWARE\\Microsoft\\Internet Explorer\\svcVersion"',
                # Uninstall registry keys
                'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Internet Explorer"',
                'reg query "HKLM\\SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Internet Explorer"',
                # Windows 10/11 specific keys
                'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\5.0\\User Agent"',
                # Windows Server specific keys
                'reg query "HKLM\\SOFTWARE\\Microsoft\\Internet Explorer\\Main\\FeatureControl\\FEATURE_BROWSER_EMULATION"',
                'reg query "HKLM\\SOFTWARE\\Microsoft\\Internet Explorer\\Main\\FeatureControl\\FEATURE_MAINHANDLER"',
                # Enterprise deployment keys
                'reg query "HKLM\\SOFTWARE\\Microsoft\\Internet Explorer\\Main\\FeatureControl\\FEATURE_ADDON_MANAGEMENT"',
                'reg query "HKLM\\SOFTWARE\\Microsoft\\Internet Explorer\\Main\\FeatureControl\\FEATURE_AUTHENTICODE"'
            ]
            
            for cmd in registry_commands:
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        version = self._extract_ie_version_from_registry(result.stdout)
                        if version:
                            return version
                except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
                    logger.debug(f"Registry command failed: {e}")
                    
        except Exception as e:
            logger.debug(f"Registry detection failed: {e}")
        
        # Try folder detection for IE
        try:
            ie_paths = [
                r"C:\Program Files\Internet Explorer",
                r"C:\Program Files (x86)\Internet Explorer",
                r"C:\Program Files\Windows NT\Accessories",
                # Windows Server specific paths
                r"C:\Program Files\Internet Explorer",
                r"C:\Program Files (x86)\Internet Explorer",
                r"C:\Program Files\Windows NT\Accessories"
            ]
            
            for base_path_str in ie_paths:
                base_path = Path(base_path_str)
                if base_path.exists():
                    # Look for version in file properties or version info
                    iexplore_path = base_path / "iexplore.exe"
                    if iexplore_path.exists():
                        # Try to get version from file properties
                        try:
                            result = subprocess.run(
                                ['wmic', 'datafile', 'where', f'name="{iexplore_path}"', 'get', 'version', '/value'],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )
                            if result.returncode == 0:
                                version_match = re.search(r'Version=(\d+\.\d+\.\d+\.\d+)', result.stdout)
                                if version_match:
                                    return version_match.group(1)
                        except Exception as e:
                            logger.debug(f"WMIC version detection failed: {e}")
                                
        except Exception as e:
            logger.debug(f"Folder detection failed: {e}")
        
        # Try executable paths
        for path in self._get_ie_paths():
            version = self._try_executable_version(path, "ie")
            if version:
                return version
                
        return None
    
    def _detect_unix_version(self, browser_type: str) -> Optional[str]:
        """Detect browser version on Unix-like systems (Linux/macOS)."""
        paths = []
        if browser_type == "chrome":
            paths = self._get_chrome_paths()
        elif browser_type == "firefox":
            paths = self._get_firefox_paths()
        elif browser_type == "edge":
            paths = self._get_edge_paths()
        elif browser_type == "ie":
            # IE is not available on Unix-like systems
            logger.debug("Internet Explorer is not available on Unix-like systems")
            return None
            
        for path in paths:
            version = self._try_executable_version(path, browser_type)
            if version:
                return version
                
        return None
    
    def detect_chrome_version(self) -> Optional[str]:
        """
        Detect Chrome version using platform-specific methods.
        
        This is the main public method for Chrome version detection.
        It delegates to platform-specific detection methods and provides
        comprehensive logging for debugging.
        
        Returns:
            Optional[str]: Chrome version string (e.g., "120.0.6099.109") or None if not found
            
        Example:
            >>> detector = BrowserVersionDetector()
            >>> version = detector.detect_chrome_version()
            >>> print(version)
            "120.0.6099.109"
        """
        try:
            if self.platform == "win32":
                logger.debug("Detecting Chrome version on Windows...")
                version = self._detect_chrome_windows()
            elif self.platform in ["linux", "linux2", "darwin"]:
                logger.debug("Detecting Chrome version on Unix-like system...")
                version = self._detect_unix_version("chrome")
            else:
                logger.warning(f"Unsupported platform: {self.platform}")
                return None
                
            if version:
                logger.info(f"Chrome version detected: {version}")
            else:
                logger.warning("Chrome version not found")
                
            return version
            
        except Exception as e:
            logger.error(f"Error detecting Chrome version: {e}")
            return None
    
    def detect_firefox_version(self) -> Optional[str]:
        """
        Detect Firefox version using platform-specific methods.
        
        This is the main public method for Firefox version detection.
        It delegates to platform-specific detection methods and provides
        comprehensive logging for debugging.
        
        Returns:
            Optional[str]: Firefox version string (e.g., "120.0") or None if not found
            
        Example:
            >>> detector = BrowserVersionDetector()
            >>> version = detector.detect_firefox_version()
            >>> print(version)
            "120.0"
        """
        try:
            if self.platform == "win32":
                logger.debug("Detecting Firefox version on Windows...")
                version = self._detect_firefox_windows()
            elif self.platform in ["linux", "linux2", "darwin"]:
                logger.debug("Detecting Firefox version on Unix-like system...")
                version = self._detect_unix_version("firefox")
            else:
                logger.warning(f"Unsupported platform: {self.platform}")
                return None
                
            if version:
                logger.info(f"Firefox version detected: {version}")
            else:
                logger.warning("Firefox version not found")
                
            return version
            
        except Exception as e:
            logger.error(f"Error detecting Firefox version: {e}")
            return None
    
    def detect_edge_version(self) -> Optional[str]:
        """
        Detect Edge version using platform-specific methods.
        
        This is the main public method for Edge version detection.
        It delegates to platform-specific detection methods and provides
        comprehensive logging for debugging.
        
        Returns:
            Optional[str]: Edge version string (e.g., "120.0.6099.109") or None if not found
            
        Example:
            >>> detector = BrowserVersionDetector()
            >>> version = detector.detect_edge_version()
            >>> print(version)
            "120.0.6099.109"
        """
        try:
            if self.platform == "win32":
                logger.debug("Detecting Edge version on Windows...")
                version = self._detect_edge_windows()
            elif self.platform in ["linux", "linux2", "darwin"]:
                logger.debug("Detecting Edge version on Unix-like system...")
                version = self._detect_unix_version("edge")
            else:
                logger.warning(f"Unsupported platform: {self.platform}")
                return None
                
            if version:
                logger.info(f"Edge version detected: {version}")
            else:
                logger.warning("Edge version not found")
                logger.debug("Edge detection methods tried: registry, folder detection, executable paths")
                
            return version
            
        except Exception as e:
            logger.error(f"Error detecting Edge version: {e}")
            return None
    
    def detect_ie_version(self) -> Optional[str]:
        """
        Detect Internet Explorer version using platform-specific methods.
        
        This is the main public method for IE version detection.
        Note that IE has been deprecated by Microsoft and may not be
        available on newer Windows versions.
        
        Returns:
            Optional[str]: IE version string (e.g., "11.0.19041.1") or None if not found
            
        Example:
            >>> detector = BrowserVersionDetector()
            >>> version = detector.detect_ie_version()
            >>> print(version)
            "11.0.19041.1"
        """
        try:
            if self.platform == "win32":
                logger.debug("Detecting Internet Explorer version on Windows...")
                version = self._detect_ie_windows()
            else:
                logger.warning(f"Unsupported platform: {self.platform}")
                return None
                
            if version:
                logger.info(f"Internet Explorer version detected: {version}")
            else:
                logger.warning("Internet Explorer not found")
                
            return version
            
        except Exception as e:
            logger.error(f"Error detecting Internet Explorer version: {e}")
            return None
    
    def detect_all_browsers(self) -> Dict[str, Any]:
        """
        Detect versions of all supported browsers.
        
        This method attempts to detect all supported browsers (Chrome, Firefox, Edge, IE)
        and returns a comprehensive dictionary with detection results for each browser.
        This is useful for system inventory, automation scripts, or when you need
        to check multiple browsers at once.
        
        Returns:
            Dict[str, Any]: Dictionary containing browser version information with structure:
                {
                    'chrome': {'version': str, 'detected': bool},
                    'firefox': {'version': str, 'detected': bool},
                    'edge': {'version': str, 'detected': bool},
                    'ie': {'version': str, 'detected': bool},
                    'platform': str
                }
            
        Example:
            >>> detector = BrowserVersionDetector()
            >>> results = detector.detect_all_browsers()
            >>> print(results)
            {
                'chrome': {'version': '120.0.6099.109', 'detected': True},
                'firefox': {'version': '120.0', 'detected': True},
                'edge': {'version': None, 'detected': False},
                'ie': {'version': None, 'detected': False},
                'platform': 'win32'
            }
            
        Note:
            - Each browser detection is independent; failure of one doesn't affect others
            - Platform information is included for reference
            - Useful for CLI scripting with --version-only flag
        """
        browsers = {}
        
        # Detect Chrome version
        chrome_version = self.detect_chrome_version()
        browsers['chrome'] = {
            'version': chrome_version,
            'detected': chrome_version is not None
        }
        
        # Detect Firefox version
        firefox_version = self.detect_firefox_version()
        browsers['firefox'] = {
            'version': firefox_version,
            'detected': firefox_version is not None
        }
        
        # Detect Edge version
        edge_version = self.detect_edge_version()
        browsers['edge'] = {
            'version': edge_version,
            'detected': edge_version is not None
        }
        
        # Detect Internet Explorer version
        ie_version = self.detect_ie_version()
        browsers['ie'] = {
            'version': ie_version,
            'detected': ie_version is not None
        }
        
        # Add platform information for reference
        browsers['platform'] = self.platform
        
        return browsers


def get_chrome_version() -> Optional[str]:
    """
    Get Chrome version using the BrowserVersionDetector.
    
    This is a convenience function that creates a BrowserVersionDetector instance
    and calls the Chrome detection method.
    
    Returns:
        Optional[str]: Chrome version string (e.g., "120.0.6099.109") or None if not found
        
    Example:
        >>> version = get_chrome_version()
        >>> print(version)
        "120.0.6099.109"
    """
    detector = BrowserVersionDetector()
    return detector.detect_chrome_version()


def get_firefox_version() -> Optional[str]:
    """
    Get Firefox version using the BrowserVersionDetector.
    
    This is a convenience function that creates a BrowserVersionDetector instance
    and calls the Firefox detection method.
    
    Returns:
        Optional[str]: Firefox version string (e.g., "120.0") or None if not found
        
    Example:
        >>> version = get_firefox_version()
        >>> print(version)
        "120.0"
    """
    detector = BrowserVersionDetector()
    return detector.detect_firefox_version()


def get_edge_version() -> Optional[str]:
    """
    Get Edge version using the BrowserVersionDetector.
    
    This is a convenience function that creates a BrowserVersionDetector instance
    and calls the Edge detection method.
    
    Returns:
        Optional[str]: Edge version string (e.g., "120.0.6099.109") or None if not found
        
    Example:
        >>> version = get_edge_version()
        >>> print(version)
        "120.0.6099.109"
    """
    detector = BrowserVersionDetector()
    return detector.detect_edge_version()


def get_ie_version() -> Optional[str]:
    """
    Get Internet Explorer version using the BrowserVersionDetector.
    
    This is a convenience function that creates a BrowserVersionDetector instance
    and calls the IE detection method. Note that IE has been deprecated by Microsoft.
    
    Returns:
        Optional[str]: IE version string (e.g., "11.0.19041.1") or None if not found
        
    Example:
        >>> version = get_ie_version()
        >>> print(version)
        "11.0.19041.1"
    """
    detector = BrowserVersionDetector()
    return detector.detect_ie_version()


def get_all_browser_versions() -> Dict[str, Any]:
    """
    Get versions of all supported browsers using the BrowserVersionDetector.
    
    This is a convenience function that creates a BrowserVersionDetector instance
    and calls the all browsers detection method. Useful for system inventory
    and automation scripts.
    
    Returns:
        Dict[str, Any]: Dictionary containing browser version information for all browsers
        
    Example:
        >>> results = get_all_browser_versions()
        >>> for browser, info in results.items():
        ...     if browser != 'platform':
        ...         print(f"{browser}: {info['version'] if info['detected'] else 'Not found'}")
        chrome: 120.0.6099.109
        firefox: 120.0
        edge: Not found
        ie: Not found
    """
    detector = BrowserVersionDetector()
    return detector.detect_all_browsers()


def main():
    """
    Main function for command-line interface.
    
    This function provides a user-friendly command-line interface for browser
    version detection. It can be used both as a standalone script and as an
    entry point for the installed package.
    
    Command-line options:
        --browser: Specify which browser to detect (chrome, firefox, edge, ie, all)
        --version-only: Print only the version number (useful for scripting)
        --script-version: Print the version of this script
    
    Output formats:
        - Standard mode: Detailed output with browser names and detection status
        - Version-only mode: Simple "browser: version" format for automation
        - All browsers: Comprehensive list of all detected browsers
    """
    import argparse
    
    # Set up command-line argument parser with descriptive help text
    parser = argparse.ArgumentParser(
        description="Detect installed web browser versions across different operating systems.",
        epilog="Examples:\n"
               "  browseversa --browser chrome\n"
               "  browseversa --browser firefox --version-only\n"
               "  browseversa --browser all --version-only\n"
               "  browseversa --script-version\n\n"
               "For more information, visit: https://github.com/pandiyarajk/browseversa"
    )
    
    # Add command-line arguments
    parser.add_argument(
        "--browser", 
        choices=["chrome", "firefox", "edge", "ie", "all"], 
        default="all", 
        help="Browser to detect (default: all)"
    )
    parser.add_argument(
        "--version-only", 
        action="store_true", 
        help="Print only the version (for scripting/automation)"
    )
    parser.add_argument(
        "--script-version", 
        action="store_true", 
        help="Print the version of this script"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose logging output"
    )
    
    # Parse command-line arguments
    args = parser.parse_args()

    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Handle script version request
    if args.script_version:
        print(__version__)
        return

    # Create detector instance
    detector = BrowserVersionDetector()

    if args.browser == "all":
        # Detect all browsers
        results = detector.detect_all_browsers()
        
        if args.version_only:
            # Version-only output for scripting
            for browser, info in results.items():
                if browser != 'platform':
                    version = info['version'] if info['detected'] else 'Not found'
                    print(f"{browser}: {version}")
        else:
            # Standard output with details
            print("Browser Version Detection Results:")
            print("=" * 40)
            for browser, info in results.items():
                if browser != 'platform':
                    if info['detected']:
                        print(f"✓ {browser.capitalize()}: {info['version']}")
                    else:
                        print(f"✗ {browser.capitalize()}: Not found")
            print(f"\nPlatform: {results['platform']}")
    else:
        # Detect specific browser
        if args.browser == "chrome":
            version = detector.detect_chrome_version()
        elif args.browser == "firefox":
            version = detector.detect_firefox_version()
        elif args.browser == "edge":
            version = detector.detect_edge_version()
        elif args.browser == "ie":
            version = detector.detect_ie_version()
        else:
            print(f"Error: Unknown browser '{args.browser}'")
            return

        if args.version_only:
            # Version-only output
            print(version if version else "Not found")
        else:
            # Standard output
            if version:
                print(f"{args.browser.capitalize()} version: {version}")
            else:
                print(f"{args.browser.capitalize()}: Not found")


if __name__ == "__main__":
    main()
        
