# ADR-016: Hot-Swap Configuration Management for TUI

## Status
Accepted

## Context

Watchgate's TUI needs the ability to hot-swap various components without requiring a full restart:

1. **MCP Servers**: Add/remove servers (GitHub, JIRA, Slack, etc.) to optimize context usage and reduce LLM confusion
2. **Security Plugins**: Enable/disable plugins like PII filtering, secrets detection during active sessions  
3. **Tool Allowlists**: Dynamically control which tools are available from each server
4. **Configuration Profiles**: Quick switching between predefined setups (minimal, development, production)

### Key Challenges

1. **Process Ownership**: Watchgate runs as part of the MCP client's process (stdio transport), so we cannot directly control it
2. **Configuration Consistency**: Need to avoid confusion about which configuration is "active" vs stored
3. **Restart Behavior**: Users expect consistent behavior when Watchgate restarts
4. **Cross-Platform Support**: Solution must work identically on Windows, macOS, and Linux
5. **State Discovery**: TUI needs to know if/where Watchgate is running and what config it's using

## Decision

We will implement an **Edit-in-Place Configuration Management** system with the following architecture:

### Core Approach: Edit-in-Place with State Tracking

1. **Watchgate tracks its active configuration file** - The specific file path used at startup
2. **File watching for hot-reload** - Uses `watchdog` library to monitor the active config file
3. **State file discovery** - Running instances write state files that TUI can discover  
4. **Explicit user control** - TUI clearly shows active vs inactive configs and lets users choose

### Architecture Components

```python
# State tracking for running instances
class WatchgateState:
    - Records: PID, config file path, start time
    - Writes: ~/.watchgate/state/instance_{pid}.json
    - Cleanup: Removes state file on shutdown

# File watching for hot-reload  
class ConfigWatcher:
    - Watches: The specific config file Watchgate was started with
    - Triggers: Hot-reload when that file changes
    - Scope: Only watches the active config, not arbitrary files

# TUI discovery and editing
class WatchgateTUI:
    - Discovers: Running instances via state files
    - Edits: Specific config files with clear save options
    - Shows: Which configs are active vs inactive
```

### User Workflow

1. **TUI Launch**: Shows detected running Watchgate instances and their config files
2. **Edit Choice**: User chooses to edit active config, create new config, or open different config
3. **Save Options**: When saving, user explicitly chooses:
   - Overwrite current file (triggers hot-reload if active)
   - Save as new file (no hot-reload)
   - Save as profile template

### Hot-Reload Mechanism

- **Single File Watching**: Watchgate only watches the specific config file it was started with
- **Atomic Updates**: Configuration changes are applied atomically to avoid partial states
- **Graceful Failures**: Invalid configs are rejected, current config remains active
- **Audit Trail**: All configuration changes are logged

## Options Considered

### 1. MCP Tools Approach ❌
**Concept**: Expose configuration management as MCP tools that TUI could invoke.

**Problems**:
- MCP tools are meant for LLMs, not direct user invocation
- Would require LLM to be in the loop for configuration changes
- Indirect and awkward user experience

### 2. Marker Files with Staging Directories ❌
**Concept**: TUI writes to staging directory, Watchgate polls for marker files.

**Problems**:
- Creates configuration file confusion (started with one config, changes in another location)
- Unclear restart behavior - which config should be used?  
- Poor user mental model of where their configuration actually lives

### 3. Signal-Based Reload ❌
**Concept**: Use Unix signals (SIGUSR1) to trigger configuration reload.

**Problems**:
- Not available on Windows
- Requires finding process PID
- Platform-specific code paths

### 4. Named Pipes/FIFO ❌
**Concept**: Secondary communication channel via named pipes.

**Problems**:
- Different APIs on Windows vs Unix
- Complex implementation for simple use case
- Would require platform-specific code

### 5. Environment Variable Switching ❌
**Concept**: Switch configs by changing environment variables.

**Problems**:
- Cannot modify parent process environment from child
- Would require process restart anyway

### 6. Configuration Profiles with Fast Switching ✅ (Complementary)
**Concept**: Pre-defined configuration sets with quick switching.

**Status**: Will implement as complementary feature to main approach
- Provides quick switching between common setups
- Stored as templates that populate the main config
- Works within the edit-in-place framework

## Cross-Platform Implementation

### Directory Structure
```
~/.watchgate/
├── state/
│   ├── instance_12345.json    # Running instance state
│   └── instance_23456.json
├── profiles/
│   ├── minimal.yaml           # Profile templates
│   ├── development.yaml
│   └── production.yaml
└── cache/
    └── server_capabilities.json
```

### Platform Compatibility
- **Path Handling**: Uses Python `pathlib.Path` for automatic platform-appropriate paths
- **Directory Location**: Uses `~/.watchgate` on all platforms (common cross-platform pattern)
- **File Watching**: `watchdog` library abstracts native OS file watching APIs
- **Process Detection**: Cross-platform PID checking for stale state cleanup

