# Implementation Guide for Quick Validation Automation

## Prerequisites Check

Before starting, verify you have the required tools:

```bash
# Check bash version (must be 4.0+)
bash --version

# Check Python (must be 3.8+)
python3 --version

# Check for grep and tail
which grep tail

# Optional: Check for validation tools
command -v jq && echo "jq installed" || echo "jq not installed (optional)"
python3 -c "import pandas" 2>/dev/null && echo "pandas installed" || echo "pandas not installed (optional)"
python3 -c "import pycef" 2>/dev/null && echo "pycef installed" || echo "pycef not installed (optional)"
```

## Step-by-Step Implementation

### Step 1: Navigate to Project Root

```bash
cd /path/to/watchgate
pwd  # Should show the watchgate project root
```

### Step 2: Backup Current Configuration

**CRITICAL**: Always backup before modifying configuration files.

```bash
# Create backup of current config
cp tests/validation/test-config.yaml tests/validation/test-config.yaml.backup

# Verify backup was created
ls -la tests/validation/test-config.yaml.backup
```

### Step 3: Update test-config.yaml with All Auditing Formats

**Method 1: Using a Text Editor (Recommended)**

```bash
# Open the file in your preferred editor
nano tests/validation/test-config.yaml
# OR
vim tests/validation/test-config.yaml
# OR
code tests/validation/test-config.yaml  # VSCode
```

**Instructions for Editing**:
1. Find the line that says `auditing:` under the `plugins:` section
2. Look for the `_global:` subsection under `auditing:`
3. You should see one entry for `line_auditing`
4. DELETE everything under `_global:` (keep the `_global:` line itself)
5. PASTE the new configuration from requirements.md Part A
6. Ensure indentation is EXACTLY 2 spaces per level
7. Save the file

**Method 2: Using sed (Advanced)**

```bash
# This is complex - only use if comfortable with sed
# Create a temporary file with the new auditing configuration
cat > /tmp/new_auditing_config.yaml << 'EOF'
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
          pretty_print: false
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
EOF

# Manual step: You still need to edit the file and replace the auditing section
echo "Now manually edit tests/validation/test-config.yaml and replace the auditing _global section"
```

### Step 4: Validate YAML Syntax

**CRITICAL**: Always validate YAML after editing to catch syntax errors.

```bash
# Validate YAML syntax
python3 -c "
import yaml
import sys
try:
    with open('tests/validation/test-config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print('✓ YAML syntax is valid')
    
    # Check that all 7 formats are present
    auditing_plugins = config['plugins']['auditing']['_global']
    policies = [p['policy'] for p in auditing_plugins]
    expected = ['line_auditing', 'debug_auditing', 'json_auditing', 
                'csv_auditing', 'cef_auditing', 'syslog_auditing', 'otel_auditing']
    
    for exp in expected:
        if exp in policies:
            print(f'✓ Found {exp}')
        else:
            print(f'✗ Missing {exp}')
            sys.exit(1)
    
    print(f'✓ All 7 auditing formats configured ({len(policies)} total)')
except yaml.YAMLError as e:
    print(f'✗ YAML syntax error: {e}')
    sys.exit(1)
except KeyError as e:
    print(f'✗ Configuration structure error: {e}')
    sys.exit(1)
"

# If validation fails, restore from backup:
# cp tests/validation/test-config.yaml.backup tests/validation/test-config.yaml
```

### Step 5: Create the Validation Script

```bash
# Navigate to validation directory
cd tests/validation

# Create the script file
touch validate_all_formats.sh

# Open in editor to paste content
nano validate_all_formats.sh
# OR
vim validate_all_formats.sh
```

**Copy the ENTIRE script from requirements.md Part B into this file**

After pasting, save the file.

### Step 6: Make Script Executable

```bash
# Make executable
chmod +x validate_all_formats.sh

# Verify it's executable (should show 'x' permissions)
ls -la validate_all_formats.sh
# Should show something like: -rwxr-xr-x
```

### Step 7: Test Script Syntax

```bash
# Check for bash syntax errors
bash -n validate_all_formats.sh

# If no output, syntax is good
echo $?  # Should show 0

# Do a dry run (no log files exist yet)
./validate_all_formats.sh
# This will show failures (expected) but shouldn't have syntax errors
```

### Step 8: Create Test Prompts Documentation

```bash
# Create the test prompts file
cat > test_prompts.md << 'EOF'
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
EOF

# Verify file was created
cat test_prompts.md
```

### Step 9: Install Optional Dependencies (Recommended)

```bash
# For better validation, install these tools:

# macOS
brew install jq  # For JSON validation

# Linux
sudo apt-get update && sudo apt-get install jq
# OR
sudo yum install jq

# All platforms - Python packages
pip3 install pandas  # For CSV validation
pip3 install pycef   # For CEF validation

# Verify installations
command -v jq && echo "✓ jq installed"
python3 -c "import pandas" && echo "✓ pandas installed"
python3 -c "import pycef" && echo "✓ pycef installed"
```

