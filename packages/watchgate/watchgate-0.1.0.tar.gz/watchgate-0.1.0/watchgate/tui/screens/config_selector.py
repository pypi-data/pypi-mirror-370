"""Configuration file selector screen for Watchgate TUI."""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple, Optional

from watchgate.config.loader import ConfigLoader

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Static


class NavigableStatic(Static, can_focus=True):
    """A Static widget with arrow key navigation support."""
    
    BINDINGS = [
        Binding("enter", "activate", "Open directory browser", show=False, priority=True),
        Binding("down", "focus_table", "Move to file table", show=False),
        Binding("up", "focus_quit", "Move to quit button", show=False),
        Binding("left", "focus_quit", "Move to quit button", show=False),
        Binding("right", "focus_table", "Move to file table", show=False),
    ]
    
    def on_click(self) -> None:
        """Handle click events."""
        # Check if this is the directory display widget and call the action directly
        if self.id == "dir_display":
            # Get the parent screen and call the action
            screen = self.screen
            if hasattr(screen, 'action_change_directory'):
                screen.action_change_directory()
    
    def action_activate(self) -> None:
        """Handle Enter key press when this widget is focused."""
        if self.id == "dir_display":
            # Get the parent screen and call the action
            screen = self.screen
            if hasattr(screen, 'action_change_directory'):
                screen.action_change_directory()
    
    def action_focus_table(self) -> None:
        """Move focus to the file table."""
        try:
            table = self.screen.query_one("#file_table", NavigableDataTable)
            table.focus()
        except Exception:
            pass
    
    def action_focus_quit(self) -> None:
        """Move focus to the quit button."""
        try:
            quit_button = self.screen.query_one("#quit_btn", NavigableQuitButton)
            quit_button.focus()
        except Exception:
            pass


class NavigableDataTable(DataTable):
    """DataTable with custom arrow key navigation for first/last row behavior."""
    
    BINDINGS = [
        # Keep all default DataTable bindings but override up/down
        Binding("shift+left", "cursor_parent", "Cursor to parent", show=False),
        Binding("shift+right", "cursor_parent_next_sibling", "Cursor to next ancestor", show=False),
        Binding("shift+up", "cursor_previous_sibling", "Cursor to previous sibling", show=False),
        Binding("shift+down", "cursor_next_sibling", "Cursor to next sibling", show=False),
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("space", "toggle_cursor", "Toggle", show=False),
        # Custom Up/Down behavior
        Binding("up", "cursor_up_or_focus_directory", "Move up or to directory", show=False),
        Binding("down", "cursor_down_or_focus_button", "Move down or to button", show=False),
    ]
    
    def action_cursor_up_or_focus_directory(self) -> None:
        """Move cursor up, or if at top, move focus to directory widget."""
        # Check if we're at the topmost row (cursor_row is 0-indexed)
        if self.cursor_row <= 0:
            # Move focus to directory display
            try:
                dir_display = self.screen.query_one("#dir_display", NavigableStatic)
                dir_display.focus()
            except Exception:
                # Fallback to normal up behavior if something goes wrong
                self.action_cursor_up()
        else:
            # Normal up behavior
            self.action_cursor_up()
    
    def action_cursor_down_or_focus_button(self) -> None:
        """Move cursor down, or if at bottom, move focus to Select button."""
        # Check if we're at the bottommost row
        current_row = self.cursor_row
        
        # Try to move down normally first
        self.action_cursor_down()
        
        # If cursor didn't move (we were already at bottom), focus the Select button
        if self.cursor_row == current_row:
            try:
                select_button = self.screen.query_one("#select_btn", NavigableSelectButton)
                select_button.focus()
            except Exception:
                # If something goes wrong, just stay where we are
                pass


