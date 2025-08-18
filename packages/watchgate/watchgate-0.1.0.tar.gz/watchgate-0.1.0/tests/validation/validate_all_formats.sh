#!/bin/bash

# Quick Validation Script for Watchgate Auditing Formats
# This script validates all 7 auditing plugin formats
# Exit codes: 0 = all pass, 1 = one or more failures

# set -e  # Exit on first error - disabled to allow validation of all formats

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

# 0. Check Plugin Loading (from debug log)
echo "0. Plugin Load Verification"
if [ -f "logs/validation.log" ]; then
    # Check that all auditing plugins loaded successfully
    missing_plugins=""
    for plugin in "line_auditing" "debug_auditing" "json_auditing" "csv_auditing" "cef_auditing" "syslog_auditing" "otel_auditing"; do
        if ! grep -q "Loaded auditing plugin '$plugin'" logs/validation.log 2>/dev/null; then
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
    # Check for proper line format (timestamp - REQUEST/RESPONSE/etc) in last 20 lines
    if tail -20 logs/validation-line.log | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}.*UTC - (REQUEST|RESPONSE|SECURITY_BLOCK|REDACTION|MODIFICATION|NOTIFICATION|TOOLS_FILTERED):'; then
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
    if tail -20 logs/validation-debug.log | grep -qE '\[.*\].*REQUEST_ID=.*EVENT=.*METHOD='; then
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
                print_status "pass" "JSON format: Valid JSON with required fields (jq)"
            else
                print_status "fail" "JSON format: Valid JSON but missing required fields"
            fi
        else
            print_status "fail" "JSON format: Invalid JSON structure"
        fi
    else
        # Fallback: Python JSON validation (check last 20 lines)
        if python3 -c "import json; [json.loads(line) for line in open('logs/validation-json.jsonl').readlines()[-20:]]" 2>/dev/null; then
            print_status "pass" "JSON format: Valid JSON (FALLBACK: Python validation)"
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
            print_status "pass" "CSV format: Valid CSV (FALLBACK: basic Python csv module)"
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
            print_status "pass" "CEF format: Valid CEF structure (FALLBACK: regex pattern matching)"
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
        # Validate OTLP/JSON log record structure with jq (check last 20 lines)
        if tail -20 logs/validation-otel.jsonl | head -1 | jq -e '.time_unix_nano and .severity_number and .body and .attributes and .resource' > /dev/null 2>&1; then
            print_status "pass" "OTEL format: Valid OTLP/JSON log record structure (jq)"
        else
            print_status "fail" "OTEL format: Invalid OTLP/JSON log record structure"
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
                if 'time_unix_nano' in data and 'severity_number' in data and 'body' in data:
                    valid_count += 1
            except:
                pass
        if valid_count > 0:
            print('VALID')
        else:
            print('INVALID: Missing required OTLP log fields in all lines')
except Exception as e:
    print(f'ERROR: {e}')
" 2>&1)
        
        if [[ "$validation_result" == "VALID" ]]; then
            print_status "pass" "OTEL format: Valid OTLP structure (FALLBACK: Python validation)"
        else
            print_status "fail" "OTEL format: $validation_result"
        fi
    fi
fi
echo ""

# Track validation methods used
VALIDATION_METHODS=""

# Check which tools are available
echo ""
echo "Validation Tools Status:"
if command -v jq &> /dev/null; then
    echo -e "${GREEN}✓${NC} jq: Available (preferred for JSON/OTEL validation)"
else
    echo -e "${YELLOW}⚠${NC} jq: Not available (using Python fallback)"
    VALIDATION_METHODS="${VALIDATION_METHODS}JSON:Python fallback, OTEL:Python fallback, "
fi

if python3 -c "import pandas" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} pandas: Available (preferred for CSV validation)"
else
    echo -e "${YELLOW}⚠${NC} pandas: Not available (using basic csv module)"
    VALIDATION_METHODS="${VALIDATION_METHODS}CSV:Basic fallback, "
fi

if python3 -c "import pycef" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} pycef: Available (preferred for CEF validation)"
else
    echo -e "${YELLOW}⚠${NC} pycef: Not available (using regex pattern matching)"
    VALIDATION_METHODS="${VALIDATION_METHODS}CEF:Regex fallback, "
fi

# Summary
echo ""
echo "════════════════════════════════════════════════════════════"
echo "                    Validation Summary"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Total Formats: $TOTAL_FORMATS"
echo -e "${GREEN}Passed: $PASSED_FORMATS${NC}"
echo -e "${RED}Failed: $FAILED_FORMATS${NC}"

if [ -n "$VALIDATION_METHODS" ]; then
    echo ""
    echo -e "${YELLOW}Note: Some formats validated using fallback methods${NC}"
fi

echo ""

if [ $FAILED_FORMATS -eq 0 ]; then
    echo -e "${GREEN}✓ All auditing formats validated successfully!${NC}"
    if [ -n "$VALIDATION_METHODS" ]; then
        echo ""
        echo "For more accurate validation, consider installing:"
        if ! command -v jq &> /dev/null; then
            echo "  - jq: brew install jq (macOS) or apt-get install jq (Linux)"
        fi
        if ! python3 -c "import pandas" 2>/dev/null; then
            echo "  - pandas: pip install pandas"
        fi
        if ! python3 -c "import pycef" 2>/dev/null; then
            echo "  - pycef: pip install pycef"
        fi
    fi
    exit 0
else
    echo -e "${RED}✗ Validation failed for $FAILED_FORMATS format(s)${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Ensure Watchgate is running with the validation-config.yaml"
    echo "2. Trigger test events in Claude Desktop"
    echo "3. Check that all plugins are enabled in the config"
    echo "4. Review logs for error messages"
    exit 1
fi