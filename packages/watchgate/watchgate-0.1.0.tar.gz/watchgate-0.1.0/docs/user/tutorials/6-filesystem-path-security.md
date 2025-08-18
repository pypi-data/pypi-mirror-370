# Tutorial 6: Filesystem Path Security

This tutorial demonstrates how to use Watchgate's `filesystem_server_security` plugin to implement granular path-based access control for the official `@modelcontextprotocol/server-filesystem` MCP server.

## Overview

The `filesystem_server_security` plugin provides path-level security - controlling which files and directories filesystem tools can access based on glob patterns. This allows for fine-grained control over filesystem operations beyond simple tool-level restrictions.

**Important**: This plugin is specifically designed for `@modelcontextprotocol/server-filesystem`. It understands the tool names and argument structures used by that server. For other filesystem MCP servers, the plugin would need to be adapted.

## Prerequisites

- Watchgate installed and configured
- The official `@modelcontextprotocol/server-filesystem` MCP server
- Basic understanding of Watchgate configuration

## Setting Up the MCP Filesystem Server

First, ensure you have the official MCP filesystem server available. You can use it directly via npx:

```bash
# The official MCP filesystem server (no installation needed with npx)
npx @modelcontextprotocol/server-filesystem /path/to/your/project
```

**Note**: This tutorial is specifically for `@modelcontextprotocol/server-filesystem`. Other filesystem servers may use different tool names and would require plugin adaptation.

## Basic Path-Based Security

Let's start with a simple configuration that allows reading documentation but prevents writing:

```yaml
# watchgate.yaml
proxy:
  transport: "stdio"

upstream:
  command: "npx @modelcontextprotocol/server-filesystem /path/to/your/project"

plugins:
  security:
    - policy: "filesystem_server_security"
      enabled: true
      config:
        read: ["docs/**/*", "README.md", "*.txt"]
        # No write permissions = all write operations blocked
        priority: 50
```

With this configuration:
- Claude can read any file in the `docs/` directory and subdirectories
- Claude can read `README.md` and any `.txt` files in the root
- Claude cannot write files anywhere
- Claude cannot perform operations like moving files

## Testing Read-Only Access

Start Watchgate with the configuration above:

```bash
cd /path/to/your/project
watchgate
```

In Claude Desktop, try these operations:

1. **Allowed**: "Please read the README.md file"
   - ✅ This will work because `README.md` matches the read pattern

2. **Allowed**: "List the contents of the docs directory"
   - ✅ This will work because `docs/**/*` allows reading the directory

3. **Blocked**: "Create a new file called test.txt with the content 'Hello'"
   - ❌ This will be blocked because no write permissions are configured

## Adding Write Permissions

Now let's allow writing to specific directories:

```yaml
plugins:
  security:
    - policy: "filesystem_server_security"
      enabled: true
      config:
        read: ["docs/**/*", "README.md", "*.txt", "src/**/*"]
        write: ["drafts/**/*", "temp/*.tmp", "logs/*.log", "archive/**/*"]
        priority: 50
```

Now Claude can:
- Read from docs, src, README.md, and .txt files
- Write to the `drafts/` directory (any files)
- Write `.tmp` files to the `temp/` directory
- Write `.log` files to the `logs/` directory
- Move files to/from the `archive/` directory

## Using Exclusion Patterns

Protect sensitive files using exclusion patterns with `!`:

```yaml
plugins:
  security:
    - policy: "filesystem_server_security"
      enabled: true
      config:
        read: [
          "project/**/*",      # Allow reading entire project
          "!project/.env*",    # Except environment files
          "!project/secrets/*", # Except secrets directory
          "!project/**/*.key"   # Except any .key files
        ]
        write: [
          "project/src/**/*",   # Allow writing to source
          "project/tests/**/*", # Allow writing to tests
          "project/temp/**/*",  # Allow temp file operations including moves
          "!project/tests/fixtures/readonly/*" # Except readonly fixtures
        ]
```

## Advanced Use Case: Content Management System

Here's a realistic configuration for a content management scenario:

