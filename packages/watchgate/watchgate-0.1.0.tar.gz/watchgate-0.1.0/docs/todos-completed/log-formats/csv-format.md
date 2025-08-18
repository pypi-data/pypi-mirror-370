# CSV Format Implementation Requirements

## Overview

CSV (Comma-Separated Values) format provides a simple, widely-supported format for log data that can be easily imported into spreadsheets, databases, and data analysis tools. This format is particularly useful for compliance reporting and ad-hoc analysis.

## Implementation Requirements

### 1. Format Structure

**CSV Header:**
```csv
timestamp,event_type,method,tool,status,request_id,plugin,reason,duration_ms,server_name
```

**Example Output:**
```csv
timestamp,event_type,method,tool,status,request_id,plugin,reason,duration_ms,server_name
2023-12-01T14:30:25.123456Z,REQUEST,tools/call,read_file,ALLOWED,123,tool_allowlist,Request approved,,server1
2023-12-01T14:30:25.150000Z,RESPONSE,tools/call,read_file,success,123,,,45,server1
2023-12-01T14:30:26.200000Z,SECURITY_BLOCK,tools/call,delete_file,BLOCKED,124,tool_allowlist,Tool not in allowlist,,server1
```

### 2. Standard Library Implementation

**Core Requirements:**
- No external dependencies in runtime code
- Use Python's built-in `csv` module
- Handle proper CSV escaping and quoting
- Support field ordering consistency
- Handle missing/empty values

**Implementation Class:**
```python
import csv
import io
from typing import Dict, Any, List, Optional

class CSVFormatter:
    def __init__(self):
        # Define consistent field order
        self.field_order = [
            'timestamp',
            'event_type',
            'method',
            'tool',
            'status',
            'request_id',
            'plugin',
            'reason',
            'duration_ms',
            'server_name'
        ]
        self.header_written = False
    
    def format_event(self, event_data: Dict[str, Any]) -> str:
        """Format Watchgate event as CSV row"""
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=self.field_order,
            quoting=csv.QUOTE_MINIMAL,
            lineterminator='\n'
        )
        
        # Write header if this is the first event
        if not self.header_written:
            writer.writeheader()
            self.header_written = True
        
        # Convert event data to CSV row
        csv_row = self._map_event_to_csv(event_data)
        writer.writerow(csv_row)
        
        return output.getvalue()
    
    def _map_event_to_csv(self, event_data: Dict[str, Any]) -> Dict[str, str]:
        """Map Watchgate event data to CSV fields"""
        csv_row = {}
        
        for field in self.field_order:
            value = event_data.get(field, '')
            # Convert to string and handle None values
            csv_row[field] = str(value) if value is not None else ''
        
        return csv_row
    
    def get_header(self) -> str:
        """Get CSV header row"""
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=self.field_order,
            quoting=csv.QUOTE_MINIMAL,
            lineterminator='\n'
        )
        writer.writeheader()
        return output.getvalue()
```

### 3. Watchgate Event Mapping

**Field Mappings:**
```python
CSV_FIELD_MAPPINGS = {
    'timestamp': 'timestamp',           # ISO 8601 timestamp
    'event_type': 'event_type',         # REQUEST, RESPONSE, SECURITY_BLOCK, etc.
    'method': 'method',                 # MCP method name
    'tool': 'tool',                     # Tool name for tools/call
    'status': 'status',                 # ALLOWED, BLOCKED, success, error
    'request_id': 'request_id',         # Request correlation ID
    'plugin': 'plugin',                 # Plugin that made decision
    'reason': 'reason',                 # Human-readable reason
    'duration_ms': 'duration_ms',       # Request duration (responses only)
    'server_name': 'server_name'        # Multi-server support
}
```

**Data Type Handling:**
```python
def format_csv_value(self, value: Any) -> str:
    """Format values for CSV output"""
    if value is None:
        return ''
    elif isinstance(value, bool):
        return 'true' if value else 'false'
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, dict):
        # Convert dict to JSON string for complex data
        return json.dumps(value, separators=(',', ':'))
    else:
        return str(value)
```

### 4. Header Management

**File-Based Header Handling:**
```python
class CSVFileManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.header_exists = self._check_header_exists()
    
    def _check_header_exists(self) -> bool:
        """Check if CSV file already has header"""
        try:
            with open(self.file_path, 'r', newline='') as f:
                first_line = f.readline().strip()
                return first_line.startswith('timestamp,event_type')
        except FileNotFoundError:
            return False
    
    def write_event(self, csv_data: str) -> None:
        """Write CSV data to file, handling header appropriately"""
        mode = 'a' if self.header_exists else 'w'
        with open(self.file_path, mode, newline='') as f:
            f.write(csv_data)
        
        if not self.header_exists:
            self.header_exists = True
```

