"""Config picker modal for switching configurations during TUI session."""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple, Optional

from watchgate.config.loader import ConfigLoader

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Static, ListView, ListItem, Label
from textual import on


class ConfigPickerModal(ModalScreen[Optional[Path]]):
    """Modal dialog for choosing/creating configuration files during TUI session."""
    
    CSS = """
    ConfigPickerModal {
        align: center middle;
    }
    
    .dialog {
        width: 80;
        height: 25;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }
    
    .title {
        text-align: center;
        margin-bottom: 1;
        color: $primary;
    }
    
    .section-header {
        color: $accent;
        margin-top: 1;
        margin-bottom: 1;
    }
    
    .quick-options {
        height: 8;
        margin-bottom: 1;
        border: solid $secondary;
        padding: 1;
    }
    
    .recent-configs {
        height: 1fr;
        margin-bottom: 1;
        border: solid $secondary;
        padding: 1;
    }
    
    .button-row {
        height: 3;
        align: center middle;
    }
    
    ListView {
        height: 5;
    }
    
    DataTable {
        height: 1fr;
        min-height: 8;
    }
    
    Button {
        margin: 0 1;
    }
    
    .info-text {
        color: $text-muted;
        margin-bottom: 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "dismiss", "Cancel", priority=True),
        Binding("enter", "select", "Select", priority=True),
    ]
    
    def __init__(self, current_config: Optional[Path] = None):
        """Initialize the config picker modal.
        
        Args:
            current_config: Currently loaded configuration file (if any)
        """
        super().__init__()
        self.current_config = current_config
        self.selected_option: Optional[str] = None
        self.selected_recent_config: Optional[Path] = None
        
    def compose(self) -> ComposeResult:
        """Compose the modal layout."""
        with Container(classes="dialog"):
            yield Static("Open Configuration", classes="title")
            
            # Quick options section
            yield Static("Quick Options", classes="section-header")
            with Container(classes="quick-options"):
                yield ListView(id="quick_options")
            
            # Recent configurations section
            yield Static("Recent Configurations", classes="section-header")
            yield Static("Select from recently used configuration files:", classes="info-text")
            with Container(classes="recent-configs"):
                table = DataTable(id="recent_table", cursor_type="row")
                table.add_columns("File", "Modified", "Servers")
                yield table
            
            # Action buttons
            with Horizontal(classes="button-row"):
                yield Button("Select", id="select_btn", variant="primary")
                yield Button("Cancel", id="cancel_btn")
    
    def on_mount(self) -> None:
        """Initialize the modal when mounted."""
        self._populate_quick_options()
        self._populate_recent_configs()
        # Focus the quick options list initially
        self.query_one("#quick_options", ListView).focus()
    
    def _populate_quick_options(self) -> None:
        """Populate the quick options ListView."""
        quick_list = self.query_one("#quick_options", ListView)
        quick_list.append(ListItem(Label("📁 Browse for configuration file...")))
        quick_list.append(ListItem(Label("✨ Create new configuration...")))
        quick_list.append(ListItem(Label("🏠 Use default config location")))
    
    def _populate_recent_configs(self) -> None:
        """Populate the recent configurations table."""
        table = self.query_one("#recent_table", DataTable)
        table.clear()
        
        # Get recent config files from common locations
        recent_configs = self._discover_recent_configs()
        
        if not recent_configs:
            table.add_row("No recent configurations found", "", "")
            return
        
        for config_path, modified, servers in recent_configs:
            # Show relative path if it's in current working directory
            try:
                display_name = str(config_path.relative_to(Path.cwd()))
            except ValueError:
                display_name = str(config_path)
            
            # Mark current config with indicator
            if self.current_config and config_path.samefile(self.current_config):
                display_name = f"● {display_name}"
            
            table.add_row(display_name, modified, servers)
    
    def _discover_recent_configs(self) -> List[Tuple[Path, str, str]]:
        """Discover recent configuration files from common locations.
        
        Returns:
            List of tuples containing (file_path, formatted_modified_time, servers_list)
        """
        configs = []
        search_paths = [
            Path.cwd(),  # Current directory
            Path.cwd() / "configs",  # configs subdirectory
            Path.home() / ".config" / "watchgate",  # User config directory
            Path.home() / "watchgate",  # User home watchgate directory
        ]
        
        # Add current config's directory if it exists
        if self.current_config:
            search_paths.append(self.current_config.parent)
        
        # Search for YAML files in these locations
        seen_files = set()
        for search_path in search_paths:
            if not search_path.exists():
                continue
                
            try:
                for config_file in search_path.rglob("*.yaml"):
                    if config_file.is_file() and config_file not in seen_files:
                        seen_files.add(config_file)
                        
                        # Check if it's actually a watchgate config by trying to load it
                        if self._is_watchgate_config(config_file):
                            stat = config_file.stat()
                            modified = self._format_timestamp(stat.st_mtime)
                            servers = self._extract_server_names(config_file)
                            configs.append((config_file, modified, servers))
            except (OSError, PermissionError):
                continue
        
        # Sort by modification time (most recent first)
        configs.sort(key=lambda x: x[0].stat().st_mtime, reverse=True)
        
        # Limit to most recent 10 configs to avoid cluttering
        return configs[:10]
    
    def _is_watchgate_config(self, config_path: Path) -> bool:
        """Check if a YAML file is likely a Watchgate configuration.
        
        Args:
            config_path: Path to the YAML file
            
        Returns:
            True if it appears to be a Watchgate config
        """
        try:
            loader = ConfigLoader()
            config = loader.load_from_file(config_path)
            # If it loads successfully with our loader, it's probably a watchgate config
            return True
        except Exception:
            return False
    
    def _format_timestamp(self, timestamp: float) -> str:
        """Format a timestamp for display.
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Formatted time string
        """
        file_time = datetime.fromtimestamp(timestamp)
        now = datetime.now()
        diff = now - file_time
        
        if diff < timedelta(days=1):
            if diff < timedelta(hours=1):
                return "Now" if diff < timedelta(minutes=5) else f"{int(diff.total_seconds() // 60)}m ago"
            else:
                return f"{int(diff.total_seconds() // 3600)}h ago"
        elif diff < timedelta(days=2):
            return "Yesterday"
        elif diff < timedelta(days=7):
            return f"{int(diff.days)} days ago"
        else:
            return file_time.strftime("%Y-%m-%d")
    
    def _extract_server_names(self, config_path: Path) -> str:
        """Extract MCP server names from a config file.
        
        Args:
            config_path: Path to the config file
            
        Returns:
            Comma-separated list of server names, or error message
        """
        try:
            loader = ConfigLoader()
            config = loader.load_from_file(config_path)
            
            if not config.upstreams:
                return "No servers"
            
            server_names = [upstream.name for upstream in config.upstreams]
            servers_text = ", ".join(server_names)
            
            # Truncate if too long
            if len(servers_text) > 40:
                return servers_text[:37] + "..."
            return servers_text
                
        except Exception:
            return "Parse error"
    
    @on(ListView.Selected)
    def on_quick_option_selected(self, event: ListView.Selected) -> None:
        """Handle quick option selection."""
        if event.list_view.id == "quick_options":
            item = event.item
            if item:
                label_text = item.children[0].renderable  # Get the Label's text
                
                if "Browse for configuration" in str(label_text):
                    self.selected_option = "browse"
                elif "Create new configuration" in str(label_text):
                    self.selected_option = "create"
                elif "Use default config" in str(label_text):
                    self.selected_option = "default"
    
    @on(DataTable.RowSelected)
    def on_recent_config_selected(self, event: DataTable.RowSelected) -> None:
        """Handle recent config selection."""
        table = self.query_one("#recent_table", DataTable)
        
        if table.row_count == 0:
            return
        
        # Get the selected row data
        row_key = event.row_key
        name_cell = table.get_cell(row_key, "Name")
        
        if name_cell and not name_cell.startswith("No recent configurations"):
            # Remove the "current config" indicator if present
            clean_name = name_cell.replace("● ", "")
            
            # Try to resolve the path
            config_path = Path(clean_name)
            if not config_path.is_absolute():
                config_path = Path.cwd() / config_path
            
            if config_path.exists() and config_path.is_file():
                self.selected_recent_config = config_path
                self.selected_option = None  # Clear quick option selection
    
    @on(Button.Pressed, "#select_btn")
    def on_select_button(self) -> None:
        """Handle select button press."""
        self.action_select()
    
    @on(Button.Pressed, "#cancel_btn")
    def on_cancel_button(self) -> None:
        """Handle cancel button press."""
        self.action_dismiss()
    
    def action_select(self) -> None:
        """Handle selection action."""
        # Check if a recent config is selected
        if self.selected_recent_config:
            self.dismiss(self.selected_recent_config)
            return
        
        # Check if a quick option is selected
        if self.selected_option == "browse":
            self._handle_browse()
        elif self.selected_option == "create":
            self._handle_create_new()
        elif self.selected_option == "default":
            self._handle_default_config()
        else:
            # Try to get currently highlighted recent config
            table = self.query_one("#recent_table", DataTable)
            if table.cursor_row is not None:
                try:
                    row_key = table.cursor_row
                    name_cell = table.get_cell(row_key, "Name")
                    
                    if name_cell and not name_cell.startswith("No recent configurations"):
                        clean_name = name_cell.replace("● ", "")
                        config_path = Path(clean_name)
                        if not config_path.is_absolute():
                            config_path = Path.cwd() / config_path
                        
                        if config_path.exists() and config_path.is_file():
                            self.dismiss(config_path)
                            return
                except Exception:
                    pass
            
            # Nothing valid selected
            self.app.bell()
    
    def _handle_browse(self) -> None:
        """Handle browse for configuration file."""
        # Launch file browser - for now, use the existing directory dialog
        # This could be enhanced with a proper file picker in the future
        from .directory_dialog import DirectoryInputScreen
        
        # Start from current config's directory if available
        start_dir = Path.cwd()
        if self.current_config:
            start_dir = self.current_config.parent
        
        self.app.push_screen(DirectoryInputScreen(start_dir), self._on_browse_directory_selected)
    
    def _on_browse_directory_selected(self, directory: Optional[Path]) -> None:
        """Handle directory selection from browse dialog."""
        if directory:
            # For now, just switch to the config selector in that directory
            # In a full implementation, this would show a file picker
            from .config_selector import ConfigSelectorScreen
            self.app.push_screen(
                ConfigSelectorScreen(directory), 
                lambda config: self.dismiss(config) if config else None
            )
    
    def _handle_create_new(self) -> None:
        """Handle create new configuration."""
        # For now, just dismiss with a special marker
        # The main app will handle launching the config creation wizard
        self.dismiss("__CREATE_NEW__")
    
    def _handle_default_config(self) -> None:
        """Handle use default config location."""
        # Look for default config locations
        default_locations = [
            Path.cwd() / "watchgate.yaml",
            Path.home() / ".config" / "watchgate" / "config.yaml",
            Path.home() / "watchgate" / "config.yaml",
        ]
        
        for default_path in default_locations:
            if default_path.exists():
                self.dismiss(default_path)
                return
        
        # No default found, create one
        self.dismiss("__CREATE_DEFAULT__")
    
    def action_dismiss(self) -> None:
        """Dismiss the modal without selection."""
        self.dismiss(None)