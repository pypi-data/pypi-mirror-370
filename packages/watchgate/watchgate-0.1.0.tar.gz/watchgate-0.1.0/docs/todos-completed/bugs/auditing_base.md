# Auditing Base Plugin Bug Fixes and Improvements

## Overview
Comprehensive list of bugs and improvements needed for the base auditing plugin (`watchgate/plugins/auditing/base.py`) identified through quality control review.

## Critical Bugs (Must Fix)

### 1. AttributeError in _extract_plugin_info
**Location**: base.py:309
**Issue**: `decision.metadata.get("plugin", "unknown")` crashes when metadata is None
**Impact**: Causes plugin failure when PolicyDecision created without metadata
**Fix**: Add None check before accessing metadata
```python
def _extract_plugin_info(self, decision: PolicyDecision) -> str:
    if decision.metadata is None:
        return "unknown"
    return decision.metadata.get("plugin", "unknown")
```

### 2. Memory Leak in request_timestamps
**Location**: base.py:68, 280-297
**Issue**: 
- Dictionary not thread/async safe for concurrent access
- Orphaned entries never cleaned up if responses don't arrive
**Impact**: Unbounded memory growth in long-running processes
**Fix Implementation**:
```python
import time
from typing import Dict, Tuple

class BaseAuditingPlugin:
    def __init__(self, config):
        # Use tuple of (timestamp, start_time) for TTL tracking
        self.request_timestamps: Dict[str, Tuple[float, datetime]] = {}
        self._timestamps_lock = threading.Lock()  # Use threading.Lock for sync code
        self._last_cleanup = time.time()
        self._cleanup_interval = 60  # Cleanup every minute
        self._ttl_seconds = 300  # 5 minute TTL
    
    def _store_request_timestamp(self, request: MCPRequest):
        """Store request timestamp with TTL tracking."""
        if request.id:
            with self._timestamps_lock:
                self.request_timestamps[request.id] = (time.time(), datetime.utcnow())
                self._cleanup_orphaned_timestamps()
    
    def _cleanup_orphaned_timestamps(self, now: Optional[float] = None):
        """Remove timestamps older than TTL.
        
        Note: Only runs on insertion. For idle periods, call
        force_cleanup_timestamps() manually or via periodic task.
        
        Args:
            now: Optional time for testing (defaults to time.time())
        """
        if now is None:
            import time
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
```
**Acceptance Criteria**:
- Test concurrent access with 100+ simultaneous requests
- Verify orphaned entries removed after TTL expires
- Measure memory usage remains bounded over 10000 requests
- Test cleanup trigger mechanism under load

## Security Issues (High Priority)

### 3. Path Traversal and Special File Vulnerability
**Location**: base.py:134-148
**Issue**: 
- No validation against symlinks or `../` sequences
- No protection against special files (FIFO, device nodes, sockets)
**Impact**: 
- Logs written to sensitive system locations
- Blocking on special files (FIFOs)
- Writing to device files
**Fix**:
```python
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
    from watchgate.utils.paths import expand_user_path
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
                import logging
                logging.getLogger(__name__).warning(
                    f"Absolute path {expanded_file} is outside base_dir {base_dir}"
                )
            raise ValueError(f"Path {resolved} escapes base directory {base_dir}")
    elif not base_dir:
        # Log warning if no base_dir constraint
        import logging
        logging.getLogger(__name__).debug(
            f"No base_dir configured - accepting path {resolved}"
        )
    
    # Check parent directory permissions (strict mode)
    parent = resolved.parent
    if parent.exists():
        import stat
        parent_stat = parent.stat()
        # Reject or warn if world-writable
        if parent_stat.st_mode & stat.S_IWOTH:
            if self.critical:
                raise ValueError(
                    f"Critical plugin cannot use world-writable directory {parent}"
                )
            else:
                import logging
                logging.getLogger(__name__).warning(
                    f"Parent directory {parent} is world-writable - security risk"
                )
    
    # Reject special files
    if resolved.exists():
        if not resolved.is_file():
            raise ValueError(f"Path {resolved} is not a regular file")
        
        # Check for special file types using stat
        import stat
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
    
    return resolved
```
**Acceptance Criteria**:
- Test symlink resolution and rejection
- Test `../` traversal attempts
- Test FIFO/pipe rejection
- Test device file rejection (/dev/null, /dev/zero)
- Test socket file rejection
- Verify regular files and new files accepted

