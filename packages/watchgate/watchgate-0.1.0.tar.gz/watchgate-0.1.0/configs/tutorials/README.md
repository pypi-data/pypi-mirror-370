# Tutorial Configuration Files

This directory contains ready-to-use YAML configuration files for each Watchgate tutorial. These files can be used directly in your Claude Desktop configuration without needing to copy them.

## Available Configurations

| File | Tutorial | Description |
|------|----------|-------------|
| `1-securing-tool-access.yaml` | [Securing Tool Access](../1-securing-tool-access.md) | Basic tool access control with filesystem MCP server |
| `2-implementing-audit-logging.yaml` | [Implementing Audit Logging](../2-implementing-audit-logging.md) | Audit logging configuration with file output |
| `3-protecting-sensitive-content.yaml` | [Protecting Sensitive Content](../3-protecting-sensitive-content.md) | Content protection and sanitization policies |
| `4-multi-plugin-security.yaml` | [Multi-Plugin Security](../4-multi-plugin-security.md) | Multiple security plugins working together |
| `5-logging-configuration.yaml` | [Logging Configuration](../5-logging-configuration.md) | Advanced logging setup and configuration |

## How to Use

1. **Reference directly in Claude Desktop configuration**:
   ```json
   {
     "mcpServers": {
       "watchgate-tutorial": {
         "command": "<watchgate_root>/watchgate",
         "args": [
           "--config", "<watchgate_root>/docs/user/tutorials/configs/1-securing-tool-access.yaml"
         ]
       }
     }
   }
   ```

2. **Replace `<watchgate_root>`** with your actual Watchgate installation path

3. **Follow the corresponding tutorial** for detailed explanations and testing instructions

## Path Examples

- **macOS/Linux**: `/Users/yourusername/watchgate` or `/home/yourusername/watchgate`
- **Windows**: `C:\Users\yourusername\watchgate`

## Customization

If you need to customize a configuration:

1. **Copy the file** to your working directory:
   ```bash
   cp docs/user/tutorials/configs/1-securing-tool-access.yaml my-custom-config.yaml
   ```

2. **Modify as needed** for your specific requirements

3. **Update Claude Desktop** to reference your custom file

## What's in Each Config

All configuration files contain:
- **Proxy settings** for MCP server communication
- **Plugin configurations** specific to each tutorial's focus
- **Detailed comments** explaining each setting
- **Example values** that work out of the box

## Contributing

When adding new tutorials, please also add the corresponding configuration file here following the naming convention `{number}-{tutorial-name}.yaml`.
