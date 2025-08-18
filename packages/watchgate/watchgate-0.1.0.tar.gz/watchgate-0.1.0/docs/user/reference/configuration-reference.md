# Watchgate Configuration Reference

*[Home](../../../README.md) → [User Documentation](../../README.md) → [Reference](../README.md) → Configuration Reference*

This document provides a comprehensive reference for Watchgate's YAML configuration format.

## Configuration File Structure

Watchgate uses a YAML configuration file with the following top-level structure:

```yaml
proxy:
  transport: "stdio"  # or "http"
  upstream:
    # Upstream server configuration
  timeouts:
    # Timeout configuration
  http:  # Optional, required only for HTTP transport
    # HTTP server configuration
  plugins:  # Optional
    # Plugin configuration
```

## Configuration Sections

### 1. Proxy Section (Required)

The `proxy` section contains the main configuration for Watchgate.

#### Transport

**Field**: `transport`  
**Type**: `string`  
**Required**: Yes  
**Values**: `"stdio"` or `"http"`  
**Default**: N/A

Specifies the transport mechanism used to communicate with Claude Desktop.

- `"stdio"`: Uses standard input/output 
- `"http"`: Uses HTTP server 

### 2. Upstream Section (Required)

The `upstream` section configures the target MCP server that Watchgate will proxy to.

```yaml
proxy:
  upstream:
    command: "python -m my_mcp_server"
    restart_on_failure: true
    max_restart_attempts: 3
```

#### Command

**Field**: `command`  
**Type**: `string` or `array of strings`  
**Required**: Yes  
**Default**: N/A

The command line arguments to start the upstream MCP server. 

**String Format** (recommended):
```yaml
command: "npx @modelcontextprotocol/server-filesystem /path/to/directory"
```

**Array Format** (for advanced use cases):
```yaml
command: ["npx", "@modelcontextprotocol/server-filesystem", "/path with spaces/directory"]
```

**Format Selection Guidelines:**
- Use **string format** for most commands - Watchgate will parse arguments automatically
- Use **array format** only when you need precise control over argument parsing, such as:
  - Arguments containing spaces that shouldn't be split
  - Arguments with special shell characters that need to be preserved literally
  - Complex quoting scenarios where automatic parsing might be insufficient

#### Restart on Failure

**Field**: `restart_on_failure`  
**Type**: `boolean`  
**Required**: No  
**Default**: `true`

Whether to automatically restart the upstream server if it fails.

#### Max Restart Attempts

**Field**: `max_restart_attempts`  
**Type**: `integer`  
**Required**: No  
**Default**: `3`

Maximum number of times to attempt restarting the upstream server before giving up.

### 3. Timeouts Section (Required)

The `timeouts` section configures connection and request timeouts.

```yaml
proxy:
  timeouts:
    connection_timeout: 30
    request_timeout: 60
```

#### Connection Timeout

**Field**: `connection_timeout`  
**Type**: `integer`  
**Required**: No  
**Default**: `30`  
**Unit**: seconds

Timeout for establishing connections to the upstream server.

#### Request Timeout

**Field**: `request_timeout`  
**Type**: `integer`  
**Required**: No  
**Default**: `60`  
**Unit**: seconds

Timeout for individual requests to the upstream server.

### 4. HTTP Section (Conditional)

The `http` section is required only when `transport` is set to `"http"`.

```yaml
proxy:
  transport: "http"
  http:
    host: "127.0.0.1"
    port: 8080
```

#### Host

**Field**: `host`  
**Type**: `string`  
**Required**: No  
**Default**: `"127.0.0.1"`

The host address to bind the HTTP server to.

#### Port

**Field**: `port`  
**Type**: `integer`  
**Required**: No  
**Default**: `8080`  
**Range**: 1-65535

The port number to bind the HTTP server to.

### 5. Plugins Section (Optional)

The `plugins` section configures security and auditing plugins.