### 4. Log Injection and Control Character Attacks
**Location**: base.py:198
**Issue**: User-controlled data can inject malicious content
**Specific Threats**:
- Newline injection (both LF and CRLF)
- ANSI escape sequences for terminal manipulation
- Other control characters (NULL, backspace, etc.)
- Excessively large messages causing DoS
**Impact**: Log forgery, terminal hijacking, parser confusion, resource exhaustion
**Fix**:
```python
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
            import logging
            logging.getLogger(__name__).warning(
                f"Message truncated to {max_length} chars. "
                f"Set max_message_length in config to adjust."
            )
    
    # Normalize line endings (CRLF -> LF -> space)
    message = message.replace('\r\n', '\n').replace('\r', '\n').replace('\n', ' ')
    
    # Remove ANSI escape sequences
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    message = ansi_escape.sub('', message)
    
    # Remove dangerous control characters but preserve tabs
    # Note: This may remove some Unicode separators. For full Unicode
    # safety, consider using unicodedata.category() filtering
    message = ''.join(
        c if c.isprintable() or c in ' \t' else f'\\x{ord(c):02x}'
        for c in message
    )
    
    return message
```
**Acceptance Criteria**:
- Test with CRLF, LF, and mixed line endings
- Test with ANSI color codes and cursor movement
- Test with NULL bytes and other control chars
- Test message truncation at max_length with "...[truncated]" suffix
- Test truncation warning logged once
- Test tabs preserved, other control chars hex-encoded
- Verify no log injection possible

## Resource Management Issues

### 5. File Descriptor and Logger Leaks
**Location**: base.py:189-206
**Issue**: 
- No cleanup on plugin deletion/reload
- Python logging module keeps references
- Multiple instances accumulate handlers
**Impact**: File descriptor exhaustion, memory leaks
**Fix**:
```python
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
```
**Acceptance Criteria**:
- Test file descriptor count before/after multiple instantiations
- Verify no handler accumulation with this test:
```python
def test_no_handler_accumulation():
    """Cross-platform test for handler accumulation."""
    import sys
    import logging
    
    # Platform-specific FD counting
    if sys.platform == 'linux':
        initial_fd_count = len(os.listdir('/proc/self/fd'))
    elif sys.platform == 'darwin':  # macOS
        # Fallback: count handlers in logging system
        initial_handler_count = sum(
            len(logger.handlers) 
            for logger in logging.Logger.manager.loggerDict.values()
            if isinstance(logger, logging.Logger)
        )
    else:
        # Generic fallback: try psutil if available
        try:
            import psutil
            proc = psutil.Process()
            initial_fd_count = proc.num_fds()
        except ImportError:
            # Last resort: count root logger handlers
            initial_handler_count = len(logging.root.handlers)
    
    for i in range(100):
        plugin = BaseAuditingPlugin(config)
        plugin.cleanup()
    
    # Check based on platform
    if sys.platform == 'linux':
        final_fd_count = len(os.listdir('/proc/self/fd'))
        assert final_fd_count == initial_fd_count
    elif sys.platform == 'darwin':
        final_handler_count = sum(
            len(logger.handlers) 
            for logger in logging.Logger.manager.loggerDict.values()
            if isinstance(logger, logging.Logger)
        )
        assert final_handler_count == initial_handler_count
    # ... similar for other platforms
```
- Test cleanup called on plugin reload
- Verify no errors during garbage collection

