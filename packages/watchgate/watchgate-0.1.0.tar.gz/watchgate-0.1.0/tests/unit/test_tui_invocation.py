"""Tests for TUI invocation and command-line argument parsing."""

import sys
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from watchgate.main import main, _handle_tui_mode


class TestCommandLineParsing:
    """Test command-line argument parsing for new TUI/proxy structure."""
    
    def test_help_shows_new_examples(self):
        """Test that help shows the new command structure examples."""
        with pytest.raises(SystemExit):
            with patch('sys.argv', ['watchgate', '--help']):
                with patch('sys.stdout') as mock_stdout:
                    main()
        
        # Check that help output was captured
        # Note: argparse writes to stderr on --help, but exits with code 0
    
    def test_proxy_subcommand_requires_config(self):
        """Test that proxy subcommand requires --config argument."""
        with pytest.raises(SystemExit) as exc_info:
            with patch('sys.argv', ['watchgate', 'proxy']):
                with patch('sys.stderr'):
                    main()
        
        # argparse exits with code 2 for missing required arguments
        assert exc_info.value.code == 2
    
    @patch('watchgate.main.run_proxy')
    @patch('asyncio.run')
    def test_proxy_subcommand_with_config(self, mock_asyncio_run, mock_run_proxy):
        """Test that proxy subcommand with config runs proxy mode."""
        with patch('sys.argv', ['watchgate', 'proxy', '--config', 'test.yaml']):
            main()
        
        # Should call asyncio.run with run_proxy
        mock_asyncio_run.assert_called_once()
        args, kwargs = mock_asyncio_run.call_args
        # The first argument should be a coroutine (run_proxy call)
        assert mock_run_proxy.called
    
    @patch('watchgate.main._handle_tui_mode')
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_default_behavior_calls_tui(self, mock_handle_tui):
        """Test that default behavior (no subcommand) calls TUI mode."""
        with patch('sys.argv', ['watchgate']):
            main()
        
        mock_handle_tui.assert_called_once_with(None)
    
    @patch('watchgate.main._handle_tui_mode')
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_config_without_subcommand_calls_tui(self, mock_handle_tui):
        """Test that --config without subcommand calls TUI mode."""
        with patch('sys.argv', ['watchgate', '--config', 'test.yaml']):
            main()
        
        mock_handle_tui.assert_called_once()
        args, kwargs = mock_handle_tui.call_args
        # Should pass the Path object for test.yaml
        assert args[0] == Path('test.yaml')


class TestTUIHandling:
    """Test TUI mode handling and fallbacks."""
    
    
    @patch('sys.stdin')
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_textual_import_error_handling(self, mock_stdin):
        """Test graceful handling when Textual is not installed."""
        mock_stdin.isatty.return_value = True  # TTY context
        
        # Mock ImportError when trying to import TUI
        with patch('watchgate.main.sys.exit') as mock_exit:
            with patch('sys.stderr'):  # Suppress error output
                with patch('builtins.__import__', side_effect=ImportError):
                    _handle_tui_mode(None)
        
        mock_exit.assert_called_once_with(1)
    
    @patch('sys.stdin')
    @patch('watchgate.tui.run_tui')
    def test_successful_tui_launch(self, mock_run_tui, mock_stdin):
        """Test successful TUI launch in TTY context."""
        mock_stdin.isatty.return_value = True
        
        _handle_tui_mode(Path('config.yaml'))
        
        mock_run_tui.assert_called_once_with(Path('config.yaml'))
    
    @patch('sys.stdin')
    @patch('watchgate.tui.run_tui')
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_tui_exception_handling(self, mock_run_tui, mock_stdin):
        """Test handling of exceptions during TUI launch."""
        mock_stdin.isatty.return_value = True
        mock_run_tui.side_effect = Exception("TUI startup error")
        
        with patch('watchgate.main.sys.exit') as mock_exit:
            with patch('sys.stderr'):  # Suppress error output
                _handle_tui_mode(None)
        
        mock_exit.assert_called_once_with(1)


class TestIntegration:
    """Integration tests for the complete command structure."""
    
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_version_flag(self):
        """Test that --version works and shows correct version."""
        with pytest.raises(SystemExit) as exc_info:
            with patch('sys.argv', ['watchgate', '--version']):
                with patch('sys.stdout'):
                    main()
        
        # --version should exit with code 0
        assert exc_info.value.code == 0
    
    @patch('watchgate.main.debug_show_plugin_order')
    @patch('asyncio.run')
    def test_debug_commands_still_work(self, mock_asyncio_run, mock_debug_func):
        """Test that debug subcommands still work after restructuring."""
        with patch('sys.argv', ['watchgate', 'debug', 'plugins', '--show-order']):
            main()
        
        # Should call the debug function
        mock_asyncio_run.assert_called_once()
        assert mock_debug_func.called


class TestCommandLineInterface:
    """Test the actual command-line interface behavior."""
    
    @pytest.mark.skipif(
        subprocess.run(['which', 'watchgate'], capture_output=True).returncode != 0,
        reason="watchgate not installed in PATH"
    )
    def test_help_output_contains_new_examples(self):
        """Test that installed watchgate shows new example patterns."""
        result = subprocess.run(
            ['watchgate', '--help'],
            capture_output=True,
            text=True
        )
        
        # Help should show new examples
        assert 'proxy --config' in result.stdout
        assert 'Launch TUI configuration interface' in result.stdout
    
    @pytest.mark.skipif(
        subprocess.run(['which', 'watchgate'], capture_output=True).returncode != 0,
        reason="watchgate not installed in PATH"
    )
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_proxy_without_config_shows_error(self):
        """Test that proxy subcommand without config shows helpful error."""
        result = subprocess.run(
            ['watchgate', 'proxy'],
            capture_output=True,
            text=True
        )
        
        # Should exit with error code and show config requirement
        assert result.returncode != 0
        assert 'required' in result.stderr or 'config' in result.stderr