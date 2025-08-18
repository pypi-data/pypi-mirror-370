"""Directory selection dialog for Watchgate TUI."""

from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static


class DirectoryInputScreen(ModalScreen[Optional[Path]]):
    """Modal screen for entering a directory path."""
    
    CSS = """
    DirectoryInputScreen {
        align: center middle;
    }
    
    .dialog {
        width: 60;
        height: 15;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }
    
    .title {
        text-align: center;
        margin-bottom: 1;
    }
    
    .input-container {
        margin-bottom: 1;
    }
    
    .suggestions {
        height: 6;
        margin-bottom: 1;
    }
    
    .button-row {
        align: center middle;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def __init__(self, current_directory: Path):
        """Initialize the directory input dialog.
        
        Args:
            current_directory: The current directory to show as default
        """
        super().__init__()
        self.current_directory = current_directory
    
    def compose(self) -> ComposeResult:
        """Compose the dialog layout."""
        with Container(classes="dialog"):
            yield Static("Change Directory", classes="title")
            
            with Container(classes="input-container"):
                yield Static("Enter path to configuration directory:")
                yield Input(
                    value=str(self.current_directory),
                    placeholder="Enter directory path...",
                    id="dir_input"
                )
            
            with Container(classes="suggestions"):
                yield Static("Suggestions:")
                yield Static("• configs/")
                yield Static("• ~/watchgate/")
                yield Static("• ~/.config/watchgate/")
                yield Static("• /etc/watchgate/")
            
            with Horizontal(classes="button-row"):
                yield Button("OK", id="ok_btn", variant="primary")
                yield Button("Cancel", id="cancel_btn")
    
    def on_mount(self) -> None:
        """Focus the input when mounted."""
        self.query_one("#dir_input", Input).focus()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "ok_btn":
            self._handle_ok()
        elif event.button.id == "cancel_btn":
            self.dismiss(None)
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)."""
        if event.input.id == "dir_input":
            self._handle_ok()
    
    def _handle_ok(self) -> None:
        """Handle OK button or Enter key."""
        input_widget = self.query_one("#dir_input", Input)
        path_str = input_widget.value.strip()
        
        if not path_str:
            self.dismiss(None)
            return
        
        # Expand user home directory
        if path_str.startswith("~"):
            path_str = str(Path(path_str).expanduser())
        
        directory_path = Path(path_str)
        
        # Validate the directory
        if not directory_path.exists():
            # Show error in the input (for now, just ring bell)
            self.app.bell()
            return
        
        if not directory_path.is_dir():
            # Show error that it's not a directory
            self.app.bell()
            return
        
        self.dismiss(directory_path)