```yaml
plugins:
  security:
    - policy: "filesystem_server_security"
      enabled: true
      config:
        # Read access to content and assets
        read: [
          "content/**/*",
          "assets/**/*", 
          "templates/**/*",
          "config/*.yaml",
          "!config/secrets.yaml"
        ]
        
        # Write access for content creation and uploads
        write: [
          "content/drafts/**/*",    # Draft content
          "content/posts/**/*.md",  # Published posts (markdown only)
          "uploads/**/*",           # File uploads
          "assets/generated/**/*",  # Generated assets
          "content/archive/**/*",   # Content management (including moves)
          "uploads/temp/**/*"       # Temporary upload management
        ]
        
        priority: 20
```



## Debugging Path Matching

If path matching isn't working as expected, enable debug logging:

```yaml
logging:
  level: "DEBUG"
  
plugins:
  security:
    - policy: "filesystem_server_security"
      enabled: true
      config:
        read: ["debug/**/*"]
        priority: 50
```

Watchgate will log detailed information about:
- Which paths are being extracted from tool calls
- Which patterns are being matched against
- Why access was granted or denied

## Testing Your Configuration

Here's a systematic way to test your filesystem security configuration:

### 1. Test Read Permissions

```bash
# In Claude Desktop, try reading files that should be allowed
"Please read the file docs/README.md"

# Try reading files that should be blocked  
"Please read the file secrets/api-key.txt"
```

### 2. Test Write Permissions

```bash
# Try writing to allowed locations
"Create a file drafts/test.md with the content 'Hello World'"

# Try writing to blocked locations
"Create a file secrets/new-secret.txt with some content"
```

### 3. Test Pattern Matching

```bash
# Test glob patterns work correctly
"List all .md files in the docs directory"

# Test exclusion patterns
"Try to read any .env files in the project"
```

## Security Best Practices

1. **Default Deny**: Start with minimal permissions and add only what's needed
2. **Principle of Least Privilege**: Grant the minimum access level required
3. **Use Exclusions**: Explicitly exclude sensitive files even in allowed directories
4. **Layer Security**: Consider combining with other security plugins for comprehensive protection
5. **Test Thoroughly**: Verify your patterns match the intended files
6. **Monitor Access**: Use auditing plugins to log filesystem access

## Common Patterns

### Development Sandbox
```yaml
config:
  read: ["project/**/*", "!project/.git/**/*", "!project/node_modules/**/*"]
  write: ["project/src/**/*", "project/tests/**/*", "project/docs/**/*", 
          "project/temp/**/*", "project/build/**/*"]
```

### Documentation Only
```yaml
config:
  read: ["docs/**/*", "README.md", "*.md", "examples/**/*.md"]
  # No write permissions = read-only access
```

### Safe Testing Environment
```yaml
config:
  read: ["tests/**/*", "fixtures/**/*", "src/**/*"]
  write: ["tests/output/**/*", "temp/**/*", "tests/temp/**/*"]
```

## Troubleshooting

### Issue: Patterns Not Matching

**Problem**: Your glob patterns don't match the expected files.

**Solution**: 
- Check that patterns are relative to the filesystem server's allowed directories
- Use debug logging to see what paths are being extracted
- Test patterns using tools like `pathspec` in Python

### Issue: Access Still Blocked

**Problem**: Access is blocked even with matching patterns.

**Solution**:
- Verify plugin configuration is correct
- Check if the filesystem server itself allows the path
- Use debug logging to see why access was denied

### Issue: Empty Configuration

**Problem**: Empty configuration blocks all access.

**Solution**: This is by design. Add explicit permissions for the access you want to allow.

## Next Steps

- Learn about [Multi-Plugin Security](4-multi-plugin-security.md) for complex scenarios
- Explore [Auditing](5-auditing-mcp-communications.md) to monitor filesystem access
- Check the [Configuration Reference](../reference/configuration-reference.md) for all options

## Summary

The `filesystem_server_security` plugin provides powerful path-based access control for MCP filesystem operations. By using glob patterns and permission levels, you can create fine-grained security policies that allow safe filesystem access while protecting sensitive files and directories.

Key takeaways:
- Use read/write permission levels appropriately
- Leverage glob patterns for flexible path matching  
- Always test your configuration thoroughly
- Start with minimal permissions and add as needed
