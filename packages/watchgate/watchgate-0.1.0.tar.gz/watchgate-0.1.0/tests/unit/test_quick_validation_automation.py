"""
Tests for quick validation automation functionality.

This module tests the validation automation system that verifies all 7 auditing 
plugin formats are working correctly.
"""

import os
import tempfile
import yaml
import pytest
from pathlib import Path


class TestConfigurationValidation:
    """Test configuration updates for all 7 auditing formats."""
    
    def test_config_contains_all_seven_auditing_formats(self):
        """Test that validation-config.yaml contains all 7 required auditing formats."""
        config_path = Path("tests/validation/validation-config.yaml")
        assert config_path.exists(), "validation-config.yaml must exist"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Check that auditing section exists
        assert "plugins" in config
        assert "auditing" in config["plugins"]
        assert "_global" in config["plugins"]["auditing"]
        
        # Get all auditing policies
        auditing_plugins = config["plugins"]["auditing"]["_global"]
        policies = [plugin["policy"] for plugin in auditing_plugins]
        
        # Expected 7 auditing formats
        expected_policies = [
            "line_auditing",
            "debug_auditing", 
            "json_auditing",
            "csv_auditing",
            "cef_auditing",
            "syslog_auditing",
            "otel_auditing"
        ]
        
        for policy in expected_policies:
            assert policy in policies, f"Missing required auditing policy: {policy}"
        
        assert len(policies) >= 7, f"Expected at least 7 auditing policies, got {len(policies)}"
    
    def test_config_output_files_use_logs_directory(self):
        """Test that all output files are configured to use logs/ directory."""
        config_path = Path("tests/validation/validation-config.yaml")
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        auditing_plugins = config["plugins"]["auditing"]["_global"]
        
        for plugin in auditing_plugins:
            if "output_file" in plugin["config"]:
                output_file = plugin["config"]["output_file"]
                assert output_file.startswith("logs/validation-"), \
                    f"Output file {output_file} should start with 'logs/validation-'"
    
    def test_config_yaml_syntax_is_valid(self):
        """Test that the updated configuration has valid YAML syntax."""
        config_path = Path("tests/validation/validation-config.yaml")
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Should be able to parse without error
        assert isinstance(config, dict)
        assert "plugins" in config


class TestValidationScript:
    """Test the validation script functionality."""
    
    def test_validation_script_exists_and_executable(self):
        """Test that validate_all_formats.sh exists and is executable."""
        script_path = Path("tests/validation/validate_all_formats.sh")
        assert script_path.exists(), "validate_all_formats.sh must exist"
        assert os.access(script_path, os.X_OK), "validate_all_formats.sh must be executable"
    
    def test_validation_script_validates_all_seven_formats(self):
        """Test that the script checks all 7 format types."""
        script_path = Path("tests/validation/validate_all_formats.sh")
        assert script_path.exists()
        
        with open(script_path) as f:
            content = f.read()
        
        # Should contain validation for all 7 formats
        expected_formats = [
            "Line Format", 
            "Debug Format",
            "JSON Format",
            "CSV Format", 
            "CEF",
            "Syslog Format",
            "OpenTelemetry Format"
        ]
        
        for format_name in expected_formats:
            assert format_name in content, f"Script missing validation for {format_name}"
    
    def test_validation_script_handles_missing_files(self):
        """Test that script properly handles missing log files."""
        script_path = Path("tests/validation/validate_all_formats.sh")
        assert script_path.exists()
        
        with open(script_path) as f:
            content = f.read()
        
        # Should check file existence
        assert "check_file_exists" in content
        assert "File not found" in content
    
    def test_validation_script_uses_fallback_validators(self):
        """Test that script has fallback validation when tools missing."""
        script_path = Path("tests/validation/validate_all_formats.sh")
        assert script_path.exists()
        
        with open(script_path) as f:
            content = f.read()
        
        # Should have fallback methods
        assert "command -v jq" in content  # Check for jq
        assert "python3 -c" in content     # Python fallback
        assert "pandas" in content         # Check pandas availability


class TestFormatValidators:
    """Test individual format validation logic."""
    
    def test_json_format_validator_detects_valid_jsonl(self):
        """Test JSON format validator works with valid JSON Lines."""
        # This test will fail initially - we need to implement the logic
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write('{"timestamp":"2024-01-10T10:30:00Z","event_type":"REQUEST","method":"test"}\n')
            f.write('{"timestamp":"2024-01-10T10:31:00Z","event_type":"RESPONSE","method":"test"}\n')
            temp_file = f.name
        
        try:
            # This should pass when we implement the validator
            result = self._validate_json_format(temp_file)
            assert result is True, "Valid JSON Lines should pass validation"
        finally:
            os.unlink(temp_file)
    
    def test_csv_format_validator_detects_valid_csv(self):
        """Test CSV format validator works with valid CSV."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('timestamp,event_type,method,status\n')
            f.write('2024-01-10T10:30:00Z,REQUEST,test,ALLOWED\n')
            temp_file = f.name
        
        try:
            result = self._validate_csv_format(temp_file)
            assert result is True, "Valid CSV should pass validation"
        finally:
            os.unlink(temp_file)
    
    def test_cef_format_validator_detects_valid_cef(self):
        """Test CEF format validator works with valid CEF."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write('CEF:0|Watchgate|MCP-Proxy|0.1.0|100|Request|3|msg=Tool call\n')
            temp_file = f.name
        
        try:
            result = self._validate_cef_format(temp_file)
            assert result is True, "Valid CEF should pass validation"
        finally:
            os.unlink(temp_file)
    
    def _validate_json_format(self, file_path):
        """Validate JSON Lines format."""
        import json
        try:
            with open(file_path) as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line.strip())
                        # Check for required fields
                        if 'timestamp' in data and 'event_type' in data and 'method' in data:
                            return True
            return False
        except (json.JSONDecodeError, FileNotFoundError):
            return False
    
    def _validate_csv_format(self, file_path):
        """Validate CSV format."""
        import csv
        try:
            with open(file_path, newline='') as f:
                reader = csv.reader(f)
                headers = next(reader)  # Read headers
                if len(headers) >= 4:  # Should have at least basic columns
                    row = next(reader)  # Read first data row
                    return len(row) >= 4  # Should have data
            return False
        except (csv.Error, FileNotFoundError, StopIteration):
            return False
    
    def _validate_cef_format(self, file_path):
        """Validate CEF format."""
        try:
            with open(file_path) as f:
                for line in f:
                    if line.strip():
                        # Basic CEF format check: CEF:version|vendor|product|version|signature|name|severity|extension
                        if line.startswith('CEF:') and line.count('|') >= 7:
                            return True
            return False
        except FileNotFoundError:
            return False


