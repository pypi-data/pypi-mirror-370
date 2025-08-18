# Notification Routing Requirements (Updated)

## Overview
Fix the current notification routing logic that sends notifications to the first available server instead of implementing proper routing when multiple servers are configured.

## Problem Statement
Currently, in `proxy/server.py:393-404`, notifications from clients are sent to the first available server connection, which doesn't work correctly when multiple servers are configured. 

**Key Insight**: MCP clients (like Claude Desktop) will always send standard MCP notifications without Watchgate-specific namespacing. We must work within this constraint.

**Major Simplification**: Progress notifications do NOT require complex routing! The MCP protocol specifies that clients provide `progressToken` values in request metadata, and servers echo those same tokens in progress notifications. This means Watchgate can forward progress notifications transparently - the client already has everything needed to correlate progress back to operations.

## Notification Types and Routing Strategy

### 1. Client→Server Notifications

#### `notifications/cancelled`
**Routing**: Stateful - route based on request tracking
- **Challenge**: Client sends `{"method": "notifications/cancelled", "params": {"requestId": "123"}}` with no server indication
- **Solution**: Watchgate tracks which server handled each request ID
- **Implementation**: Maintain `request_id → server_name` mapping during request processing

#### `notifications/initialized` 
**Routing**: Broadcast to all servers
- **Rationale**: This notification indicates the client is ready, all servers should know
- **Implementation**: Send to all connected servers in parallel
- **Error Handling**: Log failures but don't block if some servers fail

### 2. Server→Client Notifications

#### `notifications/progress`
**Routing**: Transparent forwarding (NO server tracking needed)
- **Current**: Server sends progress → Watchgate → Client
- **Key Insight**: Client provides `progressToken` in request metadata, server uses that same token in progress notifications
- **Solution**: Forward progress notifications unchanged - client correlates using its own tokens
- **Implementation**: Simple pass-through, no modification or tracking required

#### Other server→client notifications
**Routing**: Direct forwarding
- Forward standard MCP notifications maintaining original method names
- No namespacing to preserve MCP protocol compliance

## Implementation Strategy

### Phase 1: Request Tracking Infrastructure
- Add request tracking to proxy server
- Map `request_id → server_name` during request processing
- Implement cleanup for completed/expired requests

### Phase 2: Client→Server Routing
- Update notification handler to use request tracking for cancellations
- Implement broadcast logic for initialization notifications
- Add fallback behavior for untrackable notifications

### Phase 3: Server→Client Progress (Simplified)
- Implement transparent forwarding for progress notifications
- No server context preservation needed (client uses its own tokens)
- Test progress notification flow with multiple servers

## Technical Details

### Request Tracking
```python
class MCPProxy:
    def __init__(self):
        self._request_to_server: Dict[str, str] = {}
    
    async def handle_request(self, request):
        # Track which server will handle this request
        server_name = self._determine_target_server(request)
        if request.id:
            self._request_to_server[request.id] = server_name
        
        # ... existing request handling
        
    async def _cleanup_completed_request(self, request_id: str):
        self._request_to_server.pop(request_id, None)
```

### Notification Routing
```python
async def handle_notification(self, notification):
    if notification.method == "notifications/cancelled":
        request_id = notification.params.get("requestId")
        target_server = self._request_to_server.get(request_id)
        if target_server:
            await self._route_to_server(target_server, notification)
        else:
            logger.warning(f"Cannot route cancellation for unknown request {request_id}")
    
    elif notification.method == "notifications/initialized":
        # Broadcast to all servers
        await self._broadcast_to_all_servers(notification)
    
    elif notification.method == "notifications/progress":
        # Forward transparently - client provided the token, no routing needed
        await self._forward_to_client(notification)
    
    else:
        # Default: forward other server→client notifications transparently
        await self._forward_to_client(notification)
```

## Success Criteria

1. **Cancellation notifications** route to the correct server that handled the original request
2. **Initialization notifications** reach all connected servers
3. **Single-server mode** continues to work unchanged (no routing complexity)
4. **Error handling** provides clear logging when routing fails
5. **Memory management** prevents request tracking from growing unbounded
6. **Progress notifications** forward transparently using client-provided tokens

## Open Questions

1. **Request cleanup timing**: When should we remove completed requests from tracking?
2. **Error notification routing**: Should error notifications be broadcast or tracked?  
3. **Unknown notification types**: Should unrecognized notification types be broadcast or dropped?
4. **Client→server notification ordering**: Do we need to preserve notification ordering relative to requests?

## Non-Goals

- **Client modification**: We will NOT require changes to MCP clients
- **Protocol extensions**: We will NOT extend the MCP protocol with Watchgate-specific features
- **Perfect routing**: Some edge cases (like notifications for unknown requests) will be logged and gracefully handled rather than perfectly routed