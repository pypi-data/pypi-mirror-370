"""Version utility for Watchgate.

This module provides a centralized way to retrieve the Watchgate version
dynamically, with fallback mechanisms for different deployment scenarios.
"""

import importlib.metadata
from typing import Optional


def get_watchgate_version() -> str:
    """Get Watchgate version dynamically.
    
    Returns:
        str: The Watchgate version string, or "unknown" if not determinable
    """
    try:
        # Try to get version from package metadata (installed package)
        return importlib.metadata.version("watchgate")
    except (ImportError, importlib.metadata.PackageNotFoundError):
        # Fallback to reading from version file
        try:
            from watchgate import __version__
            return __version__
        except ImportError:
            return "unknown"


def get_watchgate_version_with_fallback(fallback: Optional[str] = None) -> str:
    """Get Watchgate version with custom fallback.
    
    Args:
        fallback: Custom fallback version string if version cannot be determined
        
    Returns:
        str: The Watchgate version string, or fallback if not determinable
    """
    version = get_watchgate_version()
    if version == "unknown" and fallback is not None:
        return fallback
    return version