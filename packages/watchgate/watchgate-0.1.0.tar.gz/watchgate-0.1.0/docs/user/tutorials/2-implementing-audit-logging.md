# Implementing Audit Logging

*[Home](../../../README.md) → [User Documentation](../../README.md) → [Tutorials](../README.md) → Implementing Audit Logging*

This tutorial will teach you how to set up comprehensive audit logging for Watchgate, giving you complete visibility into AI agent behavior and MCP communications. You'll use the popular filesystem MCP server as a practical example while learning how to implement production-ready audit logging.

## What You'll Accomplish

When AI agents have access to powerful tools like file operations, database queries, or API calls, it's crucial to maintain detailed logs of their activities. Without proper audit logging, you can't track what your AI agents are doing, troubleshoot issues, or maintain compliance with security policies.

In this tutorial, you'll learn how to implement Watchgate's audit logging to create comprehensive activity monitoring. By the end, you'll have:

- **Complete MCP communication logs**: Every request, response, and tool call recorded
- **Security event monitoring**: Visibility into blocked operations and policy violations  
- **Production-ready audit trails**: Structured logs suitable for compliance and analysis
- **Log management automation**: Rotation and retention policies to prevent disk space issues

This approach gives you the visibility needed for debugging, security monitoring, compliance, and understanding AI agent behavior patterns.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Verify Watchgate Installation](#verify-watchgate-installation)
3. [Filesystem MCP Server](#filesystem-mcp-server)
4. [Configure Watchgate with Audit Logging](#configure-watchgate-with-audit-logging)
5. [Configure Claude Desktop](#configure-claude-desktop)
6. [Test Your Audit Logging Setup](#test-your-audit-logging-setup)
7. [Understanding Your Audit Logs](#understanding-your-audit-logs)
8. [Log Format and Mode Options](#log-format-and-mode-options)
9. [Log Management and Rotation](#log-management-and-rotation)
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

The filesystem MCP server allows Claude to read and write files in specified directories. No installation is needed - Watchgate will automatically run it using `npx` when you start the proxy. This gives us a concrete example to demonstrate audit logging with real tool operations.

## Configure Watchgate with Audit Logging

We'll use the provided configuration file that includes comprehensive audit logging settings.

1. **Understanding the configuration**:

   The tutorial uses the configuration file at `configs/tutorials/2-implementing-audit-logging.yaml`, which contains:

   ```yaml
   # Watchgate Configuration for Audit Logging
   proxy:
     # How Watchgate communicates with the MCP server (stdio = command-line interface)
     transport: stdio
     upstream:
       # This starts the filesystem MCP server using npx (Node.js package runner)
       # @modelcontextprotocol/server-filesystem is the official filesystem server
       # ~/claude-sandbox/ is the directory the filesystem server will operate within
       command: "npx @modelcontextprotocol/server-filesystem ~/claude-sandbox/"

   plugins:
     # Audit logging configuration
     auditing:
       # Enable the file auditing plugin to log all MCP communications
       - policy: "file_auditing"
         enabled: true
         config:
           # Where to store audit logs (directory will be created if it doesn't exist)
           output_file: "logs/audit.log"
           # Log format: "json" (machine-readable), "line" (human-readable), "debug" (comprehensive), "csv" (spreadsheet-compatible)
           format: "json"
           # Log rotation settings to prevent disk space issues
           max_file_size_mb: 10
           backup_count: 5

     # Optional: Add security controls to demonstrate security event logging
     security:
       - policy: "tool_allowlist"
         enabled: true
         config:
           # "allowlist" mode: only specified tools are permitted
           mode: "allowlist"
           tools:
             - "read_file"
             - "write_file"
             - "create_directory"
             - "list_directory"
             - "search_files"
           block_message: "Tool access denied by security policy"
   ```

   **Key Points:**
   - **Auditing Plugin**: Logs all MCP communications to `logs/audit.log`
   - **Format**: `json` format provides machine-readable audit entries for analysis tools
   - **Log Rotation**: Prevents disk space issues with size limits and backup counts
   - **Security Integration**: Tool access control generates security events for auditing

   > **Note**: This tutorial focuses on **auditing** which logs MCP communications and security decisions. For configuring Watchgate's internal system logs, see the [System Logging Configuration Tutorial](5-logging-configuration.md).

2. **Create the sandbox and logs directories**:

   ```bash
   # Create a directory for Claude to work in (using home directory for predictable paths)
   mkdir ~/claude-sandbox
   
   # Create a directory for audit logs
   mkdir logs
   
   # Add some sample files for testing
   echo "Hello from the sandbox!" > ~/claude-sandbox/readme.txt
   mkdir ~/claude-sandbox/projects
   echo "Project info" > ~/claude-sandbox/projects/info.txt
   ```

   **Note**: We use `~/claude-sandbox/` (in your home directory) to ensure a predictable absolute path. If you prefer a different location, update the `command:` line in the configuration file to point to your chosen directory.

## Configure Claude Desktop

Configure Claude Desktop to use Watchgate as a proxy to the filesystem MCP server with audit logging enabled.

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
    "filesystem-with-audit-logging": {
      "command": "<watchgate_root>/watchgate",
      "args": [
        "--config", "<watchgate_root>/configs/tutorials/2-implementing-audit-logging.yaml"
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

## Test Your Audit Logging Setup

Now let's test that audit logging is working correctly by performing operations and examining the generated logs.

1. **Test the setup with Claude Desktop**:
   
   - Launch Claude Desktop and start a new conversation
   - Test with: "Can you list the files in my sandbox directory?"
   - Test with: "Please create a test file called 'audit-test.txt' with the content 'Testing audit logging!'"
   - Test with: "Can you read the contents of the readme.txt file?"
   - Test a blocked operation (if you included security controls): "Can you delete the readme.txt file?"

   **What happens behind the scenes**: When you start a conversation, Claude Desktop automatically launches Watchgate with your configuration. Watchgate will show output similar to this in its logs:
   
   ```
   [INFO] watchgate.main: Loading configuration from watchgate-audit-config.yaml
   [INFO] watchgate.main: Starting Watchgate MCP Gateway
   [INFO] watchgate.plugins.manager: Loaded auditing plugin: file_auditing
   [INFO] watchgate.plugins.manager: Loaded security plugin: tool_allowlist
   [INFO] watchgate.proxy.server: Connected to upstream server
   [INFO] watchgate.proxy.server: MCPProxy now accepting client connections
   ```

2. **Check your audit logs**:

   ```bash
   # View the audit log to see recorded operations
   cat logs/audit.log
   
   # Follow the log in real-time as you test
   tail -f logs/audit.log
   ```

   You should see entries like:
   ```json
   {"timestamp": "2024-06-16T10:30:15Z", "event_type": "REQUEST", "method": "tools/call", "tool": "list_directory", "status": "ALLOWED", "request_id": "123"}
   {"timestamp": "2024-06-16T10:30:16Z", "event_type": "RESPONSE", "status": "success", "request_id": "123", "duration_ms": 1333}
   {"timestamp": "2024-06-16T10:30:45Z", "event_type": "REQUEST", "method": "tools/call", "tool": "write_file", "status": "ALLOWED", "request_id": "124"}
   {"timestamp": "2024-06-16T10:30:46Z", "event_type": "RESPONSE", "status": "success", "request_id": "124", "duration_ms": 892}
   ```

### Log Format Options

Choose the format that best fits your needs:

#### JSON Format (Default - Machine Readable)
```yaml
config:
  format: "json"
```

Example output:
```json
{"timestamp": "2024-06-16T10:30:15Z", "event_type": "TOOL_CALL", "tool": "list_directory", "params": {"path": "/Users/username/claude-sandbox"}, "request_id": "123"}
{"timestamp": "2024-06-16T10:30:16Z", "event_type": "TOOL_RESULT", "tool": "list_directory", "status": "SUCCESS", "request_id": "123"}
```

**Best for**: Log analysis tools, automated processing, integration with log management systems.

#### Line Format (Human Readable)
```yaml
config:
  format: "line"
```

Example output:
```
2024-06-16 10:30:15 UTC - REQUEST: tools/call - list_directory - ALLOWED
2024-06-16 10:30:16 UTC - RESPONSE: success
2024-06-16 10:30:45 UTC - SECURITY_BLOCK: delete_file - [tool_allowlist] Tool blocked by allowlist policy
```

**Best for**: Manual log review, debugging, and general monitoring.

#### Debug Format (Comprehensive)
```yaml
config:
  format: "debug"
```

Example output:
```
[2024-06-16 10:30:15.123] REQUEST_ID=123 SOURCE=claude_desktop EVENT=TOOL_CALL TOOL=list_directory PARAMS={"path": "/Users/username/claude-sandbox"} SECURITY_CHECKS=["tool_allowlist:ALLOWED"]
[2024-06-16 10:30:16.456] REQUEST_ID=123 SOURCE=filesystem_server EVENT=TOOL_RESULT TOOL=list_directory STATUS=SUCCESS DURATION=1.333s
```

**Best for**: Deep debugging, security analysis, and compliance auditing.

#### CSV Format (Spreadsheet Compatible)
```yaml
config:
  format: "csv"
  output_file: "logs/audit.csv"
  csv_config:
    quote_style: "minimal"
    delimiter: ","
```

Example output:
```csv
timestamp,event_type,method,tool,status,request_id,plugin,reason,duration_ms,server_name
2024-06-16T10:30:15Z,REQUEST,tools/call,list_directory,ALLOWED,123,tool_allowlist,Request approved,,
2024-06-16T10:30:16Z,RESPONSE,,,success,123,,,1333,
2024-06-16T10:30:45Z,SECURITY_BLOCK,tools/call,delete_file,BLOCKED,124,tool_allowlist,Tool blocked by allowlist policy,,
```

**Best for**: Data analysis, spreadsheet import, business intelligence tools, compliance reporting.

## Understanding Your Audit Logs

Your audit logs provide comprehensive visibility into AI agent behavior. Here's how to interpret the different types of log entries:

### Tool Execution Logs
```json
{"timestamp": "2024-06-16T10:30:15Z", "event_type": "REQUEST", "method": "tools/call", "tool": "write_file", "status": "ALLOWED", "request_id": "123", "plugin": "tool_allowlist"}
{"timestamp": "2024-06-16T10:30:16Z", "event_type": "RESPONSE", "status": "success", "request_id": "123", "duration_ms": 892}
```

This shows:
- **Timestamp**: When the operation occurred (ISO 8601 format)
- **Event Type**: `REQUEST` or `RESPONSE`
- **Tool Name**: The specific tool being used
- **Status**: Whether the request was allowed/blocked or response success/error
- **Request ID**: For correlating requests with responses
- **Plugin**: Which security plugin made the decision

### Security Decision Logs
If you have security controls enabled, you'll see entries like:
```json
{"timestamp": "2024-06-16T10:30:45Z", "event_type": "SECURITY_BLOCK", "method": "tools/call", "tool": "delete_file", "reason": "Tool 'delete_file' is not in allowlist", "request_id": "124", "plugin": "tool_allowlist", "plugin_metadata": {"mode": "allowlist"}}
{"timestamp": "2024-06-16T10:30:50Z", "event_type": "TOOLS_FILTERED", "method": "tools/list", "reason": "Filtered 3 tools from response", "plugin": "tool_allowlist", "request_id": "125", "plugin_metadata": {"filtered_count": 3}}
```

This shows:
- **Security Blocks**: When requests are denied by security policies
- **Tool Filtering**: When tools/list responses are filtered
- **Plugin Attribution**: Which plugin made the security decision
- **Policy Context**: The security mode and metadata for analysis

### Protocol Events
```json
{"timestamp": "2024-06-16T10:29:45Z", "event_type": "REQUEST", "method": "initialize", "status": "ALLOWED", "request_id": "1"}
{"timestamp": "2024-06-16T10:29:46Z", "event_type": "RESPONSE", "status": "success", "request_id": "1", "duration_ms": 45}
```

This shows the initial MCP protocol handshake between Claude Desktop and the filesystem server.

## Log Format and Mode Options

The `file_auditing` plugin supports different formats and verbosity levels to meet various needs:

## Log Management and Rotation

Proper log management ensures your audit logs don't consume excessive disk space while retaining the information you need.

### Automatic Log Rotation

Configure automatic log rotation in your Watchgate configuration:

```yaml
plugins:
  auditing:
    - policy: "file_auditing"
      enabled: true
      config:
        output_file: "logs/audit.log"
        format: "simple"
        mode: "all"
        # Rotate when log reaches 10MB
        max_file_size_mb: 10
        # Keep 5 backup files
        backup_count: 5
```

This creates:
- `audit.log` (current log)
- `audit.log.1` (previous log)  
- `audit.log.2` (older log)
- `audit.log.3`, `audit.log.4`, `audit.log.5` (oldest)

### Log Analysis Commands

```bash
# View recent entries in real-time
tail -f logs/audit.log

# Count total requests performed using jq
jq -r 'select(.event_type == "REQUEST") | .event_type' logs/audit.log | wc -l

# Find security events and blocked operations
jq -r 'select(.event_type == "SECURITY_BLOCK" or .event_type == "TOOLS_FILTERED")' logs/audit.log

# Extract usage of specific tools
jq -r 'select(.tool == "write_file")' logs/audit.log

# View logs from a specific time period
jq -r 'select(.timestamp | startswith("2024-06-16"))' logs/audit.log
```

### Useful Analysis Examples

```bash
# Most frequently used tools
jq -r 'select(.event_type == "REQUEST" and .tool) | .tool' logs/audit.log | sort | uniq -c | sort -nr

# Security blocks by tool type
jq -r 'select(.event_type == "SECURITY_BLOCK") | .tool' logs/audit.log | sort | uniq -c

# Operations per hour
jq -r 'select(.event_type == "REQUEST") | .timestamp[0:13]' logs/audit.log | sort | uniq -c

# Average response time
jq -r 'select(.event_type == "RESPONSE" and .duration_ms) | .duration_ms' logs/audit.log | awk '{sum+=$1; count++} END {printf "Average: %.2f ms\n", sum/count}'

# Security plugin activity
jq -r 'select(.plugin) | .plugin' logs/audit.log | sort | uniq -c | sort -nr
```

## Troubleshooting

### Common Issues:

1. **"No audit logs appearing"**
   - Verify the logs directory exists and is writable: `ls -la logs/`
   - Check the `output_file` path in your configuration
   - Ensure the auditing plugin is enabled: `enabled: true`
   - Try `mode: "all"` to capture everything
   - Test with: `watchgate --config watchgate-audit-config.yaml --verbose`

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
   - Check that Watchgate is running with: `watchgate --config watchgate-audit-config.yaml --verbose`

5. **"Logs not rotating"**
   - Check `max_file_size_mb` setting in your configuration
   - Verify disk space is available
   - Ensure Watchgate has write permissions to the log directory

6. **"Too much logging / disk space issues"**
   - Consider using multiple smaller log files instead of one large file
   - Reduce `backup_count` to keep fewer old logs  
   - Decrease `max_file_size_mb` for more frequent rotation
   - Use external log processing to filter events if needed

### Debugging Steps:

1. **Test audit logging is working**:
   ```bash
   # Check if log file is being created and written to
   ls -la logs/
   tail -f logs/audit.log
   ```

2. **Verify configuration loading**:
   ```bash
   watchgate --config watchgate-audit-config.yaml --verbose
   ```

3. **Test filesystem server directly**:
   ```bash
   npx @modelcontextprotocol/server-filesystem ./claude-sandbox/
   ```

4. **Check log permissions**:
   ```bash
   ls -la logs/audit.log
   touch logs/test.log  # Test write permissions
   ```

## Next Steps

Now that you have comprehensive audit logging working, you can explore these additional capabilities:

### Advanced Security Controls

Combine audit logging with security plugins for complete monitoring:

- **Tool Access Control**: Restrict which tools Claude can use and log all blocked attempts
- **Content Access Control**: Control file and directory access with detailed audit trails
- **Defense in Depth**: Layer multiple security controls while maintaining full audit visibility

See the [Securing Tool Access](1-securing-tool-access.md) tutorial for detailed instructions.

### Production Log Management

For production environments, consider these enhancements:

- **Log Aggregation**: Send logs to centralized logging systems (ELK, Splunk, etc.)
- **Real-time Monitoring**: Set up alerts for security events and blocked operations  
- **Log Analysis**: Create dashboards and reports for AI agent behavior patterns
- **Compliance Integration**: Structure logs to meet regulatory and compliance requirements

### Advanced Audit Configuration

1. **Multiple Log Files**: Separate security events from operational logs
2. **Environment-Specific Logging**: Different verbosity for development vs production
3. **Custom Log Formats**: Tailor log output for your specific analysis tools
4. **Integration with Monitoring**: Connect audit logs to your existing observability stack

For more advanced configuration options and plugin development, see the [Configuration Reference](../reference/configuration-reference.md).

### JSON Log Analysis Best Practices

Since Watchgate now defaults to JSON format, here are some practical examples for analyzing your audit logs:

#### Real-time Security Monitoring
```bash
# Monitor for security events in real-time
tail -f logs/audit.log | jq -r 'select(.event_type == "SECURITY_BLOCK") | "⚠️  \\(.timestamp) - \\(.tool) blocked by \\(.plugin): \\(.reason)"'

# Watch for unusual tool usage patterns
tail -f logs/audit.log | jq -r 'select(.tool == "delete_file" or .tool == "execute_command") | "🔍 \\(.timestamp) - High-risk tool: \\(.tool) (\\(.status))"'
```

#### Security Analytics Queries
```bash
# Find the most blocked tools (potential attack patterns)
jq -r 'select(.event_type == "SECURITY_BLOCK") | .tool' logs/audit.log | sort | uniq -c | sort -nr | head -10

# Analyze failed vs successful requests by tool
jq -r 'select(.tool) | "\\(.tool),\\(.status)"' logs/audit.log | sort | uniq -c | sort -k2,2 -k1,1nr

# Find requests with unusually long response times (potential issues)
jq -r 'select(.duration_ms and .duration_ms > 5000) | {tool, duration_ms, timestamp, request_id}' logs/audit.log

# Security plugin effectiveness report
jq -r 'select(.plugin) | .plugin' logs/audit.log | sort | uniq -c | awk '{printf "Plugin: %-25s Events: %d\\n", $2, $1}'
```

### CSV Format Analysis

When using CSV format, you can analyze audit data with spreadsheet tools or command-line utilities:

#### Analysis with Command-Line Tools
```bash
# Count total requests (excluding header)
tail -n +2 logs/audit.csv | wc -l

# Most frequently used tools
tail -n +2 logs/audit.csv | cut -d',' -f4 | grep -v '^$' | sort | uniq -c | sort -nr

# Security blocks by tool
tail -n +2 logs/audit.csv | awk -F',' '$2=="SECURITY_BLOCK" {print $4}' | sort | uniq -c

# Average response time
tail -n +2 logs/audit.csv | awk -F',' '$9 != "" {sum+=$9; count++} END {if(count>0) printf "Average: %.2f ms\n", sum/count}'
```

#### Analysis with Python/Pandas
```python
import pandas as pd

# Load CSV audit data
df = pd.read_csv('logs/audit.csv')

# Basic statistics
print(f"Total events: {len(df)}")
print(f"Unique tools: {df['tool'].nunique()}")

# Most used tools
print("\nMost used tools:")
print(df[df['tool'].notna()]['tool'].value_counts())

# Security events
security_events = df[df['event_type'] == 'SECURITY_BLOCK']
print(f"\nSecurity blocks: {len(security_events)}")

# Response times
response_times = df[df['duration_ms'].notna()]['duration_ms']
print(f"\nAverage response time: {response_times.mean():.2f}ms")
```

#### Analysis with Excel/Google Sheets
- **Import**: File → Open → Select audit.csv
- **Filter**: Use Data → Filter to focus on specific event types
- **Charts**: Create charts for tool usage, response times, security events
- **Pivot tables**: Summarize data by tool, plugin, or time period

#### Daily/Weekly Reports
```bash
# Generate daily activity summary
echo "=== Daily Activity Report ===" && \
jq -r '.timestamp[0:10]' logs/audit.log | sort | uniq -c | awk '{printf "Date: %s - Events: %d\\n", $2, $1}' | tail -7

# Weekly security events summary
jq -r 'select(.event_type == "SECURITY_BLOCK") | .timestamp[0:10]' logs/audit.log | sort | uniq -c | tail -7

# Tool usage trends
echo "=== Most Used Tools ===" && \
jq -r 'select(.event_type == "REQUEST" and .tool) | .tool' logs/audit.log | sort | uniq -c | sort -nr | head -10
```

#### Integration with Log Management Tools

**For ELK Stack:**
```yaml
# Filebeat configuration for Watchgate JSON logs
filebeat.inputs:
- type: log
  paths:
    - /path/to/logs/audit.log
  json.keys_under_root: true
  json.add_error_key: true
  fields:
    logtype: watchgate
    environment: production
```

**For Datadog:**
```bash
# Using Datadog agent to ship logs
echo "logs:" >> /etc/datadog-agent/conf.d/watchgate.d/conf.yaml
echo "  - type: file" >> /etc/datadog-agent/conf.d/watchgate.d/conf.yaml
echo "    path: \"/path/to/logs/audit.log\"" >> /etc/datadog-agent/conf.d/watchgate.d/conf.yaml
echo "    service: watchgate" >> /etc/datadog-agent/conf.d/watchgate.d/conf.yaml
echo "    source: json" >> /etc/datadog-agent/conf.d/watchgate.d/conf.yaml
```

## Support

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting Guide](../reference/troubleshooting.md)
2. Review the documentation in the [Reference](../reference/) section
3. File an issue on the Watchgate GitHub repository
