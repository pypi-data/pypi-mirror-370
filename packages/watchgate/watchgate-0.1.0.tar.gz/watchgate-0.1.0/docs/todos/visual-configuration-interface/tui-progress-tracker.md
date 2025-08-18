# TUI Progress Tracker - Session Starter


## 🎯 The Vision

We're building a Terminal User Interface (TUI) for Watchgate that lets users visually configure security policies, manage MCP servers, and see real-time status. Unlike other Watchgate features where we design detailed requirements first, **we're doing the TUI iteratively and intuitively** - building, testing, refining based on feel.

### Core User Experience Goals
- **Visual configuration editing** instead of hand-editing YAML
- **Hot-reload changes** without restarting proxy instances  
- **Server management** - add/remove/enable/disable MCP servers
- **Plugin configuration** through native Textual widgets (no abstraction layers)
- **Real-time status** - see what's connected, what's blocked, audit logs

### Layout Philosophy: Horizontal Split
```
╭─ Watchgate Security Configuration ─────────────────────╮
│ GLOBAL SECURITY & AUDITING (always visible)          │
├────────────────────────────────────────────────────────┤
│ ┌─ Servers ─┐ ┌─ Server Plugins ─┐ ┌─ Config Details ─┐│
│ │filesystem │ │• Tool Allowlist  │ │Selected plugin   ││
│ │github     │ │• Path Security   │ │configuration     ││
│ │sqlite     │ │• Rate Limiting   │ │forms/widgets     ││
│ └───────────┘ └──────────────────┘ └──────────────────┘│
╰────────────────────────────────────────────────────────╯
```

## 🚀 What's Working Now

### ✅ Basic TUI Framework
- **Entry Point**: `watchgate` (no args) launches TUI, `watchgate proxy --config` runs as MCP server
- **Main App**: Basic Textual app with header/footer, placeholder content
- **Navigation**: Keyboard shortcuts (q/Ctrl+C to quit, Ctrl+O for config)

### ✅ Configuration File Management
- **Automatic Config Picker**: When `watchgate` runs without config, immediately opens config selector (no welcome screen)
- **Smart Directory Detection**: Automatically starts in `configs/` directory when it exists, falls back to current directory
- **Config Picker Modal**: Recent configs discovery, quick options (browse/create/default) - available via Ctrl+O
- **Config Selector Screen**: Shows YAML files with modification times and server lists from configs directory
- **Scoped File Discovery**: Only searches current directory + immediate subdirectories, excludes hidden dirs (like `.venv`)
- **Enhanced Directory Browser**: Hybrid text input + visual tree navigation with autocomplete
- **Config Discovery**: Automatically finds Watchgate configs in common locations
- **Validation**: Uses existing ConfigLoader to verify files are valid Watchgate configs

### ✅ File Intelligence
- **Server Extraction**: Reads YAML files and shows which MCP servers they configure
- **Enhanced Error Messages**: Specific error types (Invalid YAML, Missing proxy section, Path validation error, etc.)
- **Timestamp Display**: Human-friendly relative times (2h ago, yesterday, etc.)
- **Path Resolution**: Handles relative paths, current directory indicators
- **Error Handling**: Graceful handling of invalid configs, permission errors, validation failures

### ✅ Directory Navigation & Autocomplete ⭐ **COMPLETE & POLISHED**
- **Intelligent Path Input**: Custom PathInput widget with real-time directory autocomplete
- **Tab Completion**: Tab key accepts autocomplete suggestions (like shell terminals)
- **Context-Aware Tab**: When no autocomplete available, Tab moves focus to directory tree
- **True Bidirectional Sync**: Text input ↔ Tree selection sync in real-time (typing paths navigates tree, clicking tree updates input)
- **Complete Focus Cycling**: Perfect circular navigation flow - Path Input ↕ Directory Tree ↕ Select Button ↔ Cancel Button ↕ Path Input
- **Silent Navigation**: No annoying error beeps during arrow key navigation between UI elements
- **Path Validation**: Real-time visual feedback (green/red borders) for valid/invalid paths
- **Common Paths**: Built-in suggestions for configs/, ~/.config, ~/Documents, etc.
- **No Text Selection**: Cursor positioned at end of path (not selected) for safe editing
- **Cancel Options**: Both Cancel button and Escape key properly dismiss modal
- **Cross-Platform**: Works identically on Windows, macOS, and Linux

