# Hot-Swap Configuration Architecture

## Overview

This document describes the hot-swap configuration management system that enables the Watchgate TUI to dynamically modify running configurations without requiring restarts. The complete decision record and rationale can be found in [ADR-016: Hot-Swap Configuration Management](../../decision-records/016-hot-swap-configuration-management.md).

**Core Principle**: Edit-in-place configuration management where users modify the actual config files that Watchgate is using, triggering immediate hot-reload through file watching.

## System Architecture

### Component Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Watchgate     │    │  File System    │    │ Watchgate TUI   │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ~/.watchgate/   │    │ ┌─────────────┐ │
│ │WatchgateState│◄┼────┤   state/        │    │ │Instance     │ │
│ │             │ │    │   instance_*.json│◄───┤ │Discovery    │ │
│ └─────────────┘ │    │                 │    │ └─────────────┘ │
│                 │    │ /path/to/       │    │                 │
│ ┌─────────────┐ │    │   config.yaml   │    │ ┌─────────────┐ │
│ │ConfigWatcher│◄┼────┤                 │◄───┤ │Config       │ │
│ │             │ │    │                 │    │ │Editor       │ │
│ └─────────────┘ │    │                 │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. WatchgateState - Instance Tracking

**Purpose**: Tracks running Watchgate instances so TUI can discover and interact with them.

**Key Features**:
- Records PID, config file path, and start time
- Writes state to `~/.watchgate/state/instance_{pid}.json`
- Automatic cleanup on graceful shutdown
- Signal handlers for SIGTERM/SIGINT
- Startup cleanup of stale state files

**Example State File**:
```json
{
  "pid": 12345,
  "config_path": "/Users/alice/projects/myapp/watchgate.yaml",
  "start_time": "2025-01-15T14:30:25.123456"
}
```

### 2. ConfigWatcher - File Monitoring

**Purpose**: Monitors the specific configuration file that Watchgate was started with for changes.

**Key Features**:
- Uses `watchdog` library for efficient native file watching
- Watches only the active config file (not arbitrary staging directories)
- Debounced change detection to handle multiple rapid writes
- Atomic configuration reloading with validation
- Graceful error handling - keeps current config if new config is invalid

**Trigger Conditions**:
- File modification detected
- Validation passes
- Configuration differs from current

### 3. Instance Discovery - TUI Integration

**Purpose**: Allows TUI to find running Watchgate instances and their configurations.

**Key Features**:
- Scans `~/.watchgate/state/` for instance files
- Process liveness checking with `psutil`
- Automatic cleanup of stale state files
- Verification that PID belongs to actual Watchgate process (handles PID reuse)

**Discovery Process**:
1. List all `instance_*.json` files
2. Check if PID is alive and is Watchgate process
3. Remove stale files for dead/non-Watchgate processes
4. Return valid running instances

### 4. Stale State Cleanup - Reliability

**Purpose**: Handle state files left behind by crashed Watchgate instances.

**Multi-Layered Strategy**:

**Primary - Process Liveness Check**:
```python
import psutil

def is_process_alive(pid: int) -> bool:
    """Check if process is still running and is actually Watchgate."""
    try:
        process = psutil.Process(pid)
        cmdline = process.cmdline()
        return any('watchgate' in arg.lower() for arg in cmdline)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False
```

**Secondary - Startup Cleanup**: Each Watchgate instance cleans up stale files on startup

**Tertiary - Age-Based Cleanup**: TUI removes files older than 24 hours after verifying process death

**Prevention - Graceful Shutdown**: Signal handlers and `atexit` callbacks

## Integration Points

### Server Hot-Swapping

**User Action**: Toggle servers on/off in TUI
**Implementation**:
1. TUI reads current config from active Watchgate instance
2. User modifies server list in TUI interface
3. TUI writes updated config back to the same file
4. ConfigWatcher detects change and triggers reload
5. Watchgate hot-swaps server connections without restart

**Example Flow**:
```yaml
# Before: User has GitHub + JIRA + Filesystem
servers:
  github: {...}
  jira: {...}      # User disables this
  filesystem: {...}

# After: TUI writes updated config
servers:
  github: {...}
  filesystem: {...}
```

### Plugin Toggling

**User Action**: Enable/disable security plugins
**Implementation**:
1. User toggles PII filter, secrets detection, etc. in TUI
2. TUI updates plugin configuration section
3. File write triggers hot-reload
4. Plugin manager unloads/loads plugins dynamically

### Configuration Management

**User Action**: Create, edit, and manage configuration files
**Implementation**:
1. User creates or edits configuration through TUI
2. TUI writes changes to active config file
3. Hot-reload applies changes immediately

### Real-Time Configuration Editing

**User Action**: Direct configuration editing in TUI forms
**Implementation**:
1. TUI presents current config as forms/toggles
2. User makes changes through UI
3. Every change triggers immediate write to config file
4. User sees effects in real-time without restart

