# Your First Plugin

*[Home](../../README.md) > [User Guide](../README.md) > [Getting Started](README.md) > Your First Plugin*

This guide will walk you through setting up your first Watchgate security plugin. You'll learn how to configure tool access control to protect your MCP server.

## What You'll Learn

By the end of this guide, you'll understand:

- How Watchgate plugins work
- How to configure tool access control
- How to test and verify plugin behavior
- How security plugins protect your AI interactions

## Prerequisites

Before starting, ensure you have:

- **Watchgate installed** (see [Installation Guide](installation.md))
- **Completed quick setup** (see [Quick Setup Guide](quick-setup.md))
- A working MCP server to protect

## Understanding Plugins

Watchgate uses plugins to provide security and auditing capabilities:

- **Security Plugins**: Control what tools and content AI agents can access
- **Auditing Plugins**: Log and monitor all AI interactions
- **Plugin Priority**: Determines the order plugins execute in

The most common first plugin is **tool access control**, which limits which MCP tools an AI agent can use.

## Step 1: Basic Tool Access Control

Let's start with a simple tool access control configuration:

```yaml
# basic-plugin-config.yaml
proxy:
  transport: stdio
  upstream:
    command: "npx @modelcontextprotocol/server-filesystem ./workspace/"

plugins:
  security:
    - policy: "tool_allowlist"
      enabled: true
      config:
        mode: "allowlist"
        tools:
          - "read_file"
          - "list_directory"
```

This configuration:
- ✅ **Allows**: Reading files and listing directories
- ❌ **Blocks**: Writing, deleting, or any other file operations

## Step 2: Test Your Plugin

1. **Save the configuration** as `basic-plugin-config.yaml`

2. **Start Watchgate**:
   ```bash
   watchgate --config basic-plugin-config.yaml --verbose
   ```

3. **In another terminal, test with a simple MCP client**:
   ```bash
   # This should work (read_file is allowed)
   echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "read_file", "arguments": {"path": "workspace/readme.txt"}}}' | watchgate --config basic-plugin-config.yaml
   ```

You should see that read operations work, but any write operations would be blocked.

## Step 3: Understanding Plugin Modes

Tool access control supports three modes:

### Allowlist Mode (Most Secure)
```yaml
config:
  mode: "allowlist"
  tools:
    - "read_file"
    - "list_directory"
  # Only specified tools are allowed, everything else is blocked
```

### Blocklist Mode (Less Restrictive)
```yaml
config:
  mode: "blocklist"
  tools:
    - "delete_file"
    - "execute_command"
  # Specified tools are blocked, everything else is allowed
```

### Allow All Mode (No Restrictions)
```yaml
config:
  mode: "allow_all"
  # All tools are permitted (useful for development/testing)
```

## Step 4: Add More Tools to Your Allowlist

Let's expand your plugin to allow more operations:

```yaml
# expanded-plugin-config.yaml
proxy:
  transport: stdio
  upstream:
    command: "npx @modelcontextprotocol/server-filesystem ./workspace/"

plugins:
  security:
    - policy: "tool_allowlist"
      enabled: true
      config:
        mode: "allowlist"
        tools:
          - "read_file"        # Read file contents
          - "write_file"       # Create/modify files
          - "list_directory"   # List directory contents
          - "create_directory" # Create new directories
          - "search_files"     # Search for files
        block_message: "This tool is not allowed by security policy"
```

The `block_message` is shown when a blocked tool is attempted.

## Step 5: Test with Claude Desktop

1. **Update your Claude Desktop configuration** to use your new config:
   ```json
   {
     "mcpServers": {
       "watchgate-filesystem": {
         "command": "watchgate",
         "args": [
           "--config", "/absolute/path/to/expanded-plugin-config.yaml"
         ]
       }
     }
   }
   ```

2. **Restart Claude Desktop**

3. **Test different operations**:
   ```
   Can you list the files in my directory?
   ✅ Should work (list_directory is allowed)
   
   Can you create a file called "test.txt" with the content "Hello"?
   ✅ Should work (write_file is allowed)
   
   Can you delete the file "test.txt"?
   ❌ Should be blocked (delete_file not in allowlist)
   
   What tools are available to you?
   ℹ️ Should only show the allowed tools
   ```

