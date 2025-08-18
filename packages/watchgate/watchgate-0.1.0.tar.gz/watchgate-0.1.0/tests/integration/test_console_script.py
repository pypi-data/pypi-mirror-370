"""Integration tests for console script functionality.

Tests that the watchgate console script works correctly.
"""

import subprocess
import sys
from pathlib import Path
import pytest


class TestConsoleScript:
    """Test the watchgate console script functionality."""
    
    def test_console_script_help(self):
        """Test that watchgate --help works and shows correct program name."""
        result = subprocess.run(
            ["watchgate", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0
        assert "Watchgate MCP Gateway Server" in result.stdout
        assert "--config" in result.stdout
        assert "--version" in result.stdout
        # Check for new command structure
        assert "proxy" in result.stdout
        assert "Launch TUI configuration interface" in result.stdout
        assert "Run as MCP proxy server" in result.stdout
    
    def test_console_script_version(self):
        """Test that watchgate --version works."""
        result = subprocess.run(
            ["watchgate", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0
        assert "Watchgate v0.1.0" in result.stdout
    
    def test_console_script_config_file_error(self):
        """Test that watchgate launches TUI gracefully with missing config file."""
        # Use echo to provide input to TUI and then exit
        result = subprocess.run(
            ["watchgate", "--config", "/nonexistent/config.yaml"],
            input="\x03",  # Send Ctrl+C to exit TUI gracefully
            text=True,
            timeout=5
        )
        
        # TUI should launch successfully (exit code 0) even with missing config
        # The TUI will handle the missing config internally with appropriate UI
        assert result.returncode == 0
    
    def test_console_script_proxy_config_file_error(self):
        """Test that watchgate proxy handles missing config file gracefully."""
        result = subprocess.run(
            ["watchgate", "proxy", "--config", "/nonexistent/config.yaml"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 1
        # Should show configuration error in proxy mode
        assert ("Configuration file not found" in result.stderr or 
                "FileNotFoundError" in result.stderr or
                "No such file" in result.stderr)
    
    def test_console_script_is_available(self):
        """Test that the console script is properly installed and available."""
        # Check that the watchgate command exists
        result = subprocess.run(
            ["which", "watchgate"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # which returns 0 if command is found, 1 if not found
        assert result.returncode == 0, "watchgate command not found in PATH"
        assert result.stdout.strip(), "watchgate command path is empty"
