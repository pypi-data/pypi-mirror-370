# MyConfig

[![PyPI version](https://badge.fury.io/py/myconfig-osx.svg)](https://badge.fury.io/py/myconfig-osx)
[![Downloads](https://pepy.tech/badge/myconfig-osx)](https://pepy.tech/project/myconfig-osx)
[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)
[![GitHub stars](https://img.shields.io/github/stars/kehr/myconfig.svg)](https://github.com/kehr/myconfig/stargazers)

A comprehensive macOS system configuration backup and restore tool.

## 🌟 Features

- 🔄 **Complete Backup**: Supports Homebrew, VS Code, dotfiles, system preferences, and more
- 🔒 **Secure & Reliable**: Automatically skips sensitive files and validates backup integrity
- 👀 **Preview Mode**: Preview what will be backed up/restored before executing
- 📊 **Progress Tracking**: Real-time progress indicators and detailed status updates
- ⚙️ **Flexible Configuration**: Multiple configuration profiles and customization options
- 🔌 **Extensible**: Plugin system for extending functionality
- 📋 **Self-Documenting**: Auto-generated README.md for every backup with detailed manifests
- 🗜️ **Compression Support**: Create compressed archives for easy storage and sharing
- 🎨 **Template System**: Customizable file generation using professional templates

## 🚀 Quick Start

### Installation Methods

**Method 1: System Installation (Recommended)**

```bash
# Clone the repository
git clone <repository-url>
cd myconfig

# Interactive installation
./install.sh

# Or direct user installation
./install.sh --user
# Or system installation (requires sudo)
./install.sh --system

# Using Makefile
make install-user    # User installation
make install-system  # System installation
```

**Method 2: Direct Usage (No Installation Required)**

```bash
# Clone the repository
git clone <repository-url>
cd myconfig

# Set execution permissions
chmod +x bin/myconfig

# Use directly
./bin/myconfig --help
```

### Basic Usage

**After Installation:**

```bash
# Export current system configuration
myconfig export

# Preview export contents
myconfig --preview export

# Restore configuration from backup
myconfig restore <backup-directory>

# System health check
myconfig doctor
```

**Direct Usage:**

```bash
# Export current system configuration
./bin/myconfig export

# Preview export contents
./bin/myconfig --preview export

# Restore configuration from backup
./bin/myconfig restore <backup-directory>

# System health check
./bin/myconfig doctor
```

## 📖 Documentation

Detailed documentation is available in the [docs](./docs/) directory:

- [Usage Guide](./docs/usage.md) - Comprehensive usage instructions and examples
- [Configuration Reference](./docs/configuration.md) - Configuration files and options
- [Security Features](./docs/security.md) - Security mechanisms and best practices
- [Plugin Development](./docs/plugins.md) - Plugin system and extension development
- [Template System](./docs/templates.md) - Customizing output file templates
- [Optimization History](./docs/OPTIMIZATION_SUMMARY.md) - Project optimization history

## 🔧 Main Commands

| Command | Description |
|---------|-------------|
| `export [dir]` | Export configuration to specified directory |
| `export --compress [dir]` | Create compressed backup archive (.tar.gz) |
| `restore <dir>` | Restore configuration from backup directory |
| `unpack <archive>` | Unpack compressed backup archive |
| `doctor` | System environment check and diagnostics |
| `--preview` | Preview mode - show what will be processed |
| `--dry-run` | Test run mode - don't execute actual operations |

## 🛡️ Security Features

- Automatically skips sensitive files (SSH keys, password files, etc.)
- Backup integrity verification and validation
- Detailed operation logging
- Security-filtered dotfiles export
- Safe restoration with automatic backups of existing files

## 📋 Supported Components

- **System Tools**: Homebrew (auto-generates Brewfile), Mac App Store applications
- **Development Environment**: VS Code extensions, npm/pip packages
- **Configuration Files**: Shell configs, Git settings, editor configurations
- **System Settings**: macOS preferences (defaults domains)
- **Services**: LaunchAgents user services

## 📁 Project Structure

```
myconfig/
├── bin/myconfig              # Executable script
├── config/                   # Configuration files
│   ├── config.toml          # Main configuration file
│   ├── defaults/            # defaults domain configurations
│   └── profiles/            # Configuration profiles
├── docs/                    # Documentation
├── src/                     # Python source package
│   ├── core/                # Core modules (class-based architecture)
│   │   ├── config.py        # Configuration management
│   │   ├── executor.py      # Command execution
│   │   ├── backup.py        # Backup orchestration
│   │   └── components/      # Individual backup components
│   ├── actions/             # Legacy action modules
│   ├── templates/           # File generation templates
│   ├── template_engine.py   # Template processing engine
│   ├── logger.py            # Logging configuration
│   ├── cli.py               # Command line interface
│   └── utils.py             # Utility functions
└── README.md               # Project documentation
```

## 🆕 New Features

### 📋 Auto-Generated Documentation
Every backup now includes a comprehensive `README.md` with:
- Detailed component analysis (package counts, file sizes, etc.)
- Export statistics and metadata
- Restore instructions and important notes
- Professional formatting with clear organization

### 🗜️ Compression Support
```bash
# Create compressed backup
myconfig export my-backup --compress
# Creates: my-backup.tar.gz

# Unpack compressed backup
myconfig unpack my-backup.tar.gz extracted-backup

# Restore from unpacked backup
myconfig restore extracted-backup
```

### 🎨 Template System
- Customizable file generation using templates
- Located in `src/templates/` directory
- Easy to modify without touching Python code
- Supports variables, conditionals, and loops
- Professional output formatting

## 🗑️ Uninstallation

If you need to uninstall MyConfig:

```bash
# Use uninstall script
./uninstall.sh

# Or use pip directly
pip3 uninstall myconfig

# Using Makefile
make uninstall
```

## 🛠️ Development

```bash
# Development mode installation (editable)
pip3 install -e .

# Code formatting
make format

# Code checking
make lint

# Build package
make build

# Clean up
make clean
```

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Note**: Run `myconfig doctor` (if installed) or `./bin/myconfig doctor` (direct usage) to check your system environment before first use.

## 🏗️ Architecture

MyConfig uses a modern, class-based architecture:

- **Modular Design**: Each component (Homebrew, VS Code, etc.) is a separate module
- **Abstract Base Classes**: Consistent interface for all backup components
- **Template Engine**: Flexible file generation system
- **Error Handling**: Comprehensive error handling with graceful fallbacks
- **Logging System**: Centralized logging with configurable levels
- **Configuration Management**: TOML-based configuration with profiles

## 📊 Export Example

A typical backup contains:
- System environment information
- Homebrew configuration (Brewfile with 16 packages, 5 casks)
- VS Code extensions (55+ extensions)
- Configuration files (16MB+ compressed dotfiles)
- System preferences (15+ domains)
- LaunchAgents (8+ services)
- Auto-generated README.md with complete manifest
- Metadata files (MANIFEST.json, version info)