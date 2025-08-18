# Watchgate Quick Validation Guide

## Overview

This guide provides a streamlined process to validate that all 7 Watchgate auditing formats are working correctly. The entire validation takes **under 5 minutes** and provides immediate pass/fail feedback for each format.

### What This Validates

The quick validation confirms that Watchgate's auditing system correctly logs security events in all supported formats:

1. **Line Format** - Human-readable single-line logs for operations teams
2. **Debug Format** - Detailed key-value pairs for troubleshooting  
3. **JSON Format** - Structured JSON Lines for API integration
4. **CSV Format** - Comma-separated values for compliance reporting
5. **CEF Format** - Common Event Format for SIEM integration
6. **Syslog Format** - RFC5424 syslog for centralized logging
7. **OpenTelemetry Format** - OTLP traces for observability platforms

### How It Works

1. Configure Claude Desktop to run Watchgate as an MCP server with all 7 auditing formats enabled
2. Execute 5 specific test prompts in Claude Desktop to generate different types of security events
3. Run the automated validation script that checks each format produced valid output
4. Get immediate pass/fail results with diagnostic information if issues are found

## Prerequisites

- Watchgate installed (`pip install -e .` or `uv pip install -e .`)
- Claude Desktop installed and running
- Terminal access to the Watchgate directory
- Node.js with npx available (for MCP test servers)

## Step 1: Configure Claude Desktop (One-Time Setup)

Watchgate runs as an MCP server within Claude Desktop. Edit your Claude Desktop configuration to set up Watchgate with the test configuration:

**macOS:**
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Linux:**
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

**Windows:**
```powershell
notepad %APPDATA%\Claude\claude_desktop_config.json
```

Add this configuration (adjust paths to your Watchgate installation):

```json
{
  "mcpServers": {
    "watchgate-validation": {
      "command": "watchgate",
      "args": ["--config", "/path/to/watchgate/tests/validation/validation-config.yaml", "--verbose"]
    }
  }
}
```

**Important Notes:**
- Replace `/path/to/watchgate/` with the absolute path to your Watchgate directory
- If `watchgate` is not in your PATH, use the full path to the command (e.g., `/path/to/watchgate/.venv/bin/watchgate`)
- Claude Desktop will start Watchgate automatically when it launches

## Step 2: Start the Validation Process

### 2.1 Clean Previous Validation Logs

Before starting validation, clean any old log files:

```bash
cd /path/to/watchgate/tests/validation
rm -f logs/validation-*.log logs/validation-*.csv logs/validation-*.jsonl
```

### 2.2 Restart Claude Desktop

Close and restart Claude Desktop to load the new configuration. Claude Desktop will automatically:
- Start Watchgate as a subprocess
- Load all 7 auditing plugins
- Connect to the upstream MCP servers (filesystem and SQLite)

You can verify Watchgate started correctly by checking if tools are available in Claude Desktop.

## Step 3: Execute Test Events

In Claude Desktop, execute these 5 prompts **in order** to generate the necessary security events:

### Prompt 1: Tool Verification
**Type this:** "List all available tools and group them by server"

**What to expect:** Under Watchgate server, you should see two groups of tools - filesystem tools and sqlite tools. This confirms Watchgate is properly connected.

### Prompt 2: Clean Operation (ALLOWED Event)
**Type this:** "Read the contents of clean.txt"

**What to expect:** The file contents display normally without any redactions or blocks. This generates an ALLOWED event in all audit logs.

### Prompt 3: PII Detection (REDACTED Event)  
**Type this:** "Read personal-info.txt and show me exactly what you see"

**What to expect:** You'll see content with redaction markers like:
- `[EMAIL REDACTED by Watchgate]` instead of email addresses
- `[NATIONAL_ID REDACTED by Watchgate]` instead of SSNs
- `[PHONE REDACTED by Watchgate]` instead of phone numbers

⚠️ **CRITICAL**: If you see any actual email (smoke-test@example.com) or SSN (123-45-6789), the validation has FAILED. Note that IP addresses are now not triggered in order to avoid false positives.

### Prompt 4: Security Block (BLOCKED Event)
**Type this:** "Read secrets.txt"

**What to expect:** An error message about security policy violation. You should NOT see any AWS keys or secret content.

### Prompt 5: Database Query (ALLOWED Event)
**Type this:** "Show me the products table from the database"

**What to expect:** Table data displays normally, generating another ALLOWED event with database context.

## Step 4: Run the Validation Script

After executing all 5 prompts, run the validation script:

```bash
cd /path/to/watchgate/tests/validation # ~/mcp/watchgate/tests/validation
./validate_all_formats.sh
```

## Step 5: Interpret Results

### Success Output

If everything is working correctly, you'll see:

```
════════════════════════════════════════════════════════════
     Watchgate Auditing Format Validation
════════════════════════════════════════════════════════════

✓ All auditing plugins loaded successfully

1. Line Format Validation
✓ Line format: Valid format detected

2. Debug Format Validation
✓ Debug format: Valid key-value format detected

3. JSON Format Validation
✓ JSON format: Valid JSON with required fields

4. CSV Format Validation
✓ CSV format: Valid CSV with proper structure

5. CEF (Common Event Format) Validation
✓ CEF format: Valid CEF structure

6. Syslog Format Validation
✓ Syslog format: Valid RFC5424 format

7. OpenTelemetry Format Validation
✓ OTEL format: Valid OTLP structure with traces

════════════════════════════════════════════════════════════
                    Validation Summary
════════════════════════════════════════════════════════════

Total Formats: 7
Passed: 7
Failed: 0

✓ All auditing formats validated successfully!
```

