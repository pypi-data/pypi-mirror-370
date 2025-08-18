"""Utilities for testing stdio-based components with real pipes.

This module provides helper functions to create real pipe-based streams
for testing stdio components without using mocks in production code.
"""

import asyncio
import os
import tempfile
from typing import Tuple, Optional
from contextlib import asynccontextmanager


class PipeStream:
    """A pipe-based stream that provides real file descriptors for testing."""
    
    def __init__(self, read_fd: int, write_fd: int):
        self.read_fd = read_fd
        self.write_fd = write_fd
        self._read_file = None
        self._write_file = None
    
    def fileno_read(self) -> int:
        """Get the read file descriptor."""
        return self.read_fd
    
    def fileno_write(self) -> int:
        """Get the write file descriptor."""
        return self.write_fd
    
    def get_read_file(self):
        """Get a file object for reading."""
        if self._read_file is None:
            self._read_file = os.fdopen(self.read_fd, 'rb')
        return self._read_file
    
    def get_write_file(self):
        """Get a file object for writing."""
        if self._write_file is None:
            self._write_file = os.fdopen(self.write_fd, 'wb')
        return self._write_file
    
    def close(self):
        """Close the pipe streams."""
        if self._read_file:
            self._read_file.close()
        if self._write_file:
            self._write_file.close()
        
        # Close file descriptors if they're still open
        try:
            os.close(self.read_fd)
        except OSError:
            pass
        try:
            os.close(self.write_fd)
        except OSError:
            pass


def create_pipe_pair() -> Tuple[PipeStream, PipeStream]:
    """Create a pair of connected pipes for testing.
    
    Returns:
        Tuple of (input_pipe, output_pipe) where:
        - input_pipe: Has read_fd for reading data, write_fd for writing data to be read
        - output_pipe: Has read_fd for reading written data, write_fd for writing data
        
    Example:
        # For testing StdioServer:
        stdin_pipe, stdin_feeder = create_pipe_pair()
        stdout_reader, stdout_pipe = create_pipe_pair()
        
        # stdin_pipe provides the stdin file descriptor
        # stdin_feeder is used to feed data to stdin
        # stdout_pipe provides the stdout file descriptor  
        # stdout_reader is used to read stdout data
    """
    # Create two pipes
    read_fd1, write_fd1 = os.pipe()
    read_fd2, write_fd2 = os.pipe()
    
    # First pipe: for reading from read_fd1, writing to write_fd1
    input_pipe = PipeStream(read_fd1, write_fd2)
    # Second pipe: for reading from read_fd2, writing to write_fd2
    output_pipe = PipeStream(read_fd2, write_fd1)
    
    return input_pipe, output_pipe


class MockStdinFile:
    """A file-like object that provides a real file descriptor for stdin testing."""
    
    def __init__(self, pipe_stream: PipeStream):
        self.pipe_stream = pipe_stream
        self._file = pipe_stream.get_read_file()
    
    def fileno(self) -> int:
        return self.pipe_stream.read_fd
    
    def close(self):
        self.pipe_stream.close()


class MockStdoutFile:
    """A file-like object that provides a real file descriptor for stdout testing."""
    
    def __init__(self, pipe_stream: PipeStream):
        self.pipe_stream = pipe_stream
        self._file = pipe_stream.get_write_file()
    
    def fileno(self) -> int:
        return self.pipe_stream.write_fd
    
    def close(self):
        self.pipe_stream.close()


@asynccontextmanager
async def stdio_test_environment():
    """Create a test environment with real pipes for stdin/stdout testing.
    
    Yields:
        Dict with keys:
        - 'stdin_file': Mock stdin file with real file descriptor
        - 'stdout_file': Mock stdout file with real file descriptor  
        - 'stdin_writer': Stream writer to send data to stdin
        - 'stdout_reader': Stream reader to read data from stdout
        
    Example:
        async with stdio_test_environment() as env:
            server = StdioServer(
                stdin_file=env['stdin_file'],
                stdout_file=env['stdout_file']
            )
            await server.start()
            
            # Send data to stdin
            env['stdin_writer'].write(b'{"jsonrpc": "2.0", "method": "test"}\\n')
            await env['stdin_writer'].drain()
            
            # Read data from stdout
            response = await env['stdout_reader'].readline()
    """
    # Create pipe pairs
    stdin_pipe, stdin_feeder = create_pipe_pair()
    stdout_reader, stdout_pipe = create_pipe_pair()
    
    # Create file-like objects with real file descriptors
    stdin_file = MockStdinFile(stdin_pipe)
    stdout_file = MockStdoutFile(stdout_pipe)
    
    # Create async writers/readers for the other ends
    loop = asyncio.get_event_loop()
    
    # Create writer for sending data to stdin
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
            if self._close_waiter is None:
                self._close_waiter = asyncio.Future()
            return self._close_waiter
        
        def _drain_helper(self):
            if self._closed:
                return asyncio.sleep(0)
            return asyncio.sleep(0)
    
    stdin_write_transport, stdin_write_protocol = await loop.connect_write_pipe(
        WriteProtocol,
        stdin_feeder.get_write_file()
    )
    stdin_writer = asyncio.StreamWriter(
        transport=stdin_write_transport,
        protocol=stdin_write_protocol,
        reader=None,
        loop=loop
    )
    
    # Create reader for reading data from stdout
    stdout_reader_stream = asyncio.StreamReader()
    stdout_read_transport, stdout_read_protocol = await loop.connect_read_pipe(
        lambda: asyncio.StreamReaderProtocol(stdout_reader_stream),
        stdout_reader.get_read_file()
    )
    
    try:
        yield {
            'stdin_file': stdin_file,
            'stdout_file': stdout_file,
            'stdin_writer': stdin_writer,
            'stdout_reader': stdout_reader_stream
        }
    finally:
        # Cleanup
        stdin_writer.close()
        await stdin_writer.wait_closed()
        
        stdin_file.close()
        stdout_file.close()
        stdin_feeder.close()
        stdout_reader.close()


async def send_json_message(writer: asyncio.StreamWriter, message: dict):
    """Send a JSON message through a stream writer."""
    import json
    json_data = json.dumps(message) + "\n"
    writer.write(json_data.encode('utf-8'))
    await writer.drain()


async def read_json_message(reader: asyncio.StreamReader) -> Optional[dict]:
    """Read a JSON message from a stream reader."""
    import json
    line = await reader.readline()
    if not line:
        return None
    
    try:
        return json.loads(line.decode('utf-8').strip())
    except json.JSONDecodeError:
        return None