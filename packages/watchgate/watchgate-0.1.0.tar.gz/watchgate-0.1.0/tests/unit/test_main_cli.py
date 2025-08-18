"""Unit tests for CLI main entry point."""

import logging
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch
import pytest

from watchgate.main import main, run_proxy, setup_logging


class TestCLIArgumentParsing:
    """Test argument parsing functionality."""
    
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_proxy_subcommand_default_config_path(self):
        """Test proxy subcommand with configuration file."""
        with patch('watchgate.main.argparse.ArgumentParser.parse_args') as mock_parse:
            mock_parse.return_value = MagicMock(
                command="proxy",
                config=Path("watchgate.yaml"),
                verbose=False
            )
            with patch('watchgate.main.run_proxy', new_callable=AsyncMock) as mock_run_proxy:
                with patch('watchgate.main.asyncio.run') as mock_asyncio_run:
                    main()
                    mock_asyncio_run.assert_called_once()
                    # Use assert_called_once_with since we're passing the coroutine to asyncio.run
                    mock_run_proxy.assert_called_once_with(Path("watchgate.yaml"), False)

    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_proxy_subcommand_custom_config_path(self):
        """Test proxy subcommand with custom configuration file via --config argument."""
        custom_path = Path("/custom/path/config.yaml")
        with patch('watchgate.main.argparse.ArgumentParser.parse_args') as mock_parse:
            mock_parse.return_value = MagicMock(
                command="proxy",
                config=custom_path,
                verbose=False
            )
            # Use new_callable to properly handle the async function
            with patch('watchgate.main.run_proxy', new_callable=AsyncMock) as mock_run_proxy:
                with patch('watchgate.main.asyncio.run') as mock_asyncio_run:
                    main()
                    mock_asyncio_run.assert_called_once()
                    # Use assert_called_once_with since we're passing the coroutine to asyncio.run
                    mock_run_proxy.assert_called_once_with(custom_path, False)

    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_proxy_subcommand_verbose_flag(self):
        """Test proxy subcommand verbose logging activation via --verbose flag."""
        with patch('watchgate.main.argparse.ArgumentParser.parse_args') as mock_parse:
            mock_parse.return_value = MagicMock(
                command="proxy",
                config=Path("watchgate.yaml"),
                verbose=True
            )
            # Use new_callable to properly handle the async function
            with patch('watchgate.main.run_proxy', new_callable=AsyncMock) as mock_run_proxy:
                with patch('watchgate.main.asyncio.run') as mock_asyncio_run:
                    main()
                    mock_asyncio_run.assert_called_once()
                    # Use assert_called_once_with since we're passing the coroutine to asyncio.run
                    mock_run_proxy.assert_called_once_with(Path("watchgate.yaml"), True)
    
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_default_behavior_calls_tui(self):
        """Test that default behavior (no subcommand) calls TUI mode."""
        with patch('watchgate.main.argparse.ArgumentParser.parse_args') as mock_parse:
            mock_parse.return_value = MagicMock(
                command=None,
                config=None
            )
            with patch('watchgate.main._handle_tui_mode') as mock_handle_tui:
                main()
                mock_handle_tui.assert_called_once_with(None)
        
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_version_display(self):
        """Test version information display via --version."""
        with patch('sys.argv', ['watchgate', '--version']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # argparse exits with code 0 for --version
            assert exc_info.value.code == 0
        
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_help_output(self):
        """Test help text and usage examples generation."""
        with patch('sys.argv', ['watchgate', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # argparse exits with code 0 for --help
            assert exc_info.value.code == 0


class TestCLIIntegration:
    """Test CLI integration with proxy components."""
    
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_config_file_not_found(self):
        """Test proper error handling for missing config files."""
        non_existent_path = Path("/non/existent/config.yaml")
        
        with patch('watchgate.main.setup_logging'):
            with patch('watchgate.main.ConfigLoader') as mock_loader_class:
                mock_loader = Mock()
                mock_loader.load_from_file.side_effect = FileNotFoundError("Config not found")
                mock_loader_class.return_value = mock_loader
                
                # The startup error handler will call sys.exit
                with patch('watchgate.cli.startup_error_handler.sys.exit') as mock_exit:
                    # Mock the minimal server to prevent it from running
                    with patch('watchgate.cli.startup_error_handler.StartupErrorNotifier'):
                        await run_proxy(non_existent_path, verbose=False)
                        mock_exit.assert_called_with(1)
        
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_invalid_config_format(self):
        """Test error handling for malformed YAML configuration."""
        config_path = Path("test.yaml")
        
        with patch('watchgate.main.setup_logging'):
            with patch('watchgate.main.ConfigLoader') as mock_loader_class:
                mock_loader = Mock()
                mock_loader.load_from_file.side_effect = ValueError("Invalid YAML")
                mock_loader_class.return_value = mock_loader
                
                # The startup error handler will call sys.exit
                with patch('watchgate.cli.startup_error_handler.sys.exit') as mock_exit:
                    # Mock the minimal server to prevent it from running
                    with patch('watchgate.cli.startup_error_handler.StartupErrorNotifier'):
                        await run_proxy(config_path, verbose=False)
                        mock_exit.assert_called_with(1)
        
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_keyboard_interrupt_handling(self):
        """Test graceful shutdown on Ctrl+C (SIGINT)."""
        config_path = Path("test.yaml")
        
        with patch('watchgate.main.setup_logging_from_config'):
            with patch('watchgate.main.ConfigLoader') as mock_loader_class:
                mock_loader = Mock()
                mock_config = Mock()
                mock_loader.load_from_file.return_value = mock_config
                mock_loader_class.return_value = mock_loader
                
                with patch('watchgate.main.MCPProxy') as mock_proxy_class:
                    # Create a proper AsyncMock for the proxy context manager
                    mock_proxy = Mock()
                    mock_proxy.__aenter__ = AsyncMock(return_value=mock_proxy)
                    mock_proxy.__aexit__ = AsyncMock(return_value=None)
                    mock_proxy.run = AsyncMock(side_effect=KeyboardInterrupt())
                    mock_proxy_class.return_value = mock_proxy
                    
                    # Should not raise exception or call sys.exit
                    await run_proxy(config_path, verbose=False)
        
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_async_proxy_integration(self):
        """Test CLI integration with asyncio-based proxy server."""
        config_path = Path("test.yaml")
        
        with patch('watchgate.main.setup_logging_from_config'):
            with patch('watchgate.main.ConfigLoader') as mock_loader_class:
                mock_loader = Mock()
                mock_config = Mock()
                mock_loader.load_from_file.return_value = mock_config
                mock_loader_class.return_value = mock_loader
                
                with patch('watchgate.main.MCPProxy') as mock_proxy_class:
                    # Create a proper AsyncMock for the proxy context manager
                    mock_proxy = Mock()
                    mock_proxy.__aenter__ = AsyncMock(return_value=mock_proxy)
                    mock_proxy.__aexit__ = AsyncMock(return_value=None)
                    mock_proxy.run = AsyncMock(return_value=None)
                    mock_proxy_class.return_value = mock_proxy
                    
                    await run_proxy(config_path, verbose=False)
                    
                    # Verify proxy was created with config and config_directory and run
                    mock_proxy_class.assert_called_once_with(mock_config, mock_loader.config_directory)
                    # Use assert_awaited_once for async mock
                    mock_proxy.run.assert_awaited_once()
        
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_logging_configuration(self):
        """Test logging setup and verbosity level configuration."""
        # Test non-verbose logging
        with patch('watchgate.main.logging.getLogger') as mock_get_logger, \
             patch('watchgate.main.logging.StreamHandler') as mock_stream_handler:
            
            mock_root_logger = Mock()
            mock_asyncio_logger = Mock()
            
            def mock_logger_side_effect(name=None):
                if name == 'asyncio':
                    return mock_asyncio_logger
                else:  # name is None for root logger
                    return mock_root_logger
            
            mock_get_logger.side_effect = mock_logger_side_effect
            mock_handler = Mock()
            mock_stream_handler.return_value = mock_handler
            
            setup_logging(verbose=False)
            
            # Verify root logger setup
            mock_root_logger.setLevel.assert_called_with(logging.INFO)
            mock_root_logger.handlers.clear.assert_called_once()
            mock_root_logger.addHandler.assert_called_with(mock_handler)
            
            # Verify asyncio logger setup
            mock_asyncio_logger.setLevel.assert_called_with(logging.WARNING)
        
        # Test verbose logging
        with patch('watchgate.main.logging.getLogger') as mock_get_logger, \
             patch('watchgate.main.logging.StreamHandler') as mock_stream_handler:
            
            mock_root_logger = Mock()
            mock_asyncio_logger = Mock()
            
            def mock_logger_side_effect(name=None):
                if name == 'asyncio':
                    return mock_asyncio_logger
                else:  # name is None for root logger
                    return mock_root_logger
            
            mock_get_logger.side_effect = mock_logger_side_effect
            mock_handler = Mock()
            mock_stream_handler.return_value = mock_handler
            
            setup_logging(verbose=True)
            
            # Verify root logger setup with DEBUG level
            mock_root_logger.setLevel.assert_called_with(logging.DEBUG)
            mock_root_logger.handlers.clear.assert_called_once()
            mock_root_logger.addHandler.assert_called_with(mock_handler)


class TestCLIErrorHandling:
    """Test CLI error handling and exit codes."""
    
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_unexpected_error_handling(self):
        """Test handling of unexpected errors with proper exit codes."""
        config_path = Path("test.yaml")
        
        with patch('watchgate.main.setup_logging'):
            with patch('watchgate.main.ConfigLoader') as mock_loader_class:
                mock_loader = Mock()
                mock_loader.load_from_file.side_effect = RuntimeError("Unexpected error")
                mock_loader_class.return_value = mock_loader
                
                # The startup error handler will call sys.exit
                with patch('watchgate.cli.startup_error_handler.sys.exit') as mock_exit:
                    # Mock the minimal server to prevent it from running
                    with patch('watchgate.cli.startup_error_handler.StartupErrorNotifier'):
                        await run_proxy(config_path, verbose=False)
                        mock_exit.assert_called_with(1)
        
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_main_keyboard_interrupt_handling(self):
        """Test main function handles KeyboardInterrupt gracefully."""
        with patch('watchgate.main.argparse.ArgumentParser.parse_args') as mock_parse:
            mock_parse.return_value = MagicMock(
                config=Path("watchgate.yaml"),
                verbose=False
            )
            with patch('watchgate.main.asyncio.run') as mock_run:
                mock_run.side_effect = KeyboardInterrupt()
                
                # Should not raise exception
                main()
