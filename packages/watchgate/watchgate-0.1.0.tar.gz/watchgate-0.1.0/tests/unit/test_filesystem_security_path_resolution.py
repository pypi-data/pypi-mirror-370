"""Tests for FilesystemServerSecurityPlugin path resolution improvements.

This test suite follows Test-Driven Development (TDD) methodology to verify
that FilesystemServerSecurityPlugin implements proper path resolution with the 
PathResolvablePlugin interface.
"""

import pytest
import tempfile
from pathlib import Path
from watchgate.plugins.security.filesystem_server import FilesystemServerSecurityPlugin
from watchgate.plugins.interfaces import PathResolvablePlugin


class TestFilesystemSecurityPluginPathResolution:
    """Test FilesystemServerSecurityPlugin path resolution with PathResolvablePlugin interface."""
    
    def test_implements_path_resolvable_interface(self):
        """Test that FilesystemServerSecurityPlugin implements PathResolvablePlugin interface."""
        # FilesystemServerSecurityPlugin should implement PathResolvablePlugin
        assert issubclass(FilesystemServerSecurityPlugin, PathResolvablePlugin)
        
        # Test that it can be instantiated
        config = {"read": ["src/*"], "write": ["logs/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        # Should have PathResolvablePlugin methods
        assert hasattr(plugin, 'set_config_directory')
        assert hasattr(plugin, 'validate_paths')
    
    def test_set_config_directory_resolves_relative_patterns(self):
        """Test that set_config_directory properly resolves relative path patterns."""
        config = {"read": ["src/*", "docs/*"], "write": ["logs/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        # Set config directory - should resolve relative patterns
        config_dir = Path("/project/root")
        plugin.set_config_directory(config_dir)
        
        # Should have resolved patterns relative to config directory
        assert plugin.config_directory == config_dir
        # The original patterns should be preserved for use with pathspec
        assert "src/*" in plugin.permissions.get("read", [])
        assert "logs/*" in plugin.permissions.get("write", [])
    
    def test_set_config_directory_preserves_absolute_patterns(self):
        """Test that set_config_directory preserves absolute path patterns."""
        config = {
            "read": ["/var/log/*", "~/documents/*"],
            "write": ["/tmp/*"]
        }
        plugin = FilesystemServerSecurityPlugin(config)
        
        # Set config directory - should preserve absolute patterns
        config_dir = Path("/config/dir")
        plugin.set_config_directory(config_dir)
        
        # Should preserve absolute patterns
        assert "/var/log/*" in plugin.permissions.get("read", [])
        assert "/tmp/*" in plugin.permissions.get("write", [])
        assert "~/documents/*" in plugin.permissions.get("read", [])
    
    def test_set_config_directory_with_invalid_type_raises_error(self):
        """Test that set_config_directory raises error for invalid config_directory type."""
        config = {"read": ["src/*"]}
        plugin = FilesystemServerSecurityPlugin(config)
        
        # Should raise TypeError for invalid type
        with pytest.raises(TypeError, match="config_directory must be str or Path"):
            plugin.set_config_directory(123)
    
    def test_validate_paths_returns_empty_for_valid_patterns(self):
        """Test that validate_paths returns empty list for valid path patterns."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some directories and files that match the patterns
            src_dir = Path(temp_dir) / "src"
            src_dir.mkdir()
            (src_dir / "file1.py").touch()  # Create file that matches src/*
            
            logs_dir = Path(temp_dir) / "logs"
            logs_dir.mkdir()
            (logs_dir / "app.log").touch()  # Create file that matches logs/*
            
            config = {
                "read": ["src/*"],
                "write": [str(logs_dir / "*")]  # Use absolute path
            }
            plugin = FilesystemServerSecurityPlugin(config)
            
            # Set config directory
            plugin.set_config_directory(temp_dir)
            
            # Should return no errors for valid patterns
            errors = plugin.validate_paths()
            assert errors == []
    
    def test_validate_paths_returns_warnings_for_patterns_with_no_matches(self):
        """Test that validate_paths returns warnings for patterns that don't match anything."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "read": ["nonexistent/*", "also_missing/*"],
                "write": ["missing_logs/*"]
            }
            plugin = FilesystemServerSecurityPlugin(config)
            
            # Set config directory
            plugin.set_config_directory(temp_dir)
            
            # Should return warnings for patterns that don't match anything
            errors = plugin.validate_paths()
            assert len(errors) >= 2  # At least warnings for nonexistent patterns
            assert any("nonexistent" in error for error in errors)
            assert any("missing_logs" in error for error in errors)
    
    def test_validate_paths_handles_absolute_patterns(self):
        """Test that validate_paths properly handles absolute path patterns."""
        config = {
            "read": ["/nonexistent/absolute/path/*"],
            "write": ["/another/missing/path/*"]
        }
        plugin = FilesystemServerSecurityPlugin(config)
        
        # Should return warnings for absolute paths that don't exist
        errors = plugin.validate_paths()
        assert len(errors) >= 2
        assert any("/nonexistent/absolute/path" in error for error in errors)
        assert any("/another/missing/path" in error for error in errors)
    
    def test_validate_paths_handles_home_directory_patterns(self):
        """Test that validate_paths properly handles home directory patterns."""
        config = {
            "read": ["~/nonexistent_user_dir/*"],
            "write": ["~root/missing/*"]
        }
        plugin = FilesystemServerSecurityPlugin(config)
        
        # Should validate home directory patterns
        errors = plugin.validate_paths()
        # Might return warnings if paths don't exist, but shouldn't crash
        assert isinstance(errors, list)
    
    def test_validate_paths_provides_specific_error_messages(self):
        """Test that validate_paths provides specific, actionable error messages."""
        config = {
            "read": ["completely/nonexistent/path/*"],
            "write": ["another/missing/dir/*"]
        }
        plugin = FilesystemServerSecurityPlugin(config)
        
        # Set config directory
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin.set_config_directory(temp_dir)
            
            errors = plugin.validate_paths()
            assert len(errors) >= 1
            
            # Should include pattern and permission type in error messages
            found_read_error = any("read" in error and "completely/nonexistent/path" in error for error in errors)
            found_write_error = any("write" in error and "another/missing/dir" in error for error in errors)
            assert found_read_error or found_write_error


class TestFilesystemSecurityPluginPathValidation:
    """Test path validation behavior for various pattern types."""
    
    def test_validates_glob_patterns_correctly(self):
        """Test that glob pattern validation works correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test structure
            test_dir = Path(temp_dir)
            (test_dir / "src").mkdir()
            (test_dir / "src" / "file1.py").touch()
            (test_dir / "src" / "file2.py").touch()
            (test_dir / "logs").mkdir()
            (test_dir / "logs" / "app.log").touch()  # Create file that matches logs/*
            
            config = {
                "read": ["src/*.py", "logs/*"],
                "write": ["logs/*"]
            }
            plugin = FilesystemServerSecurityPlugin(config)
            plugin.set_config_directory(temp_dir)
            
            # Should validate successfully since patterns match existing files
            errors = plugin.validate_paths()
            # Should not have any critical errors since patterns have matches
            assert len(errors) == 0
    
    def test_handles_negation_patterns(self):
        """Test that negation patterns (!pattern) are handled correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "read": ["src/*", "!src/*.tmp"],
                "write": ["logs/*", "!logs/sensitive.log"]
            }
            plugin = FilesystemServerSecurityPlugin(config)
            plugin.set_config_directory(temp_dir)
            
            # Should not crash on negation patterns
            errors = plugin.validate_paths()
            assert isinstance(errors, list)
    
    def test_handles_complex_patterns(self):
        """Test that complex glob patterns are handled correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "read": ["src/**/*.py", "docs/**/*.md"],
                "write": ["build/**/*", "logs/**/*.log"]
            }
            plugin = FilesystemServerSecurityPlugin(config)
            plugin.set_config_directory(temp_dir)
            
            # Should handle complex patterns without crashing
            errors = plugin.validate_paths()
            assert isinstance(errors, list)
    
    def test_empty_configuration_validates_successfully(self):
        """Test that empty configuration validates without errors."""
        config = {}
        plugin = FilesystemServerSecurityPlugin(config)
        
        # Should handle empty config gracefully
        errors = plugin.validate_paths()
        assert errors == []
    
    def test_configuration_with_empty_lists_validates_successfully(self):
        """Test that configuration with empty permission lists validates successfully."""
        config = {"read": [], "write": []}
        plugin = FilesystemServerSecurityPlugin(config)
        
        # Should handle empty lists gracefully
        errors = plugin.validate_paths()
        assert errors == []


class TestFilesystemSecurityPluginPathResolutionMethods:
    """Test specific path resolution methods and behaviors."""
    
    def test_resolves_patterns_relative_to_config_directory(self):
        """Test that patterns are resolved relative to config directory when checking matches."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test directory structure
            test_dir = Path(temp_dir)
            src_dir = test_dir / "src"
            src_dir.mkdir()
            (src_dir / "file.py").touch()
            
            config = {"read": ["src/*.py"]}
            plugin = FilesystemServerSecurityPlugin(config)
            plugin.set_config_directory(temp_dir)
            
            # Validation should find the file when pattern is resolved relative to config dir
            errors = plugin.validate_paths()
            assert len(errors) == 0  # No errors because pattern matches existing file
    
    def test_pattern_matching_respects_config_directory_context(self):
        """Test that pattern matching works correctly in config directory context."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "config"
            config_dir.mkdir()
            
            # Create files in subdirectory relative to config
            src_dir = config_dir / "src"
            src_dir.mkdir()
            (src_dir / "test.py").touch()
            
            config = {"read": ["src/*.py"]}
            plugin = FilesystemServerSecurityPlugin(config)
            plugin.set_config_directory(config_dir)
            
            # Should find files when patterns are evaluated relative to config directory
            errors = plugin.validate_paths()
            assert len(errors) == 0