"""Base auditing plugin with shared functionality for Watchgate MCP gateway.

This module provides the BaseAuditingPlugin class that contains common functionality
for all format-specific auditing plugins including file management, path resolution,
error handling, and logging infrastructure.
"""

from logging.handlers import RotatingFileHandler
import hashlib
import logging
import os
import re
import stat
import threading
import time
from collections import deque
from pathlib import Path
from typing import Dict, Any, Union, Optional, List, Tuple
from datetime import datetime
from watchgate.plugins.interfaces import AuditingPlugin, PathResolvablePlugin
from watchgate.protocol.messages import MCPRequest, MCPResponse, MCPNotification
from watchgate.plugins.interfaces import PolicyDecision
from watchgate.utils.paths import resolve_config_path, expand_user_path


# Compile ANSI escape regex once at module level for performance
ANSI_ESCAPE_PATTERN = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


class BaseAuditingPlugin(AuditingPlugin, PathResolvablePlugin):
    """Base class for all auditing plugins with shared functionality.
    
    Provides common functionality for:
    - File management and rotation
    - Path resolution 
    - Error handling (critical vs non-critical)
    - Logging infrastructure
    - Request timestamp tracking for duration calculation
    - Configuration validation
    
    Format-specific plugins should inherit from this class and implement
    the abstract formatting methods.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize base auditing plugin with configuration.
        
        Args:
            config: Plugin configuration dictionary with required keys:
                   - output_file: Log file path (default: "watchgate.log")
                     Supports environment variable expansion ($VAR, ${VAR}) and 
                     home directory expansion (~). Examples:
                     - "logs/audit.log" (relative to config)
                     - "/var/log/watchgate.log" (absolute)  
                     - "~/logs/audit.log" (home directory)
                     - "${LOG_DIR}/audit.log" (environment variable)
                   - max_file_size_mb: Max file size before rotation (default: 10)
                   - backup_count: Number of backup files to keep (default: 5)
                   - critical: Whether failures should halt processing (default: False)
                   
        Raises:
            ValueError: If configuration is invalid
            TypeError: If configuration has wrong types
        """
        # Validate configuration type first
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        # Initialize base class to set priority
        super().__init__(config)
        
        # Set configuration values first (needed for path resolution error handling)
        self.max_file_size_mb = config.get("max_file_size_mb", 10)
        self.backup_count = config.get("backup_count", 5)
        self.critical = config.get("critical", False)  # Default to non-critical for auditing
        
        # Store raw configuration for later path resolution
        self.raw_output_file = config.get("output_file", "watchgate.log")
        self.config_directory = None
        self.base_directory = config.get("base_directory")  # Optional security constraint
        self.max_message_length = config.get("max_message_length", 10000)  # For log injection protection
        
        # Early event buffering (configurable)
        buffer_size = config.get('event_buffer_size', 100)
        self._event_buffer = deque(maxlen=buffer_size)  # Bounded to prevent memory issues
        self._buffer_enabled = True
        self._initial_setup_warning_emitted = False
        
        # Sanitization control - preserve formatting newlines for structured formats
        self._preserve_formatting_newlines = config.get('preserve_formatting_newlines', False)
        
        # Initially use the raw path - will be resolved when config_directory is set
        self.output_file = self.raw_output_file
        
        # Initialize request tracking for duration calculation with TTL
        # Use tuple of (timestamp, start_time) for TTL tracking
        self.request_timestamps: Dict[str, Tuple[float, datetime]] = {}
        self._timestamps_lock = threading.Lock()  # Use threading.Lock for sync code
        self._last_cleanup = time.time()
        self._cleanup_interval = 60  # Cleanup every minute
        self._ttl_seconds = 300  # 5 minute TTL
        
        # Initialize logging-related attributes
        self.handler = None
        self.logger = None
        self._logging_setup_complete = False
        self._setup_lock = threading.Lock()  # Use threading.Lock for sync code
        
        # Handle path expansion (home directory and environment variables)
        try:
            expanded_file = self.raw_output_file
            
            # First expand environment variables (supports $VAR and ${VAR} syntax)
            expanded_file = os.path.expandvars(expanded_file)
            
            # Then expand home directory if present
            if expanded_file.startswith('~'):
                expanded_path = expand_user_path(expanded_file)
                self.output_file = str(expanded_path)
            else:
                self.output_file = expanded_file
            
            # Try to set up logging immediately for better error reporting
            # For absolute paths this should always work if permissions allow
            # For relative paths, this will fail but that's handled gracefully below
            try:
                # Try initial setup for both absolute and relative paths
                # For critical plugins, this should fail if there are issues
                # For non-critical plugins, allow failure and retry lazily
                self._setup_logging()
                # Return value not needed - _logging_setup_complete will be set correctly inside _setup_logging
            except Exception:
                if self.critical:
                    # Re-raise for critical plugins
                    raise
                # For non-critical plugins, setup failed, will be retried lazily during logging
                # Leave _logging_setup_complete = False to enable buffering
                    
        except Exception as e:
            # Handle home expansion or logging setup errors
            if self.critical:
                raise Exception(
                    f"Critical auditing plugin {self.__class__.__name__} failed to initialize: {e}. "
                    f"To continue with non-critical auditing, set 'critical: false' in plugin config."
                )
            # For non-critical plugins, just use the raw path
        
        # Validate configuration values
        if not isinstance(self.max_file_size_mb, (int, float)) or self.max_file_size_mb <= 0:
            raise ValueError("max_file_size_mb must be positive")
        
        if not isinstance(self.backup_count, int) or self.backup_count < 0:
            raise ValueError("backup_count must be non-negative")
    
    def set_config_directory(self, config_directory: Union[str, Path]) -> None:
        """Set the configuration directory for path resolution.
        
        Args:
            config_directory: Directory containing the configuration file
            
        Raises:
            TypeError: If config_directory is not a valid path type
            ValueError: If path resolution fails
        """
        # Validate input type
        if not isinstance(config_directory, (str, Path)):
            raise TypeError(f"config_directory must be str or Path, got {type(config_directory).__name__}")
        
        # Store config directory
        self.config_directory = Path(config_directory)
        
        # Resolve output file path with environment variable expansion
        old_output_file = self.output_file
        try:
            # First expand environment variables in raw path (consistent with __init__)
            expanded_raw = os.path.expandvars(self.raw_output_file)
            resolved_path = resolve_config_path(expanded_raw, self.config_directory)
            self.output_file = str(resolved_path)
        except (TypeError, ValueError) as e:
            # Improved error handling - don't fall back silently
            error_msg = f"Failed to resolve path '{self.raw_output_file}' relative to config directory '{self.config_directory}': {e}"
            
            if self.critical:
                raise ValueError(error_msg)
            else:
                # Log error but continue with raw path
                logger = logging.getLogger(self._get_logger_name())
                logger.error(f"Path resolution failed: {error_msg}")
                # Keep the raw path instead of falling back silently
                # This allows users to see what path is actually being used
        
        # Now that path resolution is complete, set up logging
        # If output file path changed or logging not yet set up, (re)configure logging
        if not getattr(self, '_logging_setup_complete', False) or old_output_file != self.output_file:
            with self._setup_lock:
                # Double-check pattern to avoid races - another thread may have completed setup
                # while we were waiting for the lock, or path may have been reset again
                if not getattr(self, '_logging_setup_complete', False) or old_output_file != self.output_file:
                    if getattr(self, '_logging_setup_complete', False):
                        # Path changed - need to reconfigure logging
                        # NOTE: During reconfiguration, concurrent log calls may lose some buffered 
                        # messages due to the brief period where logging is unavailable. This is 
                        # acceptable for path changes as it ensures logs go to the correct location.
                        self.cleanup()
                        self._logging_setup_complete = False
                    self._setup_logging()  # Return value not needed here, exceptions will be handled
    
    def validate_paths(self) -> List[str]:
        """Validate all paths used by this plugin.
        
        Returns:
            List[str]: List of validation error messages, empty if no errors
        """
        errors = []
        
        # Validate output file path
        try:
            output_path = Path(self.output_file)
            parent_dir = output_path.parent
            
            # Check if parent directory exists
            if not parent_dir.exists():
                errors.append(f"Parent directory does not exist: {parent_dir} (for output file: {self.output_file})")
            else:
                # Check if parent directory is writable
                if not os.access(parent_dir, os.W_OK):
                    errors.append(f"No write permission to parent directory: {parent_dir} (for output file: {self.output_file})")
                    
        except Exception as e:
            errors.append(f"Error validating output file path '{self.output_file}': {e}")
        
        return errors
    
    def _validate_output_path(self, output_file: str, base_dir: Optional[Path] = None) -> Path:
        """Validate output path is safe to use.
        
        Trust model: If base_dir not provided, allows any absolute path.
        Configure base_dir in production for strict security.
        
        Resolution order when base_dir is provided:
        1. If output_file is absolute, use as-is (still check if within base_dir)
        2. If output_file is relative, resolve relative to base_dir
        3. Expand ~ in output_file before resolution
        
        Note: TOCTTOU race exists between resolve() and open() - 
        symlink could be swapped. Low risk, documented limitation.
        """
        # Expand home directory first
        expanded_file = expand_user_path(output_file)
        
        # Handle base_dir + relative path case
        if base_dir and not Path(expanded_file).is_absolute():
            resolved = (base_dir / expanded_file).resolve()
        else:
            resolved = Path(expanded_file).resolve()
        
        # Check if within base directory (if provided)
        if base_dir:
            if not resolved.is_relative_to(base_dir):
                # Consider warning for absolute paths outside base_dir
                if Path(expanded_file).is_absolute():
                    logging.getLogger(__name__).warning(
                        f"Absolute path {expanded_file} is outside base_dir {base_dir}"
                    )
                raise ValueError(f"Path {resolved} escapes base directory {base_dir}")
        elif not base_dir:
            # Log warning if no base_dir constraint
            logging.getLogger(__name__).debug(
                f"No base_dir configured - accepting path {resolved}"
            )
        
        # Check parent directory permissions (strict mode)
        parent = resolved.parent
        if parent.exists():
            parent_stat = parent.stat()
            # Reject or warn if world-writable
            if parent_stat.st_mode & stat.S_IWOTH:
                if self.critical:
                    raise ValueError(
                        f"Critical plugin cannot use world-writable directory {parent}"
                    )
                else:
                    logging.getLogger(__name__).warning(
                        f"Parent directory {parent} is world-writable - security risk"
                    )
        
        # Reject special files
        if resolved.exists():
            # Check for special file types using stat first (more specific error messages)
            file_stat = resolved.stat()
            mode = file_stat.st_mode
            
            if stat.S_ISFIFO(mode):
                raise ValueError(f"Path {resolved} is a FIFO/pipe")
            if stat.S_ISCHR(mode):
                raise ValueError(f"Path {resolved} is a character device")
            if stat.S_ISBLK(mode):
                raise ValueError(f"Path {resolved} is a block device")
            if stat.S_ISSOCK(mode):
                raise ValueError(f"Path {resolved} is a socket")
            if not resolved.is_file():
                raise ValueError(f"Path {resolved} is not a regular file")
        
        return resolved
    
    def _setup_logging(self) -> bool:
        """Set up the rotating file handler for logging.
        
        Returns:
            bool: True if setup succeeded, False if failed (for non-critical plugins)
        """
        try:
            # Validate output path first
            base_dir = Path(self.base_directory).resolve() if self.base_directory else None
            validated_path = self._validate_output_path(self.output_file, base_dir)
            self.output_file = str(validated_path)  # Update to validated path
            
            # Create parent directories if they don't exist
            # Note: mkdir mode is subject to umask, actual permissions may be more restrictive
            log_path = Path(self.output_file)
            log_path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
            
            # Set up rotating file handler
            max_bytes = int(self.max_file_size_mb * 1024 * 1024)  # Convert MB to bytes
            self.handler = RotatingFileHandler(
                self.output_file,
                maxBytes=max_bytes,
                backupCount=self.backup_count,
                encoding='utf-8',
                mode='a',
                delay=True  # Delay file creation until first write to reduce FD usage
            )
            
            # Set up formatter - logs are formatted by format methods
            self.handler.setFormatter(logging.Formatter('%(message)s'))
            
            # Create logger with stable name for better observability
            logger_name = self._get_logger_name()
            self.logger = logging.getLogger(logger_name)
            self.logger.setLevel(logging.INFO)
            
            # Prevent duplicate handlers on reload - remove ALL existing handlers
            for existing_handler in self.logger.handlers[:]:
                self.logger.removeHandler(existing_handler)
                try:
                    existing_handler.close()
                except Exception:
                    pass  # Ignore cleanup errors
            
            self.logger.addHandler(self.handler)
            
            # Prevent propagation to avoid duplicate logs
            self.logger.propagate = False
            
            # Mark logging setup as complete
            self._logging_setup_complete = True
            return True
            
        except Exception as e:
            cwd = os.getcwd()
            
            # Provide detailed error context for better debugging
            error_details = []
            error_details.append(f"Failed to initialize auditing plugin {self.__class__.__name__}: {e}")
            error_details.append(f"Current working directory: {cwd}")
            error_details.append(f"Configured log file path: {self.output_file}")
            
            # Check if it's a path-related issue
            log_path = Path(self.output_file)
            if not log_path.is_absolute():
                error_details.append(f"ISSUE: Log file path is relative, but path resolution may not have been applied yet.")
                error_details.append(f"SOLUTION: Ensure the plugin receives config_directory for path resolution, or check if the relative path '{self.output_file}' is correct relative to the config file location.")
            else:
                # Check parent directory
                try:
                    parent_dir = log_path.parent
                    if not parent_dir.exists():
                        error_details.append(f"ISSUE: Parent directory does not exist: {parent_dir}")
                        error_details.append(f"SOLUTION: Create the directory or use a path where the parent directory exists")
                    elif not os.access(parent_dir, os.W_OK):
                        error_details.append(f"ISSUE: No write permission to parent directory: {parent_dir}")
                        error_details.append(f"SOLUTION: Check file permissions or use a writable directory")
                except Exception as path_e:
                    error_details.append(f"ISSUE: Could not analyze log file path: {path_e}")
            
            detailed_error = "\n".join(error_details)
            
            if self.critical:
                raise Exception(
                    f"Critical auditing plugin {self.__class__.__name__} failed to initialize.\n"
                    f"{detailed_error}\n"
                    f"To continue with non-critical auditing, set 'critical: false' in plugin config."
                )
            else:
                # For non-critical plugins, log the detailed error but continue
                fallback_logger = logging.getLogger(self._get_logger_name())
                # Log a compact version for the main log
                fallback_logger.error(f"Non-critical auditing plugin failed to initialize: {e} (working dir: {cwd}, config path: {self.output_file})")
                # Log the detailed version for debugging
                fallback_logger.debug(f"Detailed error information:\n{detailed_error}")
            
            # For non-critical plugins, we'll handle errors during actual logging
            self.logger = None
            return False  # Indicate setup failed
    
    def is_critical(self) -> bool:
        """Return whether this plugin is critical for operation.
        
        Returns:
            bool: True if plugin failures should halt processing, False otherwise
        """
        return self.critical
    
    def _ensure_logging_setup(self):
        """Ensure logging is set up, thread-safe."""
        if self._logging_setup_complete:
            return True  # Fast path without lock
        
        with self._setup_lock:
            # Double-check pattern to prevent race
            if self._logging_setup_complete:
                return True
            
            try:
                success = self._setup_logging()
                return success
            except Exception as e:
                if self.critical:
                    raise RuntimeError(f"Critical plugin logging failed: {e}")
                return False
    
    def _store_request_timestamp(self, request: MCPRequest):
        """Store request timestamp with TTL tracking."""
        if request.id:
            with self._timestamps_lock:
                self.request_timestamps[request.id] = (time.time(), datetime.utcnow())
                self._cleanup_orphaned_timestamps()
    
    def _calculate_duration(self, request_id: Optional[str]) -> Optional[int]:
        """Calculate request duration in milliseconds.
        
        Args:
            request_id: Request ID to calculate duration for
            
        Returns:
            Duration in milliseconds or None if not available
        """
        if request_id and request_id in self.request_timestamps:
            with self._timestamps_lock:
                if request_id in self.request_timestamps:  # Double check after acquiring lock
                    timestamp_entry, start_time = self.request_timestamps[request_id]
                    duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                    # Clean up completed request
                    del self.request_timestamps[request_id]
                    return duration_ms
        return None
    
    def _cleanup_orphaned_timestamps(self, now: Optional[float] = None):
        """Remove timestamps older than TTL.
        
        Note: Only runs on insertion. For idle periods, call
        force_cleanup_timestamps() manually or via periodic task.
        
        Args:
            now: Optional time for testing (defaults to time.time())
        """
        if now is None:
            now = time.time()
            
        if now - self._last_cleanup < self._cleanup_interval:
            return  # Skip if cleaned up recently
        
        self._last_cleanup = now
        cutoff = now - self._ttl_seconds
        
        # Remove expired entries
        expired_ids = [
            req_id for req_id, (timestamp, _) in self.request_timestamps.items()
            if timestamp < cutoff
        ]
        for req_id in expired_ids:
            del self.request_timestamps[req_id]
    
    def force_cleanup_timestamps(self, current_time: Optional[float] = None):
        """Force cleanup of orphaned timestamps (for testing/maintenance).
        
        Args:
            current_time: Optional time to use for testing (defaults to time.time())
        """
        with self._timestamps_lock:
            self._last_cleanup = 0  # Force cleanup on next call
            # Pass time directly without monkeypatching
            self._cleanup_orphaned_timestamps(now=current_time)
    
    def _extract_plugin_info(self, decision: PolicyDecision) -> str:
        """Extract plugin identification from decision metadata.
        
        Args:
            decision: The policy decision containing metadata
            
        Returns:
            str: Plugin name or 'unknown' if not found
        """
        if decision and decision.metadata:
            return decision.metadata.get("plugin", "unknown")
        return "unknown"
    
    def _sanitize_for_logging(self, message: str, max_length: Optional[int] = None) -> str:
        """Sanitize message for safe logging.
        
        Note: Preserves tabs for readability. For stricter security,
        consider JSON encoding or format-specific escaping.
        
        WARNING: This sanitization is NOT reversible and alters message
        semantics. Format-specific plugins (JSON/CEF) should NOT double-
        sanitize - call this only once in base class.
        
        Note: max_message_length applies AFTER format serialization, so
        JSON pretty-printing or other formatting won't bypass the limit.
        """
        # Use configured max length or default
        if max_length is None:
            max_length = getattr(self, 'max_message_length', 10000)
        
        # Truncate oversized messages and log warning
        if len(message) > max_length:
            message = message[:max_length] + "...[truncated]"
            if not getattr(self, '_truncation_warning_logged', False):
                self._truncation_warning_logged = True
                logging.getLogger(__name__).warning(
                    f"Message truncated to {max_length} chars. "
                    f"Set max_message_length in config to adjust."
                )
        
        # Normalize line endings (CRLF -> LF, then conditionally preserve or remove)
        message = message.replace('\r\n', '\n').replace('\r', '\n')
        if not self._preserve_formatting_newlines:
            message = message.replace('\n', ' ')
        
        # Remove ANSI escape sequences
        message = ANSI_ESCAPE_PATTERN.sub('', message)
        
        # Remove dangerous control characters but preserve tabs (and newlines if formatting preservation enabled)
        # Note: This may remove some Unicode separators. For full Unicode
        # safety, consider using unicodedata.category() filtering
        allowed_chars = ' \t'
        if self._preserve_formatting_newlines:
            allowed_chars += '\n'
        message = ''.join(
            c if c.isprintable() or c in allowed_chars else f'\\x{ord(c):02x}'
            for c in message
        )
        
        return message
    
    def _sanitize_reason(self, reason: Optional[str]) -> str:
        """Sanitize reason text to prevent log parsing issues.
        
        Args:
            reason: Original reason text
            
        Returns:
            str: Sanitized reason text safe for single-line logs
        """
        if not reason:
            return ""
        
        # Replace newlines and control characters with spaces
        import re
        sanitized = re.sub(r'[\r\n\x00-\x1f\x7f-\x9f]', ' ', reason)
        # Collapse multiple spaces
        sanitized = re.sub(r'\s+', ' ', sanitized)
        # Trim whitespace
        return sanitized.strip()
    
    def _sanitize_reason_for_kv(self, reason: Optional[str]) -> str:
        """Sanitize reason text for key-value format with quote escaping.
        
        Args:
            reason: Original reason text
            
        Returns:
            str: Sanitized reason text safe for quoted key-value pairs
        """
        if not reason:
            return ""
        
        # First apply basic sanitization
        sanitized = self._sanitize_reason(reason)
        # Escape quotes and backslashes for safe quoting
        sanitized = sanitized.replace('\\', '\\\\').replace('"', '\\"')
        return sanitized
    
    def _sanitize_user_string(self, text: Optional[str]) -> str:
        """Sanitize potentially user-controlled strings like tool names, methods.
        
        Args:
            text: Text that might be user-controlled
            
        Returns:
            str: Sanitized text safe for logging
        """
        if not text:
            return ""
        
        # Apply same sanitization as reason but more conservative
        return self._sanitize_reason(text)
    
    def _get_modification_type(self, decision: 'PolicyDecision') -> str:
        """Determine the type of modification from decision metadata.
        
        Args:
            decision: Policy decision with potential modification info
            
        Returns:
            str: Modification type (REDACTION, MODIFICATION, etc.)
        """
        if decision.metadata:
            mod_type = decision.metadata.get("modification_type")
            if mod_type == "redaction":
                return "REDACTION"
            elif mod_type == "transformation":
                return "MODIFICATION"
            elif mod_type:
                return "MODIFICATION"
        
        # Default to MODIFICATION for unknown cases
        return "MODIFICATION"
    
    def _sanitize_params(self, params: Any, max_length: int = 500) -> Any:
        """Sanitize parameters to prevent PII leakage.
        
        Args:
            params: Original parameters
            max_length: Maximum length for parameter values
            
        Returns:
            Any: Sanitized parameters with potential PII redacted
        """
        if isinstance(params, dict):
            sanitized = {}
            for key, value in params.items():
                # Common sensitive parameter names to redact
                sensitive_keys = {
                    'password', 'secret', 'token', 'key', 'credential', 'auth',
                    'api_key', 'apikey', 'bearer', 'session', 'cookie', 'csrf',
                    'authorization', 'x-api-key', 'access_token', 'refresh_token',
                    'private_key', 'client_secret', 'jwt', 'oauth', 'signature'
                }
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    sanitized[key] = "[REDACTED]"
                elif isinstance(value, str) and len(value) > max_length:
                    sanitized[key] = value[:max_length] + "...[TRUNCATED]"
                elif isinstance(value, (dict, list)):
                    sanitized[key] = self._sanitize_params(value, max_length)
                else:
                    sanitized[key] = value
            return sanitized
        elif isinstance(params, list):
            return [self._sanitize_params(item, max_length) for item in params]
        elif isinstance(params, str) and len(params) > max_length:
            return params[:max_length] + "...[TRUNCATED]"
        else:
            return params
    
    def _get_logger_name(self) -> str:
        """Generate stable logger name for better observability.
        
        Uses plugin class name and output file hash for consistency across reloads.
        This provides stable logger names that remain consistent even if the plugin
        instance is recreated, making log analysis and monitoring easier.
        
        Returns:
            str: Stable logger name
        """
        class_name = self.__class__.__name__
        
        # Use output file if available, otherwise fall back to raw output file
        file_for_hash = getattr(self, 'output_file', None) or getattr(self, 'raw_output_file', 'unknown')
        # Use fast hash for stable logger names across reloads
        file_hash = hashlib.blake2s(file_for_hash.encode(), digest_size=4).hexdigest()
        return f"watchgate.audit.{class_name}.{file_hash}"
    
    def _safe_log(self, message: str):
        """Log with buffering for early events."""
        # Sanitize first
        message = self._sanitize_for_logging(message)
        
        if not self._logging_setup_complete and self._buffer_enabled:
            # Buffer early events
            self._event_buffer.append(message)
            
            # Try setup and emit warning once
            if not self._initial_setup_warning_emitted:
                self._initial_setup_warning_emitted = True
                fallback_logger = logging.getLogger(__name__)
                fallback_logger.warning(
                    f"Auditing plugin {self.__class__.__name__} setup incomplete, "
                    f"buffering events (max {self._event_buffer.maxlen})"
                )
            
            # Attempt setup
            if self._ensure_logging_setup():
                # Flush buffered events
                self._flush_event_buffer()
            return
        
        # Normal logging path
        try:
            if self.logger:
                self.logger.info(message)
        except Exception as e:
            if self.critical:
                raise
            else:
                # For non-critical plugins, log the exception with stack trace to avoid silent drops
                fallback_logger = logging.getLogger(__name__)
                fallback_logger.exception("Non-critical auditing plugin logging failed")
    
    def _flush_event_buffer(self):
        """Flush buffered events to logger.
        
        Note: Events emit with preserved order but delayed timestamps.
        This causes temporal skew vs real-time sequence.
        """
        self._buffer_enabled = False  # Prevent re-buffering
        while self._event_buffer:
            message = self._event_buffer.popleft()
            if self.logger:
                self.logger.info(message)
    
    def cleanup(self):
        """Clean up resources - call on plugin deletion/reload."""
        if self.handler:
            # Flush and close the handler
            self.handler.flush()
            self.handler.close()
            
            # Remove handler from logger
            if self.logger:
                self.logger.removeHandler(self.handler)
            
            self.handler = None
        
        # Note: Safer NOT to remove from logging.Manager to avoid affecting
        # other references. Just removing handler is sufficient.
        self.logger = None
        self._logging_setup_complete = False

    def __del__(self):
        """Cleanup on garbage collection."""
        try:
            self.cleanup()
        except Exception:
            pass  # Suppress errors during GC
    
    # Abstract methods that format-specific plugins must implement
    async def log_request(self, request: MCPRequest, decision: PolicyDecision, server_name: str) -> None:
        """Log an incoming request and its security decision.
        
        Args:
            request: The MCP request being processed
            decision: The security policy decision for this request
            server_name: Name of the target server
            
        Raises:
            Exception: If plugin is critical and logging fails
        """
        # Store timestamp for duration calculation
        self._store_request_timestamp(request)
        
        # Format and log the request
        log_message = self._format_request_log(request, decision, server_name)
        self._safe_log(log_message)
    
    async def log_response(self, request: MCPRequest, response: MCPResponse, decision: PolicyDecision, server_name: str) -> None:
        """Log a response to a request with the security decision.
        
        Args:
            request: The original MCP request for correlation
            response: The MCP response from the upstream server
            decision: The policy decision made by security plugins for this response
            server_name: Name of the source server
            
        Raises:
            Exception: If plugin is critical and logging fails
        """
        # Calculate duration and add to metadata
        duration_ms = self._calculate_duration(request.id)
        enhanced_decision = self._enhance_decision_with_duration(decision, duration_ms)
        
        # Format and log the response
        log_message = self._format_response_log(request, response, enhanced_decision, server_name)
        self._safe_log(log_message)
    
    async def log_notification(self, notification: MCPNotification, decision: PolicyDecision, server_name: str) -> None:
        """Log a notification message.
        
        Args:
            notification: The MCP notification being processed
            decision: The policy decision from security plugins
            server_name: Name of the source server
            
        Raises:
            Exception: If plugin is critical and logging fails
        """
        # Format and log the notification
        log_message = self._format_notification_log(notification, decision, server_name)
        self._safe_log(log_message)
    
    def _enhance_decision_with_duration(self, decision: PolicyDecision, duration_ms: Optional[int]) -> PolicyDecision:
        """Add duration metadata to the decision if available.
        
        Args:
            decision: Original policy decision
            duration_ms: Duration in milliseconds
            
        Returns:
            PolicyDecision with enhanced metadata
        """
        if duration_ms is None:
            return decision
        
        # Create or copy metadata
        if decision.metadata is None:
            enhanced_metadata = {"duration_ms": duration_ms}
        else:
            enhanced_metadata = decision.metadata.copy()
            # Only set duration_ms if not already present in metadata
            if "duration_ms" not in enhanced_metadata:
                enhanced_metadata["duration_ms"] = duration_ms
        
        # Return new decision with enhanced metadata
        return PolicyDecision(
            allowed=decision.allowed,
            reason=decision.reason,
            metadata=enhanced_metadata,
            modified_content=decision.modified_content
        )
    
    # Abstract formatting methods - must be implemented by subclasses
    def _format_request_log(self, request: MCPRequest, decision: PolicyDecision, server_name: str) -> str:
        """Format a request log message. Must be implemented by subclasses.
        
        Args:
            request: The MCP request
            decision: Policy decision
            server_name: Name of the target server
            
        Returns:
            str: Formatted log message
        """
        raise NotImplementedError(f"Subclass {self.__class__.__name__} must implement _format_request_log")
    
    def _format_response_log(self, request: MCPRequest, response: MCPResponse, decision: PolicyDecision, server_name: str) -> str:
        """Format a response log message. Must be implemented by subclasses.
        
        Args:
            request: The original MCP request
            response: The MCP response
            decision: Policy decision
            server_name: Name of the source server
            
        Returns:
            str: Formatted log message
        """
        raise NotImplementedError(f"Subclass {self.__class__.__name__} must implement _format_response_log")
    
    def _format_notification_log(self, notification: MCPNotification, decision: PolicyDecision, server_name: str) -> str:
        """Format a notification log message. Must be implemented by subclasses.
        
        Args:
            notification: The MCP notification
            decision: Policy decision
            server_name: Name of the source server
            
        Returns:
            str: Formatted log message
        """
        raise NotImplementedError(f"Subclass {self.__class__.__name__} must implement _format_notification_log")