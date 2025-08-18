"""Watchgate MCP Gateway Server - Main entry point."""

import argparse
import asyncio
import logging
import logging.handlers
import sys
import time
from pathlib import Path
from typing import Optional

from watchgate.cli.startup_error_handler import StartupErrorHandler
from watchgate.config.loader import ConfigLoader
from watchgate.config.models import LoggingConfig
from watchgate.proxy.server import MCPProxy
from watchgate.plugins.manager import PluginManager


class UTCFormatter(logging.Formatter):
    """Custom formatter that uses UTC time."""
    converter = time.gmtime


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    
    # Create UTC formatter and handler
    formatter = UTCFormatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S.%fZ"
    )
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    
    # Reduce noise from some third-party libraries
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def setup_logging_from_config(logging_config: Optional[LoggingConfig] = None, verbose: bool = False) -> None:
    """Configure logging based on configuration file or fallback to default.
    
    Args:
        logging_config: Optional logging configuration from config file
        verbose: Whether to enable verbose debug logging (overrides config level)
    """
    # Determine log level - verbose flag overrides config
    if verbose:
        log_level = logging.DEBUG
    elif logging_config and hasattr(logging_config, 'level') and isinstance(logging_config.level, str):
        log_level = getattr(logging, logging_config.level.upper())
    else:
        log_level = logging.INFO
    
    # If no logging config or logging config is not a proper LoggingConfig object, use simple stderr logging
    if not logging_config or not isinstance(logging_config, LoggingConfig):
        # Use UTC formatter for default logging too
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.handlers.clear()
        
        formatter = UTCFormatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S.%fZ"
        )
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        
        # Reduce noise from some third-party libraries
        logging.getLogger("asyncio").setLevel(logging.WARNING)
        return
    
    # Determine format and date format from config
    format_str = logging_config.format
    date_format_str = logging_config.date_format
    
    # If only stderr handler, set up manually with UTC formatter
    if logging_config.handlers == ["stderr"]:
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.handlers.clear()
        
        formatter = UTCFormatter(fmt=format_str, datefmt=date_format_str)
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        
        # Reduce noise from some third-party libraries
        logging.getLogger("asyncio").setLevel(logging.WARNING)
        return
    
    # For file-only or combined handlers, set up manually
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create UTC formatter
    formatter = UTCFormatter(fmt=format_str, datefmt=date_format_str)
    
    # Set up handlers based on configuration
    for handler_type in logging_config.handlers:
        if handler_type == "stderr":
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(formatter)
            root_logger.addHandler(handler)
        elif handler_type == "file":
            if logging_config.file_path:
                # Ensure log directory exists
                logging_config.file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Create rotating file handler
                handler = logging.handlers.RotatingFileHandler(
                    logging_config.file_path,
                    maxBytes=logging_config.max_file_size_mb * 1024 * 1024,
                    backupCount=logging_config.backup_count
                )
                handler.setFormatter(formatter)
                root_logger.addHandler(handler)
    
    # Reduce noise from some third-party libraries
    logging.getLogger("asyncio").setLevel(logging.WARNING)


async def run_proxy(config_path: Path, verbose: bool = False) -> None:
    """Run the Watchgate proxy server."""
    logger = None
    try:
        # Load configuration first to get logging settings
        config_loader = ConfigLoader()
        config = config_loader.load_from_file(config_path)
        
        # Set up logging using config or fallback
        setup_logging_from_config(config.logging, verbose)
        logger = logging.getLogger(__name__)
        
        logger.info(f"Loading configuration from {config_path}")
        
        # Create and start proxy
        logger.info("Starting Watchgate MCP Gateway")
        proxy = MCPProxy(config, config_loader.config_directory)
        logger.info("Watchgate is ready and accepting connections")
        await proxy.run()
            
    except FileNotFoundError as e:
        # Use error handler to communicate to MCP client
        await StartupErrorHandler.handle_startup_error(
            e, f"Loading configuration from {config_path}"
        )
    except ValueError as e:
        # Use error handler to communicate to MCP client
        await StartupErrorHandler.handle_startup_error(
            e, "Parsing configuration file"
        )
    except KeyboardInterrupt:
        if logger:
            logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        # Use error handler to communicate to MCP client
        await StartupErrorHandler.handle_startup_error(
            e, "Starting Watchgate proxy"
        )


