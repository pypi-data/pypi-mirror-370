# Installation

*[Home](../../README.md) > [User Guide](../README.md) > [Getting Started](README.md) > Installation*

This guide will help you install Watchgate and verify that it's working correctly on your system.

## System Requirements

Before installing Watchgate, ensure your system meets these requirements:

- **Python**: Version 3.11 or higher
- **Operating System**: Windows, macOS, or Linux

## Installation Methods

### Method 1: Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager that provides reliable dependency management:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# or
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Install Watchgate
uv add watchgate
```

### Method 2: Using pip

If you prefer using pip:

```bash
# Install Watchgate
pip install watchgate

# Or install in a virtual environment (recommended)
python -m venv watchgate-env
source watchgate-env/bin/activate  # Linux/macOS
# or
watchgate-env\Scripts\activate     # Windows

pip install watchgate
```

### Method 3: Development Installation

For development or to get the latest features:

```bash
# Clone the repository
git clone https://github.com/watchgate/watchgate.git
cd watchgate

# Install in development mode
uv sync
# or
pip install -e .
```

## Verify Installation

After installation, verify that Watchgate is working correctly:

### 1. Check Version

```bash
watchgate --version
```

You should see output like:
```
watchgate 0.1.0
```

### 2. Check Help

```bash
watchgate --help
```

You should see the command-line help with available options.

### 3. Validate Installation

```bash
watchgate debug installation --check
```

This command verifies:
- Watchgate is properly installed
- All required dependencies are available
- Python version compatibility
- Basic functionality works

## Optional: MCP Server Dependencies

**Note**: Watchgate itself only requires Python. However, if you plan to secure MCP servers written in Node.js, you may need to install Node.js for those specific servers.

Many popular MCP servers are built with Node.js. If you plan to use them, install Node.js:

### Installing Node.js (If Needed)

1. **Download from nodejs.org**: Visit [nodejs.org](https://nodejs.org/) and download the LTS version
2. **Using package managers**:
   ```bash
   # macOS with Homebrew
   brew install node
   
   # Ubuntu/Debian
   sudo apt update && sudo apt install nodejs npm
   
   # Windows with Chocolatey
   choco install nodejs
   ```

### Verify Node.js Installation (If Installed)

```bash
node --version
npm --version
npx --version
```

### Test Common MCP Servers

```bash
# Test filesystem server
npx @modelcontextprotocol/server-filesystem --help

# Test other common servers
npx @modelcontextprotocol/server-web-search --help
npx @modelcontextprotocol/server-sqlite --help
```

## Installation Troubleshooting

### Common Issues

#### "Watchgate command not found"

**Problem**: Command line doesn't recognize `watchgate`

**Solutions**:
1. **Check if Python scripts are in PATH**:
   ```bash
   python -m site --user-base
   # Add /bin (Linux/macOS) or /Scripts (Windows) to PATH
   ```

2. **Use module syntax**:
   ```bash
   python -m watchgate --help
   ```

3. **Restart terminal** after installation

#### "Python version not supported"

**Problem**: Error about Python version compatibility

**Solutions**:
1. **Check Python version**:
   ```bash
   python --version
   ```

2. **Upgrade Python** to 3.11 or higher
3. **Use specific Python version**:
   ```bash
   python3.11 -m pip install watchgate
   ```

#### "Permission denied" errors

**Problem**: Installation fails due to permissions

**Solutions**:
1. **Use virtual environment** (recommended):
   ```bash
   python -m venv watchgate-env
   source watchgate-env/bin/activate
   pip install watchgate
   ```

2. **User installation**:
   ```bash
   pip install --user watchgate
   ```

3. **Fix permissions** (not recommended):
   ```bash
   sudo pip install watchgate  # Not recommended
   ```

#### "uv command not found"

**Problem**: uv is not installed or not in PATH

**Solutions**:
1. **Install uv**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Add to PATH** if needed:
   ```bash
   export PATH="$HOME/.cargo/bin:$PATH"
   ```

3. **Use pip instead**:
   ```bash
   pip install watchgate
   ```

### Platform-Specific Issues

#### macOS

**"xcode-select" tools required**:
```bash
xcode-select --install
```

**Homebrew Python conflicts**:
```bash
# Use system Python or create virtual environment
python3 -m venv watchgate-env
source watchgate-env/bin/activate
pip install watchgate
```

#### Windows

**PowerShell execution policy**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Long path issues**:
- Enable long path support in Windows settings
- Or use shorter installation paths

#### Linux

**Missing development headers**:
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3-dev build-essential

# CentOS/RHEL
sudo yum install python3-devel gcc
```

## Next Steps

Once Watchgate is installed:

1. **Configure your first setup**: Follow the [Quick Setup Guide](quick-setup.md)
2. **Create your first plugin**: Try the [First Plugin Guide](first-plugin.md)
3. **Explore tutorials**: Check out the [Tutorials](../tutorials/) section

## Uninstallation

If you need to remove Watchgate:

```bash
# If installed with uv
uv remove watchgate

# If installed with pip
pip uninstall watchgate

# Remove virtual environment if used
rm -rf watchgate-env
```

## Support

If you encounter installation issues:

1. Check the [Troubleshooting Guide](../reference/troubleshooting.md)
2. Ensure you meet the system requirements
3. Try a fresh virtual environment
4. File an issue on the Watchgate GitHub repository