### 5. Configuration Integration

**Configuration Schema:**
```yaml
plugins:
  auditing:
    - policy: "file_auditing"
      config:
        format: "csv"
        output_file: "logs/audit.csv"
        csv_config:
          include_header: true            # Include header row
          quote_style: "minimal"          # minimal, all, nonnumeric, none
          delimiter: ","                  # Field delimiter
          null_value: ""                  # How to represent null values
          date_format: "iso"              # iso, epoch, custom
```

## Testing Strategy

### Unit Tests (Standard Library Only)

**Test CSV message generation:**
```python
def test_csv_format_basic():
    """Test basic CSV message formatting"""
    formatter = CSVFormatter()
    event = {
        'timestamp': '2023-12-01T14:30:25.123456Z',
        'event_type': 'REQUEST',
        'method': 'tools/call',
        'tool': 'read_file',
        'status': 'ALLOWED',
        'request_id': '123',
        'plugin': 'tool_allowlist',
        'reason': 'Request approved'
    }
    
    result = formatter.format_event(event)
    lines = result.strip().split('\n')
    
    # Should have header and data row
    assert len(lines) == 2
    assert lines[0].startswith('timestamp,event_type')
    assert '2023-12-01T14:30:25.123456Z' in lines[1]
    assert 'REQUEST' in lines[1]
```

**Test CSV escaping:**
```python
def test_csv_escaping():
    """Test CSV field escaping and quoting"""
    formatter = CSVFormatter()
    event = {
        'timestamp': '2023-12-01T14:30:25.123456Z',
        'event_type': 'REQUEST',
        'reason': 'Contains, comma and "quotes"',
        'method': 'tools/call'
    }
    
    result = formatter.format_event(event)
    # Should properly quote fields with commas and quotes
    assert '"Contains, comma and ""quotes"""' in result
```

**Test missing values:**
```python
def test_csv_missing_values():
    """Test handling of missing/None values"""
    formatter = CSVFormatter()
    event = {
        'timestamp': '2023-12-01T14:30:25.123456Z',
        'event_type': 'REQUEST',
        'method': 'tools/call',
        # Missing other fields
    }
    
    result = formatter.format_event(event)
    lines = result.strip().split('\n')
    data_row = lines[1]
    
    # Should have empty values for missing fields
    fields = data_row.split(',')
    assert fields[0] == '2023-12-01T14:30:25.123456Z'  # timestamp
    assert fields[1] == 'REQUEST'  # event_type
    assert fields[2] == 'tools/call'  # method
    assert fields[3] == ''  # tool (missing)
```

**Test data type conversion:**
```python
def test_csv_data_types():
    """Test conversion of different data types"""
    formatter = CSVFormatter()
    event = {
        'timestamp': '2023-12-01T14:30:25.123456Z',
        'event_type': 'RESPONSE',
        'duration_ms': 45,  # Integer
        'status': True,  # Boolean
        'metadata': {'key': 'value'}  # Dict
    }
    
    result = formatter.format_event(event)
    assert '45' in result  # Integer converted to string
    assert 'true' in result  # Boolean converted to string
    assert '{"key":"value"}' in result  # Dict converted to JSON
```

### Integration Tests (Watchgate Dependencies)

**Test plugin lifecycle:**
```python
def test_csv_plugin_integration():
    """Test CSV format with file auditing plugin"""
    config = {
        'output_file': 'test.csv',
        'format': 'csv',
        'csv_config': {
            'include_header': True,
            'quote_style': 'minimal'
        }
    }
    
    plugin = FileAuditingPlugin(config)
    
    # Log multiple events
    events = [
        create_test_mcp_request(),
        create_test_mcp_response(),
        create_test_security_block()
    ]
    
    for event in events:
        plugin.log_request(event, PolicyDecision(allowed=True))
    
    # Verify file output
    with open('test.csv', 'r') as f:
        content = f.read()
        lines = content.strip().split('\n')
        
        # Should have header + 3 data rows
        assert len(lines) == 4
        assert lines[0].startswith('timestamp,event_type')
```

**Test header management:**
```python
def test_csv_header_management():
    """Test CSV header management across multiple writes"""
    config = {
        'output_file': 'test.csv',
        'format': 'csv'
    }
    
    plugin = FileAuditingPlugin(config)
    
    # Log first event (should include header)
    plugin.log_request(create_test_mcp_request(), PolicyDecision(allowed=True))
    
    # Log second event (should not duplicate header)
    plugin.log_request(create_test_mcp_response(), PolicyDecision(allowed=True))
    
    with open('test.csv', 'r') as f:
        content = f.read()
        lines = content.strip().split('\n')
        
        # Should have exactly one header line
        header_count = sum(1 for line in lines if line.startswith('timestamp,event_type'))
        assert header_count == 1
```