async def debug_show_plugin_order(config_path: Path) -> None:
    """Show the current plugin execution order with priorities.
    
    Loads the configured plugins and displays their execution order
    based on priorities. Shows both security and auditing plugins
    with their respective execution models.
    """
    _print_debug_header("Plugin Execution Order")
    
    try:
        # Load configuration first to get logging settings
        config_loader = ConfigLoader()
        config = config_loader.load_from_file(config_path)
        
        # Set up logging using config
        setup_logging_from_config(config.logging)
        logger = logging.getLogger(__name__)
        
        # Create plugin manager and load plugins
        plugins_config = config.plugins.to_dict() if config.plugins else {}
        plugin_manager = PluginManager(plugins_config, config_loader.config_directory)
        await plugin_manager.load_plugins()
        
        # Show security plugins
        if plugin_manager.security_plugins:
            print("\nSecurity Plugins (execute in order, stop on first denial):")
            for i, plugin in enumerate(plugin_manager.security_plugins, 1):
                priority = getattr(plugin, 'priority', 50)
                plugin_id = getattr(plugin, 'plugin_id', plugin.__class__.__name__)
                print(f"  {i}. {plugin_id} (priority: {priority})")
        else:
            print("\nSecurity Plugins: None configured")
        
        # Show auditing plugins
        if plugin_manager.auditing_plugins:
            print("\nAuditing Plugins (all execute in order):")
            for i, plugin in enumerate(plugin_manager.auditing_plugins, 1):
                priority = getattr(plugin, 'priority', 50)
                plugin_id = getattr(plugin, 'plugin_id', plugin.__class__.__name__)
                print(f"  {i}. {plugin_id} (priority: {priority})")
        else:
            print("\nAuditing Plugins: None configured")
        
        print(f"\nTotal plugins loaded: {len(plugin_manager.security_plugins) + len(plugin_manager.auditing_plugins)}")
        
    except Exception as e:
        setup_logging_from_config(None)
        logger = logging.getLogger(__name__)
        logger.error(f"Error in debug_show_plugin_order: {e}")
        # Use inline error handling for this case since _handle_config_error is defined later
        if isinstance(e, FileNotFoundError):
            print(f"❌ Configuration file not found: {config_path}")
        else:
            print(f"❌ Error loading plugins: {e}")
        sys.exit(1)


def _print_debug_header(title: str) -> None:
    """Print a consistent debug command header."""
    print(f"{title}:")
    print("=" * 50)


def _handle_config_error(e: Exception, config_path: Path) -> None:
    """Handle configuration loading errors with specific error types."""
    if isinstance(e, FileNotFoundError):
        print(f"❌ Configuration file not found: {config_path}")
    elif isinstance(e, ValueError):
        if "YAML" in str(e) or "syntax" in str(e).lower():
            print(f"❌ YAML syntax error: {e}")
        elif "missing" in str(e).lower() or "required" in str(e).lower():
            print(f"❌ Missing required field: {e}")
        else:
            print(f"❌ Configuration validation failed: {e}")
    elif isinstance(e, TypeError):
        print(f"❌ Type validation error: {e}")
    else:
        print(f"❌ Configuration validation failed: {e}")
    sys.exit(1)


async def debug_validate_config(config_path: Path) -> None:
    """Validate configuration file for syntax and type errors.
    
    Checks the configuration file for:
    - Valid YAML syntax
    - Required fields presence
    - Correct data types
    - Schema compliance
    """
    _print_debug_header("Configuration Validation")
    
    try:
        # Try to load the configuration
        config_loader = ConfigLoader()
        config = config_loader.load_from_file(config_path)
        
        print("✅ Configuration is valid")
        print("All required fields present")
        print("All types valid")
        print("YAML syntax correct")
        
    except Exception as e:
        _handle_config_error(e, config_path)


def _get_plugin_description(policy_class) -> str:
    """Extract description from plugin class docstring."""
    if policy_class.__doc__:
        # Get first line of docstring and clean it up
        description = policy_class.__doc__.split('\n')[0].strip()
        return description if description else "No description available"
    return "No description available"


def _print_plugin_category(category_name: str, policies: dict) -> int:
    """Print plugins for a category and return count."""
    print(f"\n{category_name} Plugins:")
    if policies:
        for policy_name, policy_class in policies.items():
            description = _get_plugin_description(policy_class)
            print(f"  - {policy_name}: {description}")
        return len(policies)
    else:
        print("  None found")
        return 0


async def debug_list_available_plugins() -> None:
    """List all available plugins with their descriptions.
    
    Discovers and displays all security and auditing plugins
    available in the system, including their descriptions
    extracted from class docstrings.
    """
    _print_debug_header("Available Plugins")
    
    try:
        # Create a temporary plugin manager to discover available plugins
        plugin_manager = PluginManager({}, None)
        
        # Discover and display security plugins
        security_policies = plugin_manager._discover_policies("security")
        security_count = _print_plugin_category("Security", security_policies)
        
        # Discover and display auditing plugins  
        auditing_policies = plugin_manager._discover_policies("auditing")
        auditing_count = _print_plugin_category("Auditing", auditing_policies)
        
        total_plugins = security_count + auditing_count
        print(f"\nTotal available plugins: {total_plugins}")
        
    except Exception as e:  
        print(f"❌ Error discovering plugins: {e}")
        sys.exit(1)


