# Tool Access Control Plugin

**Status**: Implemented

## Problem Statement
Need to control which MCP tools clients can access through allowlist/blocklist policies.

## Requirements
- Configure allowed and blocked tools via YAML
- Support glob patterns for tool matching
- Default allow or deny behavior
- Integration with audit trail
- Clear policy decision reasoning

## Success Criteria
- [x] Allowlist and blocklist configuration
- [x] Glob pattern matching for tools
- [x] Configurable default policy
- [x] Audit integration via PolicyDecision
- [x] Clear error messages for blocked tools

## Configuration
```yaml
plugins:
  security:
    - policy: "tool_allowlist"
      enabled: true
      priority: 5
      config:
        default_policy: "allow"  # or "deny"
        rules:
          allow:
            - "read_file"
            - "list_directory"
          block:
            - "write_file"
            - "delete_*"
```

## References
- Implementation: `watchgate/plugins/security/tool_allowlist.py`
- Tests: `tests/unit/test_tool_allowlist_plugin.py`