```yaml
proxy:
  plugins:
    security:
      _global:
        - policy: "tool_allowlist"
          enabled: true
          config:
            mode: "allowlist"
            tools: ["read_file", "write_file"]
    
    auditing:
      _global:
        - policy: "json_auditing"
          enabled: true
          config:
            output_file: "watchgate.log"
            mode: "all_events"
```

#### Plugin Configuration Format

Plugins are configured using an **upstream-scoped dictionary format** that allows different plugin policies for different upstream servers.

#### Security Plugins

**Field**: `security`  
**Type**: `dictionary of upstream keys to plugin configuration arrays`  
**Required**: No  
**Default**: `{}`

Dictionary of security plugins organized by upstream server. The `_global` key applies to all upstreams unless overridden.

**Example:**
```yaml
security:
  _global:                    # Applies to all upstreams
    - policy: "rate_limiting"
  github:                     # Applies only to github upstream
    - policy: "git_token_validation"
  filesystem:                 # Applies only to filesystem upstream  
    - policy: "path_restrictions"
```

#### Auditing Plugins

**Field**: `auditing`  
**Type**: `dictionary of upstream keys to plugin configuration arrays`  
**Required**: No  
**Default**: `{}`

Dictionary of auditing plugins organized by upstream server. The `_global` key applies to all upstreams.

**Example:**
```yaml
auditing:
  _global:
    - policy: "json_auditing"
  filesystem:
    - policy: "file_access_auditing"
```

#### Upstream-Scoped Plugin Configuration

The dictionary-based plugin configuration enables:

- **Global plugins** (`_global` key): Applied to all upstream servers
- **Upstream-specific plugins**: Applied only to specific upstream servers
- **Policy resolution**: Global plugins + upstream-specific plugins
- **Policy override**: Upstream-specific plugins with the same name override global ones

**Key Naming Rules:**
- `_global`: Special key for global plugins
- Upstream keys: Must match upstream server names in `upstreams` section
- Pattern: lowercase alphanumeric with hyphens/underscores (`^[a-z][a-z0-9_-]*$`)
- Cannot contain `__` (reserved for namespace delimiter)

#### Plugin Configuration

Each plugin configuration has the following structure:

##### Policy

**Field**: `policy`  
**Type**: `string`  
**Required**: Yes

Policy name for the plugin. Watchgate discovers available policies from installed plugins and loads the appropriate implementation.

**Examples**:
- `"tool_allowlist"` - Tool access control plugin
- `"json_auditing"` - JSON format audit logging plugin
- `"line_auditing"` - Human-readable audit logging plugin
- `"csv_auditing"` - CSV format audit logging plugin

##### Enabled

**Field**: `enabled`  
**Type**: `boolean`  
**Required**: No  
**Default**: `true`

Whether the plugin is enabled.

##### Config

**Field**: `config`  
**Type**: `object`  
**Required**: No  
**Default**: `{}`

Plugin-specific configuration parameters. The structure depends on the individual plugin.

### 6. Logging Section (Optional)

The `logging` section configures how Watchgate generates and manages log output.

```yaml
logging:
  level: "INFO"                    # Log level
  handlers: ["stderr", "file"]     # Output destinations  
  file_path: "logs/watchgate.log" # File path (required if using file handler)
  max_file_size_mb: 10            # File rotation size
  backup_count: 5                 # Number of backup files to keep
  format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"  # Log format
  date_format: "%Y-%m-%d %H:%M:%S" # Date format
```

#### Level

