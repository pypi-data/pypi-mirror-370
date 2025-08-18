# Test Scenarios for Quick Validation Automation

## Overview

This document provides detailed test scenarios to verify the validation automation is working correctly. Each scenario includes:
- Setup steps
- Expected outputs
- Validation criteria
- Troubleshooting steps

## Visual Verification Table

### What You Should See vs What You Should NOT See

| Prompt | ✅ You SHOULD See | ❌ You Should NOT See | If You See Wrong Thing |
|--------|-------------------|----------------------|------------------------|
| **1. List tools** | Two groups: filesystem tools (read_file, write_file, etc.) and sqlite tools (query, list_tables, etc.) | Missing server groups, connection errors | Watchgate didn't connect to both upstreams |
| **2. Read clean.txt** | Normal file content displayed | Redaction markers like [REDACTED] | PII filter incorrectly triggered |
| **3. Read personal-info.txt** | `[EMAIL REDACTED by Watchgate]`, `[NATIONAL_ID REDACTED by Watchgate]` | Raw email `smoke-test@example.com`, raw SSN `123-45-6789` | **CRITICAL FAILURE** - PII not being redacted |
| **4. Read secrets.txt** | Security policy violation error | ANY AWS key like `AKIAIOSFODNN7EXAMPLE` | **CRITICAL FAILURE** - Secrets not being blocked |
| **5. Show products table** | Table data with product names and prices | Blocking error or empty result | Database queries incorrectly blocked |

### Visual Override Rule

⚠️ **ABSOLUTE RULE**: If you visually see ANY of these in Claude's UI, the validation has FAILED:
- Raw SSN: `123-45-6789`
- Raw test email: `smoke-test@example.com`  
- Raw AWS key: `AKIAIOSFODNN7EXAMPLE`
- Any other obvious PII or secrets

This rule overrides any "PASS" result from the automated script.

## Scenario 1: Fresh Installation Test

### Purpose
Verify the validation works on a clean Watchgate installation with no prior logs.

### Setup
```bash
# Clean all previous logs
cd tests/validation
rm -rf logs/
mkdir logs/
```

### Test Steps
1. Start Watchgate with updated config
2. Execute 4 test prompts in Claude Desktop
3. Run validation script

### Expected Log Files Created
```
logs/validation-line.log      # Human-readable format
logs/validation-debug.log     # Debug key-value format
logs/validation-json.jsonl    # JSON Lines format
logs/validation-csv.csv       # CSV with headers
logs/validation-cef.log       # CEF SIEM format
logs/validation-syslog.log    # RFC5424 syslog format
logs/validation-otel.jsonl    # OpenTelemetry traces
```

### Expected Validation Output
```
All 7 formats should show: ✓ [Format] format: Valid
Summary should show: Passed: 7, Failed: 0
```

## Scenario 2: Partial Failure Test

### Purpose
Verify the script correctly identifies missing or corrupted formats.

### Setup
```bash
# Delete some log files to simulate failure
rm logs/validation-cef.log
rm logs/validation-json.jsonl
echo "corrupted data" > logs/validation-csv.csv
```

### Expected Validation Output
```
✗ CEF format: File not found at logs/validation-cef.log
✗ JSON format: File not found at logs/validation-json.jsonl
✗ CSV format: Invalid CSV structure
✓ Line format: Valid format detected
✓ Debug format: Valid key-value format detected
✓ Syslog format: Valid RFC5424 format
✓ OTEL format: Valid OTLP structure with traces

Summary: Passed: 4, Failed: 3
Exit code: 1
```

## Scenario 3: Event Type Coverage Test

### Purpose
Verify all event types are captured correctly across all formats.

### Test Events and Expected Results

#### Event 1: ALLOWED Operation
**Prompt**: "Read the contents of clean.txt"

**Line Format Sample**:
```
2024-01-10 10:30:00.123 [INFO] REQUEST: EVENT_TYPE:REQUEST method:tools/call tool:read_file status:ALLOWED
```

