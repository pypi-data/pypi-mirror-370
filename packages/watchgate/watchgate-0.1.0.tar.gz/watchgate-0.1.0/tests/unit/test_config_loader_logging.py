"""Unit tests for logging configuration in config loader."""

import pytest
from pathlib import Path

from watchgate.config.loader import ConfigLoader
from watchgate.config.models import LoggingConfig


class TestConfigLoaderLogging:
    """Test ConfigLoader with logging configuration."""
    
    def test_load_config_with_logging_section(self):
        """Test loading configuration with logging section."""
        config_dict = {
            "proxy": {
                "transport": "stdio",
                "upstreams": [
                    {
                        "name": "test_server",
                        "command": ["python", "-m", "test_server"]
                    }
                ]
            },
            "logging": {
                "level": "DEBUG",
                "handlers": ["stderr", "file"],
                "file_path": "logs/watchgate.log",
                "max_file_size_mb": 20,
                "backup_count": 3
            }
        }
        
        loader = ConfigLoader()
        config = loader.load_from_dict(config_dict)
        
        assert config.logging is not None
        assert config.logging.level == "DEBUG"
        assert config.logging.handlers == ["stderr", "file"]
        assert config.logging.file_path == Path("logs/watchgate.log")
        assert config.logging.max_file_size_mb == 20
        assert config.logging.backup_count == 3
    
    def test_load_config_without_logging_section(self):
        """Test loading configuration without logging section defaults to None."""
        config_dict = {
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
        
        loader = ConfigLoader()
        config = loader.load_from_dict(config_dict)
        
        assert config.logging is None
    
    def test_load_config_with_minimal_logging_section(self):
        """Test loading configuration with minimal logging section uses defaults."""
        config_dict = {
            "proxy": {
                "transport": "stdio",
                "upstreams": [
                    {
                        "name": "test_server",
                        "command": ["python", "-m", "test_server"]
                    }
                ]
            },
            "logging": {
                "level": "WARNING"
            }
        }
        
        loader = ConfigLoader()
        config = loader.load_from_dict(config_dict)
        
        assert config.logging is not None
        assert config.logging.level == "WARNING"
        assert config.logging.handlers == ["stderr"]  # default
        assert config.logging.file_path is None  # default
        assert config.logging.max_file_size_mb == 10  # default
        assert config.logging.backup_count == 5  # default
    
    def test_load_config_with_invalid_logging_config(self):
        """Test loading configuration with invalid logging config raises ValueError."""
        config_dict = {
            "proxy": {
                "transport": "stdio",
                "upstreams": [
                    {
                        "name": "test_server",
                        "command": ["python", "-m", "test_server"]
                    }
                ]
            },
            "logging": {
                "level": "INVALID_LEVEL"
            }
        }
        
        loader = ConfigLoader()
        with pytest.raises(ValueError, match="Configuration validation failed"):
            loader.load_from_dict(config_dict)
    
    def test_load_config_logging_file_without_path(self):
        """Test loading configuration with file handler but no path raises ValueError."""
        config_dict = {
            "proxy": {
                "transport": "stdio",
                "upstreams": [
                    {
                        "name": "test_server",
                        "command": ["python", "-m", "test_server"]
                    }
                ]
            },
            "logging": {
                "handlers": ["file"]
            }
        }
        
        loader = ConfigLoader()
        with pytest.raises(ValueError, match="Configuration validation failed"):
            loader.load_from_dict(config_dict)