## Step 6: Add Auditing to See What's Happening

Add an auditing plugin to monitor what your security plugin is doing:

```yaml
# plugin-with-auditing.yaml
proxy:
  transport: stdio
  upstream:
    command: "npx @modelcontextprotocol/server-filesystem ./workspace/"

plugins:
  security:
    - policy: "tool_allowlist"
      enabled: true
      config:
        mode: "allowlist"
        tools:
          - "read_file"
          - "write_file"
          - "list_directory"
          - "create_directory"
          - "search_files"
        block_message: "Tool access denied by security policy"
  
  auditing:
    - policy: "file_auditing"
      enabled: true
      config:
        file: "logs/plugin-audit.log"
        format: "simple"
        mode: "all"
```

Now you can see exactly what your plugin is doing:

```bash
# Watch the audit log in real-time
tail -f logs/plugin-audit.log
```

## Step 7: Understanding Plugin Behavior

Your tool access control plugin provides **dual protection**:

### 1. Tool Execution Filtering
When Claude tries to call a tool:
- ✅ **Allowed tools**: Request passes through to MCP server
- ❌ **Blocked tools**: Request is denied immediately

### 2. Tool Discovery Filtering
When Claude asks "what tools are available?":
- Only shows tools from your allowlist
- Blocked tools are completely hidden from Claude
- Claude doesn't even know forbidden tools exist

## Step 8: Common Plugin Patterns

### Development Environment
```yaml
# More permissive for development
config:
  mode: "blocklist"
  tools:
    - "delete_file"      # Block dangerous operations
    - "execute_command"  # Block command execution
```

### Production Environment
```yaml
# Very restrictive for production
config:
  mode: "allowlist"
  tools:
    - "read_file"        # Only allow reading
    - "list_directory"   # And directory listing
```

### Staging Environment
```yaml
# Balanced for testing
config:
  mode: "allowlist"
  tools:
    - "read_file"
    - "write_file"
    - "list_directory"
    - "create_directory"
    - "move_file"
    # Allow most operations but not deletion
```

## Step 9: Troubleshooting Your Plugin

### Plugin Not Working?

1. **Check plugin is enabled**:
   ```yaml
   enabled: true  # Must be true
   ```

2. **Verify plugin name**:
   ```bash
   watchgate debug plugins --list-available
   ```

3. **Check configuration syntax**:
   ```bash
   watchgate debug config --validate --config your-config.yaml
   ```

### Tools Still Not Blocked?

1. **Check mode spelling**:
   ```yaml
   mode: "allowlist"  # Not "allowlsit" or "allow_list"
   ```

2. **Verify tool names**:
   ```yaml
   tools:
     - "read_file"    # Correct case-sensitive name
   ```

3. **Test with verbose logging**:
   ```bash
   watchgate --config your-config.yaml --verbose
   ```

### Getting Unexpected Behavior?

1. **Check the audit logs** to see what's actually happening
2. **Test each tool individually** 
3. **Use `mode: "allow_all"` temporarily** to verify the MCP server works
4. **Review the [troubleshooting guide](../reference/troubleshooting.md)**

## Next Steps

Now that you have your first plugin working:

1. **Add content protection**: Learn about [content access control](../tutorials/protecting-sensitive-content.md)
2. **Combine multiple plugins**: Try [multi-plugin security](../tutorials/multi-plugin-security.md)
3. **Understand plugin ordering**: Read about [plugin priorities](../reference/plugin-ordering.md)
4. **Explore other plugins**: Check the [configuration reference](../reference/configuration-reference.md)

## Summary

You've successfully configured your first Watchgate plugin! You now understand:

- ✅ How to configure tool access control
- ✅ The difference between allowlist, blocklist, and allow_all modes
- ✅ How plugins filter both tool execution and tool discovery
- ✅ How to combine security plugins with auditing
- ✅ How to troubleshoot common plugin issues

Your AI interactions are now protected by Watchgate's security layer, giving you control over exactly what tools your AI agents can use.
