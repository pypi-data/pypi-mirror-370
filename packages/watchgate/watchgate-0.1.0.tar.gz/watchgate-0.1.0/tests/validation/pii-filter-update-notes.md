# PII and Secrets Filter Update Notes

## Issue Identified

During validation testing, it was discovered that the Basic Secrets Filter plugin was not detecting secrets in file content returned from the filesystem MCP server.

### Root Cause

The `check_response` method in `basic_secrets_filter.py` was not implemented. It was returning a simple "allowed" decision without actually checking for secrets in the response content.

```python
# Original implementation (stub)
async def check_response(self, request: MCPRequest, response: MCPResponse) -> PolicyDecision:
    """Check if response should be allowed."""
    # For now, only check requests. Response filtering can be added later.
    return PolicyDecision(
        allowed=True,
        reason="Response filtering not implemented",
        metadata={"plugin": "basic_secrets_filter"}
    )
```

This meant that while the plugin would detect secrets in outgoing requests, it would not detect secrets in incoming responses from MCP servers.

## Fix Applied

The `check_response` method has been fully implemented to:

1. **Detect secrets in responses** using the same patterns and entropy detection as requests
2. **Handle different action modes**:
   - `block`: Prevents the response from being returned to the client
   - `redact`: Replaces detected secrets with `[REDACTED BY WATCHGATE]`
   - `audit_only`: Logs the detection but allows the response through
3. **Maintain security** by falling back to blocking if redaction fails

## Additional Improvements

1. **Configuration compatibility**: Added support for both `secret_types` and `detection_types` configuration fields for backward compatibility
2. **Error handling**: Proper error handling with logging for debugging
3. **Consistent behavior**: Response handling now matches the PII filter's implementation pattern

## Testing

After applying the fix:
- The secrets.txt test file should now be blocked when accessed through the filesystem server
- The validation guide has been updated to reflect this expected behavior
- All secret patterns (AWS keys, GitHub tokens, JWT tokens, etc.) are properly detected

## Impact

This fix ensures that Watchgate provides complete protection against secrets exposure, regardless of whether they appear in requests to or responses from MCP servers.