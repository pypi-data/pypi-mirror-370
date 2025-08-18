# Active Todos

This directory contains work items that are currently pending implementation in Watchgate.

## Current Active Todos

### mcp-client-error-communication
Communication system for error reporting between MCP clients and Watchgate proxy.

### security-plugin-critical-handling  
Enhanced handling and configuration for critical security plugin failure modes.

## Adding New Todos

When adding new work items:
1. Create a new directory with a descriptive name
2. Add a `requirements.md` file outlining the work needed
3. Include success criteria and implementation notes
4. Move to `../todos-completed/` when implementation is finished

## Structure

Each todo directory should contain:
- `requirements.md` - What needs to be implemented
- Any supporting documentation or planning files
- Implementation notes and constraints

## Moving to Completed

When a todo is fully implemented:
1. Move the entire directory to `../todos-completed/`
2. Add an `implementation-summary.md` if the work was substantial
3. Update any references in project documentation