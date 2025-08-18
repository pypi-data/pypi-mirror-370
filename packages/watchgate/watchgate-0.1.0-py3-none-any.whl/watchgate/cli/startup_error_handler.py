"""Startup error handler for communicating failures to MCP clients.

This module provides the integration between Watchgate's main entry point
and the minimal server for error communication.
"""

import asyncio
import io
import logging
import sys
from typing import Optional

from watchgate.cli.startup_error_notifier import StartupErrorNotifier
from watchgate.protocol.errors import StartupError

logger = logging.getLogger(__name__)


class StartupErrorHandler:
    """Handles startup errors by communicating them to MCP clients."""
    
    @staticmethod
    async def handle_startup_error(error: Exception, context: str = "") -> None:
        """Handle a startup error by communicating it to the MCP client.
        
        This method creates a minimal server that can respond to MCP
        requests with error information before exiting.
        
        Args:
            error: The exception that occurred during startup
            context: Additional context about what was happening
        """
        # Create error notifier
        error_notifier = StartupErrorNotifier()
        
        # Categorize the error into user-friendly format
        startup_error = error_notifier.categorize_error(error, context)
        error_notifier.startup_error = startup_error
        
        # Log the error details
        logger.error(
            f"Startup failed: {startup_error.message} - {startup_error.details}",
            exc_info=error
        )
        
        # If we're in a terminal, we're definitely not in an MCP client context
        if sys.stdin.isatty():
            logger.error("Not in MCP client context (running in terminal), exiting")
            sys.exit(1)
        
        # Try to communicate with MCP client
        # The error notifier will send the error and exit immediately
        try:
            await error_notifier.run_until_shutdown()
        except Exception as e:
            logger.error(f"Error running error notifier: {e}")
            
        # Always exit with error code
        sys.exit(1)
            
    @staticmethod
    def handle_startup_error_sync(error: Exception, context: str = "") -> None:
        """Synchronous wrapper for handle_startup_error.
        
        This is used when the error occurs before the async event loop
        is running.
        
        Args:
            error: The exception that occurred during startup
            context: Additional context about what was happening
        """
        # If we're in a terminal, we're definitely not in an MCP client context
        if sys.stdin.isatty():
            error_notifier = StartupErrorNotifier()
            startup_error = error_notifier.categorize_error(error, context)
            logger.error(
                f"Startup failed: {startup_error.message} - {startup_error.details}",
                exc_info=error
            )
            sys.exit(1)
            
        try:
            # Create new event loop to avoid issues with existing loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(StartupErrorHandler.handle_startup_error(error, context))
            finally:
                loop.close()
        except Exception as e:
            # If even the error handler fails, log and exit
            logger.error(f"Failed to communicate error to client: {e}")
            sys.exit(1)