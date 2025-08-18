# MyConfig Usage Guide

## 📋 Table of Contents

- [Basic Concepts](#basic-concepts)
- [Command Reference](#command-reference)
- [Common Scenarios](#common-scenarios)
- [Advanced Features](#advanced-features)
- [Template System](#template-system)
- [Troubleshooting](#troubleshooting)

## Installation

Install MyConfig from PyPI (recommended):

```bash
# Install from PyPI
pip install myconfig-osx

# Verify installation
myconfig --version
myconfig doctor
```

Or install from source for development:

```bash
# Clone and install from source
git clone https://github.com/kehr/myconfig.git
cd myconfig
pip install -e .
```

## Basic Concepts

MyConfig is a comprehensive configuration management tool with the following core functions:

- **Export**: Save current system configurations and application lists to a backup directory
- **Restore**: Restore configurations from a backup directory to a new system
- **Preview**: View what will be processed before executing operations
- **Compress**: Create compressed archive backups for easy storage and sharing
- **Template System**: Generate professional documentation and metadata files

## Command Reference

### Export Commands

```bash
# Basic export (auto-generates directory name)
myconfig export

# Export to specific directory
myconfig export my-backup

# Export with compression
myconfig export my-backup --compress
# Creates: my-backup.tar.gz

# Preview export contents
myconfig --preview export

# Non-interactive mode (auto-confirm all operations)
myconfig -y export

# Dry run (show what would be done without executing)
myconfig --dry-run export

# Verbose mode (detailed logging)
myconfig -v export
```

**Export Contents Include:**
- System environment information (macOS version, hostname, etc.)
- Homebrew configuration (Brewfile with packages, casks, taps)
- Mac App Store application list
- VS Code extension list
- npm/pip global package lists
- Configuration files (dotfiles) with security filtering
- System preferences (defaults domains)
- LaunchAgents services
- Auto-generated README.md with detailed manifest
- Metadata files (MANIFEST.json, version info)

### Restore Commands

```bash
# Basic restore
myconfig restore backup-directory

# Preview restore contents
myconfig --preview restore backup-directory

# Skip Mac App Store applications
myconfig --no-mas restore backup-directory
```

**Restore Process:**
1. Verify backup integrity
2. Install Homebrew (if not installed)
3. Restore brew packages and applications
4. Restore dotfiles (automatically backs up existing files)
5. Restore VS Code extensions
6. Restore system preferences
7. Restore user services

### Archive Management

```bash
# Unpack compressed backup
myconfig unpack backup.tar.gz

# Unpack to specific directory
myconfig unpack backup.tar.gz extracted-backup

# Restore from unpacked backup
myconfig restore extracted-backup
```

### Other Commands

```bash
# System diagnostics
myconfig doctor

# Defaults operations
myconfig defaults export-all    # Export all defaults domains
myconfig defaults import <dir>  # Import defaults

# Backup management
myconfig diff <dir1> <dir2>     # Compare two backups
myconfig pack <dir> [file]      # Pack backup (legacy)

# Configuration profiles
myconfig profile list           # List available profiles
myconfig profile use <name>     # Use specified profile
myconfig profile save <name>    # Save current config as new profile
```

## Common Scenarios

### Scenario 1: New Machine Setup

```bash
# 1. Export configuration from old machine
myconfig export old-machine-backup --compress

# 2. Transfer backup to new machine (copy old-machine-backup.tar.gz)

# 3. On new machine, unpack and restore
myconfig unpack old-machine-backup.tar.gz
myconfig restore old-machine-backup
```

### Scenario 2: Regular Backups

```bash
# Create periodic backup script
#!/bin/bash
BACKUP_DIR="./backups/daily-$(date +%Y%m%d)"
myconfig export "$BACKUP_DIR" --compress
echo "Backup saved to: $BACKUP_DIR.tar.gz"
```

### Scenario 3: Configuration Testing

```bash
# 1. Preview what will be exported
myconfig --preview export

# 2. Test run mode
myconfig --dry-run export

# 3. Actual export
myconfig export test-backup
```

### Scenario 4: Minimal Configuration

```bash
# 1. Use minimal configuration profile
myconfig profile use minimal

# 2. Export (only includes basic configurations)
myconfig export minimal-backup

# 3. Restore full configuration profile
myconfig profile use dev-full
```

## Advanced Features

### Custom Configuration

Edit `config/config.toml` file:

```toml
# Enable/disable specific features
enable_homebrew = true
enable_vscode = true
enable_defaults = true

# Custom defaults domains
defaults_domains_file = "config/defaults/domains.txt"

# Interactive mode
interactive = true
```

### Plugin Extensions

Create plugins in `src/plugins/` directory:

```python
def register(subparsers):
    p = subparsers.add_parser("my-cmd", help="Custom command")
    
    def handle_command(args):
        # Implement command logic
        pass
```

### Configuration Profiles

Create different profiles for different use cases:

```bash
# Save current configuration as development profile
myconfig profile save development

# Create server environment profile
myconfig profile save server

# Switch profiles
myconfig profile use server
```

## Template System

MyConfig uses a powerful template system for generating documentation and metadata files.

### Template Locations

Templates are stored in `src/templates/`:
- `README.md.template` - Export documentation template
- `ENVIRONMENT.txt.template` - System environment template
- `MANIFEST.json.template` - Backup metadata template

### Customizing Templates

You can modify templates to customize the output format:

```bash
# Edit the README template
vim src/templates/README.md.template

# Next export will use your custom template
myconfig export my-backup
```

### Template Syntax

Templates use Mustache-like syntax:

```markdown
# Export Time: {{export_time}}
# Hostname: {{hostname}}

{{#homebrew}}
## Homebrew
- Packages: {{brew_count}}
- Casks: {{cask_count}}
{{/homebrew}}
```

### Available Variables

- `{{export_time}}` - Export timestamp
- `{{hostname}}` - System hostname
- `{{version}}` - MyConfig version
- `{{total_components}}` - Number of exported components
- `{{total_files}}` - Total number of files
- `{{total_size_formatted}}` - Human-readable total size

### Conditional Sections

```markdown
{{#system_environment}}
### System Environment
- File: {{filename}}
- Size: {{size}} bytes
{{/system_environment}}
```

## Troubleshooting

### Common Issues

**1. Permission Errors**

```bash
# Ensure script has execution permissions
chmod +x bin/myconfig
```

**2. Python Not Found**

```bash
# Install Python
brew install python3
```

**3. Backup Verification Failed**

```bash
# Check backup directory permissions and disk space
ls -la backup-directory
df -h
```

**4. Restore Interrupted**

```bash
# Check log files
tail -f logs/myconfig.log
```

### Debugging Tips

```bash
# Verbose mode for detailed logs
myconfig -v export

# Dry run mode to test commands
myconfig --dry-run restore backup-dir

# System environment check
myconfig doctor
```

### Getting Help

```bash
# View help information
myconfig --help

# View subcommand help
myconfig export --help
myconfig restore --help
```

## Best Practices

1. **Regular Backups**: Perform weekly or monthly full backups
2. **Test Restores**: Regularly verify backup usability in test environments
3. **Version Control**: Use Git for important configuration files
4. **Secure Storage**: Encrypt backup files or use secure cloud storage
5. **Document Changes**: Record the meaning of custom configurations and special settings
6. **Compression**: Use `--compress` flag for space-efficient storage
7. **Template Customization**: Customize templates for your organization's needs

## Performance Tips

- Use `--no-mas` if Mac App Store restore is not needed
- Compress large backups for faster transfers
- Use profiles to create targeted backups for specific use cases
- Regular cleanup of old backup directories

For more information, refer to other documentation files or check the project source code.

## File Size Reference

Typical backup sizes:
- **Homebrew config**: ~2KB (Brewfile)
- **VS Code extensions**: ~1-2KB (extension list)
- **Dotfiles archive**: 15-20MB (compressed configuration files)
- **System defaults**: ~100KB (preference files)
- **LaunchAgents**: ~10KB (service configurations)
- **Documentation**: ~2KB (generated README.md)
- **Total compressed**: ~16MB (typical full backup)