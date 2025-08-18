"""TUI screens for Watchgate configuration interface."""

from .config_selector import ConfigSelectorScreen
from .config_picker_modal import ConfigPickerModal

# This module will contain various screens for the TUI as they are developed:
# - MainScreen: Primary configuration interface
# - ServerManagementScreen: MCP server configuration
# - PluginConfigScreen: Security and audit plugin configuration  
# - LogViewerScreen: Real-time log viewing
# - HelpScreen: Help and documentation

__all__ = ["ConfigSelectorScreen", "ConfigPickerModal"]