class NavigableSelectButton(Button):
    """Select button with custom arrow key navigation."""
    
    BINDINGS = Button.BINDINGS + [
        Binding("up", "focus_table", "Move to file table", show=False),
        Binding("left", "focus_table", "Move to file table", show=False),
        Binding("down", "focus_refresh", "Move to refresh button", show=False),
        Binding("right", "focus_refresh", "Move to refresh button", show=False),
    ]
    
    def action_focus_table(self) -> None:
        """Move focus back to file table (at bottom)."""
        try:
            table = self.screen.query_one("#file_table", NavigableDataTable)
            table.focus()
            # Move cursor to bottom of table for intuitive navigation
            if table.row_count > 0:
                table.cursor_row = table.row_count - 1
        except Exception:
            pass
    
    def action_focus_refresh(self) -> None:
        """Move focus to refresh button."""
        try:
            refresh_button = self.screen.query_one("#refresh_btn", NavigableRefreshButton)
            refresh_button.focus()
        except Exception:
            pass


class NavigableRefreshButton(Button):
    """Refresh button with custom arrow key navigation."""
    
    BINDINGS = Button.BINDINGS + [
        Binding("up", "focus_select", "Move to select button", show=False),
        Binding("left", "focus_select", "Move to select button", show=False),
        Binding("down", "focus_quit", "Move to quit button", show=False),
        Binding("right", "focus_quit", "Move to quit button", show=False),
    ]
    
    def action_focus_select(self) -> None:
        """Move focus to select button."""
        try:
            select_button = self.screen.query_one("#select_btn", NavigableSelectButton)
            select_button.focus()
        except Exception:
            pass
    
    def action_focus_quit(self) -> None:
        """Move focus to quit button."""
        try:
            quit_button = self.screen.query_one("#quit_btn", NavigableQuitButton)
            quit_button.focus()
        except Exception:
            pass


class NavigableQuitButton(Button):
    """Quit button with custom arrow key navigation."""
    
    BINDINGS = Button.BINDINGS + [
        Binding("up", "focus_refresh", "Move to refresh button", show=False),
        Binding("left", "focus_refresh", "Move to refresh button", show=False),
        Binding("down", "focus_directory", "Move to directory", show=False),
        Binding("right", "focus_directory", "Move to directory", show=False),
    ]
    
    def action_focus_refresh(self) -> None:
        """Move focus to refresh button."""
        try:
            refresh_button = self.screen.query_one("#refresh_btn", NavigableRefreshButton)
            refresh_button.focus()
        except Exception:
            pass
    
    def action_focus_directory(self) -> None:
        """Move focus to directory display (completing the cycle)."""
        try:
            dir_display = self.screen.query_one("#dir_display", NavigableStatic)
            dir_display.focus()
        except Exception:
            pass


