"""Stdio server implementation for accepting MCP client connections.

This module provides the StdioServer class that accepts MCP client connections
via stdin/stdout, as specified in the v0.1.0 requirements.
"""

import asyncio
import json
import logging
import sys
from io import UnsupportedOperation
from typing import Optional, Union

from ..protocol.messages import MCPRequest, MCPResponse, MCPNotification
from ..protocol.validation import MessageValidator, ValidationError
from ..protocol.errors import MCPErrorCodes, create_error_response, create_error_dict

logger = logging.getLogger(__name__)


class JSONParseError(Exception):
    """Exception raised when JSON parsing fails."""
    pass


class StdioServer:
    """Stdio-based MCP server that accepts client connections via stdin/stdout.
    
    This server reads JSON-RPC messages from stdin and writes responses to stdout,
    allowing it to act as an MCP server that clients can connect to via stdio transport.
    """
    
    def __init__(self, stdin_file=None, stdout_file=None):
        """Initialize the stdio server.
        
        Args:
            stdin_file: Override default stdin (for testing)
            stdout_file: Override default stdout (for testing)
        """
        self._validator = MessageValidator()
        self._running = False
        self._stdin_reader: Optional[asyncio.StreamReader] = None
        self._stdout_writer: Optional[asyncio.StreamWriter] = None
        self._stdin_file = stdin_file or sys.stdin
        self._stdout_file = stdout_file or sys.stdout
    
    async def start(self) -> None:
        """Start the stdio server and begin accepting connections."""
        if self._running:
            raise RuntimeError("Server is already running")
        
        logger.info("Starting stdio MCP server")
        
        # In test environments, we may not have real stdin/stdout with fileno()
        # In this case, we'll create a mock server that can be controlled by tests
        try:
            # Check if we can get file descriptors (real environment)
            self._stdin_file.fileno()
            self._stdout_file.fileno()
            
            # Create async stdin/stdout streams
            loop = asyncio.get_running_loop()
            
            # Create stdin reader
            self._stdin_reader = asyncio.StreamReader()
            stdin_transport, stdin_protocol = await loop.connect_read_pipe(
                lambda: asyncio.StreamReaderProtocol(self._stdin_reader),
                self._stdin_file
            )
            
            # Create stdout writer using a basic protocol
            class WriteProtocol(asyncio.Protocol):
                def __init__(self):
                    self.transport = None
                    self._closed = False
                    self._close_waiter = None
                
                def connection_made(self, transport):
                    self.transport = transport
                    
                def connection_lost(self, exc):
                    self._closed = True
                    if self._close_waiter and not self._close_waiter.done():
                        if exc is None:
                            self._close_waiter.set_result(None)
                        else:
                            self._close_waiter.set_exception(exc)
                
                def _get_close_waiter(self, *args):
                    # Accept any number of arguments for compatibility
                    if self._close_waiter is None:
                        self._close_waiter = asyncio.Future()
                    return self._close_waiter
                
                def _drain_helper(self):
                    # This method is required by StreamWriter.drain()
                    # For stdout, we don't need complex flow control
                    if self._closed:
                        return asyncio.sleep(0)
                    return asyncio.sleep(0)
            
            write_protocol = WriteProtocol()
            stdout_transport, _ = await loop.connect_write_pipe(
                lambda: write_protocol,
                self._stdout_file
            )
            
            self._stdout_writer = asyncio.StreamWriter(
                transport=stdout_transport,
                protocol=write_protocol,
                reader=None,
                loop=loop
            )
            
        except (UnsupportedOperation, AttributeError, OSError) as e:
            # Production code should always have real stdio streams
            raise RuntimeError(
                f"Cannot initialize stdio streams: {e}. "
                f"This usually means stdin/stdout don't have file descriptors. "
                f"For testing, use dependency injection or real pipe-based streams."
            )
        
        self._running = True
        logger.info("Stdio MCP server started")
    
    async def stop(self) -> None:
        """Stop the stdio server."""
        if not self._running:
            return
        
        logger.info("Stopping stdio MCP server")
        
        if self._stdout_writer:
            try:
                self._stdout_writer.close()
                await self._stdout_writer.wait_closed()
            except Exception as e:
                logger.debug(f"Error closing stdout writer: {e}")
        
        self._running = False
        logger.info("Stdio MCP server stopped")
    
    
    def is_running(self) -> bool:
        """Check if the server is currently running."""
        return self._running
    
    async def read_message(self) -> Union[MCPRequest, MCPNotification]:
        """Read a single MCP message from stdin.
        
        This method reads and validates both requests and notifications.
        
        Returns:
            The parsed MCP request or notification
            
        Raises:
            RuntimeError: If server not running or connection closed
            ValidationError: If message is invalid
        """
        if not self._running:
            raise RuntimeError("Server is not running")
        
        if not self._stdin_reader:
            raise RuntimeError("stdin reader not initialized")
        
        # Loop to skip empty lines without recursion
        while True:
            # Read a line from stdin
            line_bytes = await self._stdin_reader.readline()
            
            if not line_bytes:
                raise RuntimeError("Client connection closed")
            
            line = line_bytes.decode('utf-8').strip()
            
            # Skip empty lines by continuing the loop
            if not line:
                continue  # Read next line
            
            # Found non-empty line, break out of loop
            break
            
        logger.debug(f"Received message: {line}")
        
        # Parse JSON
        try:
            message_dict = json.loads(line)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise JSONParseError(f"Invalid JSON: {e}")
        
        # Determine message type and validate accordingly
        try:
            message_type = self._validator.determine_message_type(message_dict)
            
            if message_type == 'request':
                return self._validator.validate_request(message_dict)
            elif message_type == 'notification':
                return self._validator.validate_notification(message_dict)
            else:
                # Should not happen if determine_message_type works correctly
                raise ValueError(f"Unexpected message type: {message_type}")
                
        except ValueError as e:
            logger.error(f"Failed to validate message: {e}")
            raise ValidationError(str(e))
    
    async def read_request(self) -> MCPRequest:
        """Read a single MCP request from stdin, filtering out notifications."""
        while True:
            message = await self.read_message()
            if isinstance(message, MCPRequest):
                return message
            elif isinstance(message, MCPNotification):
                logger.debug(f"Received notification while waiting for request: {message.method}")
                # Log and discard notifications when expecting requests
                continue
    
    
    async def write_response(self, response: MCPResponse) -> None:
        """Write an MCP response to stdout.
        
        Args:
            response: The MCP response to send
            
        Raises:
            RuntimeError: If server not running or write fails
        """
        if not self._running:
            raise RuntimeError("Server is not running")
        
        if not self._stdout_writer:
            raise RuntimeError("stdout writer not initialized")
        
        # Serialize response to JSON
        response_dict = {
            "jsonrpc": response.jsonrpc,
            "id": response.id
        }
        
        if response.result is not None:
            response_dict["result"] = response.result
        elif response.error is not None:
            response_dict["error"] = response.error
        
        json_data = json.dumps(response_dict) + "\n"
        
        try:
            logger.debug(f"Sending response: {json_data.strip()}")
            self._stdout_writer.write(json_data.encode('utf-8'))
            await self._stdout_writer.drain()
        except Exception as e:
            logger.error(f"Failed to write response: {e}")
            self._running = False  # Stop server on write failure
            raise RuntimeError(f"Failed to write response: {e}")
    
    async def write_notification(self, notification: MCPNotification) -> None:
        """Write an MCP notification to stdout.
        
        Args:
            notification: The MCP notification to send to client
            
        Raises:
            RuntimeError: If server not running or write fails
        """
        if not self._running:
            raise RuntimeError("Server is not running")
        
        if not self._stdout_writer:
            raise RuntimeError("stdout writer not initialized")
        
        # Serialize notification to JSON
        notification_dict = {
            "jsonrpc": notification.jsonrpc,
            "method": notification.method
        }
        
        if notification.params is not None:
            notification_dict["params"] = notification.params
        
        json_data = json.dumps(notification_dict) + "\n"
        
        try:
            logger.debug(f"Sending notification: {json_data.strip()}")
            self._stdout_writer.write(json_data.encode('utf-8'))
            await self._stdout_writer.drain()
        except Exception as e:
            logger.error(f"Failed to write notification: {e}")
            self._running = False  # Stop server on write failure
            raise RuntimeError(f"Failed to write notification: {e}")
    
    async def handle_messages(self, request_handler, notification_handler=None):
        """Main server loop that handles incoming messages (requests and notifications).
        
        Args:
            request_handler: Async function that takes MCPRequest and returns MCPResponse
            notification_handler: Optional async function that takes MCPNotification (no return)
        """
        if not self._running:
            raise RuntimeError("Server is not running")
        
        logger.info("Starting message handling loop")
        
        try:
            while self._running:
                try:
                    # Read message from client
                    message = await self.read_message()
                    
                    if isinstance(message, MCPRequest):
                        # Process request through handler
                        response = await request_handler(message)
                        # Send response back to client
                        await self.write_response(response)
                        
                    elif isinstance(message, MCPNotification):
                        # Process notification if handler provided
                        if notification_handler:
                            await notification_handler(message)
                        else:
                            logger.debug(f"Received notification {message.method} but no handler configured")
                    
                    else:
                        logger.error(f"Unexpected message type: {type(message)}")
                    
                except JSONParseError as e:
                    # Handle JSON parse errors by sending parse error response
                    logger.warning(f"JSON parse error: {e}")
                    error_response = create_error_response(
                        request_id=None,
                        code=MCPErrorCodes.PARSE_ERROR,
                        message=str(e)
                    )
                    await self.write_response(error_response)
                    
                except (ValidationError, ValueError) as e:
                    # Handle validation errors by sending error response
                    logger.warning(f"Request validation failed: {e}")
                    error_response = create_error_response(
                        request_id=None,
                        code=MCPErrorCodes.INVALID_REQUEST,
                        message=f"Invalid request: {e}"
                    )
                    await self.write_response(error_response)
                    
                except RuntimeError as e:
                    if "connection closed" in str(e).lower():
                        logger.info("Client disconnected")
                        break
                    else:
                        logger.error(f"Runtime error in request handling: {e}")
                        break
                        
                except Exception as e:
                    logger.error(f"Unexpected error in request handling: {e}")
                    # Send internal error response
                    try:
                        error_response = create_error_response(
                            request_id=None,
                            code=MCPErrorCodes.INTERNAL_ERROR,
                            message=f"Internal server error: {e}"
                        )
                        await self.write_response(error_response)
                    except Exception:
                        # If we can't even send the error, just continue
                        pass
                    # Try to continue serving other requests
                    continue
                    
        except Exception as e:
            logger.error(f"Fatal error in request handling loop: {e}")
        finally:
            logger.info("Request handling loop ended")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
