# MCP Notification Support - Future Work

**Status**: Not Implemented  
**Priority**: Medium  
**Target**: Future Release

## Overview

MCP (Model Context Protocol) supports three message types:
- Requests (client → server)
- Responses (server → client)  
- Notifications (bidirectional, no response expected)

Watchgate currently implements full support for request/response flows but does not yet handle MCP notifications.

## Current State

### What's Implemented
- Plugin interfaces include `check_notification()` methods
- Message type definitions include `MCPNotification` class
- Plugin base classes support notification handling

### What's Missing
- Proxy server notification routing
- Stdio transport notification handling
- Bidirectional notification flow
- Notification-specific security policies

## Implementation Notes

When implementing notification support:

1. **Proxy Server Changes**
   - Add notification handler alongside request handler
   - Implement bidirectional routing (client→server and server→client)
   - Handle notifications that don't expect responses

2. **Transport Layer Changes**
   - Update stdio transport to handle notifications
   - Ensure proper message routing without blocking on responses

3. **Plugin Considerations**
   - Most plugins can use simple pass-through for notifications
   - Some plugins may want notification-specific policies
   - Audit plugins should log notifications

4. **Testing Requirements**
   - Add notification flow tests
   - Test bidirectional routing
   - Verify non-blocking behavior

## Security Considerations

Notifications present unique security challenges:
- No response means no error feedback
- Bidirectional flow requires careful access control
- Potential for notification flooding
- State change notifications may leak information

## Migration Path

When notifications are implemented:
1. Existing configurations will continue to work
2. Notification handling will be opt-in initially
3. Plugins can gradually add notification support
4. Clear documentation for security implications