### ✅ Configuration Screen Navigation ⭐ **COMPLETE & POLISHED**
- **Intuitive Arrow Key Navigation**: Full directional navigation between all interface elements
- **Complete Navigation Cycle**: Directory widget ↕ File table ↕ Select button → Refresh button → Quit button ↺ Directory widget
- **Contextual Focus Behavior**: Table navigation respects top/bottom boundaries (up at top goes to directory, down at bottom goes to buttons)
- **Bidirectional Navigation**: All arrow keys work intuitively (up/down for vertical movement, left/right for horizontal/alternative movement)
- **Preserves Existing Functionality**: Click handlers, Enter key actions, and keyboard shortcuts remain unchanged
- **Custom Widget Classes**: NavigableStatic, NavigableDataTable, NavigableSelectButton, NavigableRefreshButton, NavigableQuitButton
- **Silent Navigation**: No error sounds during navigation, smooth transitions between focused elements


### ✅ Integration Points
- **Human-First Invocation**: `watchgate` (default) launches TUI, `watchgate proxy --config` for MCP clients (ADR-017)
- **Graceful Fallback**: Clear error if Textual not installed, suggests proxy mode
- **Config Path Handling**: Supports --config flag to start with specific file
- **Backward Compatibility**: Detects MCP client usage and shows deprecation warning
- **Example Configs**: All dummy configs in `configs/dummy/` are valid and load properly with correct server lists

## 🔧 Architecture Ready But Not Implemented

### Hot-Swap Configuration System
**Status**: Fully designed in ADR-016, ready for implementation

**Core Principle**: Edit-in-place configuration management where users modify the actual config files that Watchgate is using, triggering immediate hot-reload through file watching.

**Components Needed**:
- **WatchgateState**: Track running instances in `~/.watchgate/state/instance_*.json` with PID, config path, start time
- **ConfigWatcher**: File watching with `watchdog` library for hot-reload of active config file only
- **Instance Discovery**: Let TUI find and configure running proxy instances via state file scanning
- **Multi-layered Stale Cleanup**: Process liveness check (primary), startup cleanup (secondary), age-based cleanup (tertiary), graceful shutdown prevention

**Dependencies**: `watchdog>=3.0.0`, `psutil>=5.8.0` (both zero-dependency, widely adopted)

**Directory Structure**:
```
~/.watchgate/
├── state/           # Running instance tracking
│   ├── instance_12345.json
│   └── instance_23456.json
└── cache/           # Server capabilities cache
    └── server_capabilities.json
```

### Plugin UI System
**Status**: Designed in `plugin-ui-implementation.md`, not yet coded

**Plugin Contract**: Plugins provide their own Textual widgets directly
```python
@classmethod
def get_config_widget(cls, current_config: dict, context: dict = None):
    """Return a Textual widget for configuration."""
    if not HAS_TEXTUAL:
        return None
    return cls.MyConfigWidget(current_config, context)
```

**Philosophy**: No abstraction layers, no schema generation - maximum freedom for plugin authors

### Server Compatibility System  
**Status**: Designed in `server-compatibility-design.md`, not yet coded

**Plugin Declarations**:
```python
# Universal plugins (no declaration needed)
class PiiFilterPlugin: pass

# Server-specific plugins
class FilesystemServerSecurity:
    COMPATIBLE_SERVERS = ["secure-filesystem-server"]

# Dynamic configuration plugins
class ToolAllowlistPlugin:
    REQUIRES_DISCOVERY = ["tools"]
```

## 🎯 What's Next

**Current Phase**: Directory Navigation and Autocomplete Complete, Ready for Hot-Swap Foundation

