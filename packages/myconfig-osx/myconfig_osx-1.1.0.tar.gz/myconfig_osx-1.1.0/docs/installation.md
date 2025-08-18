# Installation Guide

This document provides detailed instructions for installing and setting up MyConfig.

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Verification](#verification)
- [Uninstallation](#uninstallation)
- [Development Installation](#development-installation)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Required

- **Operating System**: macOS 10.14 or later
- **Python**: 3.8 or later
- **pip**: Python package manager

### Optional

- **Homebrew**: For package management features
- **Git**: For version control integration
- **VS Code**: For extension management features
- **mas**: For Mac App Store application management

### Recommended Tools

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python via Homebrew (optional, but recommended)
brew install python3

# Install mas for Mac App Store management
brew install mas
```

## Installation Methods

### Method 1: PyPI Installation (Recommended)

The simplest and fastest way to install MyConfig:

```bash
# Install from PyPI
pip install myconfig-osx

# Verify installation
myconfig --version
myconfig doctor
```

**Advantages:**
- ✅ One-command installation
- ✅ Automatic dependency management  
- ✅ Easy updates with `pip install --upgrade myconfig-osx`
- ✅ Same command works across all platforms
- ✅ Works in virtual environments
- ✅ Official stable releases only

**Requirements:**
- Python 3.8+ and pip installed
- Internet connection

### Method 2: Interactive Installation (Source)

The easiest way to install MyConfig is using the interactive installer:

```bash
# Clone the repository
git clone <repository-url>
cd myconfig

# Run interactive installer
./scripts/install.sh
```

The installer will guide you through the process and offer these options:

1. **User Installation** (Recommended) - Installs to current user
2. **System Installation** - Installs system-wide (requires sudo)
3. **Development Installation** - Editable installation for development
4. **Cancel** - Exit without installing

### Method 2: Direct Installation Commands

#### User Installation (Recommended)

```bash
# Clone and navigate
git clone <repository-url>
cd myconfig

# Install for current user
pip3 install --user .

# Add to PATH (if needed)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### System Installation

```bash
# Clone and navigate
git clone <repository-url>
cd myconfig

# Install system-wide (requires admin privileges)
sudo pip3 install .
```

#### Using Makefile

```bash
# User installation
make install-user

# System installation
make install-system

# Development installation
make install-dev
```

### Method 3: Direct Usage (No Installation)

You can use MyConfig without installing it:

```bash
# Clone the repository
git clone <repository-url>
cd myconfig

# Set execution permissions
chmod +x bin/myconfig

# Use directly
./bin/myconfig --help
./bin/myconfig doctor
./bin/myconfig export my-backup
```

### Method 4: Package Installation (Future)

When available through package managers:

```bash
# Via Homebrew (future)
brew install myconfig

# Via PyPI (future)
pip3 install myconfig
```

## Verification

### Basic Verification

After installation, verify that MyConfig is working correctly:

```bash
# Check if command is available
which myconfig

# Check version
myconfig --version

# Run system check
myconfig doctor

# Test basic functionality
myconfig --help
```

### Comprehensive Testing

```bash
# Test export preview (safe, doesn't create files)
myconfig --preview export

# Test with dry run
myconfig --dry-run export test-backup

# Create actual test backup
myconfig export test-backup

# Verify backup contents
ls -la test-backup/
cat test-backup/README.md

# Clean up test
rm -rf test-backup
```

### Expected Output

**Successful Installation:**
```bash
$ myconfig --version
myconfig 2.0

$ myconfig doctor
▸ System health check
▸ ────────────────────────────────────────────────────────────
▸ ✔ Xcode CLT installed
▸ ✔ Homebrew 4.6.3
▸ ✔ code command available
⚠ mas not installed
▸ ────────────────────────────────────────────────────────────
▸ ✔ Health check completed
```

## Uninstallation

### Using Uninstall Script

```bash
# Navigate to MyConfig directory
cd myconfig

# Run uninstall script
./uninstall.sh

# Follow the prompts for complete removal
```

### Manual Uninstallation

#### User Installation

```bash
# Uninstall package
pip3 uninstall myconfig

# Remove user binary (if exists)
rm -f ~/.local/bin/myconfig

# Clean up PATH (edit your shell config)
vim ~/.zshrc  # Remove MyConfig PATH additions
```

#### System Installation

```bash
# Uninstall package (requires admin privileges)
sudo pip3 uninstall myconfig

# Remove system binary (if exists)
sudo rm -f /usr/local/bin/myconfig
```

### Complete Cleanup

```bash
# Remove configuration files (optional)
rm -rf ~/.config/myconfig

# Remove log files (optional)
rm -rf ~/.local/share/myconfig/logs

# Remove cached data (optional)
rm -rf ~/.cache/myconfig
```

## Development Installation

For developers who want to modify MyConfig:

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd myconfig

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install in editable mode
pip3 install -e .

# Install development dependencies
pip3 install -e ".[dev]"

# Or use the development installer
./install.sh --dev
```

### Development Dependencies

The development installation includes:

- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Code linting
- **mypy**: Type checking
- **pre-commit**: Git hooks

### Development Workflow

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
pytest

# Format code
black src/

# Check code quality
flake8 src/
mypy src/

# Install pre-commit hooks
pre-commit install

# Run all checks
make check
```

## Troubleshooting

### Common Installation Issues

#### Issue: "Python command not found"

```bash
# Check Python installation
python3 --version

# Install Python via Homebrew
brew install python3

# Or download from python.org
```

#### Issue: "pip command not found"

```bash
# Install pip
python3 -m ensurepip --upgrade

# Or via Homebrew
brew install python3  # includes pip3
```

#### Issue: "Permission denied"

```bash
# For user installation
pip3 install --user .

# Or fix permissions
sudo chown -R $(whoami) ~/.local
```

#### Issue: "Command not found after installation"

```bash
# Check if binary exists
ls ~/.local/bin/myconfig
ls /usr/local/bin/myconfig

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Or create symlink
ln -s ~/.local/bin/myconfig /usr/local/bin/myconfig
```

#### Issue: "ModuleNotFoundError"

```bash
# Reinstall with dependencies
pip3 install --force-reinstall .

# Or install missing dependencies
pip3 install -r requirements.txt
```

### Platform-Specific Issues

#### macOS Big Sur / Monterey / Ventura

```bash
# If installation fails due to system restrictions
pip3 install --user --break-system-packages .

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip3 install .
```

#### Apple Silicon (M1/M2) Macs

```bash
# Install Rosetta if needed for compatibility
softwareupdate --install-rosetta

# Use native Python
arch -arm64 brew install python3
arch -arm64 pip3 install .
```

### Debug Installation

#### Enable Verbose Installation

```bash
# Verbose pip installation
pip3 install -v .

# Debug installer
bash -x ./install.sh
```

#### Check Installation Details

```bash
# Show installed package info
pip3 show myconfig

# List installed files
pip3 show -f myconfig

# Check package location
python3 -c "import myconfig; print(myconfig.__file__)"
```

### Getting Help

#### Check System Health

```bash
# Run comprehensive system check
myconfig doctor

# Check with verbose output
myconfig -v doctor
```

#### Log Files

```bash
# Check installation logs
tail -f ~/.pip/pip.log

# Check MyConfig logs
tail -f logs/myconfig.log
```

#### Community Support

- **Issues**: Report bugs on GitHub
- **Discussions**: Join community discussions
- **Documentation**: Check docs/ directory
- **Examples**: See examples/ directory

## Advanced Installation

### Custom Installation Paths

```bash
# Install to custom directory
pip3 install --target /custom/path .

# Set PYTHONPATH
export PYTHONPATH="/custom/path:$PYTHONPATH"
```

### Network-Restricted Environments

```bash
# Download dependencies offline
pip3 download -r requirements.txt -d deps/

# Install from local files
pip3 install --find-links deps/ --no-index .
```

### Container Installation

```dockerfile
# Dockerfile example
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y git

# Copy and install MyConfig
COPY . /app/myconfig
WORKDIR /app/myconfig
RUN pip3 install .

# Set entrypoint
ENTRYPOINT ["myconfig"]
```

### Automated Installation

```bash
#!/bin/bash
# automated-install.sh

set -e

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "Python 3 required" >&2; exit 1; }
command -v pip3 >/dev/null 2>&1 || { echo "pip3 required" >&2; exit 1; }

# Clone and install
git clone <repository-url> /tmp/myconfig
cd /tmp/myconfig
pip3 install --user .

# Verify installation
myconfig --version

echo "MyConfig installed successfully!"
```

For additional support, please refer to the [Usage Guide](usage.md) or check the project's issue tracker.