### 6. Multiple Plugins Writing to Same File
**Location**: Throughout file handling
**Issue**: No coordination between plugins targeting same output file
**Impact**: Corrupted logs, lock contention, interleaved output
**Design Decision**: Use shared handler registry
**Implementation**:
```python
# Global registry for handler sharing
_handler_registry: Dict[str, Tuple[RotatingFileHandler, int]] = {}
_registry_lock = threading.Lock()

class BaseAuditingPlugin:
    def _setup_logging(self):
        """Set up logging with shared handler registry.
        
        Note: RotatingFileHandler is not inherently thread-safe but
        acceptable for shared use with proper locking.
        
        IMPORTANT: When sharing handlers, the first plugin's size/backup
        settings win. All plugins sharing a file must use identical
        rotation settings or accept first-creator's configuration.
        """
        resolved_path = str(Path(self.output_file).resolve())
        
        with _registry_lock:
            if resolved_path in _handler_registry:
                # Reuse existing handler
                handler, ref_count = _handler_registry[resolved_path]
                _handler_registry[resolved_path] = (handler, ref_count + 1)
                self.handler = handler
                self._shared_handler = True
                
                # Warn if settings differ from first creator
                if (self.max_file_size_mb * 1024 * 1024) != handler.maxBytes:
                    import logging
                    logging.getLogger(__name__).warning(
                        f"Plugin settings ignored for {resolved_path}: "
                        f"max_file_size_mb={self.max_file_size_mb} "
                        f"differs from existing handler ({handler.maxBytes} bytes)"
                    )
                if self.backup_count != handler.backupCount:
                    import logging
                    logging.getLogger(__name__).warning(
                        f"Plugin settings ignored for {resolved_path}: "
                        f"backup_count={self.backup_count} "
                        f"differs from existing handler ({handler.backupCount})"
                    )
            else:
                # Create new handler
                max_bytes = int(self.max_file_size_mb * 1024 * 1024)
                self.handler = RotatingFileHandler(
                    self.output_file,
                    maxBytes=max_bytes,
                    backupCount=self.backup_count
                )
                _handler_registry[resolved_path] = (self.handler, 1)
                self._shared_handler = False
            
            # Create logger that uses the handler
            self.logger = logging.getLogger(f"watchgate.audit.{id(self)}")
            
            # CRITICAL: Check if handler already attached to prevent duplicates
            if self.handler not in self.logger.handlers:
                self.logger.addHandler(self.handler)
    
    def cleanup(self):
        """Cleanup with registry management.
        
        Responsibility: Each plugin must call cleanup() to remove its
        handler reference. The registry will close the handler when the
        last reference is removed.
        """
        # Remove handler from logger first
        if self.logger and self.handler:
            self.logger.removeHandler(self.handler)
        
        if self.handler:
            resolved_path = str(Path(self.output_file).resolve())
            
            with _registry_lock:
                if resolved_path in _handler_registry:
                    handler, ref_count = _handler_registry[resolved_path]
                    if ref_count <= 1:
                        # Last reference - close handler and remove from any loggers
                        handler.close()
                        
                        # Clean up any remaining references in logging system
                        for logger_name, logger in logging.Logger.manager.loggerDict.items():
                            if isinstance(logger, logging.Logger) and handler in logger.handlers:
                                logger.removeHandler(handler)
                        
                        del _handler_registry[resolved_path]
                    else:
                        # Decrement reference count
                        _handler_registry[resolved_path] = (handler, ref_count - 1)
```
**Acceptance Criteria**:
- Test multiple plugins writing to same file produce valid output
- Verify handler reuse when paths resolve to same file
- Test reference counting and cleanup
- No file corruption under concurrent writes
- Performance test with 10 plugins → 1 file
- Test log rotation with shared handler:
```python
def test_shared_handler_rotation():
    """Test that rotation works correctly with shared handler."""
    import logging
    import tempfile
    import shutil
    
    # Use temporary directory for test files
    with tempfile.TemporaryDirectory() as tmpdir:
        test_log = Path(tmpdir) / "test.log"
        
        config1 = {"output_file": str(test_log), "max_file_size_mb": 0.001, "backup_count": 3}
        config2 = {"output_file": str(test_log), "max_file_size_mb": 10, "backup_count": 10}
        
        try:
            # Track warnings
            with self.assertLogs(level=logging.WARNING) as logs:
                plugin1 = BaseAuditingPlugin(config1)
                plugin2 = BaseAuditingPlugin(config2)
            
            # First creator's settings should win
            assert plugin1.handler is plugin2.handler  # Same handler
            assert plugin1.handler.maxBytes == 1024  # First plugin's setting
            assert plugin1.handler.backupCount == 3  # First plugin's backup count
            
            # Warning should include resolved path
            assert any(str(test_log) in log for log in logs.output)
            
            # Write enough to trigger rotation
            for i in range(100):
                plugin1._safe_log("x" * 100)
            
            # Verify rotation occurred
            assert (Path(tmpdir) / "test.log.1").exists()
            
        finally:
            # Cleanup plugins
            plugin1.cleanup()
            plugin2.cleanup()
```
- Test no stale handlers on root logger after cleanup:
```python
def test_no_root_logger_handlers_after_cleanup():
    """Verify no handlers linger on root logger."""
    import logging
    import tempfile
    
    initial_root_handlers = list(logging.root.handlers)
    
    # Use temporary directory to avoid file pollution
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create and cleanup multiple plugins
        plugins = []
        for i in range(5):
            log_file = Path(tmpdir) / f"test{i}.log"
            plugin = BaseAuditingPlugin({"output_file": str(log_file)})
            plugins.append(plugin)
        
        # Cleanup all
        for plugin in plugins:
            plugin.cleanup()
        
        # Check root logger has no new handlers
        final_root_handlers = list(logging.root.handlers)
        assert final_root_handlers == initial_root_handlers
        
        # Also verify no handlers in registry
        assert len(_handler_registry) == 0
    # tmpdir automatically cleaned up
```