def _print_validated_plugins(plugins_config: dict) -> None:
    """Print the list of successfully validated plugins."""
    for category in ["security", "auditing"]:
        if plugins_config.get(category):
            category_config = plugins_config[category]
            
            # Handle upstream-scoped format (dictionary only)
            if isinstance(category_config, dict):
                # Iterate through upstream configs
                for upstream_name, plugin_list in category_config.items():
                    if isinstance(plugin_list, list):
                        for plugin_config in plugin_list:
                            if plugin_config.get("enabled", True):
                                policy_name = plugin_config.get("policy", "unknown")
                                upstream_display = f" ({upstream_name})" if upstream_name != "_global" else ""
                                print(f"  {policy_name}{upstream_display}: Valid")


async def debug_validate_plugin_config(config_path: Path) -> None:
    """Validate plugin configurations for correctness.
    
    Validates all configured plugins by attempting to load them
    and checking for configuration errors. Reports specific
    validation failures and lists successfully validated plugins.
    """
    _print_debug_header("Plugin Configuration Validation")
    
    try:
        # Load configuration first
        config_loader = ConfigLoader()
        config = config_loader.load_from_file(config_path)
        
        plugins_config = config.plugins.to_dict() if config.plugins else {}
        
        if not plugins_config or (not plugins_config.get("security") and not plugins_config.get("auditing")):
            print("No plugins configured")
            return
        
        # Create plugin manager and try to load plugins to validate config
        plugin_manager = PluginManager(plugins_config, config_loader.config_directory)
        
        try:
            await plugin_manager.load_plugins()
            
            # Check if any plugins failed to load
            if plugin_manager.has_load_failures():
                failures = plugin_manager.get_load_failures()
                print("❌ Plugin configuration errors found:")
                for failure in failures:
                    print(f"  {failure['type'].title()} plugin '{failure['policy']}': {failure['error']}")
                sys.exit(1)
            else:
                print("✅ All plugin configurations are valid")
                _print_validated_plugins(plugins_config)
            
        except Exception as e:
            print(f"❌ Plugin configuration errors found:")
            print(f"  Configuration validation failed: {e}")
            sys.exit(1)
            
    except Exception as e:
        _handle_config_error(e, config_path)


async def debug_validate_priorities(config_path: Path) -> None:
    """Validate plugin priority configuration.
    
    Validates that all plugin priorities are within the valid range
    (0-100) and warns about potential issues such as duplicate
    priorities that may cause unpredictable execution order.
    """
    _print_debug_header("Plugin Priority Validation")
    
    try:
        # Load configuration first to get logging settings
        config_loader = ConfigLoader()
        config = config_loader.load_from_file(config_path)
        
        # Set up logging using config
        setup_logging_from_config(config.logging)
        logger = logging.getLogger(__name__)
        
        # Create plugin manager and validate
        plugins_config = config.plugins.to_dict() if config.plugins else {}
        plugin_manager = PluginManager(plugins_config, config_loader.config_directory)
        
        validation_passed = True
        issues = []
        
        try:
            await plugin_manager.load_plugins()
            
            # Check if any plugins failed to load
            if plugin_manager.has_load_failures():
                validation_passed = False
                failures = plugin_manager.get_load_failures()
                print("❌ Priority validation failed:")
                for failure in failures:
                    print(f"  {failure['type'].title()} plugin '{failure['policy']}': {failure['error']}")
            else:
                print("✅ All plugin priorities are valid (0-100 range)")
            
            # Only check for potential issues if no load failures
            if not plugin_manager.has_load_failures():
                # Check for potential issues
                all_plugins = plugin_manager.security_plugins + plugin_manager.auditing_plugins
            
                # Check for same priorities
                priorities = {}
                for plugin in all_plugins:
                    priority = getattr(plugin, 'priority', 50)
                    plugin_id = getattr(plugin, 'plugin_id', plugin.__class__.__name__)
                    
                    if priority not in priorities:
                        priorities[priority] = []
                    priorities[priority].append(plugin_id)
                
                same_priority = {p: plugins for p, plugins in priorities.items() if len(plugins) > 1}
                if same_priority:
                    print("\n⚠️  Plugins with same priority (execution order may be unpredictable):")
                    for priority, plugins in same_priority.items():
                        print(f"  Priority {priority}: {', '.join(plugins)}")
                    issues.append("Multiple plugins with same priority")
                
                # Summary
                if issues:
                    print(f"\n⚠️  {len(issues)} potential issue(s) found, but priorities are valid")
                    print("Consider reviewing plugin priority assignments for optimal ordering")
                else:
                    print("\n✅ Plugin priority configuration looks good!")
                
        except ValueError as e:
            validation_passed = False
            print(f"❌ Priority validation failed: {e}")
        except Exception as e:
            validation_passed = False
            print(f"❌ Error validating priorities: {e}")
        
        if not validation_passed:
            sys.exit(1)
            
    except Exception as e:
        setup_logging_from_config(None)
        logger = logging.getLogger(__name__)
        logger.error(f"Error in debug_validate_priorities: {e}")
        _handle_config_error(e, config_path)


