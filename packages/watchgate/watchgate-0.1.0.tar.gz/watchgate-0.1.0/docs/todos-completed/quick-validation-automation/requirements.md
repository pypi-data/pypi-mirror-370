# Quick Validation Automation Requirements

## Critical Diagnostic Information

### Log File Locations for Troubleshooting

When validation fails or errors occur, Claude (or another assistant) will need to examine these log files to diagnose the problem:

#### Claude Desktop Logs
**macOS** (User: dbright):
```bash
# Claude Desktop configuration
/Users/dbright/Library/Application Support/Claude/claude_desktop_config.json

# MCP connection logs
/Users/dbright/Library/Logs/Claude/mcp.log
```

**macOS** (General paths):
```bash
# Claude Desktop configuration
~/Library/Application Support/Claude/claude_desktop_config.json

# MCP connection logs
~/Library/Logs/Claude/mcp.log
```

**Linux**:
```bash
# Claude Desktop configuration
~/.config/Claude/claude_desktop_config.json

# MCP connection logs
~/.config/Claude/logs/mcp.log
```

**Windows**:
```bash
# Claude Desktop configuration
%APPDATA%\Claude\claude_desktop_config.json

# MCP connection logs
%APPDATA%\Claude\logs\mcp.log
```

#### Watchgate Logs
```bash
# Main Watchgate debug log (configured in test-config.yaml)
tests/validation/logs/validation.log

# Audit logs for each format
tests/validation/logs/validation-line.log
tests/validation/logs/validation-debug.log
tests/validation/logs/validation-json.jsonl
tests/validation/logs/validation-csv.csv
tests/validation/logs/validation-cef.log
tests/validation/logs/validation-syslog.log
tests/validation/logs/validation-otel.jsonl
```

### Diagnostic Commands for Claude

**Note**: Claude can detect the platform from the environment. Look for `Platform: darwin` (macOS), `Platform: linux`, or `Platform: win32` (Windows) in your environment context. For user dbright on macOS, use the `/Users/dbright/` paths directly.

When asked to diagnose validation problems, use these commands:

```bash
# 1. Check if Watchgate process is running
ps aux | grep watchgate

# 2. Check Claude Desktop configuration
cat /Users/dbright/Library/Application\ Support/Claude/claude_desktop_config.json | jq '.mcpServers.watchgate'

# 3. Check MCP connection logs for errors
tail -50 /Users/dbright/Library/Logs/Claude/mcp.log | grep -E "ERROR|WARN|watchgate"

# 4. Check Watchgate debug log for startup issues
tail -100 tests/validation/logs/validation.log | grep -E "ERROR|CRITICAL|Failed"

# 5. Check if audit log files exist
ls -la tests/validation/logs/validation-*.{log,csv,jsonl} 2>/dev/null

# 6. Check last error in each audit log
for f in tests/validation/logs/validation-*; do
  echo "=== $f ==="
  tail -3 "$f" 2>/dev/null || echo "File not found"
done

# 7. Check for permission issues
ls -la tests/validation/logs/
stat tests/validation/logs/

# 8. Check disk space
df -h tests/validation/logs/
```

### Common Error Patterns to Look For

When examining logs, search for these patterns:

1. **Connection Errors**:
   - `"error": "ECONNREFUSED"`
   - `"Failed to connect to upstream"`
   - `"Server disconnected"`

2. **Configuration Errors**:
   - `"Invalid configuration"`
   - `"Plugin not found"`
   - `"YAML parsing error"`

3. **Permission Errors**:
   - `"Permission denied"`
   - `"Cannot write to file"`
   - `"Directory does not exist"`

4. **Plugin Loading Errors**:
   - `"Failed to load plugin"`
   - `"Unknown policy"`
   - `"Plugin initialization failed"`

5. **Format-Specific Errors**:
   - `"Invalid format specification"`
   - `"Encoding error"`
   - `"Serialization failed"`

### Diagnostic Workflow

When user reports validation failure:

