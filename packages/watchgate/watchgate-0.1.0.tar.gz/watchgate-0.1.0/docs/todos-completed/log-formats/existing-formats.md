# Existing Format Renaming Requirements

## Overview

The current file_auditing plugin format names need to be updated to better reflect their technical implementation and intended use cases. Since this is a first release (v0.1.0), we can make breaking changes without backward compatibility concerns.

## Current Format Analysis

### Format: `simple` → Rename to: `line`

**Current Implementation:**
```
2023-12-01 14:30:25 UTC - REQUEST: tools/call - read_file - ALLOWED
2023-12-01 14:30:25 UTC - SECURITY_BLOCK: delete_file - [tool_allowlist] Tool not in allowlist
```

**Justification for Rename:**
- "Simple" is vague and doesn't describe the technical format
- "Line" accurately describes the single-line-per-event format
- More descriptive for users understanding log structure
- Aligns with industry terminology (line-based logs)

### Format: `json` → Rename to: `jsonl`

**Current Implementation:**
```json
{"timestamp": "2023-12-01T14:30:25.123456Z", "event_type": "REQUEST", "method": "tools/call", "tool": "read_file", "status": "ALLOWED"}
```

**Justification for Rename:**
- Current implementation is actually JSON Lines format (one JSON object per line)
- Standard JSON array format would be inefficient for logging
- "jsonl" is the correct technical term for this format
- Improves accuracy and prevents confusion with standard JSON arrays

### Format: `detailed` → Rename to: `debug`

**Current Implementation:**
```
[2023-12-01 14:30:25.123] REQUEST_ID=123 EVENT=REQUEST METHOD=tools/call TOOL=read_file STATUS=ALLOWED PLUGIN=tool_allowlist REASON="Request approved"
```

**Justification for Rename:**
- "Detailed" is ambiguous - all formats can be detailed
- "Debug" clearly indicates purpose for troubleshooting
- More accurately reflects verbose, multi-field format
- Signals to users this is for diagnostic purposes

## Implementation Requirements

### 1. Direct Format Name Changes

**Requirement:** Update format names directly in code and configuration.

**Implementation:**
```python
# Updated format handler mapping
FORMAT_HANDLERS = {
    'line': self._format_line,      # Previously 'simple'
    'jsonl': self._format_jsonl,    # Previously 'json' 
    'debug': self._format_debug     # Previously 'detailed'
}

def validate_format_config(config: Dict[str, Any]) -> List[str]:
    """Validate format configuration"""
    errors = []
    format_name = config.get('format', 'jsonl')
    
    if format_name not in FORMAT_HANDLERS:
        valid_formats = ', '.join(FORMAT_HANDLERS.keys())
        errors.append(f"Invalid format '{format_name}'. Valid formats: {valid_formats}")
    
    return errors
```

### 2. Configuration Updates

**Requirements:**
- Update all example configurations to use new format names
- Update plugin documentation
- Update test configurations
- Update default format from 'json' to 'jsonl'

**Example Configuration:**
```yaml
plugins:
  auditing:
    - policy: "file_auditing"
      config:
        format: "jsonl"  # New default (was 'json')
        output_file: "logs/audit.log"
```

## Testing Strategy

### Unit Tests

**Test format name validation:**
```python
def test_format_name_validation():
    """Test format name validation"""
    # Valid formats
    for format_name in ['line', 'jsonl', 'debug']:
        config = {'format': format_name}
        errors = validate_format_config(config)
        assert len(errors) == 0
    
    # Invalid format
    config = {'format': 'invalid'}
    errors = validate_format_config(config)
    assert len(errors) == 1
    assert "Invalid format" in errors[0]

def test_format_handler_mapping():
    """Test format handler mapping"""
    formatter = FileAuditingFormatter()
    
    # Test all format handlers exist
    for format_name in ['line', 'jsonl', 'debug']:
        assert format_name in formatter.FORMAT_HANDLERS
    
    # Test old format names are removed
    for old_name in ['simple', 'json', 'detailed']:
        assert old_name not in formatter.FORMAT_HANDLERS
```

### Integration Tests

**Test plugin lifecycle with new format names:**
```python
def test_plugin_initialization_with_new_formats():
    """Test plugin works with new format names"""
    for format_name in ['line', 'jsonl', 'debug']:
        config = {
            'output_file': 'test.log',
            'format': format_name
        }
        plugin = FileAuditingPlugin(config)
        # Should work without errors
        assert plugin.format_name == format_name

def test_config_loading_with_new_formats():
    """Test YAML config loading with new format names"""
    yaml_config = """
    plugins:
      auditing:
        - policy: "file_auditing"
          config:
            format: "jsonl"
    """
    config = load_config(yaml_config)
    # Should load successfully
    assert config['plugins']['auditing'][0]['config']['format'] == 'jsonl'
```

### Validation Tests

**Test format output correctness:**
```python
def test_format_output_correctness():
    """Test that renamed formats produce correct output"""
    test_event = create_test_event()
    
    # Test line format (previously simple)
    plugin_line = FileAuditingPlugin({'format': 'line'})
    output_line = plugin_line.format_event(test_event)
    assert isinstance(output_line, str)
    assert '\n' not in output_line  # Single line
    
    # Test jsonl format (previously json)
    plugin_jsonl = FileAuditingPlugin({'format': 'jsonl'})
    output_jsonl = plugin_jsonl.format_event(test_event)
    json.loads(output_jsonl)  # Should parse as valid JSON
    
    # Test debug format (previously detailed)
    plugin_debug = FileAuditingPlugin({'format': 'debug'})
    output_debug = plugin_debug.format_event(test_event)
    assert '=' in output_debug  # Key-value pairs
```

## Implementation Strategy

### Single Phase Implementation
Since we haven't released yet, we can implement all changes in one phase:

1. **Update format handlers** - Rename internal format methods
2. **Update configuration validation** - Use new format names in validation
3. **Update documentation** - Replace all references to old format names
4. **Update tests** - Use new format names in all test cases
5. **Update default configuration** - Change default from 'json' to 'jsonl'

## Risk Assessment

### Low Risk
- **No backward compatibility concerns** - First release allows breaking changes
- **Simple renaming operation** - Minimal code changes required
- **Clear naming improvements** - Better user experience with descriptive names

### Mitigation Strategies
- **Comprehensive testing** - Test all new format names
- **Clear documentation** - Update all references to format names
- **Consistent naming** - Use new names throughout codebase

## Acceptance Criteria

### Implementation Complete When:
- [ ] All three format names updated to new names (line, jsonl, debug)
- [ ] Configuration validation uses new format names
- [ ] Documentation updated with new format names
- [ ] Unit tests cover all new format name scenarios
- [ ] Integration tests validate plugin lifecycle with new names
- [ ] Default format changed from 'json' to 'jsonl'
- [ ] All references to old format names removed from codebase
- [ ] Format output correctness verified for all renamed formats