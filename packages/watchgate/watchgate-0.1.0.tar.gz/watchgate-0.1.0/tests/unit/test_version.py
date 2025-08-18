"""Tests for version utility module."""

import importlib.metadata
import pytest
from unittest.mock import patch
from watchgate.utils.version import get_watchgate_version, get_watchgate_version_with_fallback


class TestGetWatchgateVersion:
    """Test the get_watchgate_version function."""

    def test_version_from_package_metadata(self):
        """Test getting version from package metadata."""
        with patch('importlib.metadata.version') as mock_version:
            mock_version.return_value = "1.2.3"
            assert get_watchgate_version() == "1.2.3"
            mock_version.assert_called_once_with("watchgate")

    def test_version_from_init_fallback(self):
        """Test fallback to __version__ from __init__.py."""
        with patch('importlib.metadata.version') as mock_version:
            mock_version.side_effect = ImportError("No module")
            with patch('watchgate.__version__', "0.1.0"):
                assert get_watchgate_version() == "0.1.0"

    def test_version_unknown_fallback(self):
        """Test fallback to 'unknown' when all methods fail."""
        with patch('importlib.metadata.version') as mock_version:
            mock_version.side_effect = ImportError("No module")
            with patch('watchgate.utils.version.importlib.metadata.PackageNotFoundError', ImportError):
                with patch.dict('sys.modules', {'watchgate': None}):
                    # This should trigger the ImportError in the fallback
                    with patch('builtins.__import__', side_effect=ImportError("No module")):
                        assert get_watchgate_version() == "unknown"

    def test_version_package_not_found_fallback(self):
        """Test fallback when package not found."""
        with patch('importlib.metadata.version') as mock_version:
            mock_version.side_effect = importlib.metadata.PackageNotFoundError("watchgate")
            with patch('watchgate.__version__', "0.1.0"):
                assert get_watchgate_version() == "0.1.0"


class TestGetWatchgateVersionWithFallback:
    """Test the get_watchgate_version_with_fallback function."""

    def test_version_with_custom_fallback(self):
        """Test custom fallback when version is unknown."""
        with patch('watchgate.utils.version.get_watchgate_version') as mock_get_version:
            mock_get_version.return_value = "unknown"
            assert get_watchgate_version_with_fallback("2.0.0") == "2.0.0"

    def test_version_with_fallback_when_known(self):
        """Test that fallback is not used when version is known."""
        with patch('watchgate.utils.version.get_watchgate_version') as mock_get_version:
            mock_get_version.return_value = "1.5.0"
            assert get_watchgate_version_with_fallback("2.0.0") == "1.5.0"

    def test_version_with_no_fallback_unknown(self):
        """Test that 'unknown' is returned when no fallback provided."""
        with patch('watchgate.utils.version.get_watchgate_version') as mock_get_version:
            mock_get_version.return_value = "unknown"
            assert get_watchgate_version_with_fallback() == "unknown"

    def test_version_with_none_fallback(self):
        """Test that None fallback behaves same as no fallback."""
        with patch('watchgate.utils.version.get_watchgate_version') as mock_get_version:
            mock_get_version.return_value = "unknown"
            assert get_watchgate_version_with_fallback(None) == "unknown"