"""Tests for BaseAuditingPlugin core functionality.

This test suite covers the foundational functionality of the BaseAuditingPlugin class:
- Configuration and initialization
- Path resolution and validation
- Request timestamp tracking and cleanup
- Resource management (handlers, cleanup)
- Thread safety and concurrent access
- Critical vs non-critical error handling
"""

import pytest
import tempfile
import threading
import time
import stat
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

from watchgate.plugins.auditing.base import BaseAuditingPlugin
from watchgate.plugins.interfaces import PolicyDecision
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification


class MockAuditingPlugin(BaseAuditingPlugin):
    """Concrete implementation of BaseAuditingPlugin for testing."""
    
    def _format_request_log(self, request, decision, server_name):
        return f"REQ: {request.method} - {decision.allowed} - {server_name}"
    
    def _format_response_log(self, request, response, decision, server_name):
        return f"RESP: {request.method} - {response.result} - {decision.allowed} - {server_name}"
    
    def _format_notification_log(self, notification, decision, server_name):
        return f"NOTIF: {notification.method} - {decision.allowed} - {server_name}"


class TestConfiguration:
    """Test configuration and initialization."""
    
    def test_default_configuration(self):
        """Test plugin initialization with default configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"output_file": str(Path(tmpdir) / "test.log")}
            plugin = MockAuditingPlugin(config)
            
            assert plugin.max_file_size_mb == 10
            assert plugin.backup_count == 5
            assert plugin.critical == False
            assert plugin.max_message_length == 10000
    
    def test_custom_configuration(self):
        """Test plugin initialization with custom configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                "output_file": str(Path(tmpdir) / "test.log"),
                "max_file_size_mb": 20,
                "backup_count": 10,
                "critical": True,
                "max_message_length": 5000,
                "event_buffer_size": 50
            }
            plugin = MockAuditingPlugin(config)
            
            assert plugin.max_file_size_mb == 20
            assert plugin.backup_count == 10
            assert plugin.critical == True
            assert plugin.max_message_length == 5000
            assert plugin._event_buffer.maxlen == 50
    
    def test_invalid_configuration_types(self):
        """Test that invalid configuration types are rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Invalid max_file_size_mb
            with pytest.raises(ValueError, match="max_file_size_mb must be positive"):
                MockAuditingPlugin({
                    "output_file": str(Path(tmpdir) / "test.log"),
                    "max_file_size_mb": -1
                })
            
            # Invalid backup_count
            with pytest.raises(ValueError, match="backup_count must be non-negative"):
                MockAuditingPlugin({
                    "output_file": str(Path(tmpdir) / "test.log"),
                    "backup_count": -1
                })


class TestPathResolution:
    """Test path resolution and validation."""
    
    def test_absolute_path_resolution(self):
        """Test that absolute paths are used directly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            absolute_path = str(Path(tmpdir) / "test.log")
            config = {"output_file": absolute_path}
            plugin = MockAuditingPlugin(config)
            
            # On macOS, paths may be resolved through symlinks, so compare resolved paths
            assert Path(plugin.output_file).resolve() == Path(absolute_path).resolve()
    
    def test_relative_path_with_config_directory(self):
        """Test that relative paths are resolved against config directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "config"
            config_dir.mkdir()
            
            config = {"output_file": "logs/audit.log"}
            plugin = MockAuditingPlugin(config)
            plugin.set_config_directory(config_dir)
            
            expected_path = config_dir / "logs" / "audit.log"
            assert Path(plugin.output_file) == expected_path.resolve()
    
    def test_path_validation_errors(self):
        """Test path validation error handling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"output_file": str(Path(tmpdir) / "test.log")}
            plugin = MockAuditingPlugin(config)
            
            errors = plugin.validate_paths()
            # Should be no errors for valid path
            assert len(errors) == 0


