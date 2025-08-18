# Quick Setup

*[Home](../../README.md) > [User Guide](../README.md) > [Getting Started](README.md) > Quick Setup*

This guide will get you up and running with Watchgate in just a few minutes. By the end of this guide, you'll have Watchgate protecting an MCP server with basic security controls.

## Prerequisites

Before you begin, ensure you have:

- **Watchgate installed** (see [Installation Guide](installation.md))
- **Claude Desktop** or another MCP client
- **Basic understanding** of MCP (Model Context Protocol)

## Step 1: Create a Configuration File

Create a basic Watchgate configuration file called `watchgate.yaml`:

```yaml
# Basic Watchgate configuration
proxy:
  transport: stdio
  upstream:
    command: "npx @modelcontextprotocol/server-filesystem ./workspace/"

# Add logging for development
logging:
  level: "INFO"                    # Show important events
  handlers: ["stderr", "file"]     # Console + file output
  file_path: "logs/watchgate.log" # Store persistent logs

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
  
  auditing:
    - policy: "file_auditing"
      enabled: true
      config:
        file: "logs/watchgate.log"
        format: "simple"
        mode: "all"
```

## Step 2: Create Required Directories

Create the directories Watchgate needs:

```bash
# Create workspace directory for the MCP server
mkdir -p workspace

# Create logs directory for audit logs
mkdir -p logs

# Add a sample file to test with
echo "Hello from Watchgate!" > workspace/readme.txt
```

## Step 3: Test Watchgate

Test that Watchgate starts correctly:

```bash
watchgate --config watchgate.yaml --verbose
```

You should see output like:
```
[INFO] Loading configuration from watchgate.yaml
[INFO] Starting Watchgate MCP Gateway
[INFO] Loaded security plugin: tool_allowlist
[INFO] Loaded auditing plugin: file_auditing
[INFO] Connected to upstream server
[INFO] MCPProxy now accepting client connections
```

If you see this output, Watchgate is working correctly. Press `Ctrl+C` to stop it.

## Step 4: Configure Your MCP Client

### For Claude Desktop

1. **Locate your Claude Desktop configuration**:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Update the configuration**:
   ```json
   {
     "mcpServers": {
       "watchgate-filesystem": {
         "command": "watchgate",
         "args": [
           "--config", "/absolute/path/to/your/watchgate.yaml"
         ],
         "env": {}
       }
     }
   }
   ```

   **Important**: Replace `/absolute/path/to/your/watchgate.yaml` with the actual path to your configuration file.

3. **Restart Claude Desktop** for the changes to take effect.

### For Other MCP Clients

If you're using a different MCP client, configure it to run:
```bash
watchgate --config /path/to/watchgate.yaml
```

## Step 5: Test Your Setup

1. **Start a conversation** in Claude Desktop (or your MCP client)

2. **Test basic functionality**:
   ```
   What files can you see in my directory?
   ```

3. **Test security controls**:
   ```
   Can you delete the readme.txt file?
   ```
   
   You should see this request blocked because `delete_file` is not in the allowlist.

4. **Check the audit logs**:
   ```bash
   cat logs/watchgate.log
   ```
   
   You should see entries for all the operations Claude attempted.

## Step 6: Verify Security is Working

Your Watchgate setup should now be:

✅ **Allowing approved tools**: `read_file`, `write_file`, `list_directory`, `create_directory`
✅ **Blocking unapproved tools**: Any tools not in the allowlist (like `delete_file`)
✅ **Logging all activity**: Check `logs/watchgate.log` for complete audit trail
✅ **Protecting your workspace**: Only files in the `./workspace/` directory are accessible

## Understanding Your Configuration

Let's break down what each part of your configuration does:

### Proxy Section
```yaml
proxy:
  transport: stdio              # How Watchgate communicates with MCP server
  upstream:
    command: "npx @modelcontextprotocol/server-filesystem ./workspace/"
    # Starts the filesystem server, restricted to ./workspace/ directory
```

### Logging Section
```yaml
logging:
  level: "INFO"                    # Show important events
  handlers: ["stderr", "file"]     # Console + file output
  file_path: "logs/watchgate.log" # Store persistent logs
```