## Directory Structure

```
~/.watchgate/
├── state/
│   ├── instance_12345.json    # Running instance tracking
│   └── instance_23456.json
└── cache/
    └── server_capabilities.json
```

## Dependencies

### Runtime Dependencies

**watchdog** (file watching):
- **Version**: >=3.0.0
- **Dependencies**: None
- **Purpose**: Cross-platform file system event monitoring

**psutil** (process management):
- **Version**: >=5.8.0  
- **Dependencies**: None
- **Purpose**: Cross-platform process detection and verification

Both libraries are zero-dependency and widely adopted (watchdog: major projects, psutil: 1.2B+ downloads).

## Implementation Roadmap

### Phase 1: Foundation ✅ (Planned)
- [ ] Add `watchdog` and `psutil` dependencies  
- [ ] Implement `WatchgateState` class with cleanup handlers
- [ ] Add `ConfigWatcher` with file monitoring
- [ ] Implement stale state file cleanup mechanisms
- [ ] Update main startup to write state files

### Phase 2: TUI Integration 🔄 (In Progress)
- [ ] Implement instance discovery in TUI
- [ ] Add configuration editing interface  
- [ ] Server management (add/remove/toggle)
- [ ] Plugin management (enable/disable/configure)
- [ ] Save options with hot-reload indication

### Phase 3: Polish 🎯 (Future)
- [ ] Comprehensive error handling and recovery
- [ ] User documentation and tutorials
- [ ] Cross-platform testing
- [ ] Performance optimization

## Cross-Platform Considerations

### File Paths
- Uses `pathlib.Path` for automatic platform-appropriate path handling
- `Path.home() / ".watchgate"` works identically on Windows/macOS/Linux
- State files use consistent JSON format across platforms

### Process Management
- `psutil` abstracts platform differences in process detection
- Works with Windows Task Manager, Unix ps, macOS Activity Monitor equivalently
- Handles PID reuse and zombie processes correctly

### File Watching
- `watchdog` uses native OS APIs (Windows: ReadDirectoryChangesW, macOS: FSEvents, Linux: inotify)
- Consistent behavior across platforms
- Efficient, no polling required

## Error Handling Strategies

### Configuration Validation Failures
- Invalid configurations are rejected
- Current configuration remains active
- Error details logged and shown to user
- TUI indicates validation failure clearly

### File System Issues
- Permission errors handled gracefully
- Temporary file unavailability managed with retries
- Atomic file operations where possible

### Process Management Errors
- Handle AccessDenied exceptions for protected processes
- Manage race conditions with PID reuse
- Graceful degradation if psutil unavailable (though not recommended)

### Network/Connection Failures
- Server connection failures during hot-swap handled gracefully
- Partial success scenarios (some servers connect, others fail)
- Clear status indication in TUI

## Security Considerations

### State File Security
- State files contain no sensitive information (only PID, path, timestamp)
- Located in user home directory with appropriate permissions
- No credentials or secrets stored

### Configuration File Access
- TUI only modifies configs user already has write access to
- No privilege escalation or system-wide configuration changes
- Users maintain full control over their configuration files

## Performance Characteristics

### File Watching Overhead
- **Idle**: Zero CPU usage (native OS events)
- **Change Detection**: Sub-100ms response time
- **Memory**: Minimal overhead (~1MB for watchdog)

### State File Operations
- **Instance Discovery**: O(n) where n = number of state files
- **Cleanup**: Batched operations, infrequent
- **Storage**: ~100 bytes per running instance

### Configuration Reload
- **Validation**: Fast YAML parsing and Pydantic validation
- **Plugin Reload**: Depends on plugin complexity
- **Server Reconnection**: Network-bound, typically 1-5 seconds

## Testing Strategy

### Unit Testing
- Mock file system operations for reliable tests
- Simulate process scenarios (running, crashed, PID reuse)
- Test configuration validation edge cases

### Integration Testing  
- Real file watching with temporary directories
- Multi-instance scenarios
- Cross-platform compatibility verification

### End-to-End Testing
- Complete TUI workflows
- Real Watchgate instance interaction
- Profile switching and server management

## See Also

- [ADR-016: Hot-Swap Configuration Management](../../decision-records/016-hot-swap-configuration-management.md) - Complete decision record and rationale
- [initial-thoughts.md](./initial-thoughts.md) - High-level TUI design concepts and user experience
- [plugin-interface-spec.md](./plugin-interface-spec.md) - Plugin configuration UI specification
- [server-compatibility-design.md](./server-compatibility-design.md) - Server compatibility system for plugin filtering

## Status

**Current Phase**: Design Complete ✅  
**Next Milestone**: Begin Phase 1 implementation
**Last Updated**: January 2025

This architecture enables seamless hot-swapping of Watchgate configurations through the TUI while maintaining reliability, cross-platform compatibility, and clear user mental models of configuration management.