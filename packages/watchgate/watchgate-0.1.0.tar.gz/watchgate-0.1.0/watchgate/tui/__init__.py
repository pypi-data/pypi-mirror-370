"""Watchgate Terminal User Interface (TUI) module.

This module provides a terminal-based user interface for configuring and
managing Watchgate security policies and server connections.
"""

import os
from pathlib import Path
from typing import Optional


def run_tui(config_path: Optional[Path] = None) -> None:
    """Run the Watchgate TUI application.
    
    Args:
        config_path: Optional path to configuration file to load
    """
    from .app import WatchgateConfigApp
    
    # Detect if we're running in Claude Code environment and disable mouse to prevent terminal corruption
    # when the process is killed (Claude can't properly cleanup mouse tracking on SIGKILL)
    is_claude_environment = os.getenv('CLAUDECODE') == '1'
    mouse_enabled = not is_claude_environment
    
    app = WatchgateConfigApp(config_path)
    app.run(mouse=mouse_enabled)


__all__ = ["run_tui"]