## Consequences

### Benefits

1. **Clear Configuration Management**: 
   - No confusion about which config is active
   - Predictable restart behavior (uses same config file)
   - Explicit user control over when hot-reload occurs

2. **Cross-Platform Consistency**:
   - Identical behavior on Windows, macOS, Linux
   - No platform-specific code paths required
   - Leverages proven libraries (`watchdog`, `pathlib`)

3. **Process Independence**:
   - Works with stdio transport where we don't control the process
   - State discovery allows TUI to find running instances
   - Graceful handling of multiple concurrent instances

4. **User Experience**:
   - TUI clearly shows active vs inactive configurations
   - Immediate hot-reload feedback when editing active configs
   - Safe fallback behavior when configuration changes fail

5. **Performance**:
   - Zero overhead when no changes (native file watching)
   - Minimal dependency footprint (`watchdog` has no dependencies)
   - Efficient atomic configuration updates

### Trade-offs

1. **State File Management**:
   - Requires cleanup of stale state files from crashes
   - Additional directory structure in user home
   - Mitigation: Multi-layered cleanup strategy (see Stale State File Handling)

2. **File Watching Dependency**:
   - Adds `watchdog` dependency to core Watchgate
   - Mitigation: Well-maintained, zero-dependency library used by major projects

3. **Process Detection Dependency**:
   - Requires `psutil` for robust process liveness checking
   - Mitigation: Zero-dependency library, 1.2B+ downloads, widely trusted

4. **Configuration Validation Overhead**:
   - Must validate configurations on every change
   - Mitigation: Fast validation, only applies to active config changes

5. **Multi-Instance Complexity**:
   - Users could run multiple Watchgate instances with different configs
   - Mitigation: TUI clearly shows all instances and their configs

## Implementation Plan

### Phase 1: Core Infrastructure
1. Add `watchdog` and `psutil` dependencies to project
2. Implement `WatchgateState` for instance tracking with cleanup handlers
3. Add `ConfigWatcher` for file monitoring
4. Implement stale state file cleanup mechanisms
5. Update main startup to write state files and handle graceful shutdown

### Phase 2: TUI Integration  
1. Implement instance discovery in TUI
2. Add configuration editing interface
3. Implement save options with clear hot-reload indication
4. Add validation and error handling

### Phase 3: Profile System
1. Add profile template support
2. Implement quick profile switching
3. Add profile creation from current config
4. Integrate with main editing workflow

### Phase 4: Polish
1. Comprehensive error handling and recovery
2. User documentation and examples
3. Cross-platform testing
4. Performance optimization

## Stale State File Handling

A critical implementation detail is handling stale state files left behind when Watchgate crashes or is forcibly terminated.

### The Problem

When Watchgate shuts down gracefully, it removes its state file (`~/.watchgate/state/instance_{pid}.json`). However, crashes, SIGKILL, system shutdown, or other ungraceful termination can leave stale state files that make the TUI think Watchgate instances are still running.

### Multi-Layered Cleanup Strategy

**1. Process Liveness Check (Primary)**
```python
import psutil  # Zero-dependency library

def is_process_alive(pid: int) -> bool:
    """Check if process is still running and is actually Watchgate."""
    try:
        process = psutil.Process(pid)
        # Verify it's actually Watchgate, not just any process with reused PID
        cmdline = process.cmdline()
        return any('watchgate' in arg.lower() for arg in cmdline)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False
```

**2. Startup Cleanup (Secondary)**
- Each Watchgate instance cleans up stale state files on startup
- Checks process liveness for all existing state files
- Removes files for non-existent or non-Watchgate processes

**3. Age-Based Cleanup (Tertiary)**
- TUI removes state files older than 24 hours after verifying process is dead
- Handles edge cases where PID reuse might give false positives

**4. Graceful Shutdown (Prevention)**
- Signal handlers for SIGTERM/SIGINT to ensure cleanup
- `atexit` handlers for normal Python exit

### Dependencies Required

**psutil**: Required for robust cross-platform process detection
- **Runtime dependencies**: None (only requires Python 3.6+)
- **Platform support**: Windows, macOS, Linux, BSD, Solaris, AIX
- **Adoption**: 1.2B+ downloads, used by Docker, pytest, many major projects
- **Alternative approaches** (os.kill, /proc parsing, tasklist) are platform-specific and fragile

**Updated dependency list**:
```toml
dependencies = [
    "watchdog>=3.0.0",  # File watching (0 dependencies)
    "psutil>=5.8.0",    # Process management (0 dependencies) 
    # ... existing dependencies
]
```

This multi-layered approach ensures stale state files are cleaned up reliably across crash scenarios, system reboots, and other failure modes while maintaining zero dependency bloat.

---

This approach provides clean separation of concerns while maintaining the simplicity and reliability that Watchgate users expect.