1. **First, check process status**:
   ```bash
   ps aux | grep watchgate  # Is it running?
   ```

2. **Check Claude Desktop sees Watchgate**:
   ```bash
   # Look for connection errors
   tail -50 /Users/dbright/Library/Logs/Claude/mcp.log
   ```

3. **Check Watchgate startup**:
   ```bash
   # Look for plugin loading errors
   head -50 tests/validation/logs/validation.log
   ```

4. **Check specific format that failed**:
   ```bash
   # If CEF validation failed, check:
   tail -10 tests/validation/logs/validation-cef.log
   ```

5. **Provide diagnosis** with specific error and suggested fix

## Overview

### Purpose
Create an automated validation system that allows users to quickly verify that all 7 auditing plugin formats are working correctly with minimal manual effort. The validation should complete in under 30 seconds and provide clear pass/fail indicators for each format.

### Current State
- **Problem**: Users must manually validate each auditing format individually, which is time-consuming and error-prone
- **Impact**: Validation takes 45+ minutes and requires deep knowledge of each format
- **Solution**: Automated script that validates all formats in parallel with third-party validators

### Success Criteria
1. ✅ All 7 auditing formats generate valid log files
2. ✅ Validation completes in <30 seconds
3. ✅ Clear pass/fail output for each format
4. ✅ Uses trusted third-party validators where available
5. ✅ Single command execution
6. ✅ Works on macOS, Linux, and WSL

## Implementation Requirements

### Part A: Configuration File Updates

#### File to Modify: `tests/validation/test-config.yaml`

**IMPORTANT**: Do NOT rename or create a new config file. Modify the existing `test-config.yaml` in place.

**Location in File**: Find the `auditing:` section under `plugins:` and replace the entire `_global:` subsection with the following configuration:

```yaml
  auditing:
    # Global auditing applies to all servers
    _global:
      # Line format - human-readable single line
      - policy: "line_auditing"
        enabled: true
        config:
          output_file: "logs/validation-line.log"
          max_file_size_mb: 5
          backup_count: 3
          critical: false
      
      # Debug format - detailed debugging output
      - policy: "debug_auditing"
        enabled: true
        config:
          output_file: "logs/validation-debug.log"
          max_file_size_mb: 5
          backup_count: 3
          critical: false
      
      # JSON format - structured JSON Lines
      - policy: "json_auditing"
        enabled: true
        config:
          output_file: "logs/validation-json.jsonl"
          pretty_print: false  # Must be false for JSONL format
          include_request_body: true
          critical: false
      
      # CSV format - comma-separated values
      - policy: "csv_auditing"
        enabled: true
        config:
          output_file: "logs/validation-csv.csv"
          csv_config:
            delimiter: ","
            quote_char: "\""
            include_headers: true
          critical: false
      
      # CEF format - Common Event Format for SIEM
      - policy: "cef_auditing"
        enabled: true
        config:
          output_file: "logs/validation-cef.log"
          cef_config:
            device_vendor: "Watchgate"
            device_product: "MCP-Proxy"
            device_version: "0.1.0"
          critical: false
      
      # Syslog format - RFC5424 syslog
      - policy: "syslog_auditing"
        enabled: true
        config:
          output_file: "logs/validation-syslog.log"
          syslog_config:
            rfc_format: "5424"
            facility: 16
            hostname: "watchgate-validator"
          critical: false
      
      # OpenTelemetry format - OTLP traces
      - policy: "otel_auditing"
        enabled: true
        config:
          output_file: "logs/validation-otel.jsonl"
          service_name: "watchgate-validation"
          service_version: "0.1.0"
          deployment_environment: "validation"
          critical: false
```

**Validation After Edit**: 
- Ensure YAML indentation is exactly 2 spaces per level
- Ensure all 7 policies are listed
- Ensure all output files go to `logs/` directory
- Run `python3 -c "import yaml; yaml.safe_load(open('tests/validation/test-config.yaml'))"` to verify YAML syntax