**Field**: `level`  
**Type**: `string`  
**Required**: No  
**Values**: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`  
**Default**: `"INFO"`

Controls the minimum level of messages to log:

- `"DEBUG"`: Everything including internal details (most verbose)
- `"INFO"`: Important events and status updates  
- `"WARNING"`: Problems that don't stop operation
- `"ERROR"`: Errors that prevent specific operations
- `"CRITICAL"`: Errors that may stop the entire system (least verbose)

#### Handlers

**Field**: `handlers`  
**Type**: `array of strings`  
**Required**: No  
**Values**: `["stderr"]`, `["file"]`, or `["stderr", "file"]`  
**Default**: `["stderr"]`

Specifies where logs should be written:

- `"stderr"`: Write to standard error (console output)
- `"file"`: Write to a file (requires `file_path`)
- Both can be specified for simultaneous console and file logging

#### File Path

**Field**: `file_path`  
**Type**: `string`  
**Required**: Yes, if `handlers` includes `"file"`  
**Default**: N/A

Absolute or relative path where log files should be written. Watchgate will automatically create directories if they don't exist.

Examples:
```yaml
file_path: "logs/watchgate.log"                    # Relative path
file_path: "/var/log/watchgate/watchgate.log"     # Absolute path
file_path: "app/logs/detailed/watchgate.log"       # Nested directories
```

#### File Rotation

**Field**: `max_file_size_mb`  
**Type**: `integer`  
**Required**: No  
**Default**: `10`

Maximum size of the log file in megabytes before rotation. When reached, the current file is renamed to `.log.1` and a new log file is started.

**Field**: `backup_count`  
**Type**: `integer`  
**Required**: No  
**Default**: `5`

Number of backup log files to keep. Files are named `.log.1`, `.log.2`, etc. Files older than this count are automatically deleted.

#### Format

**Field**: `format`  
**Type**: `string`  
**Required**: No  
**Default**: `"%(asctime)s [%(levelname)s] %(name)s: %(message)s"`

Python logging format string for log messages. Available placeholders:

- `%(asctime)s` - Timestamp
- `%(levelname)s` - Log level (INFO, WARNING, etc.)
- `%(name)s` - Component name (which part of Watchgate logged the message)
- `%(message)s` - The actual log message
- `%(funcName)s` - Function name where log was created
- `%(lineno)d` - Line number where log was created
- `%(process)d` - Process ID

Common format examples:
```yaml
# Standard format (default)
format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

# Detailed debugging format
format: "%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d: %(message)s"

# Minimal format  
format: "[%(levelname)s] %(message)s"

# Structured format for log parsing
format: "%(asctime)s|%(levelname)s|%(name)s|%(message)s"
```

#### Date Format

**Field**: `date_format`  
**Type**: `string`  
**Required**: No  
**Default**: `"%Y-%m-%d %H:%M:%S"`

Python strftime format string for timestamps in log messages.

Common date format examples:
```yaml
date_format: "%Y-%m-%d %H:%M:%S"           # 2024-06-15 14:30:22
date_format: "%Y-%m-%dT%H:%M:%S.%f"        # 2024-06-15T14:30:22.123456
date_format: "%Y-%m-%dT%H:%M:%S.%fZ"       # 2024-06-15T14:30:22.123456Z (ISO with timezone)
date_format: "%b %d %H:%M:%S"              # Jun 15 14:30:22 (syslog style)
```

#### Complete Logging Examples

**Console only (default behavior):**
```yaml
logging:
  level: "INFO"
  handlers: ["stderr"]
```

**File only:**
```yaml
logging:
  level: "INFO"
  handlers: ["file"]
  file_path: "logs/watchgate.log"
```

**Both console and file:**
```yaml
logging:
  level: "INFO"
  handlers: ["stderr", "file"]
  file_path: "logs/watchgate.log"
  max_file_size_mb: 20
  backup_count: 10
```

**Production configuration:**
```yaml
logging:
  level: "INFO"
  handlers: ["file"]
  file_path: "/var/log/watchgate/watchgate.log"
  max_file_size_mb: 50
  backup_count: 10
  format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
```

**Debug configuration:**
```yaml
logging:
  level: "DEBUG"
  handlers: ["stderr", "file"]
  file_path: "logs/debug.log"
  format: "%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d: %(message)s"
