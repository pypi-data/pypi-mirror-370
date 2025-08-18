# Race Condition Fixes Requirements

## Overview
Address race conditions in server connection management and request routing that could lead to inconsistent state or failed requests.

## Problem Statement
Several race conditions exist in the current implementation:

### 1. Connection Status Race (Critical)
In `_route_request` (proxy/server.py:624-627):
```python
if conn.status != "connected":
    # Try one reconnection attempt
    if not await self._server_manager.reconnect_server(server_name):
        raise Exception(f"Server '{server_name or 'default'}' is unavailable")
```

**Issue**: Another request could change connection status between the check and reconnection attempt.

### 2. Concurrent Reconnection Race
Multiple concurrent requests to the same disconnected server could all trigger reconnection attempts simultaneously.

### 3. Notification Listener Cleanup Race
In `_listen_for_upstream_notifications`, if servers disconnect during task creation, cleanup might not happen properly.

## Requirements

### 1. Atomic Connection Management
- Implement per-server connection locks
- Ensure only one reconnection attempt per server at a time
- Prevent concurrent state modifications

### 2. Request Queuing During Reconnection
- Queue requests to disconnected servers during reconnection
- Implement timeout for queued requests
- Provide clear error messages when queuing fails

### 3. Safe Notification Listener Management
- Ensure proper cleanup of notification tasks
- Handle server disconnections gracefully during listener startup
- Prevent resource leaks from orphaned tasks

### 4. Connection State Consistency
- Implement atomic state transitions
- Add connection state validation
- Ensure consistent error reporting

## Implementation Approach

### Phase 1: Connection Locking
```python
class ServerConnection:
    def __init__(self):
        self._lock = asyncio.Lock()
        self._reconnecting = False
        self._pending_requests = []
```

### Phase 2: Request Queuing
- Implement per-server request queues
- Add timeout handling for queued requests
- Provide backpressure mechanisms

### Phase 3: Notification Safety
- Use proper async context managers
- Implement graceful shutdown procedures
- Add comprehensive error handling

## Success Criteria
- No race conditions in connection management
- Concurrent requests to same server are handled safely
- Notification listeners clean up properly
- Request queuing works under load
- Error messages clearly indicate server state issues

## Testing Requirements
- Concurrent request stress tests
- Server disconnect/reconnect scenarios
- Notification listener failure cases
- Connection state validation tests

## Performance Considerations
- Minimal impact from locking overhead
- Efficient request queuing implementation
- Bounded memory usage for queued requests
- Fast path for healthy connections