### Part B: Validation Script Creation

#### File to Create: `tests/validation/validate_all_formats.sh`

**Location**: `tests/validation/validate_all_formats.sh`

**Permissions**: Must be executable (`chmod +x validate_all_formats.sh`)

**Complete Script Content**:

```bash
#!/bin/bash

# Quick Validation Script for Watchgate Auditing Formats
# This script validates all 7 auditing plugin formats
# Exit codes: 0 = all pass, 1 = one or more failures

set -e  # Exit on first error

# Colors for output (works on macOS, Linux, WSL)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track validation results
TOTAL_FORMATS=7
PASSED_FORMATS=0
FAILED_FORMATS=0

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "pass" ]; then
        echo -e "${GREEN}✓${NC} $message"
        ((PASSED_FORMATS++))
    elif [ "$status" = "fail" ]; then
        echo -e "${RED}✗${NC} $message"
        ((FAILED_FORMATS++))
    else
        echo -e "${YELLOW}⚠${NC} $message"
    fi
}

# Function to check if file exists and has content
check_file_exists() {
    local file=$1
    local format=$2
    
    if [ ! -f "$file" ]; then
        print_status "fail" "$format: File not found at $file"
        return 1
    fi
    
    if [ ! -s "$file" ]; then
        print_status "fail" "$format: File exists but is empty"
        return 1
    fi
    
    return 0
}

echo "════════════════════════════════════════════════════════════"
echo "     Watchgate Auditing Format Validation"
echo "════════════════════════════════════════════════════════════"
echo ""

# Change to validation directory
cd "$(dirname "$0")"

# MANDATORY: Clean up old logs to avoid stale data
echo "Cleaning old validation logs..."
rm -f logs/validation-*.log logs/validation-*.csv logs/validation-*.jsonl 2>/dev/null
echo "✓ Old logs cleaned"
echo ""

# 0. Check Plugin Loading (from debug log)
echo "0. Plugin Load Verification"
if [ -f "logs/validation.log" ]; then
    # Check that all auditing plugins loaded successfully
    missing_plugins=""
    for plugin in "line_auditing" "debug_auditing" "json_auditing" "csv_auditing" "cef_auditing" "syslog_auditing" "otel_auditing"; do
        if ! grep -q "Loaded $plugin" logs/validation.log 2>/dev/null; then
            missing_plugins="$missing_plugins $plugin"
        fi
    done
    
    if [ -z "$missing_plugins" ]; then
        print_status "pass" "All auditing plugins loaded successfully"
    else
        print_status "fail" "Missing plugins:$missing_plugins"
    fi
else
    print_status "warn" "Debug log not found - cannot verify plugin loading"
fi
echo ""

# 1. Validate Line Format
echo "1. Line Format Validation"
if check_file_exists "logs/validation-line.log" "Line"; then
    # Check for proper line format (timestamp, level, event) in last 20 lines
    if tail -20 logs/validation-line.log | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}.*\[.*\].*EVENT_TYPE:'; then
        print_status "pass" "Line format: Valid format detected"
    else
        print_status "fail" "Line format: Invalid format structure"
    fi
fi
echo ""

# 2. Validate Debug Format
echo "2. Debug Format Validation"
if check_file_exists "logs/validation-debug.log" "Debug"; then
    # Check for debug format markers in last 20 lines
    if tail -20 logs/validation-debug.log | grep -qE 'timestamp=.*event_type=.*method='; then
        print_status "pass" "Debug format: Valid key-value format detected"
    else
        print_status "fail" "Debug format: Invalid format structure"
    fi
fi
echo ""

# 3. Validate JSON Format
echo "3. JSON Format Validation"
if check_file_exists "logs/validation-json.jsonl" "JSON"; then
    # Check if jq is available
    if command -v jq &> /dev/null; then
        # Validate JSON with jq (check last 20 lines)
        if tail -20 logs/validation-json.jsonl | jq '.' > /dev/null 2>&1; then
            # Additional check for required fields
            if tail -20 logs/validation-json.jsonl | jq -e '.timestamp and .event_type and .method' > /dev/null 2>&1; then
                print_status "pass" "JSON format: Valid JSON with required fields"
            else
                print_status "fail" "JSON format: Valid JSON but missing required fields"
            fi
        else
            print_status "fail" "JSON format: Invalid JSON structure"
        fi
    else
        # Fallback: Python JSON validation (check last 20 lines)
        if python3 -c "import json; [json.loads(line) for line in open('logs/validation-json.jsonl').readlines()[-20:]]" 2>/dev/null; then
            print_status "pass" "JSON format: Valid JSON (validated with Python)"
        else
            print_status "fail" "JSON format: Invalid JSON structure"
        fi
    fi
fi
echo ""

# 4. Validate CSV Format
echo "4. CSV Format Validation"
if check_file_exists "logs/validation-csv.csv" "CSV"; then
    # Check if pandas is available
    if python3 -c "import pandas" 2>/dev/null; then
        # Validate with pandas
        validation_result=$(python3 -c "
import pandas as pd
try:
    df = pd.read_csv('logs/validation-csv.csv')
    if len(df) > 0 and len(df.columns) > 5:
        print('VALID')
    else:
        print('INVALID: Not enough data')
except Exception as e:
    print(f'ERROR: {e}')
" 2>&1)
        
        if [[ "$validation_result" == "VALID" ]]; then
            print_status "pass" "CSV format: Valid CSV with proper structure (pandas)"
        else
            print_status "fail" "CSV format: $validation_result"
        fi
    else
        # Fallback: Basic CSV validation
        if python3 -c "import csv; list(csv.reader(open('logs/validation-csv.csv')))" 2>/dev/null; then
            print_status "pass" "CSV format: Valid CSV (basic validation)"
        else
            print_status "fail" "CSV format: Invalid CSV structure"
        fi
    fi
fi
echo ""

# 5. Validate CEF Format
echo "5. CEF (Common Event Format) Validation"
if check_file_exists "logs/validation-cef.log" "CEF"; then
    # Check if pycef is available
    if python3 -c "import pycef" 2>/dev/null; then
        # Validate with pycef
        validation_result=$(python3 -c "
import pycef
try:
    with open('logs/validation-cef.log') as f:
        last_lines = f.readlines()[-20:]
        valid_count = 0
        for line in last_lines:
            try:
                event = pycef.parse(line.strip())
                if event:
                    valid_count += 1
            except:
                pass
        if valid_count > 0:
            print('VALID')
        else:
            print('INVALID: Could not parse any lines')
except Exception as e:
    print(f'ERROR: {e}')
" 2>&1)
        
        if [[ "$validation_result" == "VALID" ]]; then
            print_status "pass" "CEF format: Valid CEF structure (pycef)"
        else
            print_status "fail" "CEF format: $validation_result"
        fi
    else
        # Fallback: Regex validation for CEF (check last 20 lines)
        if tail -20 logs/validation-cef.log | grep -qE '^CEF:[0-9]\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|[0-9]+\|'; then
            print_status "pass" "CEF format: Valid CEF structure (regex)"
        else
            print_status "fail" "CEF format: Invalid CEF structure"
        fi
    fi
fi
echo ""

# 6. Validate Syslog Format
echo "6. Syslog Format Validation"
if check_file_exists "logs/validation-syslog.log" "Syslog"; then
    # Check for RFC5424 format: <priority>version timestamp hostname app-name (check last 20 lines)
    if tail -20 logs/validation-syslog.log | grep -qE '^<[0-9]+>[0-9]+ [0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}'; then
        print_status "pass" "Syslog format: Valid RFC5424 format"
    # Check for RFC3164 format as fallback
    elif tail -20 logs/validation-syslog.log | grep -qE '^<[0-9]+>[A-Z][a-z]{2} [ 0-9][0-9] [0-9]{2}:[0-9]{2}:[0-9]{2}'; then
        print_status "pass" "Syslog format: Valid RFC3164 format"
    else
        print_status "fail" "Syslog format: Invalid syslog structure"
    fi
fi
echo ""

# 7. Validate OpenTelemetry Format
echo "7. OpenTelemetry Format Validation"
if check_file_exists "logs/validation-otel.jsonl" "OTEL"; then
    # Check if jq is available
    if command -v jq &> /dev/null; then
        # Validate OTLP structure with jq (check last 20 lines)
        if tail -20 logs/validation-otel.jsonl | head -1 | jq -e '.resourceSpans[0].resource.attributes' > /dev/null 2>&1; then
            print_status "pass" "OTEL format: Valid OTLP structure with traces"
        else
            print_status "fail" "OTEL format: Invalid OTLP structure"
        fi
    else
        # Fallback: Python validation for OTLP
        validation_result=$(python3 -c "
import json
try:
    with open('logs/validation-otel.jsonl') as f:
        last_lines = f.readlines()[-20:]
        valid_count = 0
        for line in last_lines:
            try:
                data = json.loads(line)
                if 'resourceSpans' in data and len(data['resourceSpans']) > 0:
                    valid_count += 1
            except:
                pass
        if valid_count > 0:
            print('VALID')
        else:
            print('INVALID: Missing resourceSpans in all lines')
except Exception as e:
    print(f'ERROR: {e}')
" 2>&1)
        
        if [[ "$validation_result" == "VALID" ]]; then
            print_status "pass" "OTEL format: Valid OTLP structure (Python)"
        else
            print_status "fail" "OTEL format: $validation_result"
        fi
    fi
fi
echo ""

# Summary
echo "════════════════════════════════════════════════════════════"
echo "                    Validation Summary"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Total Formats: $TOTAL_FORMATS"
echo -e "${GREEN}Passed: $PASSED_FORMATS${NC}"
echo -e "${RED}Failed: $FAILED_FORMATS${NC}"
echo ""

if [ $FAILED_FORMATS -eq 0 ]; then
    echo -e "${GREEN}✓ All auditing formats validated successfully!${NC}"
    exit 0
else
    echo -e "${RED}✗ Validation failed for $FAILED_FORMATS format(s)${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Ensure Watchgate is running with the test-config.yaml"
    echo "2. Trigger test events in Claude Desktop"
    echo "3. Check that all plugins are enabled in the config"
    echo "4. Review logs for error messages"
    exit 1
fi
```

