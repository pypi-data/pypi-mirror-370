# MyConfig Documentation Center

Welcome to the MyConfig documentation center! Here you'll find comprehensive guides for using and extending MyConfig.

## 📚 Documentation Navigation

### Getting Started
- [Installation Guide](installation.md) - System requirements, installation methods, and troubleshooting
- [Usage Guide](usage.md) - Complete command reference and common scenarios

### Configuration
- [Configuration Reference](configuration.md) - TOML configuration, profiles, and environment variables
- [Template System](templates.md) - Customizing output files with templates

### Advanced Topics
- [Security Features](security.md) - Security mechanisms and best practices (Chinese)
- [Plugin Development](plugins.md) - Plugin system and extension development (Chinese)
- [Git Setup](git-setup.md) - Git configuration and hooks (Chinese)

### Project Information
- [Optimization Summary](OPTIMIZATION_SUMMARY.md) - Project optimization history (Chinese)

## 🎯 Quick Links

### Common Tasks
- **First time setup**: Read [Installation Guide](installation.md)
- **Basic usage**: Check [Usage Guide](usage.md) 
- **Customize output**: See [Template System](templates.md)
- **Configure MyConfig**: Reference [Configuration Guide](configuration.md)

### Advanced Users
- **Security considerations**: Review [Security Features](security.md)
- **Extend functionality**: Learn [Plugin Development](plugins.md)
- **Contribute to project**: Check [Git Setup](git-setup.md)

## 📖 Documentation Structure

```
docs/
├── README.md                    # This file - documentation overview
├── installation.md              # Installation and setup guide
├── usage.md                     # Usage instructions and examples
├── configuration.md             # Configuration reference
├── templates.md                 # Template system documentation
├── security.md                  # Security features (Chinese)
├── plugins.md                   # Plugin development (Chinese)
├── git-setup.md                 # Git configuration (Chinese)
└── OPTIMIZATION_SUMMARY.md      # Project history (Chinese)
```

## 🆕 What's New in v2.0

- **Template System**: Professional file generation with customizable templates
- **Compression Support**: Create and manage compressed backup archives
- **Auto-Generated Documentation**: Every backup includes detailed README.md
- **Class-Based Architecture**: Modern, modular codebase design
- **Enhanced CLI**: Preview modes, dry-run options, and improved feedback

## 🛠️ Feature Documentation Status

| Feature | Documentation | Status |
|---------|---------------|--------|
| Installation | [installation.md](installation.md) | ✅ Complete |
| Basic Usage | [usage.md](usage.md) | ✅ Complete |
| Configuration | [configuration.md](configuration.md) | ✅ Complete |
| Templates | [templates.md](templates.md) | ✅ Complete |
| Testing | [testing.md](testing.md) | ✅ Complete |
| Security | [security.md](security.md) | ✅ Complete |
| Plugins | [plugins.md](plugins.md) | ✅ Complete |

## 🚀 Quick Start

1. **Install MyConfig**
   ```bash
   git clone <repository-url>
   cd myconfig
   ./scripts/install.sh
   ```

2. **Verify Installation**
   ```bash
   myconfig doctor
   ```

3. **Create Your First Backup**
   ```bash
   myconfig export my-first-backup
   ```

4. **Explore Template System**
   ```bash
   cat my-first-backup/README.md
   ```

## 📋 Help and Support

### Getting Help
- Run `myconfig --help` for command-line help
- Check `myconfig doctor` for system diagnostics
- Review error logs in the `logs/` directory

### Community
- Report issues on GitHub
- Contribute improvements via pull requests
- Share templates and configurations

### Documentation Feedback
If you find any documentation issues or have suggestions for improvement, please open an issue or submit a pull request.

---

**Note**: Some documentation files are currently in Chinese and will be translated to English in future updates. The core functionality documentation (installation, usage, configuration, templates) is available in English.