### Phase 1: Hot-Swap Foundation (ADR-016 Implementation)
- [ ] Add `watchdog` and `psutil` dependencies to pyproject.toml
- [ ] Implement `WatchgateState` class with signal handlers and atexit cleanup
- [ ] Add `ConfigWatcher` with atomic configuration reloading and validation
- [ ] Implement multi-layered stale state cleanup (process liveness, startup, age-based)
- [ ] Update main startup to write state files and handle graceful shutdown
- [ ] Test instance discovery, hot-reload, and crash recovery scenarios

### Phase 2: Real Configuration Interface
- [ ] Replace placeholder content with actual config editing
- [ ] Implement server list management (add/remove/enable/disable)
- [ ] Add plugin discovery and compatibility filtering
- [ ] Build the horizontal split layout from mockups
- [ ] Enable saving changes back to config files

### Phase 3: Plugin Integration
- [ ] Add plugin widget mounting system
- [ ] Update existing plugins with `get_config_widget` methods
- [ ] Implement server capability discovery for dynamic plugins
- [ ] Build global vs server-specific plugin categorization

### Phase 4: Polish & Real-Time Features
- [ ] Live status display (connected servers, recent events)
- [ ] Audit log viewing within TUI
- [ ] Better error handling and user feedback

## 🧠 Development Philosophy

### Iterative & Intuitive
- **Build first, perfect later** - Get basic functionality working, then refine
- **User feel over technical correctness** - If it feels clunky, it is clunky
- **Real usage drives features** - Don't build what we think users want, build what feels natural

### No Backward Compatibility Constraints
- **This is v0.1.0** - We can change anything that doesn't work well
- **Tests can be updated** to match new behavior if needed
- **Configuration formats can evolve** based on TUI needs
- **Focus on clean, maintainable code** over legacy compatibility

### Direct Manipulation
- **Edit live config files** that Watchgate is actually using
- **Immediate feedback** through hot-reload and file watching
- **No staging areas** or complex save/apply workflows
- **What you see is what Watchgate uses**

## 🚨 Critical Reminders

### Testing Requirements
- **ALL TESTS MUST PASS** before marking any task complete
- **Run `pytest tests/` before every commit** - no exceptions
- **Fix failures immediately** rather than ignoring them

### Error Handling Philosophy
- **User-friendly errors** in TUI mode with clear guidance
- **Technical details in logs** for debugging
- **Graceful degradation** when features unavailable
- **Clear feedback** for all user actions

### Security Mindset
- **Secure by default** - choose safer options when alternatives exist
- **Explicit over implicit** - make behaviors observable
- **Document security implications** of convenience features
- **Consider how choices appear to security-conscious users**

## 📂 Current File Structure

```
watchgate/tui/
├── __init__.py                      # Entry point with run_tui()
├── app.py                          # Main WatchgateConfigApp with placeholder content
├── path_suggester.py               # 🆕 Path autocomplete system with Tab key support
└── screens/
    ├── __init__.py
    ├── config_picker_modal.py      # Recent configs + quick actions
    ├── config_selector.py          # Directory-based file browser
    ├── directory_dialog.py         # Simple path input dialog
    └── directory_browser_modal.py  # 🆕 Enhanced directory browser with full navigation

# Key integration points:
watchgate/main.py                    # Human-first default invocation (ADR-017)
docs/decision-records/016-*          # Hot-swap architecture specification
docs/decision-records/017-*          # TUI invocation pattern specification
```

## 🔄 Session Workflow

1. **Start here** - Read this document to understand current state
2. **Run the TUI** - `watchgate` to see what's working
3. **Test frequently** - Run actual TUI to feel the user experience
4. **Update this document** when completing major milestones

---

**Key References**:
- **ADR-016**: Hot-Swap Configuration Management - Complete architectural design with edit-in-place approach
- **ADR-017**: TUI Invocation Pattern - Human-first default with explicit proxy subcommand

**Remember**: This is iterative development focused on user experience. If something feels awkward or unintuitive in the TUI, that's feedback to improve the design, not just the implementation.