## Reliability Issues

### 7. Race Condition in Logging Setup
**Location**: base.py:266-276, 181-256
**Issue**: Concurrent coroutines could race during `_setup_logging()`
**Impact**: Duplicate handlers, setup errors
**Fix**:
```python
class BaseAuditingPlugin:
    def __init__(self, config):
        self._setup_lock = threading.Lock()  # Use threading.Lock for sync code
        self._logging_setup_complete = False
    
    def _ensure_logging_setup(self):
        """Ensure logging is set up, thread-safe."""
        if self._logging_setup_complete:
            return True  # Fast path without lock
        
        with self._setup_lock:
            # Double-check pattern to prevent race
            if self._logging_setup_complete:
                return True
            
            try:
                self._setup_logging()
                return True
            except Exception as e:
                if self.critical:
                    raise RuntimeError(f"Critical plugin logging failed: {e}")
                return False
```
**Note**: Since logging operations are synchronous, use `threading.Lock` not `asyncio.Lock`
**Acceptance Criteria**:
- Test with 100 concurrent log attempts on fresh plugin
- Verify only one handler created
- Test double-check pattern prevents duplicate setup
- No deadlocks under concurrent access

### 8. Silent Early Audit Event Loss
**Location**: base.py:91-98
**Issue**: Initial setup failure for non-critical plugins silently drops early events
**Impact**: Missing audit trail without operator awareness
**Fix Implementation**:
```python
from collections import deque
import logging

class BaseAuditingPlugin:
    def __init__(self, config):
        # Early event buffering (configurable)
        buffer_size = config.get('event_buffer_size', 100)
        self._event_buffer = deque(maxlen=buffer_size)  # Bounded to prevent memory issues
        self._buffer_enabled = True
        self._initial_setup_warning_emitted = False
        
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
```
**Acceptance Criteria**:
- Test buffer fills and flushes on successful setup
- Verify one-time warning emitted
- Test buffer overflow (>100 events) drops oldest
- Verify no buffering after successful setup

## Design Improvements

### 9. Duration Metadata Consistency
**Location**: base.py:381-402
**Issue**: Duration not added when metadata is None
**Impact**: Inconsistent audit logs
**Fix**:
```python
def _enhance_decision_with_duration(self, decision: PolicyDecision, duration_ms: Optional[int]) -> PolicyDecision:
    """Add duration metadata to the decision if available."""
    if not duration_ms:
        return decision
    
    # Create or copy metadata
    if decision.metadata is None:
        enhanced_metadata = {"duration_ms": duration_ms}
    else:
        enhanced_metadata = decision.metadata.copy()
        enhanced_metadata["duration_ms"] = duration_ms
    
    # Return new decision with enhanced metadata
    return PolicyDecision(
        allowed=decision.allowed,
        reason=decision.reason,
        metadata=enhanced_metadata,
        modified_content=decision.modified_content
    )
```
**Acceptance Criteria**:
- Test with decision.metadata=None and duration present
- Test with existing metadata and duration
- Test with no duration (returns original decision)
- Verify original decision not mutated
- Test downstream code doesn't rely on object identity:
```python
def test_decision_identity_not_relied_upon():
    """Verify downstream code handles new decision objects."""
    original = PolicyDecision(allowed=True, reason="test")
    enhanced = plugin._enhance_decision_with_duration(original, 100)
    
    assert original is not enhanced  # Different objects
    assert original.metadata is None  # Original unchanged
    assert enhanced.metadata == {"duration_ms": 100}
    
    # Test that downstream code works with new object
    # (simulate what happens in log_response)
    plugin._format_response_log(request, response, enhanced, "server")
    
    # Test equality semantics if needed
    # Note: PolicyDecision is a dataclass, so equality is value-based
    same_values = PolicyDecision(allowed=True, reason="test")
    assert original == same_values  # Equal by value
    assert original is not same_values  # Different objects
```

### 10. Environment Variable Expansion
**Status**: Won't Fix (Intentional)
**Rationale**: Security decision to avoid unexpected expansions
**Action**: Document in configuration guide that only `~` is expanded

## Implementation Priority

1. **Immediate** (Crashes/Security):
   - Fix _extract_plugin_info AttributeError
   - Add path traversal protection
   - Fix memory leak in request_timestamps

2. **High** (Data Integrity):
   - Prevent log injection
   - Add resource cleanup
   - Fix race conditions

3. **Medium** (Reliability):
   - Handle same-file coordination
   - Improve early event handling
   - Add duration consistency