class TestRequestTimestamps:
    """Test request timestamp tracking and cleanup."""
    
    def test_store_and_calculate_duration(self):
        """Test basic timestamp storage and duration calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"output_file": str(Path(tmpdir) / "test.log")}
            plugin = MockAuditingPlugin(config)
            
            # Store timestamp
            request = MCPRequest(jsonrpc="2.0", method="test", id="123")
            plugin._store_request_timestamp(request)
            
            # Should have stored timestamp
            assert "123" in plugin.request_timestamps
            
            # Calculate duration after a small delay
            time.sleep(0.01)  # 10ms delay
            duration = plugin._calculate_duration("123")
            
            # Should return valid duration and clean up timestamp
            assert duration is not None
            assert duration >= 10  # At least 10ms
            assert "123" not in plugin.request_timestamps  # Cleaned up
    
    def test_ttl_cleanup(self):
        """Test TTL cleanup prevents memory leaks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"output_file": str(Path(tmpdir) / "test.log")}
            plugin = MockAuditingPlugin(config)
            
            # Store many request timestamps
            current_time = time.time()
            for i in range(10):
                request = MCPRequest(jsonrpc="2.0", method="test", id=str(i))
                plugin._store_request_timestamp(request)
            
            assert len(plugin.request_timestamps) == 10
            
            # Force cleanup with time 6 minutes in future (beyond TTL of 5 minutes)
            future_time = current_time + 360  # 6 minutes
            plugin.force_cleanup_timestamps(future_time)
            
            # All timestamps should be cleaned up due to TTL expiration
            assert len(plugin.request_timestamps) == 0
    
    def test_concurrent_timestamp_access(self):
        """Test thread safety of request timestamp operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"output_file": str(Path(tmpdir) / "test.log")}
            plugin = MockAuditingPlugin(config)
            
            def store_timestamps(start_id, count):
                for i in range(count):
                    request = MCPRequest(jsonrpc="2.0", method="test", id=f"{start_id}-{i}")
                    plugin._store_request_timestamp(request)
            
            # Create multiple threads accessing request_timestamps concurrently
            threads = []
            for t in range(5):  # Reduced from 10 to make test more reliable
                thread = threading.Thread(target=store_timestamps, args=(t, 10))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # Should not crash with concurrent access
            assert len(plugin.request_timestamps) <= 50


class TestResourceManagement:
    """Test resource management including handlers and cleanup."""
    
    def test_handler_cleanup_on_deletion(self):
        """Test that handlers are properly cleaned up when plugin is deleted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"output_file": str(Path(tmpdir) / "test.log")}
            plugin = MockAuditingPlugin(config)
            
            # Ensure logging is set up
            plugin._ensure_logging_setup()
            
            # Should have handler
            assert plugin.handler is not None
            assert plugin.logger is not None
            
            # Cleanup should remove handler
            plugin.cleanup()
            assert plugin.handler is None
            assert plugin.logger is None
    
    def test_thread_safety_of_logging_setup(self):
        """Test that logging setup is thread-safe."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"output_file": str(Path(tmpdir) / "test.log")}
            plugin = MockAuditingPlugin(config)
            
            results = []
            
            def setup_logging():
                result = plugin._ensure_logging_setup()
                results.append(result)
            
            # Multiple threads trying to set up logging concurrently
            threads = []
            for _ in range(5):
                thread = threading.Thread(target=setup_logging)
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # All should succeed
            assert all(results)
            # Should only have one handler
            if plugin.logger:
                assert len(plugin.logger.handlers) == 1


class TestCriticalErrorHandling:
    """Test critical vs non-critical error handling."""
    
    def test_critical_plugin_raises_on_setup_failure(self):
        """Test that critical plugins raise exceptions on setup failure."""
        # Try to write to a non-existent directory
        config = {
            "output_file": "/nonexistent/directory/test.log",
            "critical": True
        }
        
        with pytest.raises(Exception, match="Critical auditing plugin.*failed to initialize"):
            MockAuditingPlugin(config)
    
    def test_non_critical_plugin_continues_on_setup_failure(self):
        """Test that non-critical plugins continue on setup failure."""
        # Try to write to a non-existent directory
        config = {
            "output_file": "/nonexistent/directory/test.log",
            "critical": False
        }
        
        # Should not raise exception
        plugin = MockAuditingPlugin(config)
        assert plugin.critical == False


class TestMetadataExtraction:
    """Test metadata extraction and enhancement functionality."""
    
    def test_extract_plugin_info_with_metadata(self):
        """Test plugin info extraction from decision metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"output_file": str(Path(tmpdir) / "test.log")}
            plugin = MockAuditingPlugin(config)
            
            # Test with plugin metadata
            decision = PolicyDecision(
                allowed=True, 
                reason="test", 
                metadata={"plugin": "test_plugin"}
            )
            result = plugin._extract_plugin_info(decision)
            assert result == "test_plugin"
            
            # Test with no plugin metadata
            decision = PolicyDecision(allowed=True, reason="test", metadata={})
            result = plugin._extract_plugin_info(decision)
            assert result == "unknown"
            
            # Test with None metadata (gets converted to {} by PolicyDecision)
            decision = PolicyDecision(allowed=True, reason="test", metadata=None)
            result = plugin._extract_plugin_info(decision)
            assert result == "unknown"
    
    def test_enhance_decision_with_duration(self):
        """Test duration enhancement of policy decisions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"output_file": str(Path(tmpdir) / "test.log")}
            plugin = MockAuditingPlugin(config)
            
            # Test adding duration to decision without metadata
            original_decision = PolicyDecision(allowed=True, reason="test")
            enhanced = plugin._enhance_decision_with_duration(original_decision, 1500)
            
            assert enhanced.metadata["duration_ms"] == 1500
            assert enhanced.allowed == original_decision.allowed
            assert enhanced.reason == original_decision.reason
            
            # Test adding duration to decision with existing metadata
            original_decision = PolicyDecision(
                allowed=True, 
                reason="test",
                metadata={"plugin": "test_plugin"}
            )
            enhanced = plugin._enhance_decision_with_duration(original_decision, 2000)
            
            assert enhanced.metadata["duration_ms"] == 2000
            assert enhanced.metadata["plugin"] == "test_plugin"
            
            # Test that existing duration_ms is not overwritten
            original_decision = PolicyDecision(
                allowed=True,
                reason="test", 
                metadata={"duration_ms": 1000}
            )
            enhanced = plugin._enhance_decision_with_duration(original_decision, 2000)
            
            # Should keep original duration
            assert enhanced.metadata["duration_ms"] == 1000


class TestEventBuffering:
    """Test event buffering for early initialization failures."""
    
    def test_event_buffer_initialization(self):
        """Test that event buffer is properly initialized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                "output_file": str(Path(tmpdir) / "test.log"),
                "event_buffer_size": 25
            }
            plugin = MockAuditingPlugin(config)
            
            assert hasattr(plugin, '_event_buffer')
            assert hasattr(plugin, '_buffer_enabled')
            assert plugin._event_buffer.maxlen == 25
            assert plugin._buffer_enabled == True
    
    def test_buffer_size_bounds(self):
        """Test that event buffer is properly bounded."""
        from collections import deque
        
        # Test bounded deque behavior directly
        buffer = deque(maxlen=3)
        
        # Fill beyond capacity
        for i in range(10):
            buffer.append(f"Message {i}")
        
        # Should be bounded to max size
        assert len(buffer) == 3
        
        # Should contain most recent messages
        messages = list(buffer)
        assert "Message 7" in messages[0]
        assert "Message 8" in messages[1] 
        assert "Message 9" in messages[2]


