# ADR-004: Error Handling Strategy

**Status**: Accepted  

## Context

Watchgate operates as a security proxy in the MCP ecosystem, requiring robust error handling for:

1. **Protocol Compliance**: Must return proper JSON-RPC 2.0 error responses
2. **Security Isolation**: Errors from upstream servers must be sanitized
3. **Debugging Support**: Developers need actionable error information
4. **Reliability**: System should gracefully handle various failure modes
5. **Monitoring**: Operations teams need visibility into error patterns

The error handling strategy will impact security, usability, and maintainability throughout the system.

## Decision

We will implement a **structured error handling strategy** using JSON-RPC 2.0 error codes with Watchgate-specific extensions:

```python
# Standard JSON-RPC error codes
class JsonRpcError(Exception):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

# Watchgate-specific error codes
class WatchgateError(JsonRpcError):
    SECURITY_VIOLATION = -32000
    UPSTREAM_CONNECTION_FAILED = -32001
    UPSTREAM_TIMEOUT = -32002
    VALIDATION_FAILED = -32003
    RATE_LIMIT_EXCEEDED = -32004
```

### Key Principles

1. **Protocol Compliance**: All errors follow JSON-RPC 2.0 specification
2. **Security-First**: Never leak sensitive information in error messages
3. **Structured Data**: Consistent error format with codes and details
4. **Contextual Information**: Include relevant context for debugging
5. **Graceful Degradation**: System continues operating despite errors

## Alternatives Considered

### Alternative 1: Simple Exception Propagation
```python
# Just let Python exceptions bubble up
try:
    result = await server.request(message)
except Exception as e:
    raise e  # Raw exception propagation
```
- **Pros**: Simple, preserves full error details
- **Cons**: Breaks JSON-RPC compliance, potential security leaks

### Alternative 2: Generic Error Responses
```python
# Always return same generic error
def handle_error(e):
    return {"error": {"code": -1, "message": "An error occurred"}}
```
- **Pros**: Maximum security, simple implementation
- **Cons**: Poor debugging experience, no actionable information

### Alternative 3: HTTP-Style Status Codes
```python
# Use HTTP status codes instead of JSON-RPC
class WatchgateError:
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    INTERNAL_ERROR = 500
```
- **Pros**: Familiar to web developers
- **Cons**: Doesn't follow JSON-RPC 2.0 specification

## Consequences

### Positive
- **Protocol Compliance**: Follows JSON-RPC 2.0 error specification exactly
- **Security**: Controlled error information prevents information leakage
- **Debugging**: Structured errors with codes enable targeted debugging
- **Monitoring**: Error codes allow for meaningful metrics and alerting
- **Client Support**: Clients can handle errors programmatically

### Negative
- **Complexity**: More code to handle error categorization and formatting
- **Maintenance**: Error codes must be documented and maintained
- **Potential Over-Engineering**: May be more structure than needed initially

## Implementation Notes

### Error Response Format
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32003,
    "message": "Validation failed",
    "data": {
      "details": "Request missing required 'method' field",
      "request_id": "req_123",
      "timestamp": "YYYY-MM-DDTHH:MM:SSZ"
    }
  },
  "id": null
}
```

### Error Handling Pipeline
```python
class ErrorHandler:
    async def handle_error(self, error: Exception, context: dict) -> dict:
        # Classify error type
        error_code, message = self._classify_error(error)
        
        # Sanitize error details for security
        safe_details = self._sanitize_details(error, context)
        
        # Log for monitoring
        self._log_error(error_code, message, context)
        
        # Return JSON-RPC error response
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": error_code,
                "message": message,
                "data": safe_details
            },
            "id": context.get("request_id")
        }
```

### Security Considerations
- **Information Filtering**: Remove stack traces and internal paths from client responses
- **Error Logging**: Full error details logged internally for debugging
- **Rate Limiting**: Prevent error-based enumeration attacks
- **Context Sanitization**: Remove sensitive data from error context

### Error Categories

#### Transport Errors
- Connection failures to upstream servers
- Timeout errors
- Protocol-level communication issues

#### Validation Errors
- Malformed JSON-RPC requests
- Missing required fields
- Invalid parameter types

#### Security Errors
- Blocked requests due to security policies
- Authentication failures
- Authorization violations

#### Internal Errors
- Unexpected system failures
- Configuration errors
- Resource exhaustion

### Monitoring Integration
```python
# Error metrics for monitoring
error_counter = Counter(
    'watchgate_errors_total',
    'Total number of errors by type',
    ['error_code', 'error_type']
)

def log_error(error_code: int, error_type: str):
    error_counter.labels(
        error_code=error_code,
        error_type=error_type
    ).inc()
```

## Review

This decision will be reviewed when:
- JSON-RPC specification changes significantly
- Security requirements become more stringent
- Debugging needs change substantially
- Monitoring requirements evolve
