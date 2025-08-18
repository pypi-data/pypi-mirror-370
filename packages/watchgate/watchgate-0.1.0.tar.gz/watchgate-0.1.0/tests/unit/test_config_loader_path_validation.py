"""Tests for ConfigLoader path validation improvements.

This test suite follows Test-Driven Development (TDD) methodology to verify
that ConfigLoader properly validates paths during configuration loading
and provides clear error messages for path-related issues.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
from watchgate.config.loader import ConfigLoader


class TestConfigLoaderPathValidation:
    """Test ConfigLoader path validation during configuration loading."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary directory for test configuration files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def basic_config_dict(self):
        """Basic valid configuration dictionary."""
        return {
            "proxy": {
                "transport": "stdio",
                "upstreams": [
                    {
                        "name": "test_server",
                        "command": ["python", "-m", "test_server"]
                    }
                ]
            }
        }
    
    def test_validates_json_auditing_plugin_paths(self, temp_config_dir, basic_config_dict):
        """Test that config loader validates file auditing plugin paths."""
        # Add file auditing plugin with invalid path
        basic_config_dict["plugins"] = {
            "auditing": {
                "_global": [
                    {
                        "policy": "json_auditing",
                        "enabled": True,
                        "config": {
                            "output_file": "/nonexistent/directory/audit.log"
                        }
                    }
                ]
            }
        }
        
        # Create config file
        config_file = temp_config_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(basic_config_dict, f)
        
        loader = ConfigLoader()
        
        # Should raise validation error about invalid path
        with pytest.raises(ValueError, match="Path validation failed"):
            loader.load_from_file(config_file)
    
    def test_validates_filesystem_security_plugin_paths(self, temp_config_dir, basic_config_dict):
        """Test that config loader validates filesystem security plugin paths."""
        # Add filesystem security plugin with invalid paths (using correct config structure)
        basic_config_dict["plugins"] = {
            "security": {
                "_global": [
                {
                    "policy": "filesystem_server_security",
                    "enabled": True,
                    "config": {
                        "read": ["/nonexistent/path1/*", "/nonexistent/path2/*"],
                        "write": ["/nonexistent/path3/*"]
                    }
                }
            ]
            }
        }
        
        # Create config file
        config_file = temp_config_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(basic_config_dict, f)
        
        loader = ConfigLoader()
        
        # Should raise validation error about invalid paths
        with pytest.raises(ValueError, match="Path validation failed"):
            loader.load_from_file(config_file)
    
    def test_validates_logging_configuration_paths(self, temp_config_dir, basic_config_dict):
        """Test that config loader validates logging configuration paths."""
        # Add logging configuration with invalid path
        basic_config_dict["logging"] = {
            "level": "INFO",
            "handlers": ["file"],
            "file_path": "/nonexistent/directory/watchgate.log"
        }
        
        # Create config file
        config_file = temp_config_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(basic_config_dict, f)
        
        loader = ConfigLoader()
        
        # Should raise validation error about invalid path
        with pytest.raises(ValueError, match="Path validation failed"):
            loader.load_from_file(config_file)
    
    def test_provides_specific_error_messages_for_path_failures(self, temp_config_dir, basic_config_dict):
        """Test that config loader provides specific error messages for path failures."""
        # Add multiple plugins with invalid paths
        basic_config_dict["plugins"] = {
            "auditing": {
                "_global": [
                {
                    "policy": "json_auditing", 
                    "enabled": True,
                    "config": {
                        "output_file": "/readonly/audit.log"
                    }
                }
            ]
            },
            "security": {
                "_global": [
                {
                    "policy": "filesystem_server_security",
                    "enabled": True,
                    "config": {
                        "read": ["/nonexistent/path/*"]
                    }
                }
            ]
            }
        }
        
        # Create config file
        config_file = temp_config_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(basic_config_dict, f)
        
        loader = ConfigLoader()
        
        with pytest.raises(ValueError) as exc_info:
            loader.load_from_file(config_file)
        
        error_message = str(exc_info.value)
        
        # Should include details about which plugins and paths failed
        assert "Path validation failed" in error_message
        assert "json_auditing" in error_message
        assert "/readonly/audit.log" in error_message or "/nonexistent/path" in error_message
    
    def test_passes_validation_with_valid_paths(self, temp_config_dir, basic_config_dict):
        """Test that config loader passes validation with valid paths."""
        # Create a valid log directory
        log_dir = temp_config_dir / "logs"
        log_dir.mkdir()
        
        # Add plugins with valid paths
        basic_config_dict["plugins"] = {
            "auditing": {
                "_global": [
                {
                    "policy": "json_auditing",
                    "enabled": True,
                    "config": {
                        "output_file": str(log_dir / "audit.log")
                    }
                }
            ]
            }
        }
        
        # Create config file
        config_file = temp_config_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(basic_config_dict, f)
        
        loader = ConfigLoader()
        
        # Should load successfully without validation errors
        config = loader.load_from_file(config_file)
        assert config is not None
        assert config.plugins is not None
    
    def test_skips_validation_for_disabled_plugins(self, temp_config_dir, basic_config_dict):
        """Test that config loader skips validation for disabled plugins."""
        # Add disabled plugin with invalid path
        basic_config_dict["plugins"] = {
            "auditing": {
                "_global": [
                {
                    "policy": "json_auditing",
                    "enabled": False,  # Disabled
                    "config": {
                        "output_file": "/definitely/nonexistent/audit.log"
                    }
                }
            ]
            }
        }
        
        # Create config file
        config_file = temp_config_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(basic_config_dict, f)
        
        loader = ConfigLoader()
        
        # Should load successfully because plugin is disabled
        config = loader.load_from_file(config_file)
        assert config is not None
    
    def test_validates_relative_paths_with_config_directory(self, temp_config_dir, basic_config_dict, tmp_path):
        """Test that config loader properly validates relative paths against config directory."""
        # Add plugin with relative path that will fail validation
        # Use a path that can't be created (contains null byte which is invalid in file paths)
        relative_path = "invalid\x00path/audit.log"
        
        basic_config_dict["plugins"] = {
            "auditing": {
                "_global": [
                {
                    "policy": "json_auditing",
                    "enabled": True,
                    "config": {
                        "output_file": relative_path  # Relative path that doesn't exist
                    }
                }
            ]
            }
        }
        
        # Create config file
        config_file = temp_config_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(basic_config_dict, f)
        
        loader = ConfigLoader()
        
        # Should raise validation error about invalid relative path
        with pytest.raises(ValueError, match="Path validation failed"):
            loader.load_from_file(config_file)
    
    def test_validates_home_directory_expansion(self, temp_config_dir, basic_config_dict):
        """Test that config loader validates paths after home directory expansion."""
        # Create a read-only directory to test permission issues with home directory paths
        import os
        readonly_dir = temp_config_dir / "readonly_test"
        readonly_dir.mkdir()
        
        # Make it read-only (remove write permission)
        os.chmod(readonly_dir, 0o444)
        
        try:
            # Add plugin with home directory path that expands to readonly location
            # We'll use a path that resolves to our readonly directory
            basic_config_dict["plugins"] = {
                "auditing": {
                    "_global": [
                    {
                        "policy": "json_auditing",
                        "enabled": True,
                        "config": {
                            "output_file": str(readonly_dir / "audit.log")
                        }
                    }
                ]
                }
            }
            
            # Create config file
            config_file = temp_config_dir / "config.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(basic_config_dict, f)
            
            loader = ConfigLoader()
            
            # Should raise validation error about permission issue
            with pytest.raises(ValueError, match="Path validation failed"):
                loader.load_from_file(config_file)
        finally:
            # Restore write permission so cleanup can work
            try:
                os.chmod(readonly_dir, 0o755)
            except:
                pass