class TestQuickValidationGuide:
    """Test the quick validation guide documentation."""
    
    def test_quick_validation_guide_contains_test_prompts(self):
        """Test that quick-validation-guide.md contains all required test prompts."""
        guide_path = Path("tests/validation/quick-validation-guide.md")
        assert guide_path.exists(), "quick-validation-guide.md must exist"
        
        with open(guide_path) as f:
            content = f.read()
        
        # Should contain all required test scenarios
        expected_prompts = [
            "List all available tools and group them by server",
            "Read the contents of clean.txt",
            "Read personal-info.txt and show me exactly what you see",
            "Read secrets.txt",
            "Show me the products table from the database"
        ]
        
        for prompt in expected_prompts:
            assert prompt in content, f"Missing test prompt: {prompt}"
    
    def test_quick_validation_guide_has_expected_results(self):
        """Test that quick validation guide includes expected results for validation."""
        guide_path = Path("tests/validation/quick-validation-guide.md")
        assert guide_path.exists()
        
        with open(guide_path) as f:
            content = f.read()
        
        # Should describe expected behaviors
        expected_behaviors = [
            "ALLOWED",
            "REDACTED",
            "BLOCKED",
            "[EMAIL REDACTED by Watchgate]",
            "[NATIONAL_ID REDACTED by Watchgate]"
        ]
        
        for behavior in expected_behaviors:
            assert behavior in content, f"Missing expected behavior: {behavior}"
    
    def test_quick_validation_guide_has_essential_instructions(self):
        """Test that quick validation guide has all essential instructions."""
        guide_path = Path("tests/validation/quick-validation-guide.md")
        assert guide_path.exists()
        
        with open(guide_path) as f:
            content = f.read()
        
        # Should contain essential instructions
        essential_elements = [
            "validate_all_formats.sh",  # Reference to validation script
            "validation-config.yaml",          # Configuration file
            "Claude Desktop",            # Setup instructions
            "5 minutes",                 # Time estimate
            "7 auditing formats",        # All formats mentioned
            "Troubleshooting"            # Help section
        ]
        
        for element in essential_elements:
            assert element in content, f"Missing essential element: {element}"


class TestEndToEndValidation:
    """Test end-to-end validation scenarios."""
    
    def test_validation_completes_in_thirty_seconds(self):
        """Test that validation script execution is fast."""
        import subprocess
        import time
        
        script_path = Path("tests/validation/validate_all_formats.sh")
        assert script_path.exists()
        
        start_time = time.time()
        try:
            # Run script (will fail due to missing logs but should be fast)
            result = subprocess.run(["./validate_all_formats.sh"], 
                                  cwd="tests/validation", 
                                  capture_output=True, 
                                  timeout=30)
            elapsed = time.time() - start_time
            assert elapsed < 30, f"Validation took {elapsed:.2f}s, should be <30s"
        except subprocess.TimeoutExpired:
            pytest.fail("Validation script timed out after 30 seconds")
    
    def test_validation_fails_with_missing_logs(self):
        """Test that validation correctly fails when logs are missing."""
        import subprocess
        import shutil
        import tempfile
        
        script_path = Path("tests/validation/validate_all_formats.sh")
        assert script_path.exists()
        
        # Create a temporary directory and clean version of validation directory
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "validation"
            shutil.copytree("tests/validation", test_dir)
            
            # Remove logs directory to simulate missing logs
            logs_dir = test_dir / "logs"
            if logs_dir.exists():
                shutil.rmtree(logs_dir)
            
            result = subprocess.run(["./validate_all_formats.sh"],
                                  cwd=str(test_dir),
                                  capture_output=True,
                                  text=True)

            # Should fail with exit code 1 when no logs exist
            assert result.returncode == 1, "Should fail when no log files exist"
            assert "File not found" in result.stdout or "missing" in result.stdout.lower()
    
    def test_script_has_proper_error_handling(self):
        """Test that script handles errors gracefully."""
        script_path = Path("tests/validation/validate_all_formats.sh")
        with open(script_path) as f:
            content = f.read()
        
        # Should have proper error handling constructs
        assert "set -e" in content, "Script should exit on first error"
        assert "print_status" in content, "Should have status reporting function"
        assert "exit 1" in content, "Should exit with error code on failure"