class ConfigSelectorScreen(Screen):
    """Screen for selecting configuration files when none is specified."""
    
    CSS = """
    ConfigSelectorScreen {
        background: $surface;
    }
    
    .header {
        height: 5;
        content-align: center middle;
        margin-bottom: 1;
    }
    
    .directory-info {
        height: 3;
        margin-bottom: 1;
        align: center middle;
    }
    
    .directory-path {
        width: 1fr;
        content-align: left middle;
        padding: 0 2;
        border: solid $secondary;
        background: $panel;
        text-style: italic;
        color: $text-muted;
    }
    
    .directory-path:hover {
        background: $secondary;
        color: $text;
        text-style: none;
        border: solid $primary;
    }
    
    .directory-path:focus {
        background: $primary;
        color: $background;
        border: solid $accent;
        text-style: bold;
    }
    
    .table-container {
        height: 1fr;
        margin-bottom: 1;
        min-height: 10;
    }
    
    .button-row {
        height: 3;
        align: center middle;
    }
    
    
    DataTable {
        margin: 1;
        height: 1fr;
        border: solid $primary;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("enter", "select_file", "Select", priority=True),
        Binding("d", "change_directory", "Change Dir", priority=True),
        Binding("r", "refresh", "Refresh", priority=True),
        Binding("q", "quit", "Quit", priority=True),
        Binding("escape", "quit", "Quit", priority=True),
    ]
    
    def __init__(self, initial_directory: Optional[Path] = None):
        """Initialize the config selector screen.
        
        Args:
            initial_directory: Directory to start browsing from
        """
        super().__init__()
        self.current_directory = initial_directory or Path("configs")
        self.selected_file: Optional[Path] = None
        
    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Static("Choose a Configuration File", classes="header")
        
        with Container(classes="directory-info"):
            yield NavigableStatic(f"Current directory: {self.current_directory}/", id="dir_display", classes="directory-path")
        
        with Container(classes="table-container"):
            table = NavigableDataTable(id="file_table", cursor_type="row")
            table.add_columns("Name", "Modified", "MCP Servers")
            yield table
        
        with Horizontal(classes="button-row"):
            yield NavigableSelectButton("Select", id="select_btn", variant="primary")
            yield NavigableRefreshButton("Refresh", id="refresh_btn")
            yield NavigableQuitButton("Quit", id="quit_btn")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        self.refresh_file_list()
        # Set focus to the file table so it's immediately interactive
        table = self.query_one("#file_table", NavigableDataTable)
        table.focus()
    
    def refresh_file_list(self) -> None:
        """Refresh the file listing in the current directory."""
        table = self.query_one("#file_table", NavigableDataTable)
        table.clear()
        
        try:
            files = self._discover_config_files()
            
            if not files:
                table.add_row("No .yaml files found", "", "")
                return
            
            for file_path, modified, servers in files:
                # Format the display name with relative path from current directory
                try:
                    display_name = str(file_path.relative_to(self.current_directory))
                except ValueError:
                    display_name = str(file_path)
                
                table.add_row(display_name, modified, servers)
                
        except (OSError, PermissionError) as e:
            table.add_row(f"Error reading directory: {e}", "", "")
        except Exception as e:
            # Debug: catch any other exceptions
            table.add_row(f"Unexpected error: {e}", "", "")
    
    def _discover_config_files(self) -> List[Tuple[Path, str, str]]:
        """Discover YAML configuration files in the current directory.
        
        Returns:
            List of tuples containing (file_path, formatted_modified_time, servers_list)
        """
        files = []
        
        if not self.current_directory.exists():
            # Debug
            return [("Directory not found", "", "")]
        
        try:
            # Only search in current directory and immediate subdirectories, not recursively
            # First, get files in current directory
            for file_path in self.current_directory.glob("*.yaml"):
                if file_path.is_file():
                    stat = file_path.stat()
                    modified = self._format_timestamp(stat.st_mtime)
                    servers = self._extract_server_names(file_path)
                    files.append((file_path, modified, servers))
            
            # Then get files in immediate subdirectories (one level deep)
            for subdir in self.current_directory.iterdir():
                if subdir.is_dir() and not subdir.name.startswith('.'):  # Skip hidden dirs like .venv
                    for file_path in subdir.glob("*.yaml"):
                        if file_path.is_file():
                            stat = file_path.stat()
                            modified = self._format_timestamp(stat.st_mtime)
                            servers = self._extract_server_names(file_path)
                            files.append((file_path, modified, servers))
            
            # Sort: current directory files first, then subdirectory files
            # Within each group, sort alphabetically
            def sort_key(file_tuple):
                file_path = file_tuple[0]
                # Check if file is in current directory (parent == current_directory)
                is_current_dir = file_path.parent == self.current_directory
                # Return (priority, name) - lower priority comes first
                return (0 if is_current_dir else 1, str(file_path).lower())
            
            files.sort(key=sort_key)
            
        except (OSError, PermissionError) as e:
            return [(f"Permission error: {e}", "", "")]
        except Exception as e:
            return [(f"Error: {e}", "", "")]
        
        return files
    
    def _format_timestamp(self, timestamp: float) -> str:
        """Format a timestamp for display.
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Formatted time string
        """
        file_time = datetime.fromtimestamp(timestamp)
        now = datetime.now()
        
        # Calculate difference
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
        """Extract MCP server names from a config file using the proper config loader.
        
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
            
            # Truncate if the text gets too long for display (around 80 chars)
            if len(servers_text) > 80:
                # Find a good place to truncate (after a comma if possible)
                truncate_pos = 77
                comma_pos = servers_text.rfind(", ", 0, truncate_pos)
                if comma_pos > 50:  # Make sure we don't truncate too early
                    return servers_text[:comma_pos] + "..."
                else:
                    return servers_text[:truncate_pos] + "..."
            else:
                return servers_text
                
        except Exception as e:
            # Handle various config loading errors
            error_msg = str(e).lower()
            if "yaml" in error_msg or "parsing" in error_msg:
                return "Invalid YAML"
            elif "permission" in error_msg or "access" in error_msg:
                return "Read error"
            elif "proxy" in error_msg and "section" in error_msg:
                return "Missing proxy section"
            elif "path validation failed" in error_msg:
                return "Path validation error"
            elif "validation" in error_msg or "invalid" in error_msg:
                return "Invalid config"
            else:
                return "Parse error"
    
    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in the file table."""
        import tempfile
        debug_file = tempfile.gettempdir() + "/watchgate_debug.log"
        with open(debug_file, "a") as f:
            f.write(f"DEBUG: Row selected event fired: {event.row_key}\n")
        table = self.query_one("#file_table", NavigableDataTable)
        
        if table.row_count == 0:
            return
        
        # Get the selected row data
        row_key = event.row_key
        name_cell = table.get_cell(row_key, "Name")
        
        if name_cell and not name_cell.startswith("No .yaml files") and not name_cell.startswith("Error"):
            # Resolve the full path
            selected_path = self.current_directory / name_cell
            if selected_path.exists() and selected_path.is_file():
                self.selected_file = selected_path
    
    @on(Button.Pressed, "#select_btn")
    def on_select_button(self) -> None:
        """Handle select button press."""
        import tempfile
        debug_file = tempfile.gettempdir() + "/watchgate_debug.log"
        with open(debug_file, "a") as f:
            f.write(f"DEBUG: Select button pressed\n")
        self.action_select_file()
    
    @on(Button.Pressed, "#refresh_btn")
    def on_refresh_button(self) -> None:
        """Handle refresh button press."""
        self.action_refresh()
    
    
    @on(Button.Pressed, "#quit_btn")
    def on_quit_button(self) -> None:
        """Handle quit button press."""
        self.action_quit()
    
    def action_select_file(self) -> None:
        """Select the currently highlighted file and load its configuration."""
        import tempfile
        debug_file = tempfile.gettempdir() + "/watchgate_debug.log"
        with open(debug_file, "a") as f:
            f.write(f"DEBUG: action_select_file called via ENTER or button\n")
        
        
        # Check if the directory display is focused - if so, open directory browser instead
        if self.focused and getattr(self.focused, 'id', None) == "dir_display":
            with open(debug_file, "a") as f:
                f.write(f"DEBUG: Directory display focused, opening directory browser\n")
            self.action_change_directory()
            return
        
        table = self.query_one("#file_table", NavigableDataTable)
        
        # Get the currently highlighted row
        selected_path = None
        with open(debug_file, "a") as f:
            f.write(f"DEBUG: Table row count: {table.row_count}\n")
        if table.row_count > 0:
            try:
                # Get the row and column keys for the cursor position
                with open(debug_file, "a") as f:
                    f.write(f"DEBUG: Cursor coordinate: {table.cursor_coordinate}\n")
                row_key, column_key = table.coordinate_to_cell_key(table.cursor_coordinate)
                with open(debug_file, "a") as f:
                    f.write(f"DEBUG: Row key: {row_key}, Column key: {column_key}\n")
                # Get the cell value using the row key and Name column
                # Get all column keys as a list to access the first one
                column_keys = list(table.columns.keys())
                if not column_keys:
                    with open(debug_file, "a") as f:
                        f.write(f"DEBUG: No columns found in table\n")
                    return
                
                name_column_key = column_keys[0]  # First column is "Name"
                with open(debug_file, "a") as f:
                    f.write(f"DEBUG: Using column key: {name_column_key}\n")
                name_cell = table.get_cell(row_key, name_column_key)
                with open(debug_file, "a") as f:
                    f.write(f"DEBUG: Name cell value: '{name_cell}'\n")
                
                if name_cell and not str(name_cell).startswith("No .yaml files") and not str(name_cell).startswith("Error"):
                    selected_path = self.current_directory / str(name_cell)
                    with open(debug_file, "a") as f:
                        f.write(f"DEBUG: Constructed path: {selected_path}\n")
                        f.write(f"DEBUG: Path exists: {selected_path.exists()}, Is file: {selected_path.is_file() if selected_path.exists() else 'N/A'}\n")
                    if selected_path.exists() and selected_path.is_file():
                        self.selected_file = selected_path
                        with open(debug_file, "a") as f:
                            f.write(f"DEBUG: File selected successfully\n")
                else:
                    with open(debug_file, "a") as f:
                        f.write(f"DEBUG: Name cell invalid or error message\n")
            except Exception as e:
                with open(debug_file, "a") as f:
                    f.write(f"DEBUG: Exception in file selection: {e}\n")
                    import traceback
                    f.write(traceback.format_exc())
        
        # Try to load the config to validate it
        if selected_path and selected_path.exists():
            try:
                import tempfile
                debug_file = tempfile.gettempdir() + "/watchgate_debug.log"
                with open(debug_file, "a") as f:
                    f.write(f"DEBUG: Config selector loading {selected_path}\n")
                # Load configuration using ConfigLoader to validate it
                loader = ConfigLoader()
                config = loader.load_from_file(selected_path)
                with open(debug_file, "a") as f:
                    f.write(f"DEBUG: Config selector loaded successfully, dismissing with file\n")
                
                # Store the selected file and dismiss with it
                self.selected_file = selected_path
                self.dismiss(self.selected_file)
                return
                
            except Exception as e:
                # Show error and ring bell
                import tempfile
                debug_file = tempfile.gettempdir() + "/watchgate_debug.log"
                with open(debug_file, "a") as f:
                    f.write(f"DEBUG: Config selector error: {e}\n")
                    import traceback
                    f.write(traceback.format_exc())
                self.app.bell()
                return
        else:
            # Show message that no file is selected
            self.app.bell()
    
    def action_change_directory(self) -> None:
        """Change the current directory."""
        from .directory_browser_modal import DirectoryBrowserModal
        self.app.push_screen(DirectoryBrowserModal(self.current_directory), self._on_directory_changed)
    
    def _on_directory_changed(self, new_directory: Optional[Path]) -> None:
        """Handle directory change result."""
        if new_directory and new_directory.exists():
            self.current_directory = new_directory
            self.query_one("#dir_display", NavigableStatic).update(f"Current directory: {self.current_directory}/")
            self.refresh_file_list()
    
    def _open_config_editor(self, config_path: Path, loaded_config) -> None:
        """Open the configuration editor with the selected file."""
        try:
            from .config_editor import ConfigEditorScreen
            editor_screen = ConfigEditorScreen(config_path, loaded_config)
            self.app.push_screen(editor_screen, self._on_config_editor_closed)
        except Exception as e:
            self.app.bell()
    
    def _on_config_editor_closed(self, result=None) -> None:
        """Handle config editor being closed."""
        # Refresh the file list in case the config was modified
        self.refresh_file_list()
    
    def action_refresh(self) -> None:
        """Refresh the file list."""
        self.refresh_file_list()
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()