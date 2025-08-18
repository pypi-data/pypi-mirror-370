"""Main Watchgate TUI application."""

from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button
from textual.binding import Binding


class WatchgateConfigApp(App):
    """Main Watchgate configuration TUI application."""
    
    CSS = """
    .main-content {
        padding: 1;
        margin: 1;
        border: solid $primary;
    }
    
    .welcome-text {
        text-align: center;
        margin: 2;
    }
    
    .config-info {
        text-align: center;
        color: $accent;
        margin-bottom: 1;
    }
    
    .config-error {
        text-align: center;
        color: $warning;
        margin-bottom: 1;
    }
    
    .config-help {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }
    
    .button-row {
        align: center middle;
        height: auto;
        margin-top: 2;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    TITLE = "Watchgate Configuration"
    SUB_TITLE = "Terminal User Interface"
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("ctrl+o", "open_config", "Open Config", priority=True),
        ("?", "help", "Help"),
    ]
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the TUI application.
        
        Args:
            config_path: Optional path to configuration file
        """
        super().__init__()
        self.config_path = config_path
        self.config_exists = config_path.exists() if config_path else False
        self.config_error = None
        self.should_show_config_picker = False
        
        # If config was specified but doesn't exist, note it
        if config_path and not self.config_exists:
            self.config_error = f"Configuration file not found: {config_path}"
        elif config_path is None:
            # No config specified - should immediately open config picker
            self.should_show_config_picker = True
    
    def compose(self) -> ComposeResult:
        """Compose the main application layout."""
        # Standard header and footer
        yield Header()
        
        # Main content area
        with Container(classes="main-content"):
            with Vertical():
                yield Static(
                    "Welcome to Watchgate Configuration",
                    classes="welcome-text"
                )
                
                # Show config status with appropriate styling
                if self.config_error:
                    # Config file specified but not found - show warning
                    yield Static(
                        f"⚠️  {self.config_error}",
                        classes="config-error"
                    )
                    yield Static(
                        "Don't worry! You can create it or choose another.",
                        classes="config-help"
                    )
                elif self.config_path and self.config_exists:
                    # Valid config file
                    yield Static(
                        f"📄 Configuration: {self.config_path}",
                        classes="config-info"
                    )
                else:
                    # No config specified
                    yield Static(
                        "No configuration file specified",
                        classes="config-info"
                    )
                
                yield Static(
                    "\n🚧 Configuration Interface Coming Soon 🚧\n\n"
                    "This is a basic stub implementation to demonstrate the TUI framework.\n\n"
                    "Features being developed:\n"
                    "• Visual configuration editor\n"
                    "• Plugin management interface\n"
                    "• Real-time server status\n"
                    "• Security policy configuration\n"
                    "• Hot-reload configuration updates\n",
                    classes="welcome-text"
                )
                
                with Horizontal(classes="button-row"):
                    if self.config_error:
                        # Config file missing - show recovery options
                        yield Button(f"Create {self.config_path.name}", id="create_missing_config", variant="primary")
                        yield Button("Choose Different Config", id="open_config")
                        yield Button("Start Fresh", id="start_fresh")
                    else:
                        # Normal options
                        yield Button("Create Config", id="create_config")
                        yield Button("Open Config", id="open_config") 
                    yield Button("Exit", id="exit")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle app mounting - show config picker if no config specified."""
        import tempfile
        debug_file = tempfile.gettempdir() + "/watchgate_debug.log"
        with open(debug_file, "a") as f:
            f.write(f"DEBUG: App mounted, should_show_config_picker={self.should_show_config_picker}\n")
        if self.should_show_config_picker:
            # Show config selector directly when no config is specified
            with open(debug_file, "a") as f:
                f.write(f"DEBUG: Setting timer to show config selector\n")
            self.set_timer(0.05, self._show_config_selector)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "exit":
            self.exit()
        elif event.button.id == "create_config":
            self._show_placeholder_message("Create Config feature coming soon!")
        elif event.button.id == "create_missing_config":
            self._create_missing_config()
        elif event.button.id == "start_fresh":
            self._start_fresh()
        elif event.button.id == "open_config":
            self.action_open_config()
    
    def action_help(self) -> None:
        """Show help information."""
        self._show_placeholder_message(
            "Watchgate TUI Help\n\n"
            "Keyboard shortcuts:\n"
            "• q, Ctrl+C: Quit application\n"
            "• Ctrl+O: Open configuration file\n"
            "• ?: Show this help message\n\n"
            "This is a development stub. Full features coming soon!"
        )
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    def action_open_config(self) -> None:
        """Open configuration file picker modal."""
        from .screens.config_picker_modal import ConfigPickerModal
        self.push_screen(ConfigPickerModal(self.config_path), self._on_config_picked)
    
    def _show_config_selector(self) -> None:
        """Show config selector screen directly (bypassing the modal)."""
        import tempfile
        debug_file = tempfile.gettempdir() + "/watchgate_debug.log"
        with open(debug_file, "a") as f:
            f.write(f"DEBUG: _show_config_selector called\n")
        from .screens.config_selector import ConfigSelectorScreen
        # Start from configs directory if it exists, otherwise current working directory
        configs_dir = Path.cwd() / "configs"
        start_dir = configs_dir if configs_dir.exists() else Path.cwd()
        with open(debug_file, "a") as f:
            f.write(f"DEBUG: Pushing ConfigSelectorScreen with start_dir={start_dir}\n")
        self.push_screen(ConfigSelectorScreen(start_dir), self._on_config_selected)
    
    def _show_placeholder_message(self, message: str) -> None:
        """Show a placeholder message (temporary implementation)."""
        # For now, just update the main text area with the message
        # In the future, this would show a proper modal/dialog
        content = self.query_one(".welcome-text", Static)
        content.update(message)
    
    def _on_config_selected(self, selected_config: Optional[Path]) -> None:
        """Handle config selection from the config selector screen.
        
        Args:
            selected_config: The selected configuration file path, or None if cancelled
        """
        import tempfile
        debug_file = tempfile.gettempdir() + "/watchgate_debug.log"
        with open(debug_file, "a") as f:
            f.write(f"DEBUG: Config selected callback called with: {selected_config}\n")
        if selected_config:
            with open(debug_file, "a") as f:
                f.write(f"DEBUG: Calling _load_config with {selected_config}\n")
            self._load_config(selected_config)
        else:
            with open(debug_file, "a") as f:
                f.write(f"DEBUG: No config selected, user cancelled\n")
            # User cancelled
            if self.should_show_config_picker:
                # If we showed the selector because no config was specified initially,
                # exit the app since there's nothing meaningful to show
                self.exit()
            # Otherwise, just return to main screen
    
    def _on_config_picked(self, picked_config: Optional[Path | str]) -> None:
        """Handle config selection from the config picker modal.
        
        Args:
            picked_config: The selected configuration file path, special action string, or None
        """
        if picked_config is None:
            # User cancelled
            if self.should_show_config_picker:
                # If we showed the picker because no config was specified initially,
                # exit the app since there's nothing meaningful to show
                self.exit()
            return
        
        if isinstance(picked_config, str):
            # Handle special actions
            if picked_config == "__CREATE_NEW__":
                self._show_placeholder_message("Create new config wizard coming soon!")
            elif picked_config == "__CREATE_DEFAULT__":
                self._show_placeholder_message("Create default config coming soon!")
        else:
            # Normal config file path
            self._load_config(picked_config)
    
    def _create_missing_config(self) -> None:
        """Handle creating the missing config file."""
        self._show_placeholder_message(
            f"Create missing config feature coming soon!\n\n"
            f"This would create: {self.config_path}\n\n"
            "For now, you can:\n"
            "• Use 'Choose Different Config' to select an existing file\n"
            "• Use 'Start Fresh' to work without a config file\n"
            "• Manually create the file and restart"
        )
    
    def _start_fresh(self) -> None:
        """Handle starting fresh without a config file."""
        # Clear the config path and error
        self.config_path = None
        self.config_exists = False
        self.config_error = None
        
        # Update the UI - refresh the main content
        self._show_placeholder_message(
            "Started fresh without a configuration file.\n\n"
            "🚧 Configuration Interface Coming Soon 🚧\n\n"
            "You can create a new configuration using the interface\n"
            "or choose an existing one with Ctrl+O."
        )
    
    def _load_config(self, config_path: Path) -> None:
        """Load a configuration file and update the UI.
        
        Args:
            config_path: Path to the configuration file to load
        """
        # Update the app's config path and status
        self.config_path = config_path
        self.config_exists = config_path.exists() if config_path else False
        self.config_error = None
        self.should_show_config_picker = False  # Clear the flag since we now have a config
        
        if config_path and not self.config_exists:
            self.config_error = f"Configuration file not found: {config_path}"
            # Update the welcome message to show the error
            self._show_placeholder_message(
                f"⚠️  {self.config_error}\n\n"
                "The configuration file you specified doesn't exist.\n"
                "You can create it, choose a different file, or start fresh.\n\n"
                "Press Ctrl+O to open the file picker."
            )
        else:
            # Try to load and open the config editor
            try:
                import tempfile
                debug_file = tempfile.gettempdir() + "/watchgate_debug.log"
                with open(debug_file, "a") as f:
                    f.write(f"DEBUG: Loading config from {config_path}\n")
                from watchgate.config.loader import ConfigLoader
                from .screens.config_editor import ConfigEditorScreen
                
                # Load the configuration
                loader = ConfigLoader()
                with open(debug_file, "a") as f:
                    f.write(f"DEBUG: Created config loader\n")
                loaded_config = loader.load_from_file(config_path)
                with open(debug_file, "a") as f:
                    f.write(f"DEBUG: Config loaded successfully, creating editor screen\n")
                
                # Open the config editor directly
                editor_screen = ConfigEditorScreen(config_path, loaded_config)
                with open(debug_file, "a") as f:
                    f.write(f"DEBUG: Editor screen created, pushing to app\n")
                self.push_screen(editor_screen)
                with open(debug_file, "a") as f:
                    f.write(f"DEBUG: Editor screen pushed successfully\n")
                
            except Exception as e:
                # If loading fails, show error message
                import tempfile
                debug_file = tempfile.gettempdir() + "/watchgate_debug.log"
                with open(debug_file, "a") as f:
                    f.write(f"DEBUG: Error loading config: {e}\n")
                    import traceback
                    f.write(traceback.format_exc())
                self._show_placeholder_message(
                    f"❌ Error loading configuration: {e}\n\n"
                    "Please check your configuration file syntax.\n\n"
                    "Press Ctrl+O to choose a different configuration file."
                )