### Part C: Test Event Prompts

#### File to Create: `tests/validation/test_prompts.md`

Content:
```markdown
# Test Event Prompts for Validation

Execute these prompts in Claude Desktop after starting Watchgate:

## 1. Tool Verification (VERIFY CONNECTION)
**Prompt**: "List all available tools and group them by server"
**Expected**: Two groups showing filesystem tools and sqlite tools
**You should NOT see**: Missing server groups or connection errors

## 2. Clean Operation (ALLOWED event)
**Prompt**: "Read the contents of clean.txt"
**Expected**: File content displayed normally
**You should NOT see**: Redaction markers or errors

## 3. PII Detection (REDACTED event)
**Prompt**: "Read personal-info.txt and show me exactly what you see"
**Expected**: Content with [EMAIL REDACTED by Watchgate], [NATIONAL_ID REDACTED by Watchgate] etc.
**You should NOT see**: Raw email addresses (smoke-test@example.com) or SSN (123-45-6789)

## 4. Security Block (BLOCKED event)
**Prompt**: "Read secrets.txt"
**Expected**: Error message about security policy violation
**You should NOT see**: ANY actual secret content or AWS keys

## 5. Database Query (ALLOWED event)
**Prompt**: "Show me the products table from the database"
**Expected**: Table data displayed normally
**You should NOT see**: Blocking or empty results

⚠️ VISUAL OVERRIDE RULE: If you SEE any raw SSN, email, or secret in Claude's UI despite the script passing, treat the entire validation as FAILED.

Total time: ~2 minutes
```