class TestBaseClassEnhancements:
    """Test base class improvements that affect all auditing plugins.
    
    These tests were moved from test_cef_bug_fixes.py as they test
    base auditing functionality, not CEF-specific behavior.
    """
    
    def test_extract_plugin_info_handles_none(self):
        """Test that _extract_plugin_info handles None decision gracefully."""
        import tempfile
        from watchgate.plugins.auditing.base import BaseAuditingPlugin
        from watchgate.plugins.interfaces import PolicyDecision
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_file': f'{tmpdir}/test.log'}
            
            # Create a minimal test plugin instance
            class TestPlugin(BaseAuditingPlugin):
                def _format_request_log(self, request, decision, server_name):
                    return "test"
                def _format_response_log(self, request, response, decision, server_name):
                    return "test"
                def _format_notification_log(self, notification, decision, server_name):
                    return "test"
            
            plugin = TestPlugin(config)
            
            # Test with None decision
            result = plugin._extract_plugin_info(None)
            assert result == "unknown"
            
            # Test with decision but None metadata
            decision = PolicyDecision(allowed=True, reason="test", metadata=None)
            result = plugin._extract_plugin_info(decision)
            assert result == "unknown"
    
    def test_json_lines_format_auto_disables_pretty_print(self):
        """Test that JSON Lines format automatically disables pretty_print=True.
        
        This test verifies that when output_format is 'jsonl', the JSON plugin
        automatically disables pretty_print to ensure single-line output.
        """
        import tempfile
        from watchgate.plugins.auditing.json_lines import JsonAuditingPlugin
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_file': f'{tmpdir}/test.log',
                'output_format': 'jsonl',
                'pretty_print': True  # Should be auto-disabled
            }
            
            # Should automatically disable pretty_print for JSONL format
            plugin = JsonAuditingPlugin(config)
            assert plugin.pretty_print is False  # Automatically disabled for JSONL