**JSON Format Sample**:
```json
{"timestamp":"2024-01-10T10:30:00.123Z","event_type":"REQUEST","method":"tools/call","tool":"read_file","status":"ALLOWED","request_id":"req-123","server":"filesystem"}
```

**CSV Format Sample**:
```csv
timestamp,event_type,method,tool,status,server,request_id
2024-01-10T10:30:00.123Z,REQUEST,tools/call,read_file,ALLOWED,filesystem,req-123
```

**CEF Format Sample**:
```
CEF:0|Watchgate|MCP-Proxy|0.1.0|100|Tool Request|3|rt=1704882600123 act=ALLOWED cs1=read_file cs1Label=tool
```

#### Event 2: REDACTED Operation
**Prompt**: "Read personal-info.txt and show me what you see"

**Expected in All Formats**:
- Event type: REQUEST or RESPONSE
- Status: ALLOWED (but with redaction metadata)
- Should see indication of PII redaction in metadata/extension fields

#### Event 3: BLOCKED Operation
**Prompt**: "Read secrets.txt"

**Expected in All Formats**:
- Event type: SECURITY_BLOCK
- Status: BLOCKED
- Reason: Security policy violation
- Plugin: secrets_filter

#### Event 4: Database Query
**Prompt**: "Show me the products table from the database"

**Expected in All Formats**:
- Server: sqlite (not filesystem)
- Method: query or similar
- Status: ALLOWED

### Validation Criteria
Each format must contain at least 4 events (one for each test prompt).

## Scenario 4: Format-Specific Validation Tests

### JSON Format Validation

**Test valid JSON structure**:
```bash
# All lines must be valid JSON
while IFS= read -r line; do
    echo "$line" | python3 -m json.tool > /dev/null || echo "Invalid JSON: $line"
done < logs/validation-json.jsonl
```

**Expected**: No output (all lines valid)

### CSV Format Validation

**Test CSV structure**:
```python
import csv
import pandas as pd

# Using pandas
df = pd.read_csv('logs/validation-csv.csv')
print(f"Columns: {list(df.columns)}")
print(f"Rows: {len(df)}")
print(f"Has headers: {list(df.columns) != ['Unnamed: 0']}")

# Check for required columns
required = ['timestamp', 'event_type', 'method', 'status']
for col in required:
    assert col in df.columns, f"Missing required column: {col}"
```

**Expected**: 
- At least 4 rows (excluding header)
- Required columns present
- No parsing errors

### CEF Format Validation

**Test CEF structure**:
```python
import pycef

with open('logs/validation-cef.log') as f:
    for i, line in enumerate(f, 1):
        try:
            event = pycef.parse(line.strip())
            assert 'CEF' in line, "Missing CEF marker"
            assert event is not None, "Parse returned None"
            print(f"Line {i}: Valid CEF - Event name: {event.get('name', 'Unknown')}")
        except Exception as e:
            print(f"Line {i}: Invalid - {e}")
```

**Expected**: All lines show "Valid CEF"

### Syslog Format Validation

**Test RFC5424 format**:
```bash
# RFC5424: <priority>version timestamp hostname app-name
grep -E '^<[0-9]+>[0-9]+ [0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}' logs/validation-syslog.log
```

**Expected**: All lines match the pattern

### OpenTelemetry Format Validation

**Test OTLP structure**:
```python
import json

with open('logs/validation-otel.jsonl') as f:
    for i, line in enumerate(f, 1):
        data = json.loads(line)
        assert 'resourceSpans' in data, f"Line {i}: Missing resourceSpans"
        assert len(data['resourceSpans']) > 0, f"Line {i}: Empty resourceSpans"
        
        # Check for trace structure
        span = data['resourceSpans'][0]
        assert 'resource' in span, f"Line {i}: Missing resource"
        assert 'scopeSpans' in span, f"Line {i}: Missing scopeSpans"
        
        print(f"Line {i}: Valid OTLP structure")
```

**Expected**: All lines show "Valid OTLP structure"

## Scenario 5: Performance Test

### Purpose
Verify validation completes within performance requirements.

### Test
```bash
# Time the validation script
time ./validate_all_formats.sh
```