### Validation Tests (Test-Only Dependencies)

**Test with pandas:**
```python
def test_csv_with_pandas():
    """Test CSV format with pandas DataFrame"""
    pytest.importorskip("pandas")
    import pandas as pd
    
    formatter = CSVFormatter()
    events = [
        create_test_event(),
        create_test_event(),
        create_test_event()
    ]
    
    # Generate CSV data
    csv_data = []
    for event in events:
        csv_data.append(formatter.format_event(event))
    
    # Combine and parse with pandas
    full_csv = ''.join(csv_data)
    df = pd.read_csv(io.StringIO(full_csv))
    
    # Verify structure
    assert len(df) == 3
    assert list(df.columns) == formatter.field_order
    assert df['event_type'].notna().all()
```

**Test with csvlint:**
```python
def test_csv_with_csvlint():
    """Test CSV format with csvlint validator"""
    if not shutil.which('csvlint'):
        pytest.skip("csvlint command not available")
    
    formatter = CSVFormatter()
    event = create_test_event()
    csv_data = formatter.format_event(event)
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_data)
        temp_file = f.name
    
    try:
        # Validate with csvlint
        result = subprocess.run(
            ['csvlint', temp_file],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
    finally:
        os.unlink(temp_file)
```

### Compliance Tests

**Test CSV RFC 4180 compliance:**
```python
def test_csv_rfc4180_compliance():
    """Test adherence to CSV RFC 4180 specification"""
    formatter = CSVFormatter()
    event = create_comprehensive_test_event()
    csv_data = formatter.format_event(event)
    
    # Test basic structure
    lines = csv_data.strip().split('\n')
    assert len(lines) >= 1  # At least header
    
    # Test that all lines have same number of fields
    reader = csv.reader(io.StringIO(csv_data))
    rows = list(reader)
    if len(rows) > 1:
        field_counts = [len(row) for row in rows]
        assert all(count == field_counts[0] for count in field_counts)
```

## External Validation Tools

### Test-Only Dependencies

**Python Libraries:**
```python
# pyproject.toml
[project.optional-dependencies]
test = [
    "pandas>=1.0.0",  # DataFrame validation
    "csvkit>=1.0.0",  # CSV analysis tools
]
```

**Command-Line Tools:**
```bash
# Install csvlint for validation
pip install csvlint

# Usage
csvlint audit.csv
```

### CI/CD Integration

**GitHub Actions validation:**
```yaml
- name: Install CSV Validators
  run: |
    pip install pandas csvkit csvlint
    
- name: Test CSV Format
  run: |
    pytest tests/validation/test_csv_compliance.py -v
```

## Risk Assessment

### Implementation Complexity: **Low**

**Challenges:**
- CSV escaping and quoting rules
- Header management across file writes
- Data type conversion consistency
- File rotation with CSV headers

**Mitigation Strategies:**
- Use Python's built-in CSV module for proper escaping
- Implement header existence checking
- Comprehensive test coverage for edge cases
- Clear documentation of field meanings

### Security Considerations

**Potential Issues:**
- CSV injection attacks via formula injection
- Information disclosure in exported data
- File permission issues with CSV files

**Safeguards:**
- Sanitize values that could be interpreted as formulas
- Proper file permissions for CSV output
- Input validation for all field values
- Regular security review of CSV generation logic

## Acceptance Criteria

### Implementation Complete When:
- [ ] CSV formatter implemented using Python's csv module
- [ ] All Watchgate event types mapped to CSV fields
- [ ] Proper CSV escaping and quoting implemented
- [ ] Header management handles file appends correctly
- [ ] Data type conversion handles all Watchgate field types
- [ ] Configuration integration with CSV-specific settings
- [ ] Unit tests cover all formatting scenarios
- [ ] Integration tests validate plugin lifecycle
- [ ] Validation tests pass with pandas DataFrame parsing
- [ ] Validation tests pass with csvlint tool
- [ ] Compliance tests verify RFC 4180 adherence
- [ ] Performance benchmarks meet requirements
- [ ] Security review completed for CSV injection
- [ ] Documentation updated with CSV format examples

### Success Metrics:
- **Format Compliance**: 100% of CSV files parse correctly in Excel/LibreOffice
- **Performance**: CSV formatting adds <2ms overhead per message
- **Security**: No CSV injection vulnerabilities identified
- **Usability**: CSV files import cleanly into common analysis tools