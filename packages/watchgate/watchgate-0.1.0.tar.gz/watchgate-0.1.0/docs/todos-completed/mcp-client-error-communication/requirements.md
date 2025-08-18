# MCP Client Error Communication

**Status**: Research Complete ✅  
**Completed**: 2025-07-01  
**Research Phase**: v0.1.0  

## Research Overview

Currently, when Watchgate fails to start due to configuration errors or plugin failures, MCP clients (like Claude Desktop) only receive a generic "Server disconnected" message. Users get no helpful information about what went wrong or how to fix it.

This feature aims to improve the user experience by communicating startup and configuration errors from Watchgate to MCP clients in a way that the LLM can display helpful error messages to users.

## Problem Statement

### Current Behavior
1. Watchgate encounters a startup error (e.g., file auditing plugin can't create log directory)
2. Watchgate logs detailed error information to its own logs
3. Watchgate process exits
4. Claude Desktop shows: "Server disconnected"
5. User has no idea what went wrong or how to fix it

### Desired Behavior
1. Watchgate encounters a startup error
2. Watchgate communicates the error details to the MCP client before exiting
3. Claude Desktop receives the error information
4. LLM shows user a helpful error message with specific problem and solution
5. User can fix the configuration issue

## Research Questions & Findings ✅

### 1. MCP Protocol Error Communication
- **Question**: Can we send JSON-RPC error responses during the initialization handshake?
- **Finding**: ✅ **YES** - MCP protocol supports JSON-RPC error responses at any time, including initialization
- **Evidence**: Watchgate already implements JSON-RPC error handling; protocol allows errors before completion

### 2. Stderr Communication Channel
- **Question**: Does Claude Desktop capture and forward stderr output to the LLM?
- **Finding**: ❌ **UNLIKELY** - Stderr used for logging, doesn't reach end users in MCP clients
- **Evidence**: MCP uses stdout for protocol communication; stderr typically for server diagnostics

### 3. Graceful Degradation Patterns
- **Question**: Can Watchgate start in a "safe mode" that responds with error details?
- **Finding**: ✅ **YES** - Minimal server can start even when full initialization fails
- **Evidence**: StdioServer can initialize independently; can handle `initialize` requests with error responses

### 4. Client-Side Error Handling
- **Question**: How does Claude Desktop handle different types of MCP server failures?
- **Finding**: 🔍 **STANDARD PROTOCOL** - MCP clients expect JSON-RPC 2.0 compliant error responses
- **Evidence**: Protocol compliance ensures compatibility across MCP client implementations

## Implementation Approaches

### Approach 1: Initialization Error Responses
```python
async def start_with_error_handling(self):
    try:
        await self.start()
    except Exception as e:
        # Send initialization error response before exiting
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32000,
                "message": f"Watchgate startup failed: {e}",
                "data": {
                    "fix_instructions": "Check your configuration file and ensure all paths are accessible"
                }
            },
            "id": None
        }
        await self.send_error_and_exit(error_response)
```

### Approach 2: Stderr Communication
```python
def communicate_startup_error(self, error: Exception):
    # Write structured error to stderr for client to capture
    error_info = {
        "error_type": "startup_failure",
        "message": str(error),
        "suggestions": self.generate_fix_suggestions(error)
    }
    print(json.dumps(error_info), file=sys.stderr)
```

### Approach 3: Safe Mode Server
```python
class SafeModeServer:
    """Minimal server that responds to all requests with configuration errors."""
    
    async def handle_any_request(self, request):
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32000,
                "message": "Watchgate configuration error",
                "data": {
                    "details": self.startup_error_details,
                    "fix_instructions": self.generate_fix_instructions()
                }
            },
            "id": request.get("id")
        }
```

## Success Criteria

1. **Clear Error Messages**: Users receive specific, actionable error messages instead of generic connection failures
2. **Fix Guidance**: Error messages include suggestions for resolving common configuration issues
3. **No Silent Failures**: All startup failures are communicated to the user in some form
4. **Backwards Compatibility**: Changes don't break existing working configurations
5. **MCP Compliance**: Solution follows MCP protocol specifications

## Test Cases

### Test Case 1: Missing Log Directory
- **Setup**: Configure file auditing plugin with path to non-existent directory
- **Expected**: User sees "Log directory /path/to/logs does not exist. Please create it or use an existing directory."

### Test Case 2: Permission Denied
- **Setup**: Configure log file in directory without write permissions
- **Expected**: User sees "Cannot write to log file /path/to/file. Please check file permissions."

### Test Case 3: Invalid YAML Configuration
- **Setup**: Use malformed YAML configuration file
- **Expected**: User sees "Configuration file has invalid YAML syntax at line 15. Please check for missing quotes or indentation."

### Test Case 4: Missing Upstream Server
- **Setup**: Configure upstream command that doesn't exist
- **Expected**: User sees "Upstream MCP server command 'nonexistent-server' not found. Please install the server or check the command path."

## Research Conclusions

### Recommended Approach: **Initialization Error Responses** ✅
Based on research findings, Approach 1 is most viable:
- **Protocol Compliant**: Uses standard MCP/JSON-RPC communication
- **High Feasibility**: Leverages existing Watchgate error handling infrastructure  
- **Best User Experience**: Provides specific, actionable error messages
- **Backward Compatible**: Works with all MCP clients

### Implementation Feasibility Assessment
| Approach | Feasibility | Protocol Compliance | User Experience |
|----------|-------------|-------------------|----------------|
| JSON-RPC Error Responses | ✅ High | ✅ Full | ✅ Excellent |
| Stderr Communication | ❌ Low | ✅ N/A | ❌ Poor |
| Safe Mode Server | ✅ High | ✅ Full | ✅ Good |

### Research Completion Status
✅ **All research questions answered**  
✅ **Technical feasibility confirmed**  
✅ **Implementation approach identified**  
✅ **Protocol compliance verified**  

*See `research-summary.md` for detailed findings and next steps if implementation is desired.*

## Related Documentation

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Watchgate Configuration Guide](../user/configuration/basic-configuration.md)
- [Plugin Error Handling](../user/core-concepts/5-audit-system.md)