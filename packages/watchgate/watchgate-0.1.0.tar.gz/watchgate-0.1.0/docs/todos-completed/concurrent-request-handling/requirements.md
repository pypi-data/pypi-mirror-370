# Concurrent Request Handling

## Overview

Watchgate's MCPProxy currently processes requests sequentially - it sends a request to the upstream server and waits for its response before handling the next request. This limitation prevents optimal performance when multiple MCP clients send requests simultaneously or when a single client sends multiple requests without waiting for responses.

## Problem Statement

The current implementation in `MCPProxy.handle_request()` uses a simple pattern:
```python
await self._upstream_transport.send_message(upstream_request)
response = await self._upstream_transport.receive_message()
```

This pattern fails with concurrent requests because:
1. `receive_message()` returns ANY available response, not the specific response for the request
2. Multiple concurrent requests lead to mismatched request/response pairs
3. The proxy cannot leverage the upstream server's ability to process requests concurrently

## Requirements

### Functional Requirements

1. **Request/Response Correlation**
   - The proxy MUST correctly match responses to their corresponding requests using the JSON-RPC `id` field
   - The proxy MUST handle out-of-order response delivery
   - The proxy MUST support both string and integer request IDs as per JSON-RPC 2.0

2. **Concurrent Processing**
   - The proxy MUST be able to handle multiple in-flight requests simultaneously
   - The proxy MUST NOT block on waiting for a specific response when other responses are available
   - The proxy SHOULD forward requests to the upstream server as soon as they arrive

3. **Plugin Compatibility**
   - Security plugins MUST be able to inspect and potentially modify concurrent requests safely
   - Auditing plugins MUST be able to log concurrent requests without race conditions
   - Plugin state MUST remain isolated between concurrent requests

4. **Error Handling**
   - The proxy MUST handle timeouts for individual requests without affecting other in-flight requests
   - The proxy MUST properly clean up resources when requests fail or time out
   - The proxy MUST handle upstream server disconnection gracefully for all pending requests

### Non-Functional Requirements

1. **Performance**
   - Concurrent request handling MUST NOT degrade performance for single requests
   - The proxy SHOULD process N concurrent requests in approximately the same time as 1 request (plus overhead)
   - Memory usage SHOULD scale linearly with the number of concurrent requests

2. **Compatibility**
   - The implementation MUST maintain backward compatibility with sequential clients
   - The implementation MUST work with all supported transports (currently stdio)
   - The implementation MUST follow the JSON-RPC 2.0 specification

3. **Observability**
   - The proxy SHOULD track metrics on concurrent request count
   - The proxy SHOULD log when request concurrency is detected
   - Audit logs MUST clearly indicate which responses correspond to which requests

## Design Considerations

### Transport Layer
- The `StdioTransport` already has infrastructure for concurrent requests (message dispatcher, pending requests tracking)
- Need to expose request-specific waiting mechanism instead of generic `receive_message()`

### Proxy Layer Options

**Option 1: Request Handler Pattern**
- Add a `ConcurrentRequestHandler` that manages request/response correlation
- Maintains a background task to receive responses and route them to waiting requests
- Provides a `send_request()` method that returns the specific response

**Option 2: Future-Based Pattern**
- Modify transport to return a Future for each sent request
- Proxy awaits the specific Future for each request
- Transport's message dispatcher resolves the appropriate Future

**Option 3: Async Queue Pattern**
- Each request gets its own response queue
- Transport routes responses to the appropriate queue
- Proxy waits on its specific queue

### Plugin Considerations
- Plugins are currently stateless, which is good for concurrency
- Need to ensure plugin manager methods are thread-safe
- May need to add request context to plugin calls for correlation

## Testing Requirements

1. **Unit Tests**
   - Test correct request/response matching with various ID types
   - Test handling of out-of-order responses
   - Test error scenarios (timeouts, disconnections)

2. **Integration Tests**
   - Test with mock transport that simulates concurrent behavior
   - Test with real MCP servers that support concurrent requests
   - Test plugin behavior under concurrent load

3. **Performance Tests**
   - Measure throughput improvement with concurrent requests
   - Verify no performance regression for sequential requests
   - Test resource usage under high concurrency

## Implementation Plan

1. **Phase 1: Transport Enhancement**
   - Enhance transport interface to support request-specific waiting
   - Implement in StdioTransport without breaking existing interface
   - Add comprehensive unit tests

2. **Phase 2: Proxy Integration**
   - Update MCPProxy to use enhanced transport capabilities
   - Ensure plugin manager is thread-safe
   - Maintain backward compatibility

3. **Phase 3: Testing & Optimization**
   - Implement comprehensive test suite
   - Performance testing and optimization
   - Documentation updates

## Success Criteria

1. All existing tests continue to pass
2. New concurrent request tests pass
3. Performance improves for concurrent workloads
4. No regression for sequential workloads
5. Clear documentation for concurrent behavior