def main():
    """Main entry point for Watchgate."""
    parser = argparse.ArgumentParser(
        description="Watchgate MCP Gateway Server - Monitor and control AI tool usage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Launch TUI configuration interface
  %(prog)s --config myconfig.yaml       # Launch TUI with specific config
  %(prog)s proxy --config config.yaml  # Run as MCP proxy server
  %(prog)s debug plugins --show-order  # Debug plugin execution order
        """
    )
    
    # Global arguments (available for all modes)
    parser.add_argument(
        "--config", "-c",
        type=Path,
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Watchgate v0.1.0"
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Proxy command - for MCP client integration
    proxy_parser = subparsers.add_parser(
        "proxy", 
        help="Run as MCP proxy server",
        description="Run Watchgate as an MCP proxy server for client integration"
    )
    proxy_parser.add_argument(
        "--config", "-c",
        type=Path,
        required=True,
        help="Path to configuration file (required for proxy mode)"
    )
    proxy_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose debug logging"
    )
    
    # Debug command
    debug_parser = subparsers.add_parser("debug", help="Debug and diagnostic commands")
    debug_subparsers = debug_parser.add_subparsers(dest="debug_command", help="Debug commands")
    
    # Debug plugins command
    plugins_parser = debug_subparsers.add_parser("plugins", help="Plugin debugging commands")
    plugins_group = plugins_parser.add_mutually_exclusive_group(required=True)
    plugins_group.add_argument(
        "--show-order",
        action="store_true",
        help="Show current plugin execution order with priorities"
    )
    plugins_group.add_argument(
        "--validate-priorities",
        action="store_true", 
        help="Validate plugin priorities are in range (0-100) and check for conflicts"
    )
    plugins_group.add_argument(
        "--list-available",
        action="store_true",
        help="List all available plugins with descriptions"
    )
    plugins_group.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate plugin configurations by attempting to load them"
    )
    
    # Debug config command
    config_parser = debug_subparsers.add_parser("config", help="Configuration debugging commands")
    config_parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate configuration file syntax, types, and required fields"
    )
    
    args = parser.parse_args()
    
    # Handle commands
    try:
        if args.command == "proxy":
            # Run as MCP proxy server
            asyncio.run(run_proxy(args.config, args.verbose))
        elif args.command == "debug":
            # Handle debug commands
            config_path = getattr(args, 'config', Path("watchgate.yaml"))
            if args.debug_command == "plugins":
                if args.show_order:
                    asyncio.run(debug_show_plugin_order(config_path))
                elif args.validate_priorities:
                    asyncio.run(debug_validate_priorities(config_path))
                elif args.list_available:
                    asyncio.run(debug_list_available_plugins())
                elif args.validate_config:
                    asyncio.run(debug_validate_plugin_config(config_path))
            elif args.debug_command == "config":
                if args.validate:
                    asyncio.run(debug_validate_config(config_path))
        else:
            # Default behavior - launch TUI
            _handle_tui_mode(args.config)
    except KeyboardInterrupt:
        # Clean exit on Ctrl+C
        pass


def _handle_tui_mode(config_path: Optional[Path]) -> None:
    """Handle TUI mode launch."""
    # Try to import and run TUI
    try:
        from watchgate.tui import run_tui
        run_tui(config_path)
    except ImportError:
        print(
            "Error: TUI functionality requires the Textual library.\n\n"
            "Install with TUI support:\n"
            "  pip install 'watchgate[tui]'\n\n"
            "Or run in proxy mode:\n"
            "  watchgate proxy --config YOUR_CONFIG.yaml\n",
            file=sys.stderr
        )
        sys.exit(1)
    except Exception as e:
        print(f"Error launching TUI: {e}", file=sys.stderr)
        print("Try running in proxy mode: watchgate proxy --config YOUR_CONFIG.yaml", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