### Expected Results
- Real time: < 30 seconds
- All formats validated
- No timeouts or hangs

## Scenario 6: Missing Dependencies Test

### Purpose
Verify fallback validators work when optional tools are missing.

### Setup
```bash
# Temporarily rename optional tools (don't actually do this in production)
# This simulates missing dependencies
```

### Test Without jq
The script should fall back to Python JSON validation:
```
JSON format: Valid JSON (validated with Python)
```

### Test Without pandas
The script should fall back to basic CSV validation:
```
CSV format: Valid CSV (basic validation)
```

### Test Without pycef
The script should fall back to regex validation:
```
CEF format: Valid CEF structure (regex)
```

## Scenario 7: Concurrent Event Test

### Purpose
Verify the system handles multiple simultaneous events correctly.

### Test Steps
1. Execute all 4 test prompts rapidly without waiting
2. Immediately run validation script

### Expected Results
- All formats contain events
- Events may be interleaved but all present
- No corruption or missing data

## Scenario 8: Large Volume Test

### Purpose
Test with many events to verify no data loss.

### Setup
Execute these prompts 10 times each:
```
"List all files in the current directory"
"Read clean.txt"
"Show me the products table"
```

### Validation
```python
# Check event counts
import pandas as pd
df = pd.read_csv('logs/validation-csv.csv')
print(f"Total events logged: {len(df)}")
assert len(df) >= 30, "Expected at least 30 events"
```

## Success Criteria Summary

The validation automation is considered successful when:

1. **Basic Validation**: All 7 formats pass validation with test events
2. **Error Detection**: Script correctly identifies missing/corrupted files
3. **Event Coverage**: All event types (ALLOWED, BLOCKED, REDACTED) are captured
4. **Format Compliance**: Each format passes its specific validation rules
5. **Performance**: Validation completes in <30 seconds
6. **Robustness**: Works with and without optional dependencies
7. **Accuracy**: No false positives or false negatives

## Common Issues and Solutions

### Issue: Different Number of Events in Different Formats

**Cause**: Some formats may buffer differently or have initialization events.

**Solution**: This is acceptable as long as the main 4 test events are present.

### Issue: Timestamps Don't Match Exactly

**Cause**: Formats may use different timestamp precision or timezones.

**Solution**: This is expected. Check that timestamps are close (within 1 second).

### Issue: CSV Has Extra Columns

**Cause**: Different plugins may add format-specific columns.

**Solution**: This is fine. Only check for required core columns.

### Issue: Validation Passes But Looks Wrong

**Debug Steps**:
1. Manually inspect a few lines from each format
2. Check that events correspond to test prompts
3. Verify server names match expected values
4. Look for any ERROR or WARN messages in logs

## Regression Test Suite

For ongoing validation after changes:

```bash
#!/bin/bash
# regression_test.sh

echo "Running regression test suite..."

# Test 1: Clean start
rm -f logs/validation-*
./validate_all_formats.sh
[ $? -eq 1 ] && echo "✓ Correctly reports missing files" || echo "✗ Should fail with no files"

# Test 2: Generate events and validate
# [Run test prompts]
./validate_all_formats.sh
[ $? -eq 0 ] && echo "✓ Validation passes with events" || echo "✗ Validation should pass"

# Test 3: Corrupt a file
echo "bad data" > logs/validation-json.jsonl
./validate_all_formats.sh
[ $? -eq 1 ] && echo "✓ Detects corrupted JSON" || echo "✗ Should detect bad JSON"

echo "Regression tests complete"
```

## Final Validation Checklist

Before marking the implementation as complete:

- [ ] Scenario 1: Fresh installation test passes
- [ ] Scenario 2: Partial failure correctly detected
- [ ] Scenario 3: All event types captured
- [ ] Scenario 4: Format-specific validations pass
- [ ] Scenario 5: Performance <30 seconds
- [ ] Scenario 6: Fallback validators work
- [ ] Scenario 7: Concurrent events handled
- [ ] Scenario 8: Large volume test passes
- [ ] Regression test suite passes
- [ ] Documentation is clear and accurate