### Part D: Dependencies and Installation

#### Required Tools

Create a section in the script or a separate file documenting dependencies:

1. **Core Requirements** (must have):
   - `bash` (version 4.0+)
   - `python3` (version 3.8+)
   - `grep` (any version)
   - `tail` (any version)

2. **Optional Validators** (nice to have):
   - `jq` - JSON validator
     - macOS: `brew install jq`
     - Linux: `apt-get install jq` or `yum install jq`
     - Check: `command -v jq`
   
   - `pandas` - CSV validator
     - All platforms: `pip3 install pandas`
     - Check: `python3 -c "import pandas"`
   
   - `pycef` - CEF validator
     - All platforms: `pip3 install pycef`
     - Check: `python3 -c "import pycef"`

#### Fallback Validation Methods

If optional tools are not available:
- JSON: Use Python's built-in `json` module
- CSV: Use Python's built-in `csv` module
- CEF: Use regex pattern matching

### Part D: Test Event Prompts

#### File to Create: `tests/validation/test_prompts.md`

Content:
```markdown
# Test Event Prompts for Validation

Execute these prompts in Claude Desktop after starting Watchgate:

## 1. Clean Operation (ALLOWED event)
**Prompt**: "Read the contents of clean.txt"
**Expected**: File content displayed, all formats log ALLOWED event

## 2. PII Detection (REDACTED event)
**Prompt**: "Read personal-info.txt and show me what you see"
**Expected**: Content with [REDACTED] markers, formats log REDACTED event

## 3. Security Block (BLOCKED event)
**Prompt**: "Read secrets.txt"
**Expected**: Error message, all formats log BLOCKED event

## 4. Database Query (ALLOWED event)
**Prompt**: "Show me the products table from the database"
**Expected**: Table data displayed, all formats log ALLOWED event

Total time: ~2 minutes
```

