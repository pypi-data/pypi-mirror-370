"""Integration tests for policy-based plugin system."""

import tempfile
import pytest
from pathlib import Path

from watchgate.config import ConfigLoader
from watchgate.plugins.manager import PluginManager
from watchgate.plugins.security.tool_allowlist import ToolAllowlistPlugin
from watchgate.plugins.auditing.json_lines import JsonAuditingPlugin


class TestPolicyIntegration:
    """Test end-to-end integration of policy-based plugin system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.loader = ConfigLoader()
    
    @pytest.mark.asyncio
    async def test_load_config_and_initialize_plugins(self, tmp_path):
        """Test loading policy-based configuration and initializing plugins."""
        audit_file = tmp_path / "test_audit.log"
        yaml_content = f"""
proxy:
  transport: stdio
  upstreams:
    - name: "test_server"
      command: "python -m test_server"
    
plugins:
  security:
    _global:
      - policy: "tool_allowlist"
        enabled: true
        config:
          mode: "allowlist"
          tools: 
            test_server: ["read_file", "write_file"]
  
  auditing:
    _global:
      - policy: "json_auditing"
        enabled: true
        config:
          output_file: "{audit_file}"
          format: "json"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            # Load configuration
            config = self.loader.load_from_file(Path(f.name))
            
            # Verify configuration loaded correctly
            assert config.plugins is not None
            assert len(config.plugins.security["_global"]) == 1
            assert len(config.plugins.auditing["_global"]) == 1
            assert config.plugins.security["_global"][0].policy == "tool_allowlist"
            assert config.plugins.auditing["_global"][0].policy == "json_auditing"
            
            # Convert to format expected by PluginManager (dictionary format)
            plugins_config = {
                "security": {
                    "_global": [plugin.to_dict() for plugin in config.plugins.security["_global"]]
                },
                "auditing": {
                    "_global": [plugin.to_dict() for plugin in config.plugins.auditing.get("_global", [])]
                }
            }
            
            # Initialize plugin manager with policy-based configuration
            manager = PluginManager(plugins_config)
            await manager.load_plugins()
            
            # Verify plugins were loaded successfully
            assert len(manager.security_plugins) == 1
            assert len(manager.auditing_plugins) == 1
            
            # Verify the loaded plugins are of the correct types
            security_plugin = manager.security_plugins[0]
            auditing_plugin = manager.auditing_plugins[0]
            
            # Check class names instead of isinstance due to import path issues
            assert security_plugin.__class__.__name__ == "ToolAllowlistPlugin"
            assert auditing_plugin.__class__.__name__ == "JsonAuditingPlugin"
            
            # Verify plugin configuration was applied correctly
            assert security_plugin.mode == "allowlist"
            assert "read_file" in security_plugin.tools_config.get("test_server", [])
            assert "write_file" in security_plugin.tools_config.get("test_server", [])
            
            assert auditing_plugin.output_file == str(audit_file)
    
    @pytest.mark.asyncio
    async def test_policy_not_found_error_integration(self):
        """Test error handling when a policy is not found."""
        yaml_content = """
proxy:
  transport: stdio
  upstreams:
    - name: "test_server"
      command: "python -m test_server"
    
plugins:
  security:
    _global:
      - policy: "nonexistent_policy"
        enabled: true
        config:
          mode: "allowlist"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            # ConfigLoader should now catch nonexistent policy during path validation
            with pytest.raises(ValueError) as exc_info:
                config = self.loader.load_from_file(Path(f.name))
            
            error_msg = str(exc_info.value)
            assert "Plugin class not found for policy 'nonexistent_policy'" in error_msg
    
    @pytest.mark.asyncio
    async def test_multiple_policies_same_category(self):
        """Test loading multiple policies from the same category."""
        yaml_content = """
proxy:
  transport: stdio
  upstreams:
    - name: "test_server"
      command: "python -m test_server"
    
plugins:
  security:
    _global:
      - policy: "tool_allowlist"
        enabled: true
        config:
          mode: "allowlist"
          tools: 
            test_server: ["read_file"]
      - policy: "tool_allowlist"  # Same policy, different config
        enabled: true
        config:
          mode: "blocklist"
          tools: 
            test_server: ["delete_file"]
  
  auditing:
    _global: []
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            # Load configuration
            config = self.loader.load_from_file(Path(f.name))
            
            # Convert to format expected by PluginManager (dictionary format)
            plugins_config = {
                "security": {
                    "_global": [plugin.to_dict() for plugin in config.plugins.security["_global"]]
                },
                "auditing": {
                    "_global": [plugin.to_dict() for plugin in config.plugins.auditing.get("_global", [])]
                }
            }
            
            # Initialize plugin manager
            manager = PluginManager(plugins_config)
            await manager.load_plugins()
            
            # Should have loaded two instances of the same policy class
            assert len(manager.security_plugins) == 2
            assert len(manager.auditing_plugins) == 0
            
            # Verify both instances have different configurations
            plugin1 = manager.security_plugins[0]
            plugin2 = manager.security_plugins[1]
            
            assert plugin1.mode == "allowlist"
            assert plugin2.mode == "blocklist"
            assert "read_file" in plugin1.tools_config.get("test_server", [])  # allowlist mode stores allowed tools in .tools_config
            assert "delete_file" in plugin2.tools_config.get("test_server", [])  # blocklist mode stores blocked tools in .tools_config
