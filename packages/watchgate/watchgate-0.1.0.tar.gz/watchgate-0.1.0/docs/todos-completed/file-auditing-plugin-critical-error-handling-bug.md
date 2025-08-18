# File Auditing Plugin Critical Error Handling Bug

## Issue Summary

~~The file auditing plugin is configured as critical by default (`critical: true`) but is not properly failing Watchgate startup when it encounters permission errors that prevent it from writing to the specified audit log file.~~

**UPDATE - ISSUE RESOLVED**: Investigation revealed that critical error handling for file permission errors **was working correctly** at the config validation level. The actual bug was that **non-critical plugins** were incorrectly failing startup. The config loader and plugin manager did not respect the `critical: false` flag during path validation, causing all plugins with path issues to fail startup regardless of their critical setting.

## Problem Description

During validation testing with the configuration:

```yaml
proxy:
  upstream:
    command: ["npx", "@modelcontextprotocol/server-filesystem", "/tmp"]
plugins:
  auditing:
    - policy: "file_auditing"
      enabled: true
      config:
        file: "/root/audit.log"  # Permission denied for most users
```

**Expected Behavior:**
- Watchgate should fail to start with a clear error message about being unable to write to the critical audit log location
- The error should include information about the permission issue and suggest using a writable path

**Actual Behavior:**
- Watchgate starts successfully and functions normally
- No error messages about the permission issue
- The file `/root/audit.log` is not created (as expected due to permissions)
- All other functionality works normally

## Root Cause Analysis Needed

The file auditing plugin code shows proper critical error handling:

1. **Default critical setting**: `self.critical = config.get("critical", True)` (line 47)
2. **Initialization error handling**: Lines 73-78, 109-114 raise exceptions for critical plugins
3. **Runtime error handling**: Lines 151-155, etc. raise exceptions for critical plugins

**Possible causes:**
1. **Lazy permission checking**: The plugin may only check file permissions when first attempting to write, not during initialization
2. **Error handling bypass**: There may be a code path that's not properly checking the critical flag
3. **Silent fallback**: The plugin might be falling back to an alternative behavior without proper error propagation

## Investigation Tasks

1. **Trace plugin initialization**: Verify that the file auditing plugin is actually being initialized with the problematic config
2. **Check permission validation timing**: Determine when file permissions are checked (initialization vs. first write)
3. **Review error propagation**: Ensure critical plugin errors are properly propagated to cause startup failure
4. **Test with various permission scenarios**: Test with different types of permission errors (directory doesn't exist, file exists but not writable, etc.)

## Test Case

The issue was discovered during Part 5 error scenario validation. The test case is:

```yaml
# temp-permission-error.yaml
proxy:
  upstream:
    command: ["npx", "@modelcontextprotocol/server-filesystem", "/tmp"]
plugins:
  auditing:
    - policy: "file_auditing"
      enabled: true
      config:
        file: "/root/audit.log"
```

**To reproduce:**
1. Configure Watchgate with the above config
2. Start Watchgate
3. Observe that it starts successfully instead of failing with permission error

## Acceptance Criteria

- [x] Critical file auditing plugin failures cause Watchgate startup to fail
- [x] Clear error messages explain permission issues and suggest fixes
- [x] Non-critical plugins (`critical: false`) continue to work with degraded functionality
- [x] Error messages distinguish between permission errors, missing directories, and other file system issues

## Resolution Summary

**Root Cause**: The config loader (`watchgate/config/loader.py`) and plugin manager (`watchgate/plugins/manager.py`) were not checking the `critical` flag during path validation, causing all path validation errors to be treated as fatal regardless of the plugin's critical setting.

**Files Fixed**:
1. **`watchgate/config/loader.py`**: Modified `_validate_single_plugin_paths()` to respect the `critical` flag
2. **`watchgate/plugins/manager.py`**: Updated path validation in both security and auditing plugin loading to check `critical` flag
3. **`watchgate/plugins/auditing/file_auditing.py`**: Fixed constructor initialization order bug where logging attributes were being reset after successful setup

**Behavior After Fix**:
- **Critical plugins** (`critical: true`) with path errors → **Fail startup** with clear error messages
- **Non-critical plugins** (`critical: false`) with path errors → **Allow startup** with warning logs
- **Error messages** provide specific guidance about path resolution and configuration options

**Testing**: All file auditing plugin tests pass. Integration testing confirms both critical and non-critical scenarios work as expected.

## Priority

**High** - This affects the reliability of audit logging, which is a core security feature. Users expecting audit logs may not realize they're not being captured.

## Related Files

- `/Users/dbright/mcp/watchgate/watchgate/plugins/auditing/file_auditing.py`
- Plugin manager error handling code
- Configuration validation code

## Validation Test Impact

This bug was discovered during validation testing and means the "Test Permission Error" scenario in the validation guide needs to be updated once fixed to show the expected error behavior.