## Implementation Checklist

The implementer MUST complete these tasks in order:

### Phase 1: Configuration (5 minutes)
- [ ] 1. Backup existing `tests/validation/test-config.yaml`
- [ ] 2. Add all 7 auditing plugin configurations to the file
- [ ] 3. Verify YAML syntax with Python
- [ ] 4. Ensure all output files use `logs/` directory prefix
- [ ] 5. Test configuration loads without errors

### Phase 2: Script Creation (10 minutes)
- [ ] 6. Create `tests/validation/validate_all_formats.sh`
- [ ] 7. Copy the complete script content exactly as provided
- [ ] 8. Make script executable: `chmod +x validate_all_formats.sh`
- [ ] 9. Test script runs without syntax errors (dry run)
- [ ] 10. Verify all 7 format checks are present

### Phase 3: Documentation (5 minutes)
- [ ] 11. Create `tests/validation/test_prompts.md`
- [ ] 12. Document the 4 test prompts
- [ ] 13. Add troubleshooting section to script
- [ ] 14. Update main validation guide to reference new script
- [ ] 15. Test complete workflow end-to-end

## Testing Instructions

### How to Test the Implementation

1. **Start Watchgate**:
   ```bash
   cd /path/to/watchgate
   watchgate --config tests/validation/test-config.yaml --verbose
   ```

2. **Open new terminal and clear old logs**:
   ```bash
   cd /path/to/watchgate/tests/validation
   rm -f logs/validation-*.log logs/validation-*.csv logs/validation-*.jsonl
   ```

3. **Restart Claude Desktop** and verify Watchgate connects

4. **Execute test prompts** from `test_prompts.md` in Claude Desktop

5. **Run validation script**:
   ```bash
   cd /path/to/watchgate/tests/validation
   ./validate_all_formats.sh
   ```

### Expected Output

