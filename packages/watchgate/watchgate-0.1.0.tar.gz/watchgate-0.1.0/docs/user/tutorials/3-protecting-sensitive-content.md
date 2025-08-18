# Protecting Sensitive Content

*[Home](../../../README.md) → [User Documentation](../../README.md) → [Tutorials](../README.md) → Protecting Sensitive Content*

This tutorial will teach you how to set up fine-grained file and directory access control using Watchgate's `content_access_control` plugin. You'll learn to create secure resource boundaries that complement tool-level security for comprehensive protection.

## What You'll Accomplish

Even when you control which tools Claude can use, it's crucial to control which files and directories those tools can access. Without content access control, an AI agent with file access could potentially read sensitive configuration files, private documents, or system files - even if it's only allowed to use "safe" tools like `read_file`.

In this tutorial, you'll learn how to implement Watchgate's content access control to create secure resource boundaries. By the end, you'll have:

- **Fine-grained file access control**: Precise control over which files Claude can read or modify
- **Pattern-based resource filtering**: Use powerful gitignore-style patterns for flexible access rules
- **Defense in depth security**: Resource-level protection that works alongside tool access control
- **Comprehensive audit visibility**: Full logging of both allowed and blocked resource access attempts

This approach ensures that even if Claude has access to powerful tools, it can only use them on the files and directories you explicitly authorize.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Verify Watchgate Installation](#verify-watchgate-installation)
3. [Filesystem MCP Server](#filesystem-mcp-server)
4. [Configure Watchgate with Content Access Control](#configure-watchgate-with-content-access-control)
5. [Configure Claude Desktop](#configure-claude-desktop)
6. [Test Your Content Access Control Setup](#test-your-content-access-control-setup)
7. [Understanding Your Access Control Logs](#understanding-your-access-control-logs)
8. [Pattern Matching Guide](#pattern-matching-guide)
9. [Content Access Control Configuration Options](#content-access-control-configuration-options)
10. [Troubleshooting](#troubleshooting)
11. [Next Steps](#next-steps)

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

The filesystem MCP server allows Claude to read and write files in specified directories. We'll use this as our example to demonstrate content access control with real file operations. No installation is needed - Watchgate will automatically run it using `npx` when you start the proxy.

## Configure Watchgate with Content Access Control

We'll use the provided configuration file that includes content access control to protect sensitive files and directories.

1. **Understanding the configuration**:

   The tutorial uses the configuration file at `configs/tutorials/3-protecting-sensitive-content.yaml`, which contains:

   ```yaml
   # Watchgate Configuration for Content Access Control
   proxy:
     # How Watchgate communicates with the MCP server (stdio = command-line interface)
     transport: stdio
     upstream:
       # This starts the filesystem MCP server using npx (Node.js package runner)
       # @modelcontextprotocol/server-filesystem is the official filesystem server
       # ~/secure-workspace/ is the directory the filesystem server will operate within
       command: "npx @modelcontextprotocol/server-filesystem ~/secure-workspace/"

   plugins:
     security:
       # Enable the content access control plugin for resource-level security
       - policy: "content_access_control"
         enabled: true
         config:
           # "allowlist" mode: only specified resources are accessible (most secure)
           # Other options: "blocklist" (block specific resources), "allow_all" (no restrictions)
           mode: "allowlist"
           resources:
             # List of file patterns that Claude is allowed to access
             # These are the only files/directories Claude can read from or write to
             - "public/**/*"      # Allow all files in public directory tree
             - "docs/**/*.md"     # Allow markdown files in docs directory tree
             - "config/*.json"    # Allow JSON config files
             - "!**/.env*"        # Block all environment files (secrets)
             - "!**/secrets/*"    # Block any directory named 'secrets'
             - "!**/*.key"        # Block all key files
           # Message shown when a blocked resource is attempted
           block_message: "Resource access denied by content security policy"

     # Optional: Include audit logging to monitor access attempts
     auditing:
       - policy: "file_auditing"
         enabled: true
         config:
           output_file: "logs/content-audit.log"
           format: "simple"
           mode: "all"
   ```

   **Key Points:**
   - **Security Mode**: `allowlist` restricts access to only specified resource patterns
   - **Resource Patterns**: Uses glob patterns to define allowed files and directories
   - **Exclusion Rules**: `!` prefix blocks specific patterns (secrets, environment files, keys)
   - **Audit Integration**: Logs all access attempts for security monitoring
   - **Workspace Directory**: Filesystem server operates within `~/secure-workspace/` directory

2. **Create the secure workspace directory structure**:

   ```bash
   # Create main workspace directory (using home directory for predictable paths)
   mkdir ~/secure-workspace
   
   # Create public directory with sample files
   mkdir -p ~/secure-workspace/public
   echo "Welcome to the public area!" > ~/secure-workspace/public/readme.txt
   echo "Public project info" > ~/secure-workspace/public/project-info.txt
   
   # Create docs directory with markdown files
   mkdir -p ~/secure-workspace/docs
   echo "# User Guide" > ~/secure-workspace/docs/user-guide.md
   echo "# API Reference" > ~/secure-workspace/docs/api-reference.md
   
   # Create config directory with JSON files
   mkdir -p ~/secure-workspace/config
   echo '{"app": "demo", "debug": false}' > ~/secure-workspace/config/app.json
   
   # Create sensitive directories that should be blocked
   mkdir -p ~/secure-workspace/secrets
   echo "super-secret-password" > ~/secure-workspace/secrets/password.txt
   echo "SECRET_KEY=abc123" > ~/secure-workspace/.env
   echo "private-key-data" > ~/secure-workspace/private.key
   
   # Create logs directory for audit logs
   mkdir logs
   ```

   **Note**: We use `~/secure-workspace/` (in your home directory) to ensure a predictable absolute path. If you prefer a different location, update the `command:` line in the configuration file to point to your chosen directory.

## Configure Claude Desktop

Configure Claude Desktop to use Watchgate as a proxy to the filesystem MCP server with content access control enabled.

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
    "filesystem-with-content-control": {
      "command": "<watchgate_root>/watchgate",
      "args": [
        "--config", "<watchgate_root>/configs/tutorials/3-protecting-sensitive-content.yaml"
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

## Test Your Content Access Control Setup

Now let's test that content access control is working correctly by attempting to access both allowed and blocked resources.

1. **Test allowed resource access**:
   
   - Launch Claude Desktop and start a new conversation
   - Test with: "Can you list all the available files and directories?"
   - Test with: "Please read the contents of public/readme.txt"
   - Test with: "Can you show me the user guide from the docs directory?"
   - Test with: "What's in the config/app.json file?"

   **What happens behind the scenes**: When you start a conversation, Claude Desktop automatically launches Watchgate with your configuration. Watchgate will show output similar to this in its logs:
   
   ```
   [INFO] watchgate.main: Loading configuration from watchgate-content-config.yaml
   [INFO] watchgate.main: Starting Watchgate MCP Gateway
   [INFO] watchgate.plugins.manager: Loaded security plugin: content_access_control
   [INFO] watchgate.plugins.manager: Loaded auditing plugin: file_auditing
   [INFO] watchgate.proxy.server: Connected to upstream server
   [INFO] watchgate.proxy.server: MCPProxy now accepting client connections
   ```

2. **Test blocked resource access**:

   - Test with: "Can you read the file secrets/password.txt?"
   - Test with: "What's in the .env file?"
   - Test with: "Please show me the contents of private.key"

   These should be blocked by the content access control policy.

3. **Check your audit logs**:

   ```bash
   # View the audit log to see both allowed and blocked access attempts
   cat logs/content-audit.log
   
   # Follow the log in real-time as you test
   tail -f logs/content-audit.log
   ```

   You should see entries like:
   ```
   2024-06-16 10:30:15 - RESOURCE_READ - public/readme.txt - ALLOWED (allowlist match: public/**/*) 
   2024-06-16 10:30:45 - RESOURCE_READ - secrets/password.txt - BLOCKED (allowlist no match)
   2024-06-16 10:31:20 - RESOURCE_READ - .env - BLOCKED (negation pattern match: !**/.env*)
   ```

## Understanding Your Access Control Logs

Your content access control logs provide detailed visibility into resource access patterns and security decisions:

### Successful Access (Allowed)
```
2024-06-16 10:30:15 - RESOURCE_READ - public/readme.txt - ALLOWED (allowlist match: public/**/*) 
2024-06-16 10:30:16 - RESOURCE_LIST - docs/ - FILTERED (3 resources shown, 1 hidden)
2024-06-16 10:30:25 - RESOURCE_READ - config/app.json - ALLOWED (allowlist match: config/*.json)
```

This shows:
- **Timestamp**: When the resource access occurred
- **Operation Type**: `RESOURCE_READ` (file content) or `RESOURCE_LIST` (directory listing)
- **Resource Path**: The specific file or directory accessed
- **Decision**: `ALLOWED` with the matching pattern or `FILTERED` for partial results
- **Reason**: Which allowlist pattern permitted the access

### Blocked Access
```
2024-06-16 10:31:20 - RESOURCE_READ - secrets/password.txt - BLOCKED (allowlist no match)
2024-06-16 10:31:25 - RESOURCE_READ - .env - BLOCKED (negation pattern match: !**/.env*)
2024-06-16 10:31:30 - RESOURCE_READ - private.key - BLOCKED (negation pattern match: !**/*.key)
```

This shows:
- **Blocked Operations**: When Claude attempts to access restricted resources
- **Block Reason**: Why the access was denied (no allowlist match or negation pattern)
- **Security Effectiveness**: Proof that your content controls are working

### Pattern Matching Details
```
Resource allowlist filtered resources/list response: original=10 resources, 
filtered=6 resources, blocked=['secrets/password.txt', '.env', 'private.key'], 
allowed_patterns=['public/**/*', 'docs/**/*.md', 'config/*.json'], mode=allowlist, request_id=456
```

This shows how resource listing operations are filtered to hide blocked resources from Claude's view.

## Pattern Matching Guide

The content access control uses gitignore-style pattern matching:

### Basic Patterns

| Pattern | Matches | Example |
|---------|---------|---------|
| `file.txt` | Exact file | `file.txt` |
| `*.txt` | All .txt files | `readme.txt`, `notes.txt` |
| `dir/*` | Files in directory | `public/file.txt` |
| `dir/*/` | Subdirectories only | `public/images/`, `public/docs/` |

### Advanced Patterns

| Pattern | Matches | Example |
|---------|---------|---------|
| `dir/**/*` | All files recursively | `docs/guide.md`, `docs/api/ref.md` |
| `**/file.txt` | file.txt anywhere | `file.txt`, `some/path/file.txt` |
| `!pattern` | Negation (exclude) | `!sensitive/*` excludes sensitive dir |
| `dir/[abc]*` | Bracket expressions | `dir/apple`, `dir/banana` |

### Pattern Examples

```yaml
resources:
  # Allow specific file types
  - "*.md"              # All markdown files
  - "*.json"            # All JSON files
  - "*.txt"             # All text files
  
  # Directory patterns
  - "public/**/*"       # Everything in public tree
  - "docs/*/README.md"  # README.md in any docs subdirectory
  - "config/*.json"     # JSON files in config directory
  
  # Negation patterns (exclusions)
  - "!**/.*"           # Exclude all hidden files
  - "!**/*.key"        # Exclude all key files
  - "!temp/*"          # Exclude temp directory
  - "!*/sensitive/*"   # Exclude sensitive subdirectories
```

## Content Access Control Configuration Options

The `content_access_control` plugin supports several configuration modes to meet different security requirements:

### Allowlist Mode (Most Restrictive)
```yaml
config:
  mode: "allowlist"
  resources:
    - "public/**/*"
    - "docs/**/*.md"
    - "config/*.json"
    - "!**/.env*"     # Exclude environment files
    - "!**/secrets/*" # Exclude secrets directories
  # Only specified resources are accessible
```

**Use case**: Production environments where you want precise control over accessible resources.

### Blocklist Mode (Less Restrictive)
```yaml
config:
  mode: "blocklist"
  resources:
    - "secrets/*"     # Block secrets directory
    - "*.key"         # Block all key files
    - "admin/**/*"    # Block admin directory tree
    - ".env*"         # Block environment files
  # All resources allowed except specified ones
```

**Use case**: Development environments where you want mostly open access with specific restrictions.

### Allow All Mode (No Restrictions)
```yaml
config:
  mode: "allow_all"
  # All resources are accessible (useful for development)
```

**Use case**: Development and testing environments where you need unrestricted access.

### How Content Access Control Works

The content access control plugin provides dual protection:

1. **Resource Access Filtering**: Blocks `resources/read` requests for disallowed resources
2. **Resource Discovery Filtering**: Filters `resources/list` responses so Claude only sees allowed resources

This means if a resource isn't in your allowlist, Claude won't even know it exists!

## Troubleshooting

### Common Issues:

1. **"All resources are blocked"**
   - Check your patterns are correct (case-sensitive)
   - Verify `mode` is set to the intended value (`allowlist`, `blocklist`, or `allow_all`)
   - Use `mode: "allow_all"` temporarily to debug pattern issues
   - Check for typos in pattern syntax

2. **"Watchgate command not found"**
   - Ensure Watchgate is properly installed: `uv add watchgate` (or `pip install watchgate`)
   - Verify installation: `watchgate --help`
   - Check your PATH includes the Python scripts directory

3. **"Command 'npx' not found"**
   - Install Node.js which includes npx: Visit [nodejs.org](https://nodejs.org/) for installation instructions
   - Verify installation: `npx --version`

4. **"Claude Desktop not connecting"**
   - Verify the configuration file path and JSON syntax
   - Restart Claude Desktop after configuration changes
   - Check that Watchgate is running with: `watchgate --config watchgate-content-config.yaml --verbose`

5. **"Resources not being filtered"**
   - Ensure the plugin is enabled: `enabled: true`
   - Check the plugin policy name: `policy: "content_access_control"`
   - Verify your MCP server actually provides resource operations
   - Look for error messages in verbose logs

6. **"Patterns not matching as expected"**
   - Test patterns with specific examples
   - Remember patterns are case-sensitive
   - Use `**` for recursive directory matching
   - Check negation pattern order (more specific patterns should come after general ones)

7. **"Negation patterns not working"**
   - Ensure negation patterns (`!pattern`) come after the positive patterns they're meant to exclude
   - Example: `["public/**/*", "!public/sensitive/*"]` not `["!public/sensitive/*", "public/**/*"]`

### Debugging Steps:

1. **Test content access control is working**:
   ```bash
   # Check if audit log shows resource access attempts
   tail -f logs/content-audit.log
   ```

2. **Verify configuration loading**:
   ```bash
   watchgate --config watchgate-content-config.yaml --verbose
   ```

3. **Test filesystem server directly**:
   ```bash
   npx @modelcontextprotocol/server-filesystem ./secure-workspace/
   ```

4. **Use allow_all mode for debugging**:
   ```yaml
   config:
     mode: "allow_all"  # Temporarily allow everything to test MCP server
   ```

## Next Steps

Now that you have content access control working, you can explore these additional capabilities:

### Comprehensive Security Strategy

Combine content access control with other security plugins for defense in depth:

- **Tool Access Control**: Restrict which tools Claude can use in addition to which files it can access
- **Multi-Plugin Security**: Layer multiple security controls for comprehensive protection  
- **Audit Logging**: Monitor all tool usage and resource access attempts

See the [Multi-Plugin Security](4-multi-plugin-security.md) tutorial for detailed instructions on combining multiple security layers.

### Advanced Pattern Strategies

For more sophisticated access control:

- **Environment-Specific Patterns**: Different resource rules for development vs production
- **Role-Based Access**: Tailor resource patterns for different use cases
- **Dynamic Pattern Testing**: Validate your patterns before deploying to production

### Production Considerations

When deploying content access control in production:

1. **Start restrictive and expand**: Begin with tight allowlists and add resources as needed
2. **Monitor audit logs**: Review blocked access attempts to refine your patterns
3. **Test pattern changes**: Validate pattern modifications in staging environments
4. **Document access policies**: Maintain clear documentation of what resources are accessible and why

For more advanced configuration options and pattern examples, see the [Configuration Reference](../reference/configuration-reference.md).

## Support

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting Guide](../reference/troubleshooting.md)
2. Review the documentation in the [Reference](../reference/) section
3. File an issue on the Watchgate GitHub repository
