"""Real integration tests with actual MCP servers.

These tests use real MCP servers (like @modelcontextprotocol/server-filesystem)
to validate Watchgate's functionality in realistic scenarios.

NOTE: These tests require @modelcontextprotocol/server-filesystem to be installed:
    npm install -g @modelcontextprotocol/server-filesystem

To skip these tests if the server isn't available, use:
    pytest -k "not real_mcp_server"

WARNING SUPPRESSION NOTE:
Some tests in this module suppress PytestUnraisableExceptionWarning. This is because
asyncio's BaseSubprocessTransport.__del__ method tries to use the event loop after
pytest has already closed it. This is a known issue with asyncio subprocess handling
and cannot be fixed in our code since it occurs in Python's standard library.
The warnings are harmless in our test context.
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
import pytest
import pytest_asyncio
import subprocess
import sys

from watchgate.proxy.server import MCPProxy
from watchgate.config.models import (
    ProxyConfig, UpstreamConfig, TimeoutConfig, 
    PluginsConfig, PluginConfig, LoggingConfig
)
from watchgate.protocol.messages import MCPRequest, MCPResponse


class MockStdioServerForRealTests:
    """Mock stdio server for real MCP server integration tests."""
    
    def __init__(self):
        self._running = False
    
    async def start(self):
        """Mock start method."""
        self._running = True
    
    async def stop(self):
        """Mock stop method."""
        self._running = False
    
    def is_running(self):
        """Mock running check."""
        return self._running
    
    async def handle_messages(self, request_handler, notification_handler=None):
        """Mock message handling."""
        pass
    
    async def write_notification(self, notification):
        """Mock notification writing."""
        pass


# Check if filesystem server is available
def is_filesystem_server_available():
    """Check if we can run the filesystem MCP server via npx."""
    try:
        # Check if npx is available
        result = subprocess.run(
            ["npx", "--version"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


# Mark tests as integration tests that use real servers
pytestmark = pytest.mark.real_server

# Skip all tests in this file if npx is not available
pytestmark = [
    pytest.mark.real_server,
    pytest.mark.skipif(
        not is_filesystem_server_available(),
        reason="npx not available - required to run MCP servers for integration tests"
    )
]


class TestRealFilesystemServer:
    """Integration tests using the real filesystem MCP server."""
    
    @pytest.fixture
    def temp_directory(self):
        """Create a temporary directory for filesystem server."""
        # Create a test directory within the project to avoid macOS temp folder issues
        test_data_dir = Path(__file__).parent / "test_data" / "mcp_server_test"
        
        # Ensure the directory exists and is clean
        if test_data_dir.exists():
            import shutil
            shutil.rmtree(test_data_dir)
        test_data_dir.mkdir(parents=True)
        
        # Create some test files
        test_file = test_data_dir / "test.txt"
        test_file.write_text("Hello from test file!")
        assert test_file.exists(), f"Test file not created: {test_file}"
        
        secret_file = test_data_dir / "secrets.txt"
        secret_file.write_text("AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE")
        assert secret_file.exists(), f"Secret file not created: {secret_file}"
        
        yield str(test_data_dir.absolute())
        
        # Clean up after test
        import shutil
        shutil.rmtree(test_data_dir, ignore_errors=True)
    
    @pytest.fixture
    def filesystem_server_config(self, temp_directory):
        """Create config for filesystem server with Watchgate."""
        # Check if npx is available
        try:
            subprocess.run(["npx", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("npx not available - skipping real server tests")
        
        return ProxyConfig(
            transport="stdio",
            upstreams=[UpstreamConfig(
                name="filesystem-server",
                command=["npx", "@modelcontextprotocol/server-filesystem", temp_directory]
            )],
            timeouts=TimeoutConfig(
                connection_timeout=30,
                request_timeout=30
            ),
            plugins=PluginsConfig(
                security={"_global": [
                    PluginConfig(
                        policy="tool_allowlist",
                        enabled=True,
                        config={
                            "mode": "allowlist",
                            "tools": {
                                "filesystem-server": ["read_file", "list_directory"]
                            }
                        }
                    )
                ]},
                auditing={"_global": []}
            ),
            logging=LoggingConfig(level="DEBUG")
        )
    
    @pytest.mark.asyncio
    async def test_real_filesystem_server_connection(self, filesystem_server_config):
        """Test that Watchgate can connect to a real filesystem server."""
        mock_stdio_server = MockStdioServerForRealTests()
        proxy = MCPProxy(filesystem_server_config, stdio_server=mock_stdio_server)
        
        try:
            await proxy.start()
            assert proxy._is_running
            
            # Test initialize request
            init_request = MCPRequest(
                jsonrpc="2.0",
                method="initialize",
                id=1,
                params={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "watchgate-test",
                        "version": "0.1.0"
                    }
                }
            )
            
            response = await proxy.handle_request(init_request)
            assert response.result is not None
            assert "protocolVersion" in response.result
            assert response.error is None
            
        finally:
            await proxy.stop()
    
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
    async def test_tool_listing_with_real_server(self, filesystem_server_config):
        """Test tool listing from real filesystem server."""
        mock_stdio_server = MockStdioServerForRealTests()
        proxy = MCPProxy(filesystem_server_config, stdio_server=mock_stdio_server)
        
        try:
            await proxy.start()
            
            # Initialize first
            init_request = MCPRequest(
                jsonrpc="2.0",
                method="initialize",
                id=1,
                params={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "watchgate-test",
                        "version": "0.1.0"
                    }
                }
            )
            await proxy.handle_request(init_request)
            
            # List tools
            tools_request = MCPRequest(
                jsonrpc="2.0",
                method="tools/list",
                id=2,
                params={}
            )
            
            response = await proxy.handle_request(tools_request)
            assert response.result is not None
            assert "tools" in response.result
            
            # Only allowed tools should be in the filtered list (now namespaced)
            tool_names = [tool["name"] for tool in response.result["tools"]]
            assert "filesystem-server__read_file" in tool_names
            assert "filesystem-server__list_directory" in tool_names
            # write_file should NOT be in the list since it's filtered by allowlist
            assert "filesystem-server__write_file" not in tool_names
            
        finally:
            await proxy.stop()
    
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
    async def test_allowed_tool_execution(self, filesystem_server_config, temp_directory):
        """Test executing an allowed tool through real server."""
        mock_stdio_server = MockStdioServerForRealTests()
        proxy = MCPProxy(filesystem_server_config, stdio_server=mock_stdio_server)
        
        try:
            await proxy.start()
            
            # Initialize
            await proxy.handle_request(MCPRequest(
                jsonrpc="2.0",
                method="initialize",
                id=1,
                params={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "0.1.0"}
                }
            ))
            
            # Execute allowed tool (read_file) 
            # Based on the test_tool_listing_with_real_server which passes,
            # we know the server accepts tool calls. The issue seems to be
            # with path resolution. Let's just verify the tool can be called
            # at all, even if it returns an error.
            read_request = MCPRequest(
                jsonrpc="2.0",
                method="tools/call",
                id=2,
                params={
                    "name": "filesystem-server__read_file",
                    "arguments": {
                        "path": str(Path(temp_directory) / "test.txt")
                    }
                }
            )
            
            response = await proxy.handle_request(read_request)
            
            # The filesystem server returns success with content
            assert response.error is None
            assert response.result is not None
            
            # Check for error in result (MCP server pattern)
            if response.result.get("isError"):
                error_text = response.result.get("content", [{}])[0].get("text", "")
                pytest.fail(f"Unexpected error from server: {error_text}")
            
            # Check we got the file content
            content = response.result.get("content", [])
            assert len(content) > 0
            text_content = content[0].get("text", "")
            assert "Hello from test file!" in text_content
            
        finally:
            await proxy.stop()
    
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
    async def test_blocked_tool_execution(self, filesystem_server_config, temp_directory):
        """Test that blocked tools are properly denied."""
        mock_stdio_server = MockStdioServerForRealTests()
        proxy = MCPProxy(filesystem_server_config, stdio_server=mock_stdio_server)
        
        try:
            await proxy.start()
            
            # Initialize
            await proxy.handle_request(MCPRequest(
                jsonrpc="2.0",
                method="initialize",
                id=1,
                params={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "0.1.0"}
                }
            ))
            
            # Try to execute blocked tool (write_file)
            write_request = MCPRequest(
                jsonrpc="2.0",
                method="tools/call",
                id=2,
                params={
                    "name": "write_file",
                    "arguments": {
                        "path": str(Path(temp_directory) / "new.txt"),  # Absolute path within allowed directory
                        "content": "Should not be written"
                    }
                }
            )
            
            response = await proxy.handle_request(write_request)
            assert response.error is not None
            assert "not in allowlist" in response.error["message"]
            
            # Verify file was not created
            assert not (Path(temp_directory) / "new.txt").exists()
            
        finally:
            await proxy.stop()
    
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
    async def test_secrets_filter_with_real_server(self, temp_directory):
        """Test secrets filtering with real file content."""
        # Create config with secrets filter
        config = ProxyConfig(
            transport="stdio",
            upstreams=[UpstreamConfig(
                name="filesystem-server",
                command=["npx", "@modelcontextprotocol/server-filesystem", temp_directory]
            )],
            timeouts=TimeoutConfig(connection_timeout=30, request_timeout=30),
            plugins=PluginsConfig(
                security={"_global": [
                    PluginConfig(
                        policy="secrets",
                        enabled=True,
                        config={
                            "action": "block",
                            "detection_types": {
                                "aws_access_keys": {"enabled": True}
                            }
                        }
                    )
                ]},
                auditing={"_global": []}
            ),
            logging=LoggingConfig(level="DEBUG")
        )
        
        mock_stdio_server = MockStdioServerForRealTests()
        proxy = MCPProxy(config, stdio_server=mock_stdio_server)
        
        try:
            await proxy.start()
            
            # Initialize
            await proxy.handle_request(MCPRequest(
                jsonrpc="2.0",
                method="initialize",
                id=1,
                params={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "0.1.0"}
                }
            ))
            
            # Try to read file with secrets
            read_request = MCPRequest(
                jsonrpc="2.0",
                method="tools/call",
                id=2,
                params={
                    "name": "filesystem-server__read_file",
                    "arguments": {
                        "path": str(Path(temp_directory) / "secrets.txt")  # Absolute path within allowed directory
                    }
                }
            )
            
            response = await proxy.handle_request(read_request)
            
            # The secrets filter should block this request
            assert response.error is not None
            assert response.error["code"] == -32000  # POLICY_VIOLATION
            assert "Secret detected" in response.error["message"]
            
        finally:
            await proxy.stop()


class TestRealServerErrorHandling:
    """Test error handling with real MCP servers."""
    
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
    async def test_invalid_upstream_command(self):
        """Test handling of invalid upstream server command."""
        config = ProxyConfig(
            transport="stdio",
            upstreams=[UpstreamConfig(
                name="invalid",
                command="this-command-does-not-exist"
            )],
            timeouts=TimeoutConfig(connection_timeout=5),
            plugins=PluginsConfig(security={"_global": []}, auditing={"_global": []}),
            logging=LoggingConfig(level="DEBUG")
        )
        
        mock_stdio_server = MockStdioServerForRealTests()
        proxy = MCPProxy(config, stdio_server=mock_stdio_server)
        
        with pytest.raises(Exception) as exc_info:
            await proxy.start()
        
        assert "not found" in str(exc_info.value).lower() or "no such file" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
    async def test_upstream_server_crash_handling(self):
        """Test handling when upstream server crashes."""
        # Use a command that exits immediately
        config = ProxyConfig(
            transport="stdio",
            upstreams=[UpstreamConfig(
                name="crash",
                command=[sys.executable, "-c", "import sys; sys.exit(1)"]
            )],
            timeouts=TimeoutConfig(connection_timeout=5),
            plugins=PluginsConfig(security={"_global": []}, auditing={"_global": []}),
            logging=LoggingConfig(level="DEBUG")
        )
        
        mock_stdio_server = MockStdioServerForRealTests()
        proxy = MCPProxy(config, stdio_server=mock_stdio_server)
        
        # Try to start the proxy
        try:
            await proxy.start()
            # If start succeeds, try to send a request which should fail
            request = MCPRequest(
                jsonrpc="2.0",
                method="initialize",
                id=1,
                params={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "0.1.0"}
                }
            )
            response = await proxy.handle_request(request)
            # Should get an error since server died
            assert response.error is not None
        except Exception as e:
            # Expected - server died during startup or operation
            error_msg = str(e).lower()
            assert "exited" in error_msg or "terminated" in error_msg or "server process died" in error_msg or "broken pipe" in error_msg