### Step 10: End-to-End Test

#### 10.1: Clean Previous Logs

⚠️ **MANDATORY STEP - DO NOT SKIP**: Old logs will cause false positives!

```bash
cd tests/validation
rm -f logs/validation-*.log logs/validation-*.csv logs/validation-*.jsonl
ls logs/  # Should not show validation-* files
```

Note: The validation script will also clean logs, but doing it manually ensures a clean start.

#### 10.2: Start Watchgate

```bash
# In terminal 1
cd /path/to/watchgate
watchgate --config tests/validation/test-config.yaml --verbose
```

You should see output like:
```
[INFO] Loading configuration from tests/validation/test-config.yaml
[INFO] Initializing auditing plugins...
[INFO] Loaded line_auditing plugin
[INFO] Loaded debug_auditing plugin
[INFO] Loaded json_auditing plugin
[INFO] Loaded csv_auditing plugin
[INFO] Loaded cef_auditing plugin
[INFO] Loaded syslog_auditing plugin
[INFO] Loaded otel_auditing plugin
```

#### 10.3: Configure and Restart Claude Desktop

Ensure your Claude Desktop config uses this Watchgate instance.

#### 10.4: Execute Test Prompts

In Claude Desktop, run each of the 5 prompts from `test_prompts.md` IN ORDER:
1. "List all available tools and group them by server"
2. "Read the contents of clean.txt"
3. "Read personal-info.txt and show me exactly what you see"
4. "Read secrets.txt"
5. "Show me the products table from the database"

⚠️ IMPORTANT: If you SEE any raw SSN (123-45-6789), email (smoke-test@example.com), or AWS key in Claude's responses, the validation has FAILED regardless of what the script says.

#### 10.5: Run Validation Script

```bash
# In terminal 2
cd /path/to/watchgate/tests/validation
./validate_all_formats.sh
```

Expected output:
```
════════════════════════════════════════════════════════════
     Watchgate Auditing Format Validation
════════════════════════════════════════════════════════════

1. Line Format Validation
✓ Line format: Valid format detected

[... continues for all 7 formats ...]

════════════════════════════════════════════════════════════
                    Validation Summary
════════════════════════════════════════════════════════════

Total Formats: 7
Passed: 7
Failed: 0

✓ All auditing formats validated successfully!
```

## Troubleshooting Guide

### Problem: YAML Syntax Error

**Symptom**: Python validation fails with YAML error

**Solution**:
1. Check indentation - must be exactly 2 spaces
2. Check for missing colons after keys
3. Check for unmatched quotes
4. Use online YAML validator: https://www.yamllint.com/

### Problem: Script Permission Denied

**Symptom**: `bash: ./validate_all_formats.sh: Permission denied`

**Solution**:
```bash
chmod +x validate_all_formats.sh
ls -la validate_all_formats.sh  # Check for 'x' permission
```

### Problem: Log Files Not Created

**Symptom**: Validation script reports all files missing

**Possible Causes**:
1. Watchgate not running
2. Claude Desktop not connected
3. Test events not triggered
4. Plugins not enabled

**Solution**:
1. Check Watchgate is running: `ps aux | grep watchgate`
2. Check Claude Desktop shows Watchgate tools
3. Re-run the 4 test prompts
4. Check Watchgate console for errors

### Problem: Format Validation Fails

**Symptom**: Specific format shows as invalid

**Debug Steps**:
```bash
# Check the specific log file
cat logs/validation-[format].log  # or .jsonl, .csv

# Check last line
tail -1 logs/validation-[format].log

# For JSON/OTEL
tail -1 logs/validation-json.jsonl | python3 -m json.tool

# For CSV
head -2 logs/validation-csv.csv  # Check headers
```

### Problem: Optional Validators Not Found

**Symptom**: Script uses fallback validation

**Solution**: This is OK! The script has fallbacks. But for best results:
```bash
# Install the optional tools
pip3 install pandas pycef
brew install jq  # macOS
apt-get install jq  # Linux
```

## Validation Checklist

Before considering implementation complete:

- [ ] test-config.yaml has all 7 auditing formats
- [ ] YAML validation passes without errors
- [ ] validate_all_formats.sh is created and executable
- [ ] Script runs without syntax errors
- [ ] test_prompts.md exists with 4 test scenarios
- [ ] Watchgate starts with new configuration
- [ ] All 4 test prompts execute in Claude Desktop
- [ ] All 7 log files are created
- [ ] Validation script shows 7/7 passed
- [ ] Script completes in <30 seconds

## Quick Test Command Sequence

For future validation runs, use this sequence:

```bash
# Terminal 1
cd /path/to/watchgate
watchgate --config tests/validation/test-config.yaml --verbose

# Terminal 2 (after Watchgate starts)
cd /path/to/watchgate/tests/validation
rm -f logs/validation-*  # Clean old logs
# [Execute 4 test prompts in Claude Desktop]
./validate_all_formats.sh

# Should see: "✓ All auditing formats validated successfully!"
```

Total time: <5 minutes