class TestConfigLoaderPathValidationErrorDetails:
    """Test detailed error reporting for path validation failures."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary directory for test configuration files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def basic_config_dict(self):
        """Basic valid configuration dictionary."""
        return {
            "proxy": {
                "transport": "stdio",
                "upstreams": [
                    {
                        "name": "test_server",
                        "command": ["python", "-m", "test_server"]
                    }
                ]
            }
        }
    
    def test_error_message_includes_plugin_name_and_path(self, temp_config_dir, basic_config_dict):
        """Test that error messages include plugin name and problematic path."""
        invalid_path = "/completely/invalid/path/audit.log"
        basic_config_dict["plugins"] = {
            "auditing": {
                "_global": [
                {
                    "policy": "json_auditing",
                    "enabled": True,
                    "config": {
                        "output_file": invalid_path
                    }
                }
            ]
            }
        }
        
        config_file = temp_config_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(basic_config_dict, f)
        
        loader = ConfigLoader()
        
        with pytest.raises(ValueError) as exc_info:
            loader.load_from_file(config_file)
        
        error_message = str(exc_info.value)
        assert "json_auditing" in error_message
        assert invalid_path in error_message
    
    def test_error_message_suggests_solutions(self, temp_config_dir, basic_config_dict):
        """Test that error messages suggest solutions for common path issues."""
        basic_config_dict["plugins"] = {
            "auditing": {
                "_global": [
                {
                    "policy": "json_auditing",
                    "enabled": True,
                    "config": {
                        "output_file": "/readonly/directory/audit.log"
                    }
                }
            ]
            }
        }
        
        config_file = temp_config_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(basic_config_dict, f)
        
        loader = ConfigLoader()
        
        with pytest.raises(ValueError) as exc_info:
            loader.load_from_file(config_file)
        
        error_message = str(exc_info.value)
        # Should suggest common solutions
        assert any(keyword in error_message.lower() for keyword in ["create", "permission", "directory", "path"])
    
    def test_aggregates_multiple_path_validation_errors(self, temp_config_dir, basic_config_dict):
        """Test that multiple path validation errors are aggregated into one report."""
        basic_config_dict["plugins"] = {
            "auditing": {
                "_global": [
                {
                    "policy": "json_auditing",
                    "enabled": True,
                    "config": {
                        "output_file": "/invalid/path1/audit.log"
                    }
                }
            ]
            },
            "security": {
                "_global": [
                {
                    "policy": "filesystem_server_security",
                    "enabled": True,
                    "config": {
                        "read": ["/invalid/path2/*"],
                        "write": ["/invalid/path3/*"]
                    }
                }
            ]
            }
        }
        
        # Add logging with invalid path too
        basic_config_dict["logging"] = {
            "level": "INFO",
            "handlers": ["file"],
            "file_path": "/invalid/path4/watchgate.log"
        }
        
        config_file = temp_config_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(basic_config_dict, f)
        
        loader = ConfigLoader()
        
        with pytest.raises(ValueError) as exc_info:
            loader.load_from_file(config_file)
        
        error_message = str(exc_info.value)
        
        # Should include multiple plugin/component names
        assert "json_auditing" in error_message
        assert "filesystem_server_security" in error_message
        # Should include multiple paths or indicate multiple errors
        assert "multiple" in error_message.lower() or error_message.count("/invalid/") >= 2