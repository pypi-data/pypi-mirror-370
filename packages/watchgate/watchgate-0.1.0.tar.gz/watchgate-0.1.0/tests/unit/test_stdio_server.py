"""Comprehensive tests for StdioServer using real pipes instead of mocks.

This module tests the stdio server functionality using real pipe-based streams
instead of mock objects, providing more accurate testing of stdio behavior.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock

from watchgate.proxy.stdio_server import StdioServer
from watchgate.protocol.messages import MCPRequest, MCPResponse
from tests.utils.stdio_helpers import stdio_test_environment, send_json_message, read_json_message


class TestStdioServerInitialization:
    """Test StdioServer initialization and lifecycle."""
    
    @pytest.mark.asyncio
    async def test_start_and_stop_with_real_pipes(self):
        """Test starting and stopping the server with real pipes."""
        async with stdio_test_environment() as env:
            server = StdioServer(
                stdin_file=env['stdin_file'],
                stdout_file=env['stdout_file']
            )
            
            # Test start
            await server.start()
            assert server.is_running()
            
            # Test stop
            await server.stop()
            assert not server.is_running()
    
    @pytest.mark.asyncio
    async def test_start_already_running_raises_error(self):
        """Test that starting an already running server raises error."""
        async with stdio_test_environment() as env:
            server = StdioServer(
                stdin_file=env['stdin_file'],
                stdout_file=env['stdout_file']
            )
            
            await server.start()
            with pytest.raises(RuntimeError, match="already running"):
                await server.start()
            
            await server.stop()
    
    @pytest.mark.asyncio
    async def test_stop_not_running_is_safe(self):
        """Test that stopping a non-running server is safe."""
        async with stdio_test_environment() as env:
            server = StdioServer(
                stdin_file=env['stdin_file'],
                stdout_file=env['stdout_file']
            )
            
            # Should not raise error
            await server.stop()
            assert not server.is_running()


class TestStdioServerMessageHandling:
    """Test message handling with real pipes."""
    
    @pytest.mark.asyncio
    async def test_handle_valid_request(self):
        """Test handling a valid JSON-RPC request."""
        async with stdio_test_environment() as env:
            server = StdioServer(
                stdin_file=env['stdin_file'],
                stdout_file=env['stdout_file']
            )
            
            # Create a simple request handler
            async def handler(request):
                return MCPResponse(
                    jsonrpc="2.0",
                    id=request.id,
                    result={"status": "ok", "method": request.method}
                )
            
            await server.start()
            
            # Send a request
            request_data = {
                "jsonrpc": "2.0",
                "method": "test_method",
                "id": 1,
                "params": {"test": "value"}
            }
            
            # Start the message handling in the background
            handle_task = asyncio.create_task(
                server.handle_messages(handler, None)
            )
            
            # Give it a moment to start
            await asyncio.sleep(0.1)
            
            # Send the request
            await send_json_message(env['stdin_writer'], request_data)
            
            # Read the response
            response_data = await read_json_message(env['stdout_reader'])
            
            # Verify the response
            assert response_data is not None
            assert response_data["jsonrpc"] == "2.0"
            assert response_data["id"] == 1
            assert response_data["result"]["status"] == "ok"
            assert response_data["result"]["method"] == "test_method"
            
            # Stop the server to clean up
            await server.stop()
            handle_task.cancel()
            try:
                await handle_task
            except asyncio.CancelledError:
                pass
    
    @pytest.mark.asyncio
    async def test_handle_invalid_json(self):
        """Test handling invalid JSON input."""
        async with stdio_test_environment() as env:
            server = StdioServer(
                stdin_file=env['stdin_file'],
                stdout_file=env['stdout_file']
            )
            
            # Create a simple request handler (shouldn't be called)
            async def handler(request):
                return MCPResponse(
                    jsonrpc="2.0",
                    id=request.id,
                    result={"status": "ok"}
                )
            
            await server.start()
            
            # Start the message handling in the background
            handle_task = asyncio.create_task(
                server.handle_messages(handler, None)
            )
            
            # Give it a moment to start
            await asyncio.sleep(0.1)
            
            # Send invalid JSON
            env['stdin_writer'].write(b'{"invalid": json}\n')
            await env['stdin_writer'].drain()
            
            # Read the error response
            response_data = await read_json_message(env['stdout_reader'])
            
            # Verify error response
            assert response_data is not None
            assert response_data["jsonrpc"] == "2.0"
            assert response_data["id"] is None
            assert "error" in response_data
            assert response_data["error"]["code"] == -32700  # Parse error
            
            # Stop the server
            await server.stop()
            handle_task.cancel()
            try:
                await handle_task
            except asyncio.CancelledError:
                pass
    
    @pytest.mark.asyncio
    async def test_handle_missing_method(self):
        """Test handling request with missing method."""
        async with stdio_test_environment() as env:
            server = StdioServer(
                stdin_file=env['stdin_file'],
                stdout_file=env['stdout_file']
            )
            
            # Create a simple request handler (shouldn't be called)
            async def handler(request):
                return MCPResponse(
                    jsonrpc="2.0",
                    id=request.id,
                    result={"status": "ok"}
                )
            
            await server.start()
            
            # Start the message handling in the background
            handle_task = asyncio.create_task(
                server.handle_messages(handler, None)
            )
            
            # Give it a moment to start
            await asyncio.sleep(0.1)
            
            # Send request without method
            request_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "params": {}
            }
            await send_json_message(env['stdin_writer'], request_data)
            
            # Read the error response
            response_data = await read_json_message(env['stdout_reader'])
            
            # Verify error response
            assert response_data is not None
            assert response_data["jsonrpc"] == "2.0"
            assert response_data["id"] is None
            assert "error" in response_data
            assert response_data["error"]["code"] == -32600  # Invalid request
            
            # Stop the server
            await server.stop()
            handle_task.cancel()
            try:
                await handle_task
            except asyncio.CancelledError:
                pass


class TestStdioServerAsyncContextManager:
    """Test async context manager functionality."""
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using StdioServer as async context manager."""
        async with stdio_test_environment() as env:
            async with StdioServer(
                stdin_file=env['stdin_file'],
                stdout_file=env['stdout_file']
            ) as server:
                assert server.is_running()
            
            # Should be stopped after exiting context
            assert not server.is_running()


