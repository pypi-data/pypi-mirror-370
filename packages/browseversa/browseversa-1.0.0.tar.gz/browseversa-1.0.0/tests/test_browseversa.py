#!/usr/bin/env python3
"""
Tests for browseversa module.

This module contains comprehensive tests for the BrowserVersionDetector class
and convenience functions to ensure reliability and correctness.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from browseversa import (
    BrowserVersionDetector,
    get_chrome_version,
    get_firefox_version,
    get_edge_version,
    get_ie_version,
    get_all_browser_versions,
    __version__
)


class TestBrowserVersionDetector:
    """Test cases for BrowserVersionDetector class."""

    def test_init(self):
        """Test BrowserVersionDetector initialization."""
        detector = BrowserVersionDetector()
        assert detector.platform == sys.platform
        assert isinstance(detector.browsers, dict)
        assert detector.windows_version is not None or sys.platform != "win32"

    def test_get_windows_version_windows(self):
        """Test Windows version detection on Windows platform."""
        if sys.platform == "win32":
            detector = BrowserVersionDetector()
            version = detector._get_windows_version()
            assert version in ["Windows", "Windows Server", None]

    def test_get_windows_version_non_windows(self):
        """Test Windows version detection on non-Windows platform."""
        if sys.platform != "win32":
            detector = BrowserVersionDetector()
            version = detector._get_windows_version()
            assert version is None

    def test_extract_version_from_registry(self):
        """Test version extraction from registry output."""
        detector = BrowserVersionDetector()
        
        # Test valid registry output
        registry_output = 'DisplayVersion    REG_SZ    120.0.6099.109'
        version = detector._extract_version_from_registry(registry_output)
        assert version == "120.0.6099.109"
        
        # Test invalid registry output
        invalid_output = 'No version information here'
        version = detector._extract_version_from_registry(invalid_output)
        assert version is None

    def test_extract_ie_version_from_registry(self):
        """Test IE version extraction from registry output."""
        detector = BrowserVersionDetector()
        
        # Test valid IE registry output
        registry_output = 'Version    REG_SZ    11.0.19041.1'
        version = detector._extract_ie_version_from_registry(registry_output)
        assert version == "11.0.19041.1"
        
        # Test invalid registry output
        invalid_output = 'No IE version information here'
        version = detector._extract_ie_version_from_registry(invalid_output)
        assert version is None

    def test_get_chrome_paths(self):
        """Test Chrome paths generation for different platforms."""
        detector = BrowserVersionDetector()
        paths = detector._get_chrome_paths()
        assert isinstance(paths, list)
        assert len(paths) > 0

    def test_get_firefox_paths(self):
        """Test Firefox paths generation for different platforms."""
        detector = BrowserVersionDetector()
        paths = detector._get_firefox_paths()
        assert isinstance(paths, list)
        assert len(paths) > 0

    def test_get_edge_paths(self):
        """Test Edge paths generation for different platforms."""
        detector = BrowserVersionDetector()
        paths = detector._get_edge_paths()
        assert isinstance(paths, list)
        assert len(paths) > 0

    def test_get_ie_paths(self):
        """Test IE paths generation for different platforms."""
        detector = BrowserVersionDetector()
        paths = detector._get_ie_paths()
        if sys.platform == "win32":
            assert isinstance(paths, list)
            assert len(paths) > 0
        else:
            assert paths == []

    @patch('subprocess.run')
    def test_try_executable_version_success(self, mock_run):
        """Test successful executable version detection."""
        detector = BrowserVersionDetector()
        
        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Google Chrome 120.0.6099.109"
        mock_run.return_value = mock_result
        
        version = detector._try_executable_version("/fake/path/chrome.exe", "chrome")
        assert version == "120.0.6099.109"

    @patch('subprocess.run')
    def test_try_executable_version_failure(self, mock_run):
        """Test failed executable version detection."""
        detector = BrowserVersionDetector()
        
        # Mock failed subprocess run
        mock_run.side_effect = FileNotFoundError()
        
        version = detector._try_executable_version("/fake/path/chrome.exe", "chrome")
        assert version is None

    def test_detect_all_browsers(self):
        """Test detection of all browsers."""
        detector = BrowserVersionDetector()
        results = detector.detect_all_browsers()
        
        assert isinstance(results, dict)
        assert 'platform' in results
        assert 'chrome' in results
        assert 'firefox' in results
        assert 'edge' in results
        assert 'ie' in results
        
        for browser, info in results.items():
            if browser != 'platform':
                assert isinstance(info, dict)
                assert 'version' in info
                assert 'detected' in info
                assert isinstance(info['detected'], bool)


class TestConvenienceFunctions:
    """Test cases for convenience functions."""

    def test_get_chrome_version(self):
        """Test get_chrome_version convenience function."""
        version = get_chrome_version()
        # Should return either a version string or None
        assert version is None or isinstance(version, str)

    def test_get_firefox_version(self):
        """Test get_firefox_version convenience function."""
        version = get_firefox_version()
        # Should return either a version string or None
        assert version is None or isinstance(version, str)

    def test_get_edge_version(self):
        """Test get_edge_version convenience function."""
        version = get_edge_version()
        # Should return either a version string or None
        assert version is None or isinstance(version, str)

    def test_get_ie_version(self):
        """Test get_ie_version convenience function."""
        version = get_ie_version()
        # Should return either a version string or None
        assert version is None or isinstance(version, str)

    def test_get_all_browser_versions(self):
        """Test get_all_browser_versions convenience function."""
        results = get_all_browser_versions()
        
        assert isinstance(results, dict)
        assert 'platform' in results
        assert 'chrome' in results
        assert 'firefox' in results
        assert 'edge' in results
        assert 'ie' in results


class TestModuleMetadata:
    """Test cases for module metadata."""

    def test_version(self):
        """Test that version is defined and valid."""
        assert __version__ is not None
        assert isinstance(__version__, str)
        # Version should follow semantic versioning
        parts = __version__.split('.')
        assert len(parts) >= 2
        assert all(part.isdigit() for part in parts[:2])


class TestPlatformSpecific:
    """Test cases for platform-specific functionality."""

    def test_windows_specific_detection(self):
        """Test Windows-specific detection methods."""
        if sys.platform == "win32":
            detector = BrowserVersionDetector()
            
            # Test Windows-specific methods exist
            assert hasattr(detector, '_detect_chrome_windows')
            assert hasattr(detector, '_detect_firefox_windows')
            assert hasattr(detector, '_detect_edge_windows')
            assert hasattr(detector, '_detect_ie_windows')

    def test_unix_specific_detection(self):
        """Test Unix-specific detection methods."""
        if sys.platform in ["linux", "linux2", "darwin"]:
            detector = BrowserVersionDetector()
            
            # Test Unix-specific methods exist
            assert hasattr(detector, '_detect_unix_version')

    def test_ie_windows_only(self):
        """Test that IE detection is Windows-only."""
        detector = BrowserVersionDetector()
        
        if sys.platform == "win32":
            # Should have IE detection methods on Windows
            assert hasattr(detector, '_detect_ie_windows')
        else:
            # Should not have IE detection methods on non-Windows
            assert not hasattr(detector, '_detect_ie_windows')


class TestErrorHandling:
    """Test cases for error handling."""

    @patch('subprocess.run')
    def test_registry_query_timeout(self, mock_run):
        """Test handling of registry query timeouts."""
        detector = BrowserVersionDetector()
        
        # Mock timeout exception
        mock_run.side_effect = TimeoutError()
        
        # Should not raise exception
        version = detector._detect_chrome_windows()
        assert version is None

    @patch('subprocess.run')
    def test_executable_not_found(self, mock_run):
        """Test handling of executable not found."""
        detector = BrowserVersionDetector()
        
        # Mock file not found
        mock_run.side_effect = FileNotFoundError()
        
        # Should not raise exception
        version = detector._try_executable_version("/fake/path", "chrome")
        assert version is None


if __name__ == "__main__":
    pytest.main([__file__]) 