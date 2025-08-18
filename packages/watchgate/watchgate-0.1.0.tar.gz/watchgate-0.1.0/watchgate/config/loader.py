"""Configuration loader for Watchgate MCP Gateway."""

import threading
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List

from .models import ProxyConfig, PluginsConfig, PluginsConfigSchema, LoggingConfig, LoggingConfigSchema, ProxyConfigSchema


class ConfigLoader:
    """YAML configuration file loader with validation."""
    
    # Class-level cache for discovered plugin policies
    _plugin_policy_cache: Dict[str, Dict[str, type]] = {}
    _cache_lock = threading.RLock()  # RLock allows re-entrant access
    
    def __init__(self):
        """Initialize ConfigLoader."""
        self.config_directory: Optional[Path] = None
    
    def load_from_file(self, path: Path) -> ProxyConfig:
        """Load configuration from YAML file.
        
        Args:
            path: Path to the YAML configuration file
            
        Returns:
            ProxyConfig: Loaded and validated configuration
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            ValueError: If the YAML syntax is invalid or configuration is malformed
        """
        # Resolve config file path to absolute and store directory
        absolute_config_path = path.resolve()
        config_directory = absolute_config_path.parent
        self.config_directory = config_directory
        
        # Check if file exists
        if not absolute_config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {absolute_config_path}")
        
        try:
            # Load YAML content
            with open(absolute_config_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            # Check for empty file
            if not content:
                raise ValueError("Configuration file is empty or invalid")
                
            # Parse YAML
            config_dict = yaml.safe_load(content)
            
            # Check if YAML only had comments or was empty
            if config_dict is None:
                raise ValueError("Configuration file is empty or invalid")
                
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax: {e}") from e
        except (IOError, OSError, UnicodeDecodeError) as e:
            raise ValueError(f"Error reading configuration file: {e}") from e
        
        # Load from parsed dictionary
        return self.load_from_dict(config_dict, config_directory)
        
    def load_from_dict(self, config_dict: Dict[str, Any], config_directory: Optional[Path] = None) -> ProxyConfig:
        """Load configuration from dictionary (for testing).
        
        Args:
            config_dict: Configuration dictionary
            config_directory: Directory containing the configuration file (for path resolution)
            
        Returns:
            ProxyConfig: Loaded and validated configuration
            
        Raises:
            ValueError: If configuration is missing required sections or invalid
        """
        # Validate presence of proxy section
        if 'proxy' not in config_dict:
            raise ValueError("Configuration must contain 'proxy' section")
        
        proxy_config = config_dict['proxy']
        
        # Check for required upstream configuration
        if 'upstreams' not in proxy_config:
            raise ValueError("Missing required 'upstreams' configuration")
        
        try:
            # Use Pydantic schema for validation and normalization
            schema = ProxyConfigSchema(**proxy_config)
            
            # Parse plugins and logging from top-level if present
            if 'plugins' in config_dict:
                schema.plugins = PluginsConfigSchema(**config_dict['plugins'])
            if 'logging' in config_dict:
                schema.logging = LoggingConfigSchema(**config_dict['logging'])
            
            # Convert schema to internal representation
            config = ProxyConfig.from_schema(schema, config_directory)
            
        except (ValueError, TypeError) as e:
            # Handle Pydantic validation errors and Python type errors
            raise ValueError(f"Configuration validation failed: {e}") from e
        
        # Run additional validation
        self.validate_config(config)
        
        # Run path validation for all path-aware components
        self.validate_paths(config, config_directory)
        
        return config
    
    def validate_config(self, config: ProxyConfig) -> None:
        """Validate configuration completeness and constraints.
        
        Args:
            config: Configuration to validate
            
        Raises:
            ValueError: If configuration has validation errors
        """
        # Basic validation is already done by dataclass __post_init__
        # This method can be extended for additional validation logic
        
        # Validate transport-specific requirements
        if config.transport not in ("stdio", "http"):
            raise ValueError("Transport must be 'stdio' or 'http'")
        
        if config.transport == "http" and config.http is None:
            raise ValueError("HTTP transport requires http configuration")
        
        # The dataclass __post_init__ methods will validate individual components
        # when the objects are created, so no additional validation needed here
        # unless we want to add cross-component validation rules
    
    def validate_paths(self, config: ProxyConfig, config_directory: Optional[Path] = None) -> None:
        """Validate paths in all path-aware components.
        
        Args:
            config: Configuration to validate paths for
            config_directory: Directory containing the configuration file (for path resolution)
            
        Raises:
            ValueError: If any path validation fails
        """
        path_errors = []
        
        # Validate logging configuration paths
        if config.logging:
            logging_errors = self._validate_logging_paths(config.logging)
            if logging_errors:
                path_errors.extend([f"Logging: {error}" for error in logging_errors])
        
        # Validate plugin paths
        if config.plugins:
            plugin_errors = self._validate_plugin_paths(config.plugins, config_directory)
            if plugin_errors:
                path_errors.extend(plugin_errors)
        
        # If any path validation errors occurred, raise them
        if path_errors:
            error_summary = f"Path validation failed with {len(path_errors)} error(s):\n"
            error_details = "\n".join([f"  - {error}" for error in path_errors])
            raise ValueError(error_summary + error_details)
    
    def _validate_logging_paths(self, logging_config: LoggingConfig) -> List[str]:
        """Validate paths in logging configuration.
        
        Args:
            logging_config: Logging configuration to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Check if file handler is enabled and file_path is configured
        if hasattr(logging_config, 'file_path') and logging_config.file_path:
            try:
                from pathlib import Path
                import os
                
                log_path = Path(logging_config.file_path)
                parent_dir = log_path.parent
                
                # Check if parent directory exists
                if not parent_dir.exists():
                    errors.append(f"Log file parent directory does not exist: {parent_dir} (for file_path: {logging_config.file_path})")
                else:
                    # Check if parent directory is writable
                    if not os.access(parent_dir, os.W_OK):
                        errors.append(f"No write permission to log file parent directory: {parent_dir} (for file_path: {logging_config.file_path})")
                        
            except (OSError, IOError, PermissionError) as e:
                errors.append(f"Error validating log file path '{logging_config.file_path}': {e}")
        
        return errors
    
    def _validate_plugin_paths(self, plugins_config: PluginsConfig, config_directory: Optional[Path] = None) -> List[str]:
        """Validate paths in plugin configurations.
        
        Args:
            plugins_config: Plugin configuration to validate
            config_directory: Directory containing the configuration file (for path resolution)
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Import plugin classes for path validation
        try:
            from watchgate.plugins.interfaces import PathResolvablePlugin
        except ImportError as e:
            # Log import failure and skip path validation
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Cannot validate plugin paths due to import error: {e}. Skipping plugin path validation.")
            return []  # Return empty list - this is not a path validation error
        
        # Validate security plugin paths (upstream-scoped structure)
        for upstream, plugin_configs in plugins_config.security.items():
            for plugin_config in plugin_configs:
                if plugin_config.enabled:
                    plugin_errors = self._validate_single_plugin_paths(
                        "security", plugin_config, config_directory
                    )
                    if plugin_errors:
                        scope_label = "(global scope)" if upstream == "_global" else f"({upstream})"
                        errors.extend([f"Security plugin '{plugin_config.policy}' {scope_label}: {error}" for error in plugin_errors])
        
        # Validate auditing plugin paths (upstream-scoped structure)
        for upstream, plugin_configs in plugins_config.auditing.items():
            for plugin_config in plugin_configs:
                if plugin_config.enabled:
                    plugin_errors = self._validate_single_plugin_paths(
                        "auditing", plugin_config, config_directory
                    )
                    if plugin_errors:
                        scope_label = "(global scope)" if upstream == "_global" else f"({upstream})"
                        errors.extend([f"Auditing plugin '{plugin_config.policy}' {scope_label}: {error}" for error in plugin_errors])
        
        return errors
    
    def _validate_single_plugin_paths(self, plugin_type: str, plugin_config, config_directory: Optional[Path] = None) -> List[str]:
        """Validate paths for a single plugin.
        
        Args:
            plugin_type: Type of plugin ("security" or "auditing")
            plugin_config: Plugin configuration
            config_directory: Directory containing the configuration file (for path resolution)
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        try:
            # Get plugin class using policy discovery
            plugin_class = self._get_plugin_class(plugin_type, plugin_config.policy)
            if not plugin_class:
                return [f"Plugin class not found for policy '{plugin_config.policy}'"]
            
            # Check if plugin implements PathResolvablePlugin interface
            from watchgate.plugins.interfaces import PathResolvablePlugin
            if not issubclass(plugin_class, PathResolvablePlugin):
                # Plugin doesn't use paths, no validation needed
                return []
            
            # Check if plugin is critical (default to True for security)
            is_critical = plugin_config.config.get("critical", True)
            
            # Create temporary plugin instance for path validation
            temp_plugin = plugin_class(plugin_config.config)
            
            # Set config directory for path resolution
            if config_directory:
                temp_plugin.set_config_directory(config_directory)
            
            # Validate paths
            validation_errors = temp_plugin.validate_paths()
            if validation_errors:
                if is_critical:
                    # For critical plugins, path validation errors are fatal
                    errors.extend(validation_errors)
                else:
                    # For non-critical plugins, log path validation errors but don't fail startup
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"Non-critical {plugin_type} plugin '{plugin_config.policy}' has path validation errors: {'; '.join(validation_errors)}"
                    )
                
        except (ImportError, AttributeError, TypeError, ValueError) as e:
            # Check if plugin is critical to determine error handling behavior
            is_critical = plugin_config.config.get("critical", True)
            if is_critical:
                errors.append(f"Error validating plugin paths: {e}")
            else:
                # For non-critical plugins, log error but don't fail startup
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Non-critical {plugin_type} plugin '{plugin_config.policy}' path validation failed: {e}")
        
        return errors
    
    def _get_plugin_class(self, category: str, policy_name: str):
        """Get plugin class using PluginManager's discovery logic with thread-safe caching.
        
        Args:
            category: Plugin category ("security" or "auditing")
            policy_name: Policy name to look up
            
        Returns:
            Plugin class or None if not found
        """
        with self._cache_lock:
            # Check cache first
            if category in self._plugin_policy_cache:
                cached_result = self._plugin_policy_cache[category].get(policy_name)
                if cached_result is not None or policy_name in self._plugin_policy_cache[category]:
                    # Return cached result (could be None if policy doesn't exist)
                    return cached_result
            
            try:
                # Discover policies for this category if not cached
                if category not in self._plugin_policy_cache:
                    from watchgate.plugins.manager import PluginManager
                    temp_manager = PluginManager({}, None)
                    available_policies = temp_manager._discover_policies(category)
                    self._plugin_policy_cache[category] = available_policies
                
                return self._plugin_policy_cache[category].get(policy_name)
            except Exception:
                # Cache negative result to prevent repeated discovery failures
                if category not in self._plugin_policy_cache:
                    self._plugin_policy_cache[category] = {}
                # Don't cache individual policy failures, just empty category
                return None
