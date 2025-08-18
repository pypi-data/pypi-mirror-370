"""Unit tests for the TUI ConfigSelectorScreen."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from textual.app import App, ComposeResult
from textual.widgets import DataTable

from watchgate.tui.screens.config_selector import ConfigSelectorScreen


class ConfigSelectorTestApp(App):
    """Test app wrapper for ConfigSelectorScreen testing."""
    
    def __init__(self, initial_directory: Path):
        super().__init__()
        self.initial_directory = initial_directory
    
    def compose(self) -> ComposeResult:
        return []
    
    def on_mount(self) -> None:
        """Mount the config selector screen for testing."""
        self.push_screen(ConfigSelectorScreen(self.initial_directory))


class TestConfigSelectorScreen:
    """Test ConfigSelectorScreen widget functionality."""
    
    @pytest.mark.asyncio
    async def test_file_table_gets_focus_on_mount(self):
        """Test that the DataTable widget receives focus when the screen mounts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a test YAML file
            test_file = temp_path / "test-config.yaml"
            test_file.write_text("# Test configuration\ntest: value\n")
            
            # Create test app with the config selector screen
            app = ConfigSelectorTestApp(temp_path)
            
            # Run the app in test mode
            async with app.run_test() as pilot:
                # Wait for the screen to mount and populate
                await pilot.pause()
                
                # Get the DataTable widget from the current screen
                table = app.screen.query_one("#file_table", DataTable)
                
                # Verify that the table has focus
                assert table.has_focus, "DataTable should have focus after mounting"
                
                # Verify that at least one file was found
                assert table.row_count > 0, "Should have found at least one YAML file"
    
    @pytest.mark.asyncio
    async def test_keyboard_navigation_works_immediately(self):
        """Test that keyboard navigation works immediately after screen loads."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create multiple test YAML files
            for i in range(3):
                test_file = temp_path / f"config-{i}.yaml"
                test_file.write_text(f"# Test configuration {i}\ntest: value{i}\n")
            
            app = ConfigSelectorTestApp(temp_path)
            
            async with app.run_test() as pilot:
                await pilot.pause()
                
                table = app.screen.query_one("#file_table", DataTable)
                
                # Verify table has focus and files
                assert table.has_focus
                assert table.row_count >= 3
                
                # Test that we can navigate immediately without clicking first
                initial_coordinate = table.cursor_coordinate
                
                # Press down arrow to move cursor
                await pilot.press("down")
                await pilot.pause()
                
                # Verify cursor moved
                new_coordinate = table.cursor_coordinate
                assert new_coordinate != initial_coordinate, "Cursor should have moved with down arrow"
    
    @pytest.mark.asyncio
    async def test_action_bindings_work(self):
        """Test that key bindings are properly set up and respond to input."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a test YAML file
            test_file = temp_path / "test-config.yaml"
            test_file.write_text("# Test configuration\ntest: value\n")
            
            app = ConfigSelectorTestApp(temp_path)
            
            async with app.run_test() as pilot:
                await pilot.pause()
                
                table = app.screen.query_one("#file_table", DataTable)
                assert table.has_focus
                assert table.row_count > 0
                
                # Test that 'r' key triggers refresh (this should not crash)
                await pilot.press("r")
                await pilot.pause()
                
                # Table should still have focus after refresh
                assert table.has_focus
                
                # Test that we can navigate with arrow keys
                initial_coordinate = table.cursor_coordinate
                await pilot.press("down")
                await pilot.pause()
                
                # Cursor position may or may not change depending on table content,
                # but the key press should not crash the application
    
    @pytest.mark.asyncio
    async def test_no_files_shows_appropriate_message(self):
        """Test that empty directory shows appropriate message."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            # Don't create any YAML files
            
            app = ConfigSelectorTestApp(temp_path)
            
            async with app.run_test() as pilot:
                await pilot.pause()
                
                table = app.screen.query_one("#file_table", DataTable)
                
                # Should still have focus even with no files
                assert table.has_focus
                
                # Should show a message about no files
                assert table.row_count == 1, "Should show one row with 'no files' message"
                
                # Get the first (and only) row content
                first_row_key = list(table.rows.keys())[0]
                # Get the first column (Name column)
                first_column_key = list(table.columns.keys())[0]
                name_cell = table.get_cell(first_row_key, first_column_key)
                
                assert "No .yaml files found" in str(name_cell)
    
    @pytest.mark.asyncio
    async def test_refresh_maintains_focus(self):
        """Test that refreshing the file list maintains table focus."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create initial test file
            test_file = temp_path / "test-config.yaml"
            test_file.write_text("# Test configuration\ntest: value\n")
            
            app = ConfigSelectorTestApp(temp_path)
            
            async with app.run_test() as pilot:
                await pilot.pause()
                
                table = app.screen.query_one("#file_table", DataTable)
                assert table.has_focus
                
                # Press 'r' to refresh
                await pilot.press("r")
                await pilot.pause()
                
                # Table should still have focus after refresh
                assert table.has_focus, "DataTable should maintain focus after refresh"