### Security Plugin
```yaml
plugins:
  security:
    - policy: "tool_allowlist"  # Plugin name
      enabled: true                  # Enable the plugin
      config:
        mode: "allowlist"            # Only allow specified tools
        tools:                       # List of allowed tools
          - "read_file"
          - "write_file"
          - "list_directory"
          - "create_directory"
```

### System Logging (Optional)
```yaml
# Configure Watchgate's internal application logs
logging:
  level: "INFO"                     # Log level (DEBUG, INFO, WARNING, ERROR)
  handlers: ["stderr", "file"]      # Output to console and file
  file_path: "logs/system.log"      # System log file location
  max_file_size_mb: 10             # Rotate when file reaches this size
```

### Auditing Plugin  
```yaml
# Configure auditing of MCP communications and security decisions
  auditing:
    - policy: "file_auditing"         # Plugin name
      enabled: true                 # Enable the plugin
      config:
        file: "logs/audit.log"      # Where to write audit logs (separate from system logs)
        format: "simple"            # Log format (simple, json, detailed)
        mode: "all_events"          # Log everything (security_only, operations_only, all_events)
```

> **Important**: System logging and auditing serve different purposes:
> - **System logging** captures Watchgate's operational status and errors
> - **Auditing** logs MCP communications and security decisions for compliance

## Customizing Your Setup

Now that you have a basic setup working, you can customize it:

### Add More Security

Add content access control to restrict which files can be accessed:

```yaml
plugins:
  security:
    - policy: "tool_allowlist"
      enabled: true
      config:
        mode: "allowlist"
        tools: ["read_file", "write_file", "list_directory", "create_directory"]
    
    - policy: "content_access_control"  # Add this plugin
      enabled: true
      config:
        mode: "allowlist"
        resources:
          - "public/*"      # Only allow files in public/ directory
          - "docs/*.md"     # Only allow markdown files in docs/
```

### Change Logging Detail

Adjust logging to your needs:

```yaml
auditing:
  - policy: "file_auditing"
    enabled: true
    config:
      file: "logs/watchgate.log"
      format: "json"        # Use JSON format for machine processing
      mode: "critical"      # Only log security events
```

### Allow More Tools

Expand the tool allowlist for more functionality:

```yaml
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
        - "move_file"       # Add file moving
        - "search_files"    # Add file search
```

## Common Quick Setup Issues

### "Command not found" errors

**Problem**: `watchgate` or `npx` command not found

**Solution**: 
- Ensure Watchgate is installed: `watchgate --version`
- Install Node.js for npx: [nodejs.org](https://nodejs.org/)

### "File not found" errors

**Problem**: Configuration file or workspace directory doesn't exist

**Solution**:
- Use absolute paths in configuration
- Verify files exist: `ls -la watchgate.yaml workspace/`

### "Permission denied" errors

**Problem**: Can't create logs or access workspace

**Solution**:
- Check directory permissions: `chmod 755 workspace/ logs/`
- Ensure Watchgate can write to logs directory

### Claude Desktop not connecting

**Problem**: Claude Desktop shows connection errors

**Solution**:
- Use absolute path in Claude Desktop config
- Restart Claude Desktop after configuration changes
- Check Watchgate starts without errors

## Next Steps

Now that you have Watchgate working:

1. **Learn more about security**: Try the [Securing Tool Access](../tutorials/securing-tool-access.md) tutorial
2. **Add content protection**: Follow the [Protecting Sensitive Content](../tutorials/protecting-sensitive-content.md) guide
3. **Understand the concepts**: Read about [Watchgate's architecture](../core-concepts/plugin-architecture.md)
4. **Explore advanced features**: Check out the [Configuration Reference](../reference/configuration-reference.md)

## Support

If you run into issues during setup:

1. Check the [Troubleshooting Guide](../reference/troubleshooting.md)
2. Enable verbose logging: `watchgate --config watchgate.yaml --verbose`
3. Test each component separately
4. Review your configuration syntax
