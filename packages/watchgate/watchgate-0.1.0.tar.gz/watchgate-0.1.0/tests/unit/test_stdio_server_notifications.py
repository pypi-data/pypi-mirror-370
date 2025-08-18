"""Test notification support in stdio server using real pipes."""

import pytest
import json
import asyncio

from watchgate.proxy.stdio_server import StdioServer
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification
from tests.utils.stdio_helpers import stdio_test_environment, send_json_message


@pytest.mark.asyncio
async def test_read_message_handles_notification():
    """Test that read_message correctly identifies and validates notifications."""
    async with stdio_test_environment() as env:
        server = StdioServer(
            stdin_file=env['stdin_file'],
            stdout_file=env['stdout_file']
        )
        
        await server.start()
        
        # Create a task to read the message
        async def read_notification():
            return await server.read_message()
        
        read_task = asyncio.create_task(read_notification())
        
        # Give the reader time to start
        await asyncio.sleep(0.1)
        
        # Send a notification
        notification_data = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        await send_json_message(env['stdin_writer'], notification_data)
        
        # Read the message
        message = await read_task
        
        # Verify it's a notification
        assert isinstance(message, MCPNotification)
        assert message.method == "notifications/initialized"
        assert message.params == {}
        
        await server.stop()


@pytest.mark.asyncio
async def test_read_message_handles_request():
    """Test that read_message correctly identifies and validates requests."""
    async with stdio_test_environment() as env:
        server = StdioServer(
            stdin_file=env['stdin_file'],
            stdout_file=env['stdout_file']
        )
        
        await server.start()
        
        # Create a task to read the message
        async def read_request():
            return await server.read_message()
        
        read_task = asyncio.create_task(read_request())
        
        # Give the reader time to start
        await asyncio.sleep(0.1)
        
        # Send a request
        request_data = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1,
            "params": {}
        }
        await send_json_message(env['stdin_writer'], request_data)
        
        # Read the message
        message = await read_task
        
        # Verify it's a request
        assert isinstance(message, MCPRequest)
        assert message.method == "tools/list"
        assert message.id == 1
        assert message.params == {}
        
        await server.stop()


@pytest.mark.asyncio
async def test_read_request_filters_notifications():
    """Test that read_request filters out notifications and only returns requests."""
    async with stdio_test_environment() as env:
        server = StdioServer(
            stdin_file=env['stdin_file'],
            stdout_file=env['stdout_file']
        )
        
        await server.start()
        
        # Create a task to read a request (which should skip notifications)
        async def read_request():
            return await server.read_request()
        
        read_task = asyncio.create_task(read_request())
        
        # Give the reader time to start
        await asyncio.sleep(0.1)
        
        # Send a notification first (should be skipped)
        notification_data = {
            "jsonrpc": "2.0",
            "method": "notifications/progress",
            "params": {"token": "test"}
        }
        await send_json_message(env['stdin_writer'], notification_data)
        
        # Then send a request (should be returned)
        request_data = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {"name": "test_tool"}
        }
        await send_json_message(env['stdin_writer'], request_data)
        
        # Read should return the request, not the notification
        message = await read_task
        
        # Verify it's the request, not the notification
        assert isinstance(message, MCPRequest)
        assert message.method == "tools/call"
        assert message.id == 1
        
        await server.stop()


@pytest.mark.asyncio
async def test_write_notification():
    """Test writing notifications to stdout."""
    async with stdio_test_environment() as env:
        server = StdioServer(
            stdin_file=env['stdin_file'],
            stdout_file=env['stdout_file']
        )
        
        await server.start()
        
        # Create a notification to send
        notification = MCPNotification(
            jsonrpc="2.0",
            method="notifications/progress",
            params={"token": "test", "value": 50}
        )
        
        # Write the notification
        await server.write_notification(notification)
        
        # Read from stdout to verify it was written correctly
        line = await env['stdout_reader'].readline()
        notification_data = json.loads(line.decode('utf-8').strip())
        
        # Verify the notification format
        assert notification_data["jsonrpc"] == "2.0"
        assert notification_data["method"] == "notifications/progress"
        assert notification_data["params"] == {"token": "test", "value": 50}
        assert "id" not in notification_data  # Notifications don't have IDs
        
        await server.stop()


@pytest.mark.asyncio
async def test_handle_messages_with_notifications():
    """Test handle_messages processes both requests and notifications."""
    async with stdio_test_environment() as env:
        server = StdioServer(
            stdin_file=env['stdin_file'],
            stdout_file=env['stdout_file']
        )
        
        received_notifications = []
        received_requests = []
        
        # Create handlers
        async def request_handler(request):
            received_requests.append(request)
            return MCPResponse(
                jsonrpc="2.0",
                id=request.id,
                result={"handled": True}
            )
        
        async def notification_handler(notification):
            received_notifications.append(notification)
        
        await server.start()
        
        # Start message handling
        handle_task = asyncio.create_task(
            server.handle_messages(request_handler, notification_handler)
        )
        
        # Give it time to start
        await asyncio.sleep(0.1)
        
        # Send a notification
        notification_data = {
            "jsonrpc": "2.0",
            "method": "notifications/progress",
            "params": {"value": 25}
        }
        await send_json_message(env['stdin_writer'], notification_data)
        
        # Send a request
        request_data = {
            "jsonrpc": "2.0",
            "method": "test_method",
            "id": 1,
            "params": {}
        }
        await send_json_message(env['stdin_writer'], request_data)
        
        # Give time to process
        await asyncio.sleep(0.2)
        
        # Verify handlers were called
        assert len(received_notifications) == 1
        assert received_notifications[0].method == "notifications/progress"
        assert received_notifications[0].params == {"value": 25}
        
        assert len(received_requests) == 1
        assert received_requests[0].method == "test_method"
        assert received_requests[0].id == 1
        
        # Stop and cleanup
        await server.stop()
        handle_task.cancel()
        try:
            await handle_task
        except asyncio.CancelledError:
            pass