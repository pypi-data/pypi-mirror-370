# Securing Tool Access

*[Home](../../../README.md) → [User Documentation](../../README.md) → [Tutorials](../README.md) → Securing Tool Access*

This tutorial will teach you how to set up Claude Desktop to communicate with the popular filesystem MCP server through Watchgate, specifically focusing on the `tool_allowlist` plugin for tool-level security control.

## What You'll Accomplish

The `@modelcontextprotocol/server-filesystem` is one of the most popular MCP servers, allowing AI assistants to read, write, and manage files on your local system. While powerful, this can be risky if the AI makes unexpected decisions or encounters issues - it could potentially access sensitive files or perform unintended operations.

In this tutorial, you'll learn how to use Watchgate's tool access control to create a secure layer between Claude Desktop and the filesystem server. By the end, you'll have:

- **Restricted tool access**: Claude will only see and use the specific filesystem tools you approve
- **Security logging**: Visibility into what tools are being used and any blocked attempts
- **Production-ready setup**: A configuration you can adapt for real-world use cases

This approach lets you safely give Claude filesystem capabilities while maintaining control over exactly what it can do.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Verify Watchgate Installation](#verify-watchgate-installation)
3. [Filesystem MCP Server](#filesystem-mcp-server)
4. [Configure Watchgate for Tool Access Control](#configure-watchgate-for-tool-access-control)
5. [Configure Claude Desktop](#configure-claude-desktop)
6. [Test Your Tool Access Control Setup](#test-your-tool-access-control-setup)
7. [Tool Access Control Configuration Options](#tool-access-control-configuration-options)
8. [Troubleshooting](#troubleshooting)
9. [Next Steps](#next-steps)

## Prerequisites

Before you begin, ensure you have:

- **Claude Desktop** installed on your system
- **Python** (version 3.11 or higher) for Watchgate
- **Node.js and npm** for running the MCP filesystem server
- **uv** tool for Watchgate installation

### Verify Your Prerequisites

Before proceeding, verify your system meets all requirements:

```bash
# Verify Python version (should be 3.11 or higher)
# On macOS/Linux:
python3 --version
# On Windows:
python --version

# Verify Node.js and npm are available (required for npx)
node --version
npm --version

# Verify uv tool is available
uv --version
```

**If Node.js is missing**: Visit [nodejs.org](https://nodejs.org/) to install Node.js, which includes npm and npx.

If any of these commands fail, install the missing tools before continuing.

## Verify Watchgate Installation

If you haven't already installed Watchgate, install it using your preferred Python package manager:

```bash
uv add watchgate
# or: pip install watchgate
```

To verify Watchgate is properly installed:

```bash
watchgate --help
```

## Filesystem MCP Server

The filesystem MCP server allows Claude to read and write files in specified directories. No installation is needed - Watchgate will automatically run it using `npx` when you start the proxy.

## Configure Watchgate for Tool Access Control

We'll use the provided configuration file that includes tool access control settings.

1. **Understanding the configuration**:

   The tutorial uses the configuration file at `configs/tutorials/1-securing-tool-access.yaml`, which contains:

   ```yaml
   # Watchgate Configuration for Tool Access Control
   proxy:
     # How Watchgate communicates with the MCP server (stdio = command-line interface)
     transport: stdio
     upstream:
       # This starts the filesystem MCP server using npx (Node.js package runner)
       # @modelcontextprotocol/server-filesystem is the official filesystem server
       # ~/claude-sandbox/ is the directory the filesystem server will operate within
       command: "npx @modelcontextprotocol/server-filesystem ~/claude-sandbox/"

   plugins:
     security:
       # Enable the tool access control plugin
       - policy: "tool_allowlist"
         enabled: true
         config:
           # "allowlist" mode: only specified tools are permitted (most secure)
           # Other options: "blocklist" (block specific tools), "allow_all" (no restrictions)
           mode: "allowlist"
           tools:
             # List of filesystem operations that Claude is allowed to use
             # These are the only tools Claude will see and can execute
             - "read_file"        # Read file contents
             - "write_file"       # Create or modify files
             - "create_directory" # Create new directories
             - "list_directory"   # List directory contents
             - "move_file"        # Rename or move files
             - "search_files"     # Search for files by name/pattern
           # Message shown when a blocked tool is attempted
           block_message: "Tool access denied by security policy"
   ```

   **Key Points:**
   - **Transport**: Uses `stdio` to communicate with command-line MCP servers
   - **Upstream Command**: Starts the filesystem server with `~/claude-sandbox/` as its working directory
   - **Security Mode**: `allowlist` only permits the specified tools
   - **Tool List**: Only essential filesystem operations are allowed

2. **Create a safe sandbox directory**:
   
   ```bash
   # Create a directory for Claude to work in (using home directory for predictable paths)
   mkdir ~/claude-sandbox
   
   # Add some sample files for testing
   echo "Hello from the sandbox!" > ~/claude-sandbox/readme.txt
   mkdir ~/claude-sandbox/projects
   ```

   **Note**: We use `~/claude-sandbox/` (in your home directory) to ensure a predictable absolute path regardless of where Claude Desktop starts. If you prefer a different location, simply update the `command:` line in the configuration file to point to your chosen directory.

## Configure Claude Desktop

Configure Claude Desktop to use Watchgate as a proxy to the filesystem MCP server.

1. **Locate your Claude Desktop configuration file:**
   
   The configuration file should already exist if you've used Claude Desktop before:
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux:** `~/.config/Claude/claude_desktop_config.json`
   
   **If the file doesn't exist:** Reinstall Claude Desktop from the official website to ensure proper setup.

2. **Create or update the configuration file:**

```json
{
  "mcpServers": {
    "filesystem-via-watchgate": {
      "command": "<watchgate_root>/watchgate",
      "args": [
        "--config", "<watchgate_root>/configs/tutorials/1-securing-tool-access.yaml"
      ],
      "env": {}
    }
  }
}
```

**Important**: Replace `<watchgate_root>` with the absolute path to your Watchgate installation directory. For example:
- **macOS/Linux**: `/Users/yourusername/watchgate` or `/home/yourusername/watchgate`
- **Windows**: `C:\Users\yourusername\watchgate`

3. **Restart Claude Desktop** after making configuration changes:
   
   Close Claude Desktop completely and restart it. Configuration changes only take effect after a restart.

## Test Your Tool Access Control Setup

Now let's test that everything is working correctly.

1. **Test the setup with Claude Desktop**:
   
   - Launch Claude Desktop and start a new conversation
   - Test with: "Can you list the files in my directory?"
   - Test with: "Please create a test file called 'hello.txt' with the content 'Hello from Claude!'"
   - Verify tool access control by asking Claude what tools are available

   **What happens behind the scenes**: When you start a conversation, Claude Desktop automatically launches Watchgate with your configuration. Watchgate will show output similar to this in its logs:
   
   ```
   [INFO] watchgate.main: Loading configuration from watchgate-config.yaml
   [INFO] watchgate.main: Starting Watchgate MCP Gateway
   [INFO] watchgate.plugins.manager: Loaded security plugin: tool_allowlist
   [INFO] watchgate.proxy.server: Connected to upstream server
   [INFO] watchgate.proxy.server: MCPProxy now accepting client connections
   ```

## Tool Access Control Configuration Options

The `tool_allowlist` plugin supports several configuration modes:

### Allowlist Mode (Most Restrictive)
```yaml
config:
  mode: "allowlist"
  tools:
    - "read_file"
    - "write_file"
    - "list_directory"
  # Only specified tools are allowed
```

### Blocklist Mode (Less Restrictive)
```yaml
config:
  mode: "blocklist"
  tools:
    - "delete_file"
    - "execute_command"
    - "system_call"
  # All tools allowed except specified ones
```

### Allow All Mode (No Restrictions)
```yaml
config:
  mode: "allow_all"
  # All tools are permitted (useful for development)
```

### How Tool Access Control Works

The tool access control plugin provides dual protection:

1. **Tool Execution Filtering**: Blocks `tools/call` requests for disallowed tools
2. **Tool Discovery Filtering**: Filters `tools/list` responses so Claude only sees allowed tools

This means if a tool isn't in your allowlist, Claude won't even know it exists!

## Troubleshooting

### Common Issues:

1. **"Watchgate command not found"**
   - Ensure Watchgate is properly installed: `uv add watchgate` (or `pip install watchgate`)
   - Verify installation: `watchgate --help`
   - Check your PATH includes the Python scripts directory

2. **"Command 'uv' not found"**
   - Install the uv tool: Visit [uv installation guide](https://github.com/astral-sh/uv) for platform-specific instructions
   - Alternative: Use pip instead: `pip install watchgate`

3. **"Command 'npx' not found"**
   - Install Node.js which includes npx: Visit [nodejs.org](https://nodejs.org/) for installation instructions
   - Verify installation: `npx --version`

4. **"Claude Desktop not connecting"**
   - Verify the configuration file path and JSON syntax
   - Restart Claude Desktop after configuration changes
   - Check that Watchgate is running with: `watchgate --config watchgate-config.yaml --verbose`

### Debugging Steps:

1. **Check Watchgate status:**
   ```bash
   watchgate --config watchgate-config.yaml --verbose
   ```

2. **Verify filesystem server directly:**
   ```bash
   npx @modelcontextprotocol/server-filesystem ./claude-sandbox/
   ```

3. **Test configuration loading:**
   ```bash
   watchgate debug plugins --validate-priorities --config watchgate-config.yaml
   ```

## Next Steps

Now that you have a working setup, you can explore these additional capabilities:

### Audit Logging

Add comprehensive audit logging to monitor all tool usage:

- **Complete MCP Communication Logs**: Track every request and response
- **Security Event Monitoring**: Log blocked tools and policy violations
- **Multiple Log Formats**: Simple text, JSON, or detailed formats

See the [Implementing Audit Logging](implementing-audit-logging.md) tutorial for detailed instructions.

### Resource-Level Security

Now that you have tool-level security working, consider adding resource-level access control:

- **Content Access Control Plugin**: Control which files and directories can be accessed
- **Pattern-Based Control**: Use gitignore-style patterns for fine-grained access control
- **Defense in Depth**: Combine tool access control with content access control for comprehensive security

See the [Protecting Sensitive Content](protecting-sensitive-content.md) tutorial for detailed instructions.

### Advanced Configuration:

1. **Explore other MCP servers** like web search, database connections, or API integrations
2. **Add custom plugins** for specialized security or auditing needs  
3. **Set up multiple Watchgate instances** for different use cases
4. **Environment-specific configurations** for development vs production

For more advanced configuration options and plugin development, see the [Configuration Reference](../reference/configuration-reference.md).

## Support

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting Guide](../reference/troubleshooting.md)
2. Review the documentation in the [Reference](../reference/) section
3. File an issue on the Watchgate GitHub repository