```
════════════════════════════════════════════════════════════
     Watchgate Auditing Format Validation
════════════════════════════════════════════════════════════

1. Line Format Validation
✓ Line format: Valid format detected

2. Debug Format Validation
✓ Debug format: Valid key-value format detected

3. JSON Format Validation
✓ JSON format: Valid JSON with required fields

4. CSV Format Validation
✓ CSV format: Valid CSV with proper structure (pandas)

5. CEF (Common Event Format) Validation
✓ CEF format: Valid CEF structure (pycef)

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

## Error Handling Requirements

### Script Must Handle These Scenarios

1. **Missing Log Files**
   - Check file existence before validation
   - Report which specific files are missing
   - Continue validating other formats

2. **Empty Log Files**
   - Detect empty files separately from missing
   - Report as failure with clear message
   - Suggest user hasn't triggered events

3. **Missing Dependencies**
   - Check for optional tools (jq, pandas, pycef)
   - Use fallback validation methods
   - Report which validators were used

4. **Invalid Format Content**
   - Catch parsing errors gracefully
   - Report specific format violations
   - Show the problematic line if possible

5. **Permission Errors**
   - Check read permissions on log files
   - Report permission issues clearly
   - Suggest fixes (chmod, ownership)

## Success Criteria

The implementation is complete when:

1. ✅ All 7 auditing formats are configured in `test-config.yaml`
2. ✅ The validation script exists and is executable
3. ✅ Script validates all 7 formats in <30 seconds
4. ✅ Clear pass/fail output for each format
5. ✅ Exit code 0 for all pass, 1 for any failure
6. ✅ Works without optional dependencies (fallback validation)
7. ✅ Test prompts documentation exists
8. ✅ End-to-end test passes with all formats validated

## Notes for Implementer

### Critical Points
- **DO NOT** rename `test-config.yaml` - modify it in place
- **DO NOT** change the log file paths - keep them in `logs/` directory
- **DO NOT** skip the YAML syntax validation after editing
- **ALWAYS** test the script with both present and missing dependencies
- **ALWAYS** make the script executable with `chmod +x`

### Common Mistakes to Avoid
1. Incorrect YAML indentation (must be 2 spaces)
2. Missing quotes around special characters in YAML
3. Forgetting to make script executable
4. Not handling missing dependencies gracefully
5. Using relative paths instead of checking current directory

### Testing Your Implementation
After implementation, run this test sequence:
1. Clear all log files
2. Start Watchgate with the config
3. Run the 4 test prompts
4. Execute the validation script
5. Verify all 7 formats show as passed

If any format fails, check:
- Is the plugin enabled in the config?
- Did the test events get triggered?
- Is the log file being created?
- Is the format validator working correctly?

## Appendix: Format Specifications

### Line Format
- Single line per event
- Format: `TIMESTAMP [LEVEL] EVENT_TYPE: details`
- Example: `2024-01-10 10:30:00 [INFO] REQUEST: method=tools/call`

### Debug Format
- Key-value pairs separated by spaces
- Format: `timestamp=VALUE event_type=VALUE method=VALUE`
- Example: `timestamp=2024-01-10T10:30:00Z event_type=REQUEST method=tools/call`

### JSON Format (JSONL)
- One JSON object per line
- Required fields: `timestamp`, `event_type`, `method`
- Example: `{"timestamp":"2024-01-10T10:30:00Z","event_type":"REQUEST","method":"tools/call"}`

### CSV Format
- Comma-separated with headers
- Headers include: timestamp, event_type, method, status, etc.
- Properly escaped with quotes for special characters

### CEF Format
- Format: `CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extension`
- Example: `CEF:0|Watchgate|MCP-Proxy|0.1.0|100|Request|3|msg=Tool call`

### Syslog Format (RFC5424)
- Format: `<Priority>Version Timestamp Hostname App-name Procid Msgid StructuredData Msg`
- Example: `<134>1 2024-01-10T10:30:00.000Z watchgate watchgate - - [event@32473 type="REQUEST"] Tool call`

### OpenTelemetry Format
- OTLP JSON structure with traces
- Required: `resourceSpans` array with spans
- Contains trace context, span attributes, and events