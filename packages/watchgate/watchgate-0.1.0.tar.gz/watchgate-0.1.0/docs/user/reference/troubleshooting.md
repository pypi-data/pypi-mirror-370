# Troubleshooting Guide

*[Home](../../../README.md) → [User Documentation](../../README.md) → [Reference](../README.md) → Troubleshooting*

This guide helps you diagnose and resolve common issues with Watchgate configuration, plugins, and operation.

## Table of Contents

1. [General Troubleshooting Steps](#general-troubleshooting-steps)
2. [Installation Issues](#installation-issues)
3. [Configuration Problems](#configuration-problems)
4. [Plugin Issues](#plugin-issues)
5. [Connection Problems](#connection-problems)
6. [Performance Issues](#performance-issues)
7. [Logging and Debugging](#logging-and-debugging)
8. [Error Messages](#error-messages)

## General Troubleshooting Steps

Before diving into specific issues, try these general debugging steps:

### 1. Enable Verbose Logging
```bash
watchgate --config your-config.yaml --verbose
```

### 2. Validate Configuration
```bash
watchgate debug config --validate --config your-config.yaml
```

### 3. Check Plugin Loading
```bash
watchgate debug plugins --validate-priorities --config your-config.yaml
```

### 4. Test MCP Server Directly
```bash
# Test your upstream MCP server without Watchgate
npx @modelcontextprotocol/server-filesystem ./your-directory/
```

## Installation Issues

### "Watchgate command not found"

**Symptoms**: Command line shows `watchgate: command not found`

**Causes & Solutions**:

1. **Watchgate not installed**:
   ```bash
   # Install with uv (recommended)
   uv add watchgate
   
   # Or install with pip
   pip install watchgate
   ```

2. **Python PATH issues**:
   ```bash
   # Check if watchgate is in PATH
   which watchgate
   
   # If not found, check Python scripts directory
   python -m site --user-base
   ```

3. **Virtual environment not activated**:
   ```bash
   # If using virtual environment, activate it
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

### "Command 'uv' not found"

**Symptoms**: `uv: command not found` when trying to install

**Solution**: Install uv package manager:
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternative: use pip instead
pip install watchgate
```

### "Command 'npx' not found"

**Symptoms**: `npx: command not found` when starting MCP servers

**Solution**: Install Node.js which includes npx:
1. Visit [nodejs.org](https://nodejs.org/)
2. Download and install Node.js
3. Verify installation: `npx --version`

## Configuration Problems

### "Configuration file not found"

**Symptoms**: `Config file not found: your-config.yaml`

**Solutions**:

1. **Check file path**:
   ```bash
   # Use absolute path
   watchgate --config /full/path/to/your-config.yaml
   
   # Verify file exists
   ls -la your-config.yaml
   ```

2. **Check file permissions**:
   ```bash
   # Ensure file is readable
   chmod 644 your-config.yaml
   ```

### "Invalid YAML syntax"

**Symptoms**: YAML parsing errors on startup

**Solutions**:

1. **Check YAML syntax**:
   ```bash
   # Use online YAML validator or
   python -c "import yaml; yaml.safe_load(open('your-config.yaml'))"
   ```

2. **Common YAML issues**:
   - Inconsistent indentation (use spaces, not tabs)
   - Missing colons after keys
   - Unquoted strings with special characters
   - Missing quotes around file paths with spaces

**Example of corrected YAML**:
```yaml
# Bad
proxy:
transport: stdio    # Missing space after colon
  upstream:
    command: npx @modelcontextprotocol/server-filesystem /path with spaces/  # Unquoted path

# Good
proxy:
  transport: stdio  # Proper spacing
  upstream:
    command: "npx @modelcontextprotocol/server-filesystem '/path with spaces/'"  # Quoted path
```

### "Invalid configuration structure"

**Symptoms**: Validation errors about missing or invalid configuration sections

**Solution**: Ensure your configuration has the required structure:
```yaml
proxy:              # Required section
  transport: stdio  # Required field
  upstream:         # Required section
    command: "your-mcp-server-command"  # Required field

plugins:            # Optional section
  security:         # Optional
    - policy: "plugin_name"
      enabled: true
      config: {}
  auditing:         # Optional
    - policy: "plugin_name"
      enabled: true
      config: {}
```

## Plugin Issues

### "Plugin not loading"

**Symptoms**: Plugin appears in config but doesn't execute

**Debugging steps**:

1. **Check plugin name**:
   ```bash
   watchgate debug plugins --list-available
   ```

2. **Verify plugin is enabled**:
   ```yaml
   plugins:
     security:
       - policy: "tool_allowlist"
         enabled: true  # Must be true
   ```

3. **Check plugin configuration**:
   ```bash
   watchgate debug plugins --validate-config --config your-config.yaml
   ```

### "Plugin priority conflicts"

**Symptoms**: Plugins executing in wrong order

**Solutions**:

1. **Check priority values**:
   ```yaml
   plugins:
     security:
       - policy: "tool_allowlist"
         priority: 10  # Lower number = higher priority
       - policy: "content_access_control"
         priority: 20  # Runs after tool_allowlist
   ```

2. **Validate priorities**:
   ```bash
   watchgate debug plugins --validate-priorities --config your-config.yaml
   ```

### "Tool access control not working"

**Symptoms**: All tools are visible or none are blocked

**Common issues**:

1. **Wrong mode setting**:
   ```yaml
   # Problem: Typo in mode
   config:
     mode: "allowlsit"  # Should be "allowlist"
   
   # Solution: Correct spelling
   config:
     mode: "allowlist"
   ```

2. **Empty tools list**:
   ```yaml
   # Problem: No tools specified in allowlist mode
   config:
     mode: "allowlist"
     tools: []  # Empty list blocks everything
   
   # Solution: Add allowed tools
   config:
     mode: "allowlist"
     tools: ["read_file", "write_file"]
   ```

3. **Case sensitivity**:
   ```yaml
   # Problem: Wrong case
   tools: ["Read_File"]  # Wrong case
   
   # Solution: Correct case
   tools: ["read_file"]  # Correct case
   ```

### "Content access control patterns not matching"

**Symptoms**: Files are blocked or allowed unexpectedly

**Common pattern issues**:

1. **Case sensitivity**: Patterns are case-sensitive
   ```yaml
   # Problem
   resources: ["Public/*"]  # Won't match "public/"
   
   # Solution
   resources: ["public/*"]  # Matches "public/"
   ```

2. **Missing wildcards**:
   ```yaml
   # Problem: Only matches exact directory
   resources: ["docs"]
   
   # Solution: Add wildcards for contents
   resources: ["docs/*"]      # Files in docs/
   resources: ["docs/**/*"]   # Files in docs/ and subdirectories
   ```

3. **Negation order**:
   ```yaml
   # Problem: Negation before positive pattern
   resources:
     - "!sensitive/*"
     - "public/**/*"
   
   # Solution: Positive patterns first
   resources:
     - "public/**/*"
     - "!public/sensitive/*"
   ```

## Connection Problems

### "Connection refused"

**Symptoms**: Watchgate can't connect to upstream MCP server

**Solutions**:

1. **Test upstream server directly**:
   ```bash
   # Test the MCP server command directly
   npx @modelcontextprotocol/server-filesystem ./your-directory/
   ```

2. **Check command path**:
   ```yaml
   # Ensure command is correct and accessible
   upstream:
     command: "npx @modelcontextprotocol/server-filesystem ./existing-directory/"
   ```

3. **Verify directory exists**:
   ```bash
   # For filesystem server, ensure directory exists
   ls -la ./your-directory/
   mkdir -p ./your-directory/  # Create if missing
   ```

### "Claude Desktop not connecting"

**Symptoms**: Claude Desktop shows connection errors

**Solutions**:

1. **Check Claude Desktop configuration**:
   ```json
   {
     "mcpServers": {
       "watchgate": {
         "command": "watchgate",
         "args": [
           "--config", "/absolute/path/to/config.yaml"
         ]
       }
     }
   }
   ```

2. **Use absolute paths**:
   ```json
   // Problem: Relative path
   "args": ["--config", "config.yaml"]
   
   // Solution: Absolute path
   "args": ["--config", "/Users/username/watchgate/config.yaml"]
   ```

3. **Restart Claude Desktop** after configuration changes

## Performance Issues

### "Slow response times"

**Symptoms**: Operations take longer than expected

**Causes & Solutions**:

1. **Too many plugins**:
   - Reduce number of active plugins
   - Optimize high-priority plugins
   - Use `mode: "critical"` for auditing

2. **Complex content patterns**:
   ```yaml
   # Problem: Complex patterns
   resources:
     - "**/**/deeply/nested/**/*"
   
   # Solution: Simplify patterns
   resources:
     - "public/**/*"
     - "docs/**/*"
   ```

3. **Excessive logging**:
   ```yaml
   # Problem: Verbose logging in production
   config:
     format: "detailed"
     mode: "all"
   
   # Solution: Reduce logging
   config:
     format: "simple"
     mode: "critical"
   ```

### "High memory usage"

**Symptoms**: Watchgate consuming excessive memory

**Solutions**:

1. **Enable log rotation**:
   ```yaml
   config:
     file: "logs/audit.log"
     max_file_size_mb: 10
     backup_count: 5
   ```

2. **Reduce audit buffer size**:
   ```yaml
   config:
     buffer_size: 1000  # Reduce from default
   ```

## Logging and Debugging

### System Logging Configuration Issues

**Problem: Log file not created**

**Check:**
1. File path is correct in configuration
2. Directory permissions allow file creation  
3. Disk space is available
4. `handlers` includes `"file"`

```yaml
logging:
  handlers: ["file"]           # Must include "file"
  file_path: "logs/system.log" # Must specify path for file handler
```

**Problem: Permission denied error**

Watchgate will fall back to stderr logging if file creation fails. Check:
1. Directory permissions
2. File permissions if file already exists
3. Disk space
4. SELinux/AppArmor policies if applicable

**Problem: Too many log files**

**Solution:** Adjust backup count:
```yaml
logging:
  backup_count: 3  # Keep only 3 backup files (plus current = 4 total)
```

**Problem: Log files too large**

**Solution:** Reduce rotation size:
```yaml
logging:
  max_file_size_mb: 5  # Rotate every 5MB instead of default 10MB
```

**Problem: Not seeing expected messages**

**Check:**
1. Log level is appropriate (`DEBUG` shows everything, `CRITICAL` shows almost nothing)
2. Messages might be below the configured level
3. Use `--verbose` flag to temporarily enable DEBUG logging

### Enable Debug Logging

For detailed troubleshooting information:

```bash
# Enable verbose output
watchgate --config config.yaml --verbose

# Set debug log level
export WATCHGATE_LOG_LEVEL=DEBUG
watchgate --config config.yaml
```

### Understanding Log Messages

**Plugin Loading**:
```
[INFO] Loading plugin: tool_allowlist with priority 30
[DEBUG] Plugin tool_allowlist initialized with config: {...}
```

**Request Processing**:
```
[DEBUG] Processing request: tools/list
[DEBUG] Security plugin tool_allowlist: ALLOW
[DEBUG] Security plugin content_access_control: ALLOW
[INFO] Request processed successfully
```

**Security Blocks**:
```
[WARNING] Tool blocked by allowlist: delete_file not in ['read_file', 'write_file']
[INFO] Request denied by security policy
```

### Log File Analysis

```bash
# Find security blocks
grep "SECURITY_BLOCK\|blocked" logs/audit.log

# Monitor in real-time
tail -f logs/audit.log | grep -E "(ERROR|WARNING|BLOCK)"

# Count tool usage
grep "TOOL_CALL" logs/audit.log | cut -d'-' -f4 | sort | uniq -c

# Find performance issues
grep "DURATION" logs/audit.log | awk '{print $NF}' | sort -n
```

## Error Messages

### Common Error Messages and Solutions

**"Plugin priority must be between 0 and 100"**
- Check priority values in plugin configuration
- Ensure priority is an integer, not a string

**"Tool not found in allowlist"**
- Add the tool to your allowlist configuration
- Check tool name spelling and case

**"Resource blocked by pattern"**
- Review your content access control patterns
- Use debug mode to see pattern matching details

**"YAML parsing failed"**
- Check YAML syntax and indentation
- Ensure colons have spaces after them
- Quote strings with special characters

**"Upstream server connection failed"**
- Verify upstream server command is correct
- Test upstream server independently
- Check file paths and permissions

## Getting Help

If you're still experiencing issues:

1. **Check the logs** with verbose mode enabled
2. **Review this troubleshooting guide** for similar issues
3. **Test components individually** (plugins, upstream server, etc.)
4. **Simplify your configuration** to isolate the problem
5. **Check the [Configuration Reference](configuration-reference.md)** for correct syntax
6. **File an issue** on the Watchgate GitHub repository with:
   - Your configuration file (remove sensitive information)
   - Complete error messages
   - Steps to reproduce the issue
   - Output from `watchgate --config config.yaml --verbose`
