# Multi-Plugin Security

*[Home](../../../README.md) → [User Documentation](../../README.md) → [Tutorials](../README.md) → Multi-Plugin Security*

This tutorial will teach you how to combine multiple Watchgate security plugins to create a comprehensive defense-in-depth security strategy. You'll learn to layer tool access control, content access control, and audit logging using the filesystem MCP server as a practical example.

## What You'll Accomplish

Individual security controls are powerful, but combining multiple layers creates far more robust protection. A single security control can have gaps or be bypassed, but a properly configured defense-in-depth strategy ensures that even if one layer fails, others remain in place to protect your system.

In this tutorial, you'll learn how to implement a comprehensive multi-layer security strategy using Watchgate. By the end, you'll have:

- **Layered security controls**: Multiple independent security checks that work together
- **Plugin priority understanding**: Knowledge of how security plugins execute in order
- **Complete audit visibility**: Comprehensive logging of all security decisions and actions
- **Production-ready security**: A robust configuration suitable for real-world deployment

This approach provides maximum protection by ensuring that threats must bypass multiple security layers to succeed, making your AI agent interactions highly secure.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Defense in Depth Concept](#defense-in-depth-concept)
3. [Verify Watchgate Installation](#verify-watchgate-installation)
4. [Configure Multi-Layer Security](#configure-multi-layer-security)
5. [Configure Claude Desktop](#configure-claude-desktop)
6. [Test Your Multi-Layer Security Setup](#test-your-multi-layer-security-setup)
7. [Understanding Multi-Plugin Logs](#understanding-multi-plugin-logs)
8. [Plugin Priority and Ordering](#plugin-priority-and-ordering)
9. [Multi-Layer Configuration Examples](#multi-layer-configuration-examples)
10. [Troubleshooting](#troubleshooting)
11. [Next Steps](#next-steps)

## Prerequisites

Before you begin, ensure you have:

- **Claude Desktop** installed on your system
- **Python** (version 3.11 or higher) for Watchgate
- **Node.js and npm** for running the MCP filesystem server
- **uv** tool for Watchgate installation
- Completed the [Securing Tool Access](1-securing-tool-access.md) tutorial
- Completed the [Protecting Sensitive Content](3-protecting-sensitive-content.md) tutorial

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

## Defense in Depth Concept

Defense in depth uses multiple layers of security controls to protect against different types of threats. Each layer provides independent protection, so even if one layer fails, others remain effective:

1. **Tool Access Control**: Controls which tools/functions can be executed (first line of defense)
2. **Content Access Control**: Controls which files/resources can be accessed (second line of defense)  
3. **Audit Logging**: Monitors and logs all activities for compliance and forensics (visibility layer)
4. **Plugin Priority**: Ensures security checks happen in the correct order (coordination layer)

This layered approach means that an attacker or misconfigured AI agent would need to bypass multiple independent security controls to access restricted resources.

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

## Configure Multi-Layer Security

We'll use the provided configuration file that demonstrates multiple security layers working together.

1. **Understanding the configuration**:

   The tutorial uses the configuration file at `configs/tutorials/4-multi-plugin-security.yaml`, which contains:

   ```yaml
   # Multi-Layer Security Configuration for Watchgate
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
       # Layer 1: Tool Access Control (High Priority)
       - policy: "tool_allowlist"
         enabled: true
         priority: 10  # Execute first (lower numbers = higher priority)
         config:
           # "allowlist" mode: only specified tools are permitted
           mode: "allowlist"
           tools:
             # List of filesystem operations that Claude is allowed to use
             - "read_file"        # Read file contents
             - "write_file"       # Create or modify files
             - "create_directory" # Create new directories
             - "list_directory"   # List directory contents
             - "search_files"     # Search for files by name/pattern
           # Message shown when a blocked tool is attempted
           block_message: "Tool access denied by security policy"
       
       # Layer 2: Content Access Control (Medium Priority)  
       - policy: "content_access_control"
         enabled: true
         priority: 20  # Execute after tool control (higher number = lower priority)
         config:
           # "allowlist" mode: only specified resources are accessible
           mode: "allowlist"
           resources:
             # List of file patterns that Claude is allowed to access
             - "public/**/*"         # Allow all files in public directory tree
             - "docs/**/*.md"        # Allow markdown files in docs directory tree
             - "config/*.json"       # Allow JSON config files
             - "temp/*.txt"          # Allow text files in temp directory
             - "!**/.env*"          # Block all environment files (secrets)
             - "!**/secrets/*"      # Block any directory named 'secrets'
             - "!**/*.key"          # Block all key files
           # Message shown when a blocked resource is attempted
           block_message: "Resource access denied by content security policy"

     # Comprehensive audit logging (Highest Priority)
     auditing:
       - policy: "file_auditing"
         enabled: true
         priority: 5   # Execute first to capture everything (highest priority)
         config:
           output_file: "logs/security-audit.log"
           # Use "detailed" format for comprehensive security information
           format: "detailed"
           # Log "all" events to capture complete audit trail
           mode: "all"
           # Configure log rotation to prevent disk space issues
           max_file_size_mb: 50
           backup_count: 10
   ```

   **Key Points:**
   - **Layer 1**: Tool access control (priority 10) - Controls which tools are available
   - **Layer 2**: Content access control (priority 20) - Controls which files can be accessed
   - **Audit Layer**: File auditing (priority 5) - Captures everything for security monitoring
   - **Priority System**: Lower numbers execute first, allowing fine-grained control
   - **Comprehensive Logging**: Detailed format captures complete security information

2. **Create the secure workspace directory structure**:

   ```bash
   # Create main workspace directory (using home directory for predictable paths)
   mkdir ~/secure-workspace
   
   # Create public directory with sample files (ALLOWED)
   mkdir -p ~/secure-workspace/public
   echo "Welcome to the public area!" > ~/secure-workspace/public/readme.txt
   echo "Public project info" > ~/secure-workspace/public/project-info.txt
   
   # Create docs directory with markdown files (ALLOWED)
   mkdir -p ~/secure-workspace/docs
   echo "# User Guide" > ~/secure-workspace/docs/user-guide.md
   echo "# API Reference" > ~/secure-workspace/docs/api-reference.md
   
   # Create config directory with JSON files (ALLOWED)
   mkdir -p ~/secure-workspace/config
   echo '{"app": "demo", "debug": false}' > ~/secure-workspace/config/app.json
   
   # Create temp directory with text files (ALLOWED)
   mkdir -p ~/secure-workspace/temp
   echo "Temporary data" > ~/secure-workspace/temp/cache.txt
   
   # Create sensitive directories that should be BLOCKED
   mkdir -p ~/secure-workspace/secrets
   echo "super-secret-password" > ~/secure-workspace/secrets/password.txt
   echo "SECRET_KEY=abc123" > ~/secure-workspace/.env
   echo "private-key-data" > ~/secure-workspace/private.key
   
   # Create logs directory for audit logs
   mkdir logs
   ```

   **Note**: We use `~/secure-workspace/` (in your home directory) to ensure a predictable absolute path. If you prefer a different location, update the `command:` line in the configuration file to point to your chosen directory.

## Configure Claude Desktop

Configure Claude Desktop to use Watchgate as a proxy with multi-layer security enabled.

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
    "filesystem-multilayer-security": {
      "command": "<watchgate_root>/watchgate",
      "args": [
        "--config", "<watchgate_root>/configs/tutorials/4-multi-plugin-security.yaml"
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

## Test Your Multi-Layer Security Setup

Now let's systematically test each security layer to understand how they work together.

### 1. Test Successful Operations (All Layers Allow)

- Launch Claude Desktop and start a new conversation
- Test with: "Can you list the files in the public directory?"
- Test with: "Please read the contents of public/readme.txt"
- Test with: "Can you show me the user guide from the docs directory?"
- Test with: "What's in the config/app.json file?"

**Expected Result**: ✅ Success - Both tool access control and content access control allow these operations.

### 2. Test Tool Access Control (First Layer)

Try operations with tools that aren't in the allowlist:

- Test with: "Can you delete the file public/readme.txt?"
- Test with: "Can you move the file public/readme.txt to public/old-readme.txt?"

**Expected Result**: ❌ Blocked by tool access control - `delete_file` and `move_file` tools are not in the allowlist.

### 3. Test Content Access Control (Second Layer)

Try operations with allowed tools but blocked resources:

- Test with: "Can you read the file secrets/password.txt?"
- Test with: "What's in the .env file?"
- Test with: "Please show me the contents of private.key"

**Expected Result**: ❌ Blocked by content access control - These resources match the negation patterns.

### 4. Test Discovery Filtering

Test how the security layers filter what Claude can see:

- Test with: "What tools are available to you?"
- Test with: "What files and directories can you see?"

**Expected Results**: 
- Claude only sees allowed tools (read_file, write_file, create_directory, list_directory, search_files)
- Claude only sees allowed resources (public/, docs/, config/, temp/ but not secrets/, .env, *.key files)

### 5. Monitor Your Security Audit Logs

```bash
# View the comprehensive audit log
tail -f logs/security-audit.log

# Look for specific types of events
grep "SECURITY_CHECK" logs/security-audit.log | head -10
grep "SECURITY_BLOCK" logs/security-audit.log
```

**What happens behind the scenes**: When you start a conversation, Watchgate loads all security plugins and audit logging. You should see output similar to:

```
[INFO] watchgate.main: Loading configuration from watchgate-multilayer-config.yaml
[INFO] watchgate.main: Starting Watchgate MCP Gateway
[INFO] watchgate.plugins.manager: Loaded security plugin: tool_allowlist (priority: 10)
[INFO] watchgate.plugins.manager: Loaded security plugin: content_access_control (priority: 20)
[INFO] watchgate.plugins.manager: Loaded auditing plugin: file_auditing (priority: 5)
[INFO] watchgate.proxy.server: Connected to upstream server
[INFO] watchgate.proxy.server: MCPProxy now accepting client connections
```

## Understanding Multi-Plugin Logs

With detailed audit logging enabled, you get comprehensive visibility into how each security layer processes requests. Here's how to interpret the different types of log entries:

### Successful Request (All Layers Allow)
```
[2024-06-16 10:30:15.123] REQUEST_ID=123 EVENT=TOOL_CALL TOOL=read_file PARAMS={"path": "public/readme.txt"}
[2024-06-16 10:30:15.125] REQUEST_ID=123 SECURITY_CHECK=tool_allowlist RESULT=ALLOW REASON="tool in allowlist"
[2024-06-16 10:30:15.127] REQUEST_ID=123 SECURITY_CHECK=content_access_control RESULT=ALLOW REASON="resource matches pattern: public/**/*"
[2024-06-16 10:30:15.130] REQUEST_ID=123 EVENT=TOOL_RESULT STATUS=SUCCESS DURATION=0.007s
```

**This shows**:
- The original request and parameters
- Each security plugin's decision and reasoning
- The final successful result
- Complete timing information

### Blocked Request (Tool Access Control - First Layer)
```
[2024-06-16 10:31:20.456] REQUEST_ID=124 EVENT=TOOL_CALL TOOL=delete_file PARAMS={"path": "public/readme.txt"}
[2024-06-16 10:31:20.458] REQUEST_ID=124 SECURITY_CHECK=tool_allowlist RESULT=BLOCK REASON="tool not in allowlist"
[2024-06-16 10:31:20.460] REQUEST_ID=124 EVENT=SECURITY_BLOCK BLOCKED_BY=tool_allowlist MESSAGE="Tool access denied by security policy"
```

**This shows**:
- The request was blocked at the first security layer (tool access control)
- Content access control never executed because tool access control blocked it first
- The specific reason for the block

### Blocked Request (Content Access Control - Second Layer)
```
[2024-06-16 10:32:30.789] REQUEST_ID=125 EVENT=TOOL_CALL TOOL=read_file PARAMS={"path": "secrets/password.txt"}
[2024-06-16 10:32:30.791] REQUEST_ID=125 SECURITY_CHECK=tool_allowlist RESULT=ALLOW REASON="tool in allowlist"
[2024-06-16 10:32:30.793] REQUEST_ID=125 SECURITY_CHECK=content_access_control RESULT=BLOCK REASON="resource blocked by pattern: !**/secrets/*"
[2024-06-16 10:32:30.795] REQUEST_ID=125 EVENT=SECURITY_BLOCK BLOCKED_BY=content_access_control MESSAGE="Resource access denied by content security policy"
```

**This shows**:
- The tool was allowed by the first layer (tool access control)
- The resource was blocked by the second layer (content access control)
- The specific pattern that caused the block

## Plugin Priority and Ordering

Understanding plugin execution order is crucial for effective multi-layer security:

### Security Plugin Execution Order

Security plugins execute in priority order (lower numbers = higher priority) and **stop on first denial**:

1. **Priority 5**: Audit logging captures the incoming request
2. **Priority 10**: Tool Access Control checks if the tool is allowed
3. **Priority 20**: Content Access Control checks if the resource is allowed (only if tool was allowed)
4. If any security plugin denies access, execution stops and the request is blocked

### Auditing Plugin Execution

Auditing plugins execute in priority order but **all plugins execute** regardless of security decisions:

1. **Priority 5**: Audit logging captures the request and all security decisions
2. This ensures complete audit trails even for blocked requests

### Example Execution Flow

For a request to read `secrets/password.txt`:

1. **Audit Logger** (Priority 5): Logs the incoming request
2. **Tool Access Control** (Priority 10): Checks if `read_file` is allowed → ✅ ALLOW
3. **Content Access Control** (Priority 20): Checks if `secrets/password.txt` is allowed → ❌ BLOCK
4. **Result**: Request blocked by content access control
5. **Audit Logger**: Logs the final decision and which plugin blocked it

## Multi-Layer Configuration Examples

Here are practical configurations for different environments:

### High Security Environment
```yaml
# Maximum security for production environments
plugins:
  security:
    - policy: "tool_allowlist"
      priority: 10
      config:
        mode: "allowlist"
        tools: ["read_file", "list_directory"]  # Very restrictive
        
    - policy: "content_access_control"
      priority: 20
      config:
        mode: "allowlist"
        resources:
          - "public/docs/*.md"    # Only specific documentation
          - "!**/*"               # Block everything else by default
          
  auditing:
    - policy: "file_auditing"
      priority: 5
      config:
        file: "/var/log/watchgate/security.log"
        format: "json"
        mode: "all"
```

### Development Environment
```yaml
# Balanced security for development work
plugins:
  security:
    - policy: "tool_allowlist"
      priority: 10
      config:
        mode: "blocklist"
        tools: ["execute_command", "system_call"]  # Block dangerous tools only
        
    - policy: "content_access_control"
      priority: 20
      config:
        mode: "blocklist"
        resources:
          - "secrets/*"
          - ".env*"
          - "*.key"
          - "private/*"
          
  auditing:
    - policy: "file_auditing"
      priority: 5
      config:
        file: "logs/dev-audit.log"
        format: "simple"
        mode: "critical"  # Only log security events
```

### Staging Environment
```yaml
# Production-like security with detailed logging
plugins:
  security:
    - policy: "tool_allowlist"
      priority: 10
      config:
        mode: "allowlist"
        tools:
          - "read_file"
          - "write_file"
          - "create_directory"
          - "list_directory"
          - "search_files"
          - "move_file"
          
    - policy: "content_access_control"
      priority: 20
      config:
        mode: "allowlist"
        resources:
          - "public/**/*"
          - "docs/**/*"
          - "config/*.json"
          - "staging-data/**/*"
          - "!**/secrets/*"
          - "!**/.env*"
          
  auditing:
    - policy: "file_auditing"
      priority: 5
      config:
        file: "logs/staging-audit.log"
        format: "detailed"
        mode: "all"
        max_file_size_mb: 25
        backup_count: 5
```

### @modelcontextprotocol/server-filesystem Security
```yaml
# Comprehensive filesystem security with multiple layers
plugins:
  security:
    - policy: "tool_allowlist"
      priority: 10
      config:
        mode: "allowlist"
        tools: ["read_file", "write_file", "list_directory", "search_files"]
        
    - policy: "filesystem_server_security"
      priority: 20
      config:
        read: ["docs/**/*", "src/**/*.py", "!docs/internal/*"]
        write: ["drafts/**/*", "output/**/*", "temp/**/*"]
        
    - policy: "content_access_control" 
      priority: 30
      config:
        mode: "blocklist"
        resources: ["**/*.env*", "**/secrets/*", "**/*.key"]
        
  auditing:
    - policy: "file_auditing"
      priority: 5
      config:
        file: "logs/filesystem-audit.log"
        format: "json"
        mode: "all"
```

## Troubleshooting

### Common Issues:

1. **"Unexpected security blocks"**
   - Check plugin priorities - wrong order can cause unexpected behavior
   - Review both tool and content patterns for conflicts
   - Use verbose logging to see which plugin is blocking requests
   - Test each plugin individually before combining them

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
   - Check that Watchgate is running with: `watchgate --config watchgate-multilayer-config.yaml --verbose`

5. **"Some operations not being logged"**
   - Ensure audit plugin has higher priority (lower number) than security plugins
   - Check audit plugin `mode` setting (use "all" to capture everything)
   - Verify log file permissions and disk space
   - Check that the auditing plugin is enabled: `enabled: true`

6. **"Performance issues with complex patterns"**
   - Complex content patterns can be slow - simplify patterns where possible
   - Reduce audit logging verbosity for high-traffic environments
   - Use `mode: "security_only"` for auditing in production if full logging isn't needed

7. **"Configuration conflicts between plugins"**
   - Plugin configurations can interact in unexpected ways
   - Test configurations in isolation first
   - Use configuration validation: `watchgate debug plugins --validate-priorities`

### Debugging Steps:

1. **Test plugins individually first**:
   ```bash
   # Test with only tool access control
   watchgate --config tool-only-config.yaml --verbose
   
   # Test with only content access control  
   watchgate --config content-only-config.yaml --verbose
   ```

2. **Check plugin loading order and priorities**:
   ```bash
   watchgate debug plugins --validate-priorities --config watchgate-multilayer-config.yaml
   ```

3. **Analyze audit logs for patterns**:
   ```bash
   # Find what's being blocked most often
   grep "SECURITY_BLOCK" logs/security-audit.log | cut -d' ' -f8 | sort | uniq -c
   
   # See plugin execution order in action
   grep "SECURITY_CHECK" logs/security-audit.log | head -20
   
   # Monitor real-time security events
   tail -f logs/security-audit.log | grep "SECURITY_BLOCK"
   ```

## Next Steps

Now that you have comprehensive multi-layer security working, you can explore these advanced capabilities:

### Production Deployment

For deploying multi-layer security in production:

- **Environment-Specific Configurations**: Create separate configs for development, staging, and production
- **Security Monitoring**: Set up automated alerts for repeated security blocks (potential attacks)
- **Policy Management**: Establish processes for reviewing and updating security policies
- **Performance Tuning**: Optimize patterns and logging levels for production workloads

### Advanced Security Strategies

Consider implementing these advanced security patterns:

- **Time-Based Security**: More restrictive policies during off-hours
- **Context-Aware Policies**: Different rules based on the type of work being performed
- **Dynamic Policy Updates**: Systems that can adjust security policies based on threat intelligence

### Integration and Monitoring

For enterprise environments:

1. **Log Aggregation**: Send audit logs to centralized logging systems (ELK, Splunk, etc.)
2. **Real-time Monitoring**: Set up dashboards for security events and trends
3. **Compliance Integration**: Structure logs and policies to meet regulatory requirements
4. **Automated Response**: Create workflows that respond to repeated security violations

For more advanced configuration options and security strategies, see the [Configuration Reference](../reference/configuration-reference.md).

## Support

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting Guide](../reference/troubleshooting.md)
2. Review the documentation in the [Reference](../reference/) section
3. File an issue on the Watchgate GitHub repository
