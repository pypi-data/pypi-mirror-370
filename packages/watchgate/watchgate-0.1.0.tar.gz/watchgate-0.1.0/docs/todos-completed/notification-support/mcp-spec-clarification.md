# MCP Specification Clarification: Notifications

## Overview

This document clarifies the Model Context Protocol (MCP) specification regarding notification flows, based on research of the official MCP schema and documentation.

## Key Findings

### Notification Flow Directions

**MCP supports bidirectional notifications:**
- ✅ **Client → Server notifications** are valid and specified
- ✅ **Server → Client notifications** are valid and specified

### Base Notification Interface

All notifications follow the JSON-RPC 2.0 format with this base structure:

```typescript
export interface Notification {
  method: string;
  params?: {
    _meta?: { [key: string]: unknown };
    [key: string]: unknown;
  };
}
```

Key characteristics:
- Notifications are one-way messages
- The receiver MUST NOT send a response
- No `id` field (unlike requests/responses)

## Specified Notification Types

### Client → Server Notifications

1. **InitializedNotification** (`notifications/initialized`)
   - Sent after client initialization is complete
   - Indicates client is ready for normal operation

2. **RootsListChangedNotification** (`notifications/roots/list_changed`)
   - Informs server that the list of roots has changed
   - Server should then request updated roots list

3. **CancelledNotification** (`notifications/cancelled`)
   - Used to cancel ongoing operations

### Server → Client Notifications

1. **LoggingMessageNotification** (`notifications/message`)
   - Server sends log messages to client
   - For debugging and monitoring

2. **ResourceUpdatedNotification** (`notifications/resources/updated`)
   - Notifies client when a resource has been updated

3. **ResourceListChangedNotification** (`notifications/resources/list_changed`)
   - Informs client that the list of available resources has changed

4. **ToolListChangedNotification** (`notifications/tools/list_changed`)
   - Informs client that the list of available tools has changed

5. **PromptListChangedNotification** (`notifications/prompts/list_changed`)
   - Informs client that the list of available prompts has changed

6. **ProgressNotification** (`notifications/progress`)
   - Updates client on operation progress

## Architecture Implications for Watchgate

### Current Architecture Issues

1. **Missing Server → Client Infrastructure**
   - StdioTransport can only handle request/response, not notifications from upstream
   - StdioServer cannot write notifications to client
   - No mechanism to route notifications from upstream server to client

2. **Incomplete Client → Server Implementation**
   - Current implementation exists but may not handle all specified notification types
   - Need to verify proper forwarding to upstream server

### Required Changes

Based on the MCP specification, Watchgate must support:

1. **Bidirectional notification forwarding**
   - Client → Watchgate → Upstream Server
   - Upstream Server → Watchgate → Client

2. **Notification processing through security plugins**
   - Filter/modify notifications based on security policies
   - Maintain audit trails for notifications

3. **Concurrent handling**
   - Handle notifications alongside request/response pairs
   - Ensure notifications don't block normal operation

## Implementation Requirements

### Transport Layer
- Enhance StdioTransport to handle incoming notifications from upstream
- Distinguish between responses (have `id`) and notifications (no `id`)
- Support concurrent reading for both message types

### Server Layer
- Add `write_notification()` method to StdioServer
- Support writing notifications to client stdout

### Proxy Layer
- Background task to listen for upstream notifications
- Route notifications through plugin processing pipeline
- Forward processed notifications to client

### Plugin System
- Extend plugin interfaces to handle notifications
- Ensure plugins can modify/filter notification content
- Maintain security boundaries for notification data

## Specification Sources

- MCP Schema: `https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/schema/2025-03-26/schema.ts`
- Official Documentation: `https://modelcontextprotocol.io/specification/2025-03-26/`
- JSON-RPC 2.0 Base: All MCP messages follow JSON-RPC 2.0 specification

## Conclusion

The MCP specification clearly supports bidirectional notifications with specific, well-defined notification types. Watchgate's current implementation is incomplete and requires significant architectural changes to properly handle the full notification flow as specified by MCP.