## Testing Requirements

### Unit Tests Required
1. **_extract_plugin_info with None metadata** - Verify no AttributeError
2. **TTL cleanup mechanism** - Test orphan removal after 5 minutes
3. **Path validation** - Test all special file types rejected
4. **Control character sanitization** - Test all escape types removed
5. **Handler accumulation** - Verify FD count stays constant
6. **Duration with None metadata** - Test metadata creation
7. **Race condition prevention** - Test double-check locking
8. **Handler registry** - Test sharing and reference counting

### Integration Tests Required
1. **Concurrent access** - 100+ simultaneous requests
2. **Memory boundedness** - 10000 requests don't leak memory
3. **Multi-plugin same file** - 10 plugins writing together
4. **Cleanup on reload** - Verify resources freed
5. **Early event buffering** - Test no event loss

### Security Tests Required
1. **Path traversal attempts** - ../../../etc/passwd
2. **Symlink attacks** - Links to /etc/shadow
3. **FIFO blocking** - mkfifo attempts
4. **Log injection** - CRLF, ANSI, control chars
5. **Message truncation** - 100MB message handling

### Performance Tests Required
1. **TTL cleanup overhead** - Measure impact on throughput
2. **Lock contention** - Measure with high concurrency
3. **Sanitization overhead** - Benchmark with various payloads

### Test Cleanup Best Practices
All tests MUST clean up generated files to avoid interference:
- Use `tempfile.TemporaryDirectory()` for all test log files
- Call `plugin.cleanup()` in finally blocks
- Never write test logs to project directory
- Use unique filenames per test to avoid conflicts
- Example pattern:
```python
with tempfile.TemporaryDirectory() as tmpdir:
    log_file = Path(tmpdir) / "test.log"
    try:
        plugin = BaseAuditingPlugin({"output_file": str(log_file)})
        # ... test code ...
    finally:
        plugin.cleanup()
```

## Out of Scope Items

### Explicitly Not Implementing
1. **Environment variable expansion** - Security risk, only `~` expansion supported
2. **Log compression/archival** - Delegated to external tools (logrotate)
3. **Per-format sanitization** - Each format plugin handles own escaping
4. **Async logging interface** - Logging remains synchronous (Python limitation)
5. **Cross-platform file locking** - Using handler registry instead

### Rationale for Exclusions
- **Env vars**: Prevents injection attacks via $PATH manipulation
- **Compression**: Keeps plugin simple, use OS tools
- **Format sanitization**: Avoids double-escaping, format plugins know best
- **Async logging**: Python's logging module is inherently synchronous
- **File locking**: Platform-specific complexity, registry simpler

## Configuration Schema

### New Configuration Keys
```yaml
auditing_plugins:
  - type: json_lines  # or any format plugin
    config:
      output_file: "/var/log/watchgate.log"
      max_file_size_mb: 10  # For rotation
      backup_count: 5  # Number of rotated files
      critical: false  # Whether failures halt processing
      
      # New configuration options:
      max_message_length: 10000  # Truncate messages (default: 10000)
      event_buffer_size: 100  # Early event buffer size (default: 100)
      base_directory: "/var/log"  # Optional: constrain output paths
```

## Implementation Notes

### Critical Implementation Details
1. **Use threading.Lock not asyncio.Lock** - Logging is synchronous
2. **Don't remove from logging.Manager** - Affects other references
3. **Double-check locking pattern** - Prevents race in setup
4. **TTL cleanup triggers** - On each request store, not timer-based
5. **Handler registry is global** - Module-level, not class-level
6. **Lock ordering** - Always acquire in same order to prevent deadlock:
   ```python
   # LOCK ORDER POLICY: Always acquire in this order to prevent deadlock
   # 1. _registry_lock (global handler registry)
   # 2. _timestamps_lock (request timestamp tracking) 
   # 3. _setup_lock (logging setup)
   # NEVER acquire a lower-numbered lock while holding a higher-numbered one
   ```
7. **Sanitization integration** - Must call `_sanitize_for_logging()` in `_safe_log()`
8. **Decision immutability** - Test that PolicyDecision identity not relied upon
9. **Path validation timing** - Validate during setup, not on each log

### Backward Compatibility
- This is v0.1.0 - NO backward compatibility required
- Can make breaking changes to fix security issues
- Focus on correctness over compatibility

## Definition of Done
- [ ] All fixes implemented with tests
- [ ] No test failures in full suite
- [ ] Security tests pass
- [ ] Performance benchmarks acceptable
- [ ] Documentation updated
- [ ] Code review completed