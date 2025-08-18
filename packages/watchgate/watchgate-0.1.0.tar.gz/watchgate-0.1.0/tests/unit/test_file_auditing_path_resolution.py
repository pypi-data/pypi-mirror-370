"""Tests for JsonAuditingPlugin path resolution improvements.

This test suite follows Test-Driven Development (TDD) methodology to verify
that JsonAuditingPlugin implements proper path resolution with the PathResolvablePlugin
interface and replaces silent fallbacks with proper error reporting.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from watchgate.plugins.auditing.json_lines import JsonAuditingPlugin
from watchgate.plugins.interfaces import PathResolvablePlugin


class TestJsonAuditingPluginPathResolution:
    """Test JsonAuditingPlugin path resolution with PathResolvablePlugin interface."""
    
    def test_implements_path_resolvable_interface(self):
        """Test that JsonAuditingPlugin implements PathResolvablePlugin interface."""
        # JsonAuditingPlugin should implement PathResolvablePlugin
        assert issubclass(JsonAuditingPlugin, PathResolvablePlugin)
        
        # Test that it can be instantiated
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            config = {"output_file": log_file, "critical": False}
            plugin = JsonAuditingPlugin(config)
            
            # Should have PathResolvablePlugin methods
            assert hasattr(plugin, 'set_config_directory')
            assert hasattr(plugin, 'validate_paths')
    
    def test_set_config_directory_resolves_relative_paths(self):
        """Test that set_config_directory properly resolves relative paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use a relative path within the temp directory
            relative_path = "logs/audit.log"
            config = {"output_file": relative_path, "critical": True}  # Use critical=True to prevent file creation
            plugin = JsonAuditingPlugin(config)
            
            # Initially relative paths are resolved to absolute paths for security
            # This prevents relative path confusion attacks
            initial_resolved = Path(relative_path).resolve()
            assert Path(plugin.output_file) == initial_resolved
            
            # Set config directory - should resolve relative path
            config_dir = Path(temp_dir) / "config_dir"
            plugin.set_config_directory(config_dir)
            
            # Should have resolved relative path
            expected_path = config_dir / relative_path
            assert Path(plugin.output_file) == expected_path.resolve()
    
    def test_set_config_directory_preserves_absolute_paths(self):
        """Test that set_config_directory preserves absolute paths."""
        absolute_path = "/var/log/watchgate/audit.log"
        config = {"output_file": absolute_path, "critical": False}
        plugin = JsonAuditingPlugin(config)
        
        # Absolute paths are resolved to their canonical form for security  
        expected_resolved = Path(absolute_path).resolve()
        assert Path(plugin.output_file) == expected_resolved
        
        # Set config directory - should preserve absolute path
        config_dir = Path("/config/dir")
        plugin.set_config_directory(config_dir)
        
        # Should still resolve to the same canonical absolute path
        expected_resolved = Path(absolute_path).resolve()
        assert Path(plugin.output_file) == expected_resolved
    
    def test_set_config_directory_handles_home_expansion(self):
        """Test that set_config_directory handles home directory expansion."""
        config = {"output_file": "~/logs/audit.log", "critical": True}  # Use critical=True to prevent file creation
        plugin = JsonAuditingPlugin(config)
        
        # Set config directory
        config_dir = Path("/config/dir")
        plugin.set_config_directory(config_dir)
        
        # Should have expanded ~ to home directory (not relative to config)
        import os
        expected_path = Path(os.path.expanduser("~/logs/audit.log"))
        assert Path(plugin.output_file) == expected_path
    
    def test_set_config_directory_with_invalid_type_raises_error(self):
        """Test that set_config_directory raises error for invalid config_directory type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            config = {"output_file": log_file, "critical": False}
            plugin = JsonAuditingPlugin(config)
            
            # Should raise TypeError for invalid type
            with pytest.raises(TypeError, match="config_directory must be str or Path"):
                plugin.set_config_directory(123)  # Invalid type
    
    def test_validate_paths_returns_empty_for_valid_paths(self):
        """Test that validate_paths returns empty list for valid paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            config = {"output_file": log_file, "critical": False}
            plugin = JsonAuditingPlugin(config)
            
            # Should return no errors for valid path
            errors = plugin.validate_paths()
            assert errors == []
    
    def test_validate_paths_returns_errors_for_invalid_parent_directory(self):
        """Test that validate_paths returns errors for invalid parent directory."""
        invalid_path = "/nonexistent/directory/test.log"
        config = {"output_file": invalid_path, "critical": False}
        plugin = JsonAuditingPlugin(config)
        
        # Should return error for invalid parent directory
        errors = plugin.validate_paths()
        assert len(errors) == 1
        assert "Parent directory does not exist" in errors[0]
        assert invalid_path in errors[0]
    
    def test_validate_paths_returns_errors_for_unwritable_directory(self):
        """Test that validate_paths returns errors for unwritable directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a directory but make it read-only
            readonly_dir = os.path.join(temp_dir, "readonly")
            os.mkdir(readonly_dir)
            os.chmod(readonly_dir, 0o444)  # Read-only
            
            log_file = os.path.join(readonly_dir, "test.log")
            config = {"output_file": log_file, "critical": False}
            plugin = JsonAuditingPlugin(config)
            
            try:
                # Should return error for unwritable directory
                errors = plugin.validate_paths()
                assert len(errors) == 1
                assert "No write permission" in errors[0]
            finally:
                # Restore permissions for cleanup
                os.chmod(readonly_dir, 0o755)


class TestJsonAuditingPluginImprovedErrorHandling:
    """Test improved error handling that replaces silent fallbacks."""
    
    def test_path_resolution_error_raises_for_critical_plugin(self):
        """Test that path resolution errors raise exceptions for critical plugins."""
        # Mock resolve_config_path to raise an error
        with patch('watchgate.plugins.auditing.base.resolve_config_path') as mock_resolve:
            mock_resolve.side_effect = ValueError("Invalid path")
            
            config = {
                "output_file": "test.log",
                "critical": True
            }
            
            plugin = JsonAuditingPlugin(config)
            
            # Should raise exception for critical plugin when setting config directory
            with pytest.raises(ValueError, match="Invalid path"):
                plugin.set_config_directory("/config")
    
    def test_path_resolution_error_logs_for_non_critical_plugin(self):
        """Test that path resolution errors are logged for non-critical plugins."""
        # Mock resolve_config_path to raise an error
        with patch('watchgate.plugins.auditing.base.resolve_config_path') as mock_resolve, \
             patch('watchgate.plugins.auditing.base.logging.getLogger') as mock_get_logger:
            
            mock_resolve.side_effect = ValueError("Invalid path")
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            config = {
                "output_file": "test.log",
                "critical": False
            }
            
            # Should handle error gracefully for non-critical plugin
            plugin = JsonAuditingPlugin(config)
            
            # Set config directory - should log error but not raise
            plugin.set_config_directory("/config")
            
            # Should have logged the error
            mock_logger.error.assert_called()
            error_call = mock_logger.error.call_args[0][0]
            assert "path resolution failed" in error_call.lower()
    
    def test_no_silent_fallback_on_path_resolution_failure(self, tmp_path):
        """Test that there are no silent fallbacks on path resolution failure."""
        # Mock resolve_config_path to raise an error
        with patch('watchgate.plugins.auditing.base.resolve_config_path') as mock_resolve:
            mock_resolve.side_effect = ValueError("Invalid path")
            
            relative_log_path = tmp_path / "relative_path.log"
            config = {
                "output_file": str(relative_log_path),
                "config_directory": "/config",
                "critical": False
            }
            
            # For non-critical plugins, should not silently fall back
            # Instead should use the original path and log the error
            plugin = JsonAuditingPlugin(config)
            
            # Should still have the original path, not a "resolved" fallback
            assert plugin.output_file == str(relative_log_path)
    
    def test_proper_error_context_in_initialization_failure(self):
        """Test that initialization failures provide proper error context."""
        # Use an invalid path that will cause initialization to fail
        invalid_path = "/nonexistent/deeply/nested/path/test.log"
        config = {"output_file": invalid_path, "critical": True}
        
        with pytest.raises(Exception) as exc_info:
            JsonAuditingPlugin(config)
        
        error_message = str(exc_info.value)
        
        # Should include helpful context
        assert "Critical auditing plugin JsonAuditingPlugin failed" in error_message
        assert "Current working directory:" in error_message
        assert "Configured log file path:" in error_message
        assert invalid_path in error_message
        
        # Should include actionable guidance
        assert "SOLUTION:" in error_message
    
    def test_initialization_provides_absolute_path_guidance(self):
        """Test that initialization failure provides guidance about absolute paths."""
        # Use a relative path that will fail due to permission issues
        # Mock os.access to return False for write permission to force an error
        with patch('os.access', return_value=False), \
             patch('pathlib.Path.mkdir') as mock_mkdir:
            # Make mkdir fail to trigger the exception path
            mock_mkdir.side_effect = PermissionError("Permission denied")
            
            relative_path = "logs/test.log"
            config = {"output_file": relative_path, "critical": True}
            
            with pytest.raises(Exception) as exc_info:
                JsonAuditingPlugin(config)
            
            error_message = str(exc_info.value)
            
            # Should identify the issue and provide solution
            # Note: Relative paths are now immediately resolved, so error will be about permissions
            assert "SOLUTION:" in error_message
            assert ("config_directory for path resolution" in error_message or 
                   "permission" in error_message.lower())
            assert relative_path in error_message
    
    def test_set_config_directory_validates_path_type(self):
        """Test that set_config_directory validates path type properly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            config = {"output_file": log_file, "critical": False}
            plugin = JsonAuditingPlugin(config)
            
            # Should validate input type
            with pytest.raises(TypeError, match="config_directory must be str or Path"):
                plugin.set_config_directory(None)
            
            with pytest.raises(TypeError, match="config_directory must be str or Path"):
                plugin.set_config_directory(123)
            
            with pytest.raises(TypeError, match="config_directory must be str or Path"):
                plugin.set_config_directory(["path"])
    
    def test_validate_paths_provides_specific_error_messages(self):
        """Test that validate_paths provides specific, actionable error messages."""
        # Test with completely invalid path
        invalid_path = "/definitely/does/not/exist/test.log"
        config = {"output_file": invalid_path, "critical": False}
        plugin = JsonAuditingPlugin(config)
        
        errors = plugin.validate_paths()
        assert len(errors) == 1
        
        error_message = errors[0]
        # Should be specific about the issue
        assert "Parent directory does not exist" in error_message
        assert invalid_path in error_message
        # Should provide the actual problematic path
        assert "/definitely/does/not/exist" in error_message