### Failure Scenarios

If any format fails, you'll see specific error messages:

```
✗ JSON format: File not found at logs/validation-json.jsonl
```

This typically means:
- **File not found**: The test events weren't executed or Watchgate isn't running
- **Invalid format**: The plugin is misconfigured or there's a bug
- **Empty file**: Events were generated but not written (check permissions)

## Troubleshooting

### Watchgate Won't Start

Check the configuration file syntax:
```bash
python3 -c "import yaml; yaml.safe_load(open('tests/validation/validation-config.yaml'))"
```

Check Claude Desktop's MCP logs to see startup errors:
```bash
# macOS
tail -50 ~/Library/Logs/Claude/mcp.log

# Linux
tail -50 ~/.config/Claude/logs/mcp.log

# Windows
type %APPDATA%\Claude\logs\mcp.log
```

### Claude Desktop Shows No Tools

1. Check that the path to `watchgate` command is correct in Claude Desktop config
2. Verify the validation-config.yaml path is absolute and correct
3. Check that Watchgate is installed (`which watchgate` or check your virtual environment)
4. Restart Claude Desktop after fixing configuration
5. Look for error messages in Claude Desktop's MCP logs (see above)

### Validation Script Reports Missing Files

1. Ensure Claude Desktop config includes the `--verbose` flag in args
2. Verify you executed all 5 test prompts in Claude Desktop
3. Check the logs directory exists and is writable:
   ```bash
   ls -la tests/validation/logs/
   ```
4. Check if Watchgate process is running within Claude Desktop:
   ```bash
   ps aux | grep watchgate
   ```

### Some Formats Pass, Others Fail

Check the Watchgate debug log for plugin-specific errors:
```bash
tail -50 tests/validation/logs/validation.log
```

Each format has different validation requirements:
- **JSON/OTEL**: Requires valid JSON structure
- **CSV**: Requires proper headers and delimiters
- **CEF**: Requires specific pipe-delimited format
- **Syslog**: Requires RFC5424 compliance

### Checking Raw Log Files

To manually inspect what's being generated:

```bash
# Check line format (human-readable)
tail -20 tests/validation/logs/validation-line.log

# Check JSON format (should be valid JSON Lines)
tail -5 tests/validation/logs/validation-json.jsonl | jq '.'

# Check CSV headers
head -2 tests/validation/logs/validation-csv.csv

# Check CEF format (pipe-delimited)
tail -5 tests/validation/logs/validation-cef.log

# Check syslog format (RFC5424)
tail -5 tests/validation/logs/validation-syslog.log
```

## Advanced: Understanding the Test Configuration

The `validation-config.yaml` used for validation:

1. **Configures 7 auditing plugins** simultaneously to test format generation
2. **Sets up 2 upstream MCP servers** (filesystem and SQLite) for realistic testing
3. **Enables security plugins** to generate different event types:
   - PII filter (redact mode) for REDACTED events
   - Secrets filter (block mode) for BLOCKED events
   - Tool allowlist for access control
4. **Uses separate log files** for each format to prevent interference

## Next Steps

### After Successful Validation

- All 7 auditing formats are working correctly
- You can confidently deploy Watchgate with your preferred auditing configuration
- Choose the format(s) that best integrate with your security infrastructure

### For Production Use

Select the auditing format(s) you need and configure them in your production `watchgate.yaml`:

```yaml
plugins:
  auditing:
    _global:
      # Choose one or more formats based on your needs
      - policy: "json_auditing"  # For API integration
        enabled: true
        config:
          output_file: "/var/log/watchgate/audit.jsonl"
      
      - policy: "cef_auditing"   # For SIEM integration
        enabled: true
        config:
          output_file: "/var/log/watchgate/audit.cef"
          cef_config:
            device_vendor: "YourCompany"
            device_product: "Watchgate"
```

## Quick Reference

### Complete Validation in 5 Minutes

```bash
# 1. Configure Claude Desktop (one-time setup)
# Add watchgate-validation to claude_desktop_config.json

# 2. Clean old logs
cd /path/to/watchgate/tests/validation
rm -f logs/validation-*

# 3. Restart Claude Desktop
# This starts Watchgate automatically

# 4. In Claude Desktop: Execute 5 test prompts (see Step 3)

# 5. Run validation script
cd /path/to/watchgate/tests/validation
./validate_all_formats.sh

# Success = All 7 formats show ✓
```

### Essential Files

- **Configuration**: `tests/validation/validation-config.yaml`
- **Validation Script**: `tests/validation/validate_all_formats.sh`
- **Log Output**: `tests/validation/logs/validation-*.{log,jsonl,csv}`
- **Test Files**: `tests/validation/test-files/` (clean.txt, personal-info.txt, secrets.txt)

## Support

If validation fails after following this guide:

1. Check the Watchgate debug log: `tail -50 tests/validation/logs/validation.log`
2. Verify all prerequisites are installed
3. Ensure you have write permissions to the logs directory
4. Review the test configuration for any customizations that might affect your environment

Remember: A successful validation means all 7 auditing formats are correctly capturing and formatting security events from Watchgate's plugin system.