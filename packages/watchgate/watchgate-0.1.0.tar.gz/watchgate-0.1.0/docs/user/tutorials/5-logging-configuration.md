# System Logging Configuration

*[Home](../../../README.md) → [User Documentation](../../README.md) → [Tutorials](../README.md) → System Logging Configuration*

This tutorial will teach you how to configure Watchgate's system logging for different environments and use cases. You'll learn to set up comprehensive operational logging that provides visibility into Watchgate's internal operations, performance, and troubleshooting information.

## What You'll Accomplish

Proper system logging is essential for maintaining, debugging, and monitoring Watchgate in any environment. Without good operational logs, it becomes difficult to troubleshoot issues, understand performance patterns, or maintain reliable service in production environments.

In this tutorial, you'll learn how to configure Watchgate's system logging to meet your operational needs. By the end, you'll have:

- **Environment-appropriate logging**: Configurations optimized for development, staging, and production
- **Structured log management**: Automatic rotation and retention policies to prevent disk space issues
- **Debugging capabilities**: Detailed logging configurations for troubleshooting complex issues
- **Production-ready monitoring**: Appropriate log levels and formats for operational visibility

This approach ensures you have the operational visibility needed to maintain reliable Watchgate deployments across all environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Understanding Watchgate System Logging](#understanding-watchgate-system-logging)
3. [Verify Watchgate Installation](#verify-watchgate-installation)
4. [Basic System Logging Setup](#basic-system-logging-setup)
5. [Development Environment Configuration](#development-environment-configuration)
6. [Production Environment Configuration](#production-environment-configuration)
7. [Testing Your Logging Setup](#testing-your-logging-setup)
8. [Log Analysis and Management](#log-analysis-and-management)
9. [Troubleshooting](#troubleshooting)
10. [Next Steps](#next-steps)

## Prerequisites

Before you begin, ensure you have:

- **Watchgate** installed on your system
- **Python** (version 3.11 or higher) for Watchgate
- **uv** tool for Watchgate installation
- Basic familiarity with log levels and file systems
- Understanding of YAML configuration files

### Verify Your Prerequisites

Before proceeding, verify your system meets all requirements:

```bash
# Verify Python version (should be 3.11 or higher)
# On macOS/Linux:
python3 --version
# On Windows:
python --version

# Verify uv tool is available
uv --version
```

If any of these commands fail, install the missing tools before continuing.

## Understanding Watchgate System Logging

Watchgate has two distinct logging systems that serve different purposes:

### System Logging vs Audit Logging

- **System Logging** (this tutorial): Watchgate's internal operational logs for startup, errors, debug information, and performance monitoring
- **Audit Logging** ([Audit Logging Tutorial](2-implementing-audit-logging.md)): Plugin-based MCP communication and security decision logs

**Important**: These are separate systems with different configuration sections. This tutorial focuses on system logging configuration under the `logging` section.

### System Logging Capabilities

Watchgate's system logging provides:

- **Flexible output destinations**: Console, files, or both
- **Configurable log levels**: From DEBUG (everything) to CRITICAL (only severe errors)
- **Automatic file rotation**: Prevents log files from consuming excessive disk space
- **Customizable formats**: Standard formats or custom structured output
- **Runtime overrides**: Command-line flags for temporary debugging

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

## Basic System Logging Setup

Let's start with basic system logging configurations that you can build upon.

### Console Logging (Default)

By default, Watchgate logs to the console (stderr) at INFO level. This is perfect for initial testing:

```yaml
# Minimal configuration - system logging goes to console
proxy:
  transport: stdio
  upstream:
    command: "npx @modelcontextprotocol/server-filesystem ./workspace/"

# No logging section = stderr output at INFO level
```

### Adding File Logging

For persistent system logs that survive across sessions, add file output:

```yaml
proxy:
  transport: stdio
  upstream:
    command: "npx @modelcontextprotocol/server-filesystem ./workspace/"

logging:
  level: "INFO"                     # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
  handlers: ["stderr", "file"]      # Both console and file output
  file_path: "logs/watchgate.log"  # Where to write system log files
```

**Important**: When using file logging, you must specify `file_path`.

### Customizing Console Logging

To modify console logging behavior:

```yaml
logging:
  level: "DEBUG"        # More detailed output for development
  handlers: ["stderr"]  # Explicit console-only output
  format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
```

## Development Environment Configuration

Perfect for local development with immediate feedback and detailed debugging information.

1. **Understanding the configuration**:

   The tutorial uses the configuration file at `configs/tutorials/5-logging-configuration.yaml`, which contains:

   ```yaml
   # Development System Logging Configuration
   proxy:
     transport: stdio
     upstream:
       command: "npx @modelcontextprotocol/server-filesystem ~/workspace/"

   logging:
     level: "DEBUG"                    # See everything during development
     handlers: ["stderr", "file"]     # Console for immediate feedback + persistent storage
     file_path: "logs/development.log"
     # Log rotation settings for development
     max_file_size_mb: 5               # Small files for quick rotation
     backup_count: 3                   # Keep recent history only
     # Detailed format for debugging with function names
     format: "%(asctime)s [%(levelname)s] %(name)s:%(funcName)s: %(message)s"
   ```

   **Key Points:**
   - **Level**: `INFO` provides operational information without excessive debug details
   - **Handlers**: Both `stderr` and `file` for immediate feedback plus persistence
   - **File Rotation**: Automatic rotation prevents disk space issues
   - **Custom Format**: Includes function names for detailed debugging context
   - **Dual Plugins**: Demonstrates both security controls and audit logging

2. **Create the workspace and logs directories**:

   ```bash
   # Create workspace directory (using home directory for predictable paths)
   mkdir ~/workspace
   echo "Development test file" > ~/workspace/test.txt
   
   # Create logs directory
   mkdir logs
   ```

   **Note**: We use `~/workspace/` (in your home directory) to ensure a predictable absolute path. If you prefer a different location, update the `command:` line in the configuration file to point to your chosen directory.

3. **Test your logging configuration**:

   ```bash
   # Start with the tutorial configuration
   watchgate --config configs/tutorials/5-logging-configuration.yaml
   
   # For even more detail, use verbose flag (overrides to DEBUG level)
   watchgate --config configs/tutorials/5-logging-configuration.yaml --verbose
   ```

**Configuration Benefits:**
- Immediate console feedback for real-time monitoring
- Persistent file storage for reviewing previous sessions
- Function names in logs for detailed debugging
- Quick file rotation to manage disk space during active development

## Production Environment Configuration

For comparison, here's how you might configure production logging with different priorities.

   ```yaml
   # Production System Logging Configuration
   proxy:
     transport: stdio
     upstream:
       command: "npx @modelcontextprotocol/server-filesystem ./production-workspace/"

   logging:
     level: "INFO"                     # Operational information only (reduces log volume)
     handlers: ["file"]                # File only (no console clutter in production)
     file_path: "/var/log/watchgate/watchgate.log"  # Standard log location
     # Production rotation settings
     max_file_size_mb: 50              # Larger files for production
     backup_count: 10                  # More backup history
     # Clean format for operational monitoring
     format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
     date_format: "%Y-%m-%d %H:%M:%S"

   # Example with security plugins for production
   plugins:
     security:
       - policy: "tool_allowlist"
         enabled: true
         config:
           mode: "allowlist"
           tools: ["read_file", "write_file", "list_directory"]
   ```

2. **Set up production directories and permissions**:

   ```bash
   # Create production workspace
   sudo mkdir -p /var/log/watchgate
   sudo mkdir -p ./production-workspace
   
   # Set appropriate permissions
   sudo chown $USER:$USER /var/log/watchgate
   sudo chmod 755 /var/log/watchgate
   
   # Add some production data
   echo "Production data" > ./production-workspace/data.txt
   ```

3. **Test your production logging**:

   ```bash
   # Start with production configuration
   watchgate --config watchgate-prod-config.yaml
   
   # Check that logs are being written
   tail -f /var/log/watchgate/watchgate.log
   ```

**Production Benefits:**
- INFO level reduces log volume while capturing important events
- File-only output prevents console spam in background processes
- Larger rotation settings reduce file management overhead
- Structured format enables log analysis tools

### High-Volume Production

For environments with heavy traffic, use more restrictive logging:

```yaml
logging:
  level: "WARNING"                  # Only warnings and errors
  handlers: ["file"]
  file_path: "/var/log/watchgate/watchgate.log"
  max_file_size_mb: 100             # Larger files
  backup_count: 20                  # More backup files
  format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
```

## Testing Your Logging Setup

Let's verify that your logging configuration is working correctly across different scenarios.

### 1. Test Development Configuration

```bash
# Start Watchgate with development config
watchgate --config watchgate-dev-config.yaml --verbose

# In another terminal, watch the log file
tail -f logs/development.log
```

**Expected behavior:**
- Console output shows detailed DEBUG messages with function names
- Log file receives the same detailed information
- You should see startup messages, plugin loading, and connection information

### 2. Test Production Configuration

```bash
# Start Watchgate with production config  
watchgate --config watchgate-prod-config.yaml

# Check that production logs are being written
tail -f /var/log/watchgate/watchgate.log
```

**Expected behavior:**
- No console output (file-only logging)
- Log file shows INFO level messages only
- Clean, operational format suitable for monitoring

### 3. Test Log Rotation

To test log rotation, you can temporarily create a large log file:

```bash
# Generate enough log entries to trigger rotation
for i in {1..1000}; do
  echo "Test log entry $i - $(date)" >> logs/development.log
done

# Check that rotation occurred (you should see .1, .2 backup files)
ls -la logs/
```

### 4. Verify Log Levels

Test different log levels to ensure appropriate filtering:

```bash
# Test with different verbosity levels
watchgate --config watchgate-dev-config.yaml --verbose    # DEBUG level
watchgate --config watchgate-prod-config.yaml             # INFO level
```

Compare the output volume and detail between configurations.

## Log Analysis and Management

Effective log management ensures your system logs provide value without consuming excessive resources.

### Log Analysis Commands

```bash
# View recent system log entries in real-time
tail -f logs/development.log

# Count log entries by level
grep -o "\[.*\]" logs/development.log | sort | uniq -c

# Find error messages
grep "ERROR\|CRITICAL" logs/development.log

# View logs from a specific time period
grep "2024-06-16 14:" logs/development.log

# Monitor for specific components
grep "watchgate.proxy" logs/development.log
```

### Debugging Configurations

When you need maximum detail for troubleshooting specific issues:

```yaml
# Maximum detail debug configuration
logging:
  level: "DEBUG"
  handlers: ["stderr", "file"]
  file_path: "logs/debug.log"
  max_file_size_mb: 10
  backup_count: 5
  format: "%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d: %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S.%f"  # Include microseconds
```

**Debug Features:**
- DEBUG level shows all internal operations
- Function names and line numbers for precise tracking
- Microsecond timestamps for timing analysis
- Both console and file output for immediate review and later analysis

### Temporary Debugging

For quick issue investigation without changing config files:

```bash
# Use verbose flag for temporary DEBUG logging
watchgate --config watchgate-prod-config.yaml --verbose

# Or create a minimal debug config
cat > debug-config.yaml << EOF
proxy:
  transport: stdio
  upstream:
    command: "npx @modelcontextprotocol/server-filesystem ./workspace/"
logging:
  level: "DEBUG"
  handlers: ["stderr"]
  format: "[%(levelname)s] %(name)s: %(message)s"
EOF

watchgate --config debug-config.yaml
```

## Specialized Configurations

### Security and Compliance Logging

For environments requiring detailed audit trails:

```yaml
logging:
  level: "INFO"
  handlers: ["file"]
  file_path: "/var/log/watchgate/compliance.log"
  max_file_size_mb: 100             # Large files for audit retention
  backup_count: 50                  # Extended retention
  format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
  date_format: "%Y-%m-%dT%H:%M:%S.%fZ"  # ISO format with timezone

plugins:
  auditing:
    - policy: "file_auditing"
      enabled: true
      config:
        output_file: "/var/log/watchgate/audit.log"
        include_request_body: true
        include_response_body: true
```

**Additional Security Setup:**
```bash
# Set appropriate file permissions
sudo chmod 640 /var/log/watchgate/compliance.log
sudo chown watchgate:audit /var/log/watchgate/

# Configure log rotation with logrotate
sudo tee /etc/logrotate.d/watchgate << EOF
/var/log/watchgate/*.log {
    daily
    compress
    rotate 90
    notifempty
    create 640 watchgate audit
}
EOF
```

### Container and Cloud Deployments

For Docker and Kubernetes environments:

```yaml
logging:
  level: "INFO"
  handlers: ["stderr"]              # Use container log collection
  format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
  date_format: "%Y-%m-%dT%H:%M:%S.%fZ"  # ISO format for log aggregation
```

**Docker Example:**
```bash
# Run with container logging
docker run -v /host/config:/config watchgate --config /config/watchgate.yaml

# View logs through Docker
docker logs watchgate-container

# With log driver for centralized logging
docker run --log-driver=syslog --log-opt syslog-address=tcp://logserver:514 \
  watchgate --config /config/watchgate.yaml
```

### Resource-Constrained Environments

For edge deployments or limited storage:

```yaml
logging:
  level: "WARNING"                  # Only significant events
  handlers: ["stderr"]              # No file storage
  format: "[%(levelname)s] %(message)s"  # Minimal format
```

Or for minimal file logging:

```yaml
logging:
  level: "INFO"
  handlers: ["file"]
  file_path: "/tmp/watchgate.log"   # Temporary storage
  max_file_size_mb: 1               # Very small files
  backup_count: 2                   # Minimal backup
  format: "%(levelname)s: %(message)s"
```

## Advanced Log Analysis

### Structured Logging for Analysis

Format logs for easy parsing with analysis tools:

```yaml
logging:
  format: "%(asctime)s|%(levelname)s|%(name)s|%(message)s"
  date_format: "%Y-%m-%dT%H:%M:%S"
```

**Analysis Examples:**
```bash
# Count messages by level
cut -d'|' -f2 logs/watchgate.log | sort | uniq -c

# Extract error messages
grep "|ERROR|" logs/watchgate.log | cut -d'|' -f4

# Time-based analysis
grep "2024-06-15T14:" logs/watchgate.log | wc -l

# Real-time error monitoring
tail -f logs/watchgate.log | grep -E "ERROR|CRITICAL"
```

### JSON-Ready Format

For integration with log aggregation systems:

```yaml
logging:
  format: '{"timestamp":"%(asctime)s","level":"%(levelname)s","component":"%(name)s","message":"%(message)s"}'
  date_format: "%Y-%m-%dT%H:%M:%S.%fZ"
```

## Migration and Configuration Management

### Migrating from Basic to Advanced Logging

**Step 1: Start with basic file logging**
```yaml
# Add to existing config
logging:
  level: "INFO"
  handlers: ["stderr", "file"]
  file_path: "logs/watchgate.log"
```

**Step 2: Add rotation and formatting**
```yaml
logging:
  level: "INFO"
  handlers: ["stderr", "file"]
  file_path: "logs/watchgate.log"
  max_file_size_mb: 10
  backup_count: 5
  format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
```

**Step 3: Environment-specific optimization**
```yaml
# Development
logging:
  level: "DEBUG"
  handlers: ["stderr", "file"]
  file_path: "logs/development.log"
  format: "%(asctime)s [%(levelname)s] %(name)s:%(funcName)s: %(message)s"

# Production  
logging:
  level: "INFO"
  handlers: ["file"]
  file_path: "/var/log/watchgate/watchgate.log"
  max_file_size_mb: 50
  backup_count: 10
```

### Configuration Validation

Test your logging configuration before deployment:

```bash
# Validate configuration syntax
watchgate --config config.yaml --help  # Should not show errors

# Test log directory creation
mkdir -p logs  # Ensure directory exists or test auto-creation

# Test file permissions
touch logs/test.log && rm logs/test.log

# Test with temporary config
watchgate --config config.yaml &
PID=$!
sleep 2
kill $PID
ls -la logs/  # Verify log file was created
```

## Troubleshooting

### Common Issues:

1. **"System log file not created"**
   - Verify the logs directory exists and is writable: `ls -ld logs/`
   - Check the `file_path` setting in your configuration
   - Ensure the logging section includes `"file"` in handlers: `handlers: ["file"]`
   - Test directory creation: `mkdir -p logs && touch logs/test.log && rm logs/test.log`

2. **"Watchgate command not found"**
   - Ensure Watchgate is properly installed: `uv add watchgate` (or `pip install watchgate`)
   - Verify installation: `watchgate --help`
   - Check your PATH includes the Python scripts directory

3. **"Permission denied when creating log files"**
   - Check directory permissions: `ls -ld /var/log/watchgate/`
   - Create directory with correct permissions:
     ```bash
     sudo mkdir -p /var/log/watchgate
     sudo chown $USER:$USER /var/log/watchgate
     sudo chmod 755 /var/log/watchgate
     ```
   - Or use a directory you own: `mkdir -p ~/watchgate-logs`

4. **"Log directory filling up with backup files"**
   - Reduce number of backup files: `backup_count: 3`
   - Increase rotation size: `max_file_size_mb: 20`
   - Check log level - DEBUG creates much more output than INFO

5. **"Missing expected log messages"**
   - Check log level setting - ensure it's appropriate (DEBUG shows everything)
   - Verify the component you're looking for actually logs at your configured level
   - Use `--verbose` flag for temporary DEBUG logging

6. **"Log format issues"**
   - Ensure file handler is included: `handlers: ["file"]`
   - Check path format - relative paths are OK: `file_path: "logs/agent.log"`
   - Absolute paths are OK: `file_path: "/var/log/agent.log"`
   - Shell expansion NOT supported: avoid `~/logs/agent.log`

### Debugging Steps:

1. **Test system logging is working**:
   ```bash
   # Check if log file is being created and written to
   ls -la logs/
   tail -f logs/development.log
   ```

2. **Verify configuration loading**:
   ```bash
   watchgate --config watchgate-dev-config.yaml --verbose
   ```

3. **Test with minimal configuration**:
   ```yaml
   # Minimal test config
   proxy:
     transport: stdio
     upstream:
       command: "npx @modelcontextprotocol/server-filesystem ./workspace/"
   logging:
     level: "DEBUG"
     handlers: ["stderr"]
   ```

4. **Check log permissions**:
   ```bash
   ls -la logs/development.log
   touch logs/test.log && rm logs/test.log  # Test write permissions
   ```

## Next Steps

Now that you have system logging configured, you can explore these additional logging and monitoring capabilities:

### Audit Logging Integration

Combine system logging with audit logging for complete visibility:

- **Audit Logging**: Track all MCP communications and security decisions using the `file_auditing` plugin
- **Complete Visibility**: System logs show Watchgate's internal operations, audit logs show what it's doing
- **Coordinated Monitoring**: Use both log types together for comprehensive troubleshooting

See the [Implementing Audit Logging](2-implementing-audit-logging.md) tutorial for detailed instructions.

### Advanced Monitoring Strategies

For production environments, consider these enhancements:

- **Log Aggregation**: Send logs to centralized systems (ELK, Splunk, etc.) for analysis
- **Structured Logging**: Use JSON format for easier parsing and filtering
- **Real-time Monitoring**: Set up alerts for ERROR and CRITICAL level messages
- **Performance Monitoring**: Track startup times, connection issues, and plugin loading

### Environment-Specific Configurations

Create tailored configurations for different environments:

1. **Development**: Maximum detail with console output for immediate feedback
2. **Staging**: Production-like settings with detailed logging for testing
3. **Production**: Optimized levels with file-only output and appropriate rotation

### Configuration Management Best Practices

For maintaining logging configurations:

- **Version Control**: Track changes to logging configurations alongside your code
- **Environment Variables**: Use environment-specific values for log paths and levels
- **Configuration Validation**: Test logging configurations before deployment
- **Log Retention Policies**: Establish how long to keep logs for compliance and storage management

For more advanced configuration options and monitoring strategies, see the [Configuration Reference](../reference/configuration-reference.md).

## Support

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting Guide](../reference/troubleshooting.md)
2. Review the documentation in the [Reference](../reference/) section
3. File an issue on the Watchgate GitHub repository