class TestJsonAuditingPluginConfigDirectoryHandling:
    """Test config_directory parameter handling improvements."""
    
    def test_config_directory_none_uses_raw_path(self, tmp_path):
        """Test that config_directory=None uses raw path without resolution."""
        relative_log_path = tmp_path / "relative_path.log"
        config = {
            "output_file": str(relative_log_path),
            "config_directory": None,
            "critical": False
        }
        plugin = JsonAuditingPlugin(config)
        
        # Should use raw path when config_directory is None
        assert plugin.output_file == str(relative_log_path)
    
    def test_config_directory_present_resolves_path(self):
        """Test that presence of config_directory triggers path resolution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "output_file": "logs/audit.log",
                "critical": False
            }
            plugin = JsonAuditingPlugin(config)
            
            # Set config directory after initialization
            plugin.set_config_directory(temp_dir)
            
            # Should have resolved path relative to config directory
            expected_path = Path(temp_dir) / "logs/audit.log"
            assert Path(plugin.output_file) == expected_path.resolve()
    
    def test_home_expansion_works_without_config_directory(self):
        """Test that home expansion works even without config_directory."""
        config = {
            "output_file": "~/test.log",
            "critical": True  # Use critical=True to prevent file creation
        }
        plugin = JsonAuditingPlugin(config)
        
        # Should have expanded ~ even without config_directory
        import os
        expected_path = os.path.expanduser("~/test.log")
        assert plugin.output_file == expected_path
    
    def test_invalid_config_directory_type_handled_properly(self):
        """Test that invalid config_directory types are handled properly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            config = {
                "output_file": log_file,
                "config_directory": 123,  # Invalid type
                "critical": False
            }
            
            # Should handle invalid type gracefully and resolve path to canonical form
            plugin = JsonAuditingPlugin(config)
            expected_resolved = Path(log_file).resolve()
            assert Path(plugin.output_file) == expected_resolved
    
    def test_logging_reconfiguration_on_path_change(self):
        """Test that logging reconfigures when set_config_directory changes the output path."""
        with tempfile.TemporaryDirectory() as temp_dir1, \
             tempfile.TemporaryDirectory() as temp_dir2:
            
            # Initial relative path
            config = {
                "output_file": "audit.log",
                "critical": False
            }
            plugin = JsonAuditingPlugin(config)
            
            # Set first config directory - should trigger logging setup
            plugin.set_config_directory(temp_dir1)
            initial_path = plugin.output_file
            initial_logger_name = plugin._get_logger_name()
            
            # Verify logging is set up
            assert plugin._logging_setup_complete
            assert plugin.logger is not None
            initial_handler = plugin.handler
            
            # Log a message to the first location
            from watchgate.plugins.interfaces import PolicyDecision
            from watchgate.protocol.messages import MCPRequest
            
            request = MCPRequest(
                jsonrpc="2.0",
                id="test-reconfig",
                method="tools/call",
                params={"name": "test_tool"}
            )
            decision = PolicyDecision(allowed=True, reason="Test before reconfigure")
            
            import asyncio
            asyncio.run(plugin.log_request(request, decision, "test-server"))
            
            # Verify first file was created and has content
            assert os.path.exists(initial_path)
            with open(initial_path, 'r') as f:
                content1 = f.read()
            assert len(content1) > 0
            assert "Test before reconfigure" in content1
            
            # Change config directory - should trigger reconfiguration
            plugin.set_config_directory(temp_dir2)
            new_path = plugin.output_file
            new_logger_name = plugin._get_logger_name()
            
            # Verify path changed
            assert new_path != initial_path
            assert Path(new_path).parent.resolve() == Path(temp_dir2).resolve()
            
            # Verify logger name changed (different file hash)
            assert new_logger_name != initial_logger_name
            
            # Verify logging is still set up with new handler
            assert plugin._logging_setup_complete
            assert plugin.logger is not None
            assert plugin.handler is not None
            assert plugin.handler != initial_handler  # Should be a new handler
            
            # Log a message to the new location
            request2 = MCPRequest(
                jsonrpc="2.0",
                id="test-reconfig-2",
                method="tools/call",
                params={"name": "test_tool_2"}
            )
            decision2 = PolicyDecision(allowed=True, reason="Test after reconfigure")
            
            asyncio.run(plugin.log_request(request2, decision2, "test-server"))
            
            # Verify new file was created and has content
            assert os.path.exists(new_path)
            with open(new_path, 'r') as f:
                content2 = f.read()
            assert len(content2) > 0
            assert "Test after reconfigure" in content2
            
            # Verify old file still has only old content
            with open(initial_path, 'r') as f:
                content1_after = f.read()
            assert content1_after == content1  # Unchanged
            assert "Test after reconfigure" not in content1_after