```

## Complete Configuration Example

```yaml
# Complete Watchgate configuration example
proxy:
  # Transport configuration
  transport: "stdio"
  
  # Upstream MCP server
  upstream:
    command: "npx @modelcontextprotocol/server-filesystem /Users/username/Documents"
    restart_on_failure: true
    max_restart_attempts: 5
  
  # Timeout settings
  timeouts:
    connection_timeout: 30
    request_timeout: 120
  
  # Plugin configuration
  plugins:
    # Security plugins
    security:
      _global:
        - policy: "tool_allowlist"
          enabled: true
          config:
            mode: "allowlist"
            tools:
              - "read_file"
              - "write_file"
              - "create_directory"
              - "list_directory"
            block_message: "Tool access denied by security policy"
    
    # Auditing plugins
    auditing:
      _global:
        - policy: "json_auditing"
          enabled: true
          config:
            output_file: "~/.config/watchgate/logs/audit.log"
            max_file_size_mb: 10
            backup_count: 5
            mode: "all_events"

# Logging configuration example
logging:
  level: "DEBUG"
  handlers: ["stderr", "file"]
  file_path: "logs/debug.log"
  max_file_size_mb: 20
  backup_count: 10
  format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
```

## HTTP Transport Example

For HTTP transport, include the `http` section:

```yaml
proxy:
  transport: "http"
  
  upstream:
    command: "python -m my_mcp_server"
  
  timeouts:
    connection_timeout: 30
    request_timeout: 60
  
  # HTTP server configuration (required for HTTP transport)
  http:
    host: "0.0.0.0"
    port: 9090
```

## Built-in Plugin Configurations

### Tool Access Control Plugin

The `tool_allowlist` plugin controls access to tools in both `tools/call` requests and `tools/list` responses. It ensures consistent security policy enforcement across both tool execution and tool discovery.

```yaml
- policy: "tool_allowlist"
  config:
    mode: "allowlist"  # "allowlist", "blocklist", or "allow_all"
    tools:
      - "read_file"
      - "write_file"
    block_message: "Custom blocked message"
```

**Configuration Options:**

- `mode`: Controls how the plugin operates
  - `"allowlist"`: Only specified tools are allowed (both for calls and in list responses)
  - `"blocklist"`: All tools except specified ones are allowed
  - `"allow_all"`: All tools are allowed (no filtering applied)
- `tools`: List of tool names to allow (allowlist mode) or block (blocklist mode)
- `block_message`: Custom message when blocking tool calls (optional)
- `priority`: Plugin execution priority (optional, range: 0-100, default: 50, lower numbers = higher priority)

**Behavior:**

- **For `tools/call` requests**: Blocks calls to tools not allowed by the policy
- **For `tools/list` responses**: Filters the response to only show allowed tools
- **Other requests**: No filtering applied

**Example Filtered Response:**

If upstream returns 5 tools but only 2 are in the allowlist:
```json
{
  "jsonrpc": "2.0", 
  "id": "123",
  "result": {
    "tools": [
      {"name": "read_file", "description": "Read file content"},
      {"name": "write_file", "description": "Write file content"}
    ]
  }
}
```

**Plugin Execution Order:**

Plugins support configurable execution ordering through priority:

```yaml
- policy: "tool_allowlist"
  config:
    mode: "allowlist"
    tools: ["read_file", "write_file"]
    priority: 10  # Range: 0-100, lower numbers = higher priority (execute first)
```

### Filesystem Server Security Plugin

The `filesystem_server` plugin provides granular path-based access control for the `@modelcontextprotocol/server-filesystem` MCP server. This plugin understands filesystem operations and can enforce different permission levels (read, write) on different file paths using glob patterns.

```yaml
- policy: "filesystem_server"
  config:
    read: ["docs/*", "public/**/*.txt", "!docs/secret*"]
    write: ["uploads/*", "temp/*.tmp", "archive/**/*"]
    priority: 20
```

**Configuration Options:**

- `read`: List of glob patterns for read operations (read_file, list_directory, search_files, get_file_info, list_allowed_directories)
- `write`: List of glob patterns for write operations (write_file, edit_file, create_directory, move_file)
- `priority`: Plugin execution priority (optional, range: 0-100, default: 50)

**Supported Filesystem Tools:**
- Read operations: `read_file`, `read_multiple_files`, `list_directory`, `search_files`, `get_file_info`, `list_allowed_directories`
- Write operations: `write_file`, `edit_file`, `create_directory`, `move_file`

**Note**: These are the specific tool names used by `@modelcontextprotocol/server-filesystem`. Other filesystem servers may use different tool names.

**Pattern Matching:**
- Uses gitignore-style glob patterns (gitwildmatch)
- Supports recursive patterns with `**`
- Supports negative patterns with `!` prefix for exclusions
- Patterns are relative to the filesystem server's allowed directories

**Security Model:**
- Default deny: If no permission is configured for a tool's required level, access is denied
- Path extraction: Automatically extracts paths from different tool argument structures
- Multi-path validation: For tools like `move_file`, validates both source and destination paths
- Empty config behavior: Empty configuration denies all filesystem operations

**Example Use Cases:**

1. **Documentation Access**: Allow reading documentation but prevent writes
```yaml
config:
  read: ["docs/**/*", "README.md"]
```

2. **Sandboxed Development**: Allow full access to project directory but exclude sensitive areas
```yaml
config:
  read: ["project/**/*", "!project/secrets/*", "!project/.env*"]
  write: ["project/src/**/*", "project/tests/**/*", "project/temp/**/*"]
```

3. **Content Management**: Allow uploads and editing in specific areas
```yaml
config:
  read: ["content/**/*", "assets/**/*"]
  write: ["content/drafts/**/*", "uploads/**/*", "content/archive/**/*"]
```

### PII Filter Plugin

The `pii` plugin detects and filters personally identifiable information (PII) in MCP communications with configurable actions and comprehensive pattern matching.

```yaml
- policy: "pii"
  config:
    action: "redact"  # "block", "redact", or "audit_only"
    pii_types:
      credit_card: {"enabled": true}
      email: {"enabled": true}
      phone: {"enabled": true}
      ip_address: {"enabled": true}
      national_id: {"enabled": true}
    exemptions:
      tools: ["trusted_tool"]
      paths: ["safe/path/*"]
```

**Configuration Options:**

- `action`: Controls how PII is handled when detected
  - `"block"`: Prevents transmission of any content containing PII
  - `"redact"`: Replaces PII with placeholder text like `[EMAIL REDACTED by Watchgate]`
  - `"audit_only"`: Logs PII detections but allows content to pass through unchanged
- `pii_types`: Configures which types of PII to detect
  - `credit_card`: **Credit card numbers with Luhn validation** (Visa, MasterCard, AmEx, Discover)
  - `email`: Email addresses (RFC 5322 compliant)
  - `phone`: Phone numbers (US, UK, international formats)
  - `ip_address`: IP addresses (IPv4 and IPv6)
  - `national_id`: National ID numbers (US SSN, UK National Insurance, Canadian SIN)
- `exemptions`: Tools or paths that bypass PII filtering
- `scan_base64`: Whether to scan base64-encoded content (default: `false`)
- `priority`: Plugin execution priority (optional, range: 0-100, default: 50)

**Credit Card Detection Behavior:**

The plugin uses **Luhn algorithm validation** for credit card detection to reduce false positives. This means:

- ✅ **Valid credit cards are detected**: Numbers that pass Luhn validation (e.g., `4532015112830366`)
- ❌ **Invalid credit cards are NOT detected**: Random 16-digit numbers that fail Luhn validation (e.g., `4532123456789012`)
- 🔒 **Security benefit**: Prevents false positives from random numbers that happen to match credit card patterns

**Example Detection Results:**
```yaml
# These will be detected and handled according to your action setting:
"4532 0151 1283 0366"  # Valid Visa (passes Luhn)
"5555 5555 5555 4444"  # Valid MasterCard (passes Luhn)

# These will NOT be detected (invalid Luhn checksums):
"4532 1234 5678 9012"  # Invalid Visa
"5555 4444 3333 2222"  # Invalid MasterCard
```

**PII Type Format Configuration:**

Most PII types support format-specific detection:

```yaml
pii_types:
  phone:
    enabled: true
    formats: ["us", "international"]  # Specific formats
  # OR
  phone: {"enabled": true}  # Automatically detects all formats
```

**Common Use Cases:**

1. **Basic PII Protection** (redact sensitive data):
```yaml
config:
  action: "redact"
  pii_types:
    credit_card: {"enabled": true}
    email: {"enabled": true}
    national_id: {"enabled": true}
```

2. **Strict Security** (block any PII):
```yaml
config:
  action: "block"
  pii_types:
    credit_card: {"enabled": true}
    email: {"enabled": true}
    phone: {"enabled": true}
```

3. **Compliance Monitoring** (log but allow):
```yaml
config:
  action: "audit_only"
  pii_types:
    credit_card: {"enabled": true}
    email: {"enabled": true}
```

**Base64 Content Handling:**

By default, the PII filter skips scanning base64-encoded content to prevent corruption of binary data (like images from screenshot tools). This is controlled by the `scan_base64` option:

- `scan_base64: false` (default): Base64 content is skipped entirely, preventing binary data corruption
- `scan_base64: true`: Base64 content is scanned like regular text, which may corrupt binary data if PII patterns are found

**Important Security Trade-off:**
- **Default behavior (safer)**: Protects binary data integrity but may miss PII encoded in base64
- **Enabled scanning (riskier)**: Catches PII in base64 but may break screenshot tools and other binary data

```yaml
# Safe for binary data (default)
config:
  scan_base64: false
  action: "redact"

# Scan base64 content (may break binary data)
config:
  scan_base64: true
  action: "redact"
```

### Secrets Filter Plugin

The `secrets` plugin detects and filters well-known secrets, tokens, and credentials in MCP communications using high-confidence regex patterns and conservative entropy analysis.

```yaml
- policy: "secrets"
  config:
    action: "block"  # "block", "redact", or "audit_only"
    secret_types:
      aws_access_keys: {"enabled": true}
      github_tokens: {"enabled": true}
      google_api_keys: {"enabled": true}
      jwt_tokens: {"enabled": true}
      ssh_private_keys: {"enabled": true}
      aws_secret_keys: {"enabled": false}  # Higher false positive risk
    entropy_detection:
      enabled: true
      min_entropy: 5.5
      min_length: 32
      max_length: 200
    base64_detection:
      enabled: false  # Default: skip base64 to prevent binary data corruption
      min_length: 100
      detect_file_signatures: true
      strict_mode: false
    exemptions:
      tools: ["trusted_tool"]
      paths: ["safe/path/*"]
```

**Configuration Options:**

- `action`: Controls how secrets are handled when detected
  - `"block"`: Prevents transmission of any content containing secrets
  - `"redact"`: Replaces secrets with placeholder text like `[AWS_ACCESS_KEY REDACTED by Watchgate]`
  - `"audit_only"`: Logs secret detections but allows content to pass through unchanged
- `secret_types`: Configures which types of secrets to detect
  - `aws_access_keys`: AWS Access Keys (AKIA-prefixed patterns)
  - `github_tokens`: GitHub Personal Access Tokens (ghp_, gho_, ghu_, ghs_, ghr_ prefixes)
  - `google_api_keys`: Google API Keys (AIza-prefixed patterns)
  - `jwt_tokens`: JWT Tokens (three-part base64url structure)
  - `ssh_private_keys`: SSH Private Keys (PEM format headers)
  - `aws_secret_keys`: AWS Secret Keys (entropy-based, disabled by default due to false positives)
- `entropy_detection`: Conservative Shannon entropy analysis for unknown secrets
- `base64_detection`: Controls scanning of base64-encoded content
- `exemptions`: Tools or paths that bypass secrets filtering
- `priority`: Plugin execution priority (optional, range: 0-100, default: 50)

**Base64 Content Handling:**

By default, the secrets filter skips scanning base64-encoded content to prevent corruption of binary data. This is controlled by the `base64_detection.enabled` option:

- `enabled: false` (default): Base64 content is skipped entirely, preventing binary data corruption
- `enabled: true`: Base64 content is decoded and scanned, which may corrupt binary data if secrets are found

**Important Security Trade-off:**
- **Default behavior (safer)**: Protects binary data integrity but may miss secrets encoded in base64
- **Enabled scanning (riskier)**: Catches secrets in base64 but may break screenshot tools and other binary data

```yaml
# Safe for binary data (default)
config:
  base64_detection:
    enabled: false
  action: "block"

# Scan base64 content (may break binary data)
config:
  base64_detection:
    enabled: true
    min_length: 100
    detect_file_signatures: true
  action: "block"
```

**Common Use Cases:**

1. **Basic Secrets Protection** (block all secrets):
```yaml
config:
  action: "block"
  secret_types:
    aws_access_keys: {"enabled": true}
    github_tokens: {"enabled": true}
    google_api_keys: {"enabled": true}
```

2. **Development Environment** (redact secrets):
```yaml
config:
  action: "redact"
  secret_types:
    aws_access_keys: {"enabled": true}
    github_tokens: {"enabled": true}
    jwt_tokens: {"enabled": true}
```

3. **Audit Only** (log but allow):
```yaml
config:
  action: "audit_only"
  entropy_detection:
    enabled: true
    min_entropy: 5.0
```

### Auditing Plugins

Watchgate supports multiple auditing formats. Choose the format that best fits your monitoring and compliance needs:

```yaml
# JSON format (machine-readable)
- policy: "json_auditing"
  config:
    output_file: "audit.json"
    max_file_size_mb: 10
    backup_count: 5
    mode: "all_events"  # "security_only", "operations_only", or "all_events"
    critical: false   # true = Watchgate fails if plugin fails, false = graceful failure

# Line format (human-readable)
- policy: "line_auditing"
  config:
    output_file: "audit.log"
    max_file_size_mb: 10
    backup_count: 5
    mode: "all_events"
    critical: false

# CSV format (spreadsheet-compatible)
- policy: "csv_auditing"
  config:
    output_file: "audit.csv"
    max_file_size_mb: 10
    backup_count: 5
    mode: "all_events"
    critical: false

# Debug format (detailed)
- policy: "debug_auditing"
  config:
    output_file: "debug.log"
    max_file_size_mb: 10
    backup_count: 5
    mode: "all_events"
    critical: false
```

**Common Configuration Options** (all auditing plugins):

- `output_file`: Path to the audit log file
- `max_file_size_mb`: Maximum log file size before rotation (MB)
- `backup_count`: Number of rotated log files to keep
- `mode`: Controls what events get logged:
  - `"security_only"`: Only security-sensitive events (blocks, violations, errors, tool calls)
  - `"operations_only"`: Only successful operations (allowed calls, normal responses)
  - `"all_events"`: Everything (security events + operations + debug information)
- `critical`: Controls plugin failure behavior:
  - `true`: If this plugin fails, Watchgate blocks MCP communications (compliance mode)
  - `false`: If this plugin fails, Watchgate continues gracefully (default)

**Plugin Failure Behavior:**

The `critical` parameter determines what happens when the auditing plugin encounters an error:

```yaml
# Development/General Use - Don't break workflow on audit failures
config:
  critical: false  # Default: graceful failure

# Regulated/Compliance Environments - Audit failures must halt processing
config:
  critical: true   # Security precaution: Block MCP communications if auditing fails
```

**Use Cases:**
- **`critical: false`**: Development, testing, general use where auditing is helpful but not mandatory
- **`critical: true`**: Regulated industries, compliance requirements, environments where complete audit trails are legally required

**CSV Plugin Configuration:**

The `csv_auditing` plugin supports additional compliance and formatting options:

```yaml
- policy: "csv_auditing"
  config:
    output_file: "audit.csv"
    max_file_size_mb: 10
    backup_count: 5
    mode: "all_events"
    critical: false
    csv_config:
      delimiter: ","              # Field delimiter
      quote_style: "minimal"      # "minimal", "all", "nonnumeric", "none"
      quote_char: '"'             # Quote character
      null_value: ""              # How to represent null values
      include_compliance_columns: true  # Include compliance metadata
      audit_trail_format: "standard"   # "SOX_404", "GDPR", "standard"
      regulatory_schema: "default"     # "financial_services", "default"
```

**CSV Format Example Output:**
```csv
timestamp,event_type,method,tool,status,request_id,plugin,reason,duration_ms,server_name
2024-06-16T10:30:15Z,REQUEST,tools/call,read_file,ALLOWED,123,tool_allowlist,Request approved,,
2024-06-16T10:30:16Z,RESPONSE,,,success,123,,,150,
2024-06-16T10:30:45Z,SECURITY_BLOCK,tools/call,delete_file,BLOCKED,124,tool_allowlist,Tool not in allowlist,,
```

**CSV Format Benefits:**
- **Spreadsheet compatibility**: Direct import into Excel, Google Sheets, LibreOffice Calc
- **Data analysis**: Easy analysis with pandas, R, or other data tools
- **Business intelligence**: Import into BI tools like Tableau or Power BI
- **Compliance reporting**: Structured format for regulatory reporting
- **Standard format**: RFC 4180 compliant CSV with proper escaping

## Configuration Validation

Watchgate validates the configuration when loading:

1. **Required sections**: `proxy`, `upstream`, `timeouts` must be present
2. **Transport validation**: If `transport` is `"http"`, the `http` section is required
3. **Type validation**: All fields must be the correct type
4. **Value validation**: Numeric fields must be within valid ranges
5. **Plugin validation**: Plugin policies must exist and be available for loading

## Environment Variable Overrides

Configuration values can be overridden using environment variables with the prefix `AG_`:

```bash
# Override connection timeout
export AG_PROXY_TIMEOUTS_CONNECTION_TIMEOUT=60

# Disable a plugin
export AG_PROXY_PLUGINS_SECURITY_0_ENABLED=false

# Change HTTP port
export AG_PROXY_HTTP_PORT=9090
```

The environment variable format follows the nested structure of the YAML configuration, with underscores separating levels and array indices as numbers.

## Configuration File Locations

Watchgate looks for configuration files in the following order:

1. Path specified with `--config` argument
2. `./watchgate.yaml` (current directory)
3. `~/.config/watchgate/config.yaml`
4. `/etc/watchgate/config.yaml`

## Troubleshooting Configuration

### Common Issues

1. **Missing proxy section**: Ensure your configuration has a top-level `proxy` section
2. **Invalid YAML syntax**: Check for proper indentation and syntax
3. **Plugin path errors**: Verify plugin policies exist and are available
4. **Transport mismatch**: Include `http` section when using HTTP transport
5. **Timeout values**: Ensure timeout values are positive integers

### Validation Errors

Watchgate provides detailed error messages for configuration issues:

```
ValueError: Configuration must contain 'proxy' section
ValueError: HTTP transport requires http configuration
ValueError: Timeout values must be positive
```

Use the `--verbose` flag for detailed debugging information:

```bash
watchgate --config config.yaml --verbose
```