class TestStdioServerRuntimeErrors:
    """Test runtime error handling."""
    
    @pytest.mark.asyncio 
    async def test_read_message_not_running(self):
        """Test reading message when server not running."""
        async with stdio_test_environment() as env:
            server = StdioServer(
                stdin_file=env['stdin_file'],
                stdout_file=env['stdout_file']
            )
            
            with pytest.raises(RuntimeError, match="not running"):
                await server.read_message()
    
    @pytest.mark.asyncio
    async def test_write_response_not_running(self):
        """Test writing response when server not running."""
        async with stdio_test_environment() as env:
            server = StdioServer(
                stdin_file=env['stdin_file'],
                stdout_file=env['stdout_file']
            )
            
            response = MCPResponse(
                jsonrpc="2.0",
                id=1,
                result={"status": "ok"}
            )
            
            with pytest.raises(RuntimeError, match="not running"):
                await server.write_response(response)


class TestStdioServerNotifications:
    """Test notification handling."""
    
    @pytest.mark.asyncio
    async def test_handle_notification(self):
        """Test handling notifications."""
        async with stdio_test_environment() as env:
            server = StdioServer(
                stdin_file=env['stdin_file'],
                stdout_file=env['stdout_file']
            )
            
            notification_received = None
            
            # Create notification handler
            async def notification_handler(notification):
                nonlocal notification_received
                notification_received = notification
            
            # Create dummy request handler
            async def request_handler(request):
                return MCPResponse(jsonrpc="2.0", id=request.id, result={})
            
            await server.start()
            
            # Start the message handling in the background
            handle_task = asyncio.create_task(
                server.handle_messages(request_handler, notification_handler)
            )
            
            # Give it a moment to start
            await asyncio.sleep(0.1)
            
            # Send a notification
            notification_data = {
                "jsonrpc": "2.0",
                "method": "test_notification",
                "params": {"test": "value"}
            }
            await send_json_message(env['stdin_writer'], notification_data)
            
            # Give it time to process
            await asyncio.sleep(0.1)
            
            # Verify notification was received
            assert notification_received is not None
            assert notification_received.method == "test_notification"
            assert notification_received.params == {"test": "value"}
            
            # Stop the server
            await server.stop()
            handle_task.cancel()
            try:
                await handle_task
            except asyncio.CancelledError:
                pass