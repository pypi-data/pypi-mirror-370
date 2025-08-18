# Configuration Reference

## 📋 Table of Contents

- [Configuration File Structure](#configuration-file-structure)
- [Main Configuration Options](#main-configuration-options)
- [Domain Configuration Files](#domain-configuration-files)
- [Configuration Profile System](#configuration-profile-system)
- [Template Configuration](#template-configuration)
- [Environment Variables](#environment-variables)
- [Advanced Configuration](#advanced-configuration)

## Configuration File Structure

MyConfig uses TOML format configuration files, with the main configuration located at `config/config.toml`.

```
myconfig/
├── config/
│   ├── config.toml          # Main configuration file
│   ├── defaults/
│   │   ├── domains.txt      # defaults domain list
│   │   └── exclude.txt      # excluded domains list
│   └── profiles/            # Configuration profiles
│       ├── dev-full.toml    # Full development profile
│       └── minimal.toml     # Minimal profile
├── src/
│   └── templates/           # Template files
│       ├── README.md.template
│       ├── ENVIRONMENT.txt.template
│       └── MANIFEST.json.template
```

## Main Configuration Options

### Basic Settings

```toml
# config/config.toml

# Interactive mode - prompt for user confirmation
interactive = true

# Component enablement
enable_homebrew = true      # Homebrew packages and casks
enable_vscode = true        # VS Code extensions
enable_defaults = true      # System preferences (defaults)
enable_launchagents = true  # LaunchAgents services
enable_mas = true          # Mac App Store applications

# Package managers
enable_npm = false         # npm global packages
enable_pip_user = false    # pip user packages
enable_pipx = false        # pipx packages

# Advanced features
enable_incremental = false # Incremental backups (future feature)
```

### File Paths

```toml
# Base backup directory (empty = auto-generate)
base_backup_dir = ""

# System defaults configuration
defaults_domains_file = "config/defaults/domains.txt"
defaults_exclude_file = "config/defaults/exclude.txt"
```

### Template Settings

```toml
# Template system configuration
[templates]
# Template directory (relative to src/)
template_dir = "templates"

# Enable template processing
enable_templates = true

# Template variables (custom context)
[templates.variables]
company_name = "Your Company"
department = "IT Department"
contact_email = "admin@company.com"
```

### Export Options

```toml
[export]
# Default compression format
default_compression = "gzip"  # gzip, bzip2, xz

# Compression level (1-9 for gzip)
compression_level = 6

# Include hidden files in dotfiles
include_hidden = true

# Maximum archive size (MB, 0 = unlimited)
max_archive_size = 1000
```

### Security Settings

```toml
[security]
# Automatically skip sensitive files
skip_sensitive = true

# Additional patterns to exclude (regex)
exclude_patterns = [
    ".*\\.key$",
    ".*\\.pem$",
    ".*password.*",
    ".*secret.*"
]

# Directories to always exclude
exclude_directories = [
    ".ssh",
    ".gnupg",
    ".aws"
]
```

## Domain Configuration Files

### Defaults Domains (`config/defaults/domains.txt`)

List of macOS defaults domains to export:

```txt
# System domains
com.apple.dock
com.apple.finder
com.apple.Safari
com.apple.screencapture
com.apple.symbolichotkeys

# Accessibility
com.apple.Accessibility
com.apple.universalaccess

# Hardware
com.apple.AppleMultitouchTrackpad
com.apple.AppleMultitouchMouse

# Window management
com.apple.WindowManager
com.apple.spaces
com.apple.controlcenter

# Software Update
com.apple.SoftwareUpdate
com.apple.loginwindow

# Third-party applications
com.googlecode.iterm2
```

### Exclude Domains (`config/defaults/exclude.txt`)

Domains to explicitly exclude from export:

```txt
# Sensitive or temporary domains
com.apple.accountsd
com.apple.security.*
*.keychain*
*.password*

# Large or changing domains
com.apple.LaunchServices*
com.apple.spotlight*
```

## Configuration Profile System

### Profile Structure

Profiles allow you to create different configuration sets for different use cases:

```toml
# config/profiles/dev-full.toml
[profile]
name = "Development Full"
description = "Complete development environment backup"

# Override main config settings
enable_homebrew = true
enable_vscode = true
enable_npm = true
enable_pipx = true
enable_defaults = true
enable_launchagents = true

# Custom settings for this profile
[export]
include_dev_tools = true
include_databases = true
```

```toml
# config/profiles/minimal.toml
[profile]
name = "Minimal"
description = "Essential configurations only"

# Minimal feature set
enable_homebrew = true
enable_vscode = false
enable_npm = false
enable_defaults = false
enable_launchagents = false
```

### Using Profiles

```bash
# List available profiles
myconfig profile list

# Use a specific profile
myconfig profile use dev-full

# Save current configuration as a new profile
myconfig profile save my-custom-profile

# Export with profile
myconfig profile use minimal
myconfig export minimal-backup
```

## Template Configuration

### Custom Template Variables

Add custom variables to templates by modifying the configuration:

```toml
[templates.variables]
# Organization information
company_name = "Acme Corporation"
department = "Engineering"
contact_email = "devops@acme.com"
support_url = "https://wiki.acme.com/myconfig"

# Custom metadata
backup_policy = "Monthly full backup, weekly incremental"
retention_days = 90
compliance_standard = "SOX, GDPR"

# Environment information
environment = "production"  # development, staging, production
location = "datacenter-west"
```

### Template Overrides

```toml
[templates.overrides]
# Use custom template files
readme_template = "custom-readme.template"
environment_template = "custom-environment.template"

# Template processing options
enable_markdown = true
enable_html_export = false
include_timestamps = true
```

## Environment Variables

MyConfig supports environment variable overrides:

### Export Variables

```bash
# Override configuration via environment
export MYCONFIG_INTERACTIVE=false
export MYCONFIG_ENABLE_MAS=false
export MYCONFIG_BASE_BACKUP_DIR="/backups"

# Template variables
export MYCONFIG_COMPANY_NAME="My Company"
export MYCONFIG_DEPARTMENT="IT"

# Run with environment overrides
myconfig export
```

### Variable Precedence

1. **Environment Variables** (highest priority)
2. **Command Line Arguments**
3. **Profile Configuration**
4. **Main Configuration File**
5. **Default Values** (lowest priority)

### Common Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MYCONFIG_CONFIG_FILE` | `config/config.toml` | Main config file path |
| `MYCONFIG_INTERACTIVE` | `true` | Interactive mode |
| `MYCONFIG_VERBOSE` | `false` | Verbose logging |
| `MYCONFIG_DRY_RUN` | `false` | Dry run mode |
| `MYCONFIG_ENABLE_HOMEBREW` | `true` | Enable Homebrew export |
| `MYCONFIG_ENABLE_VSCODE` | `true` | Enable VS Code export |
| `MYCONFIG_TEMPLATE_DIR` | `src/templates` | Template directory |

## Advanced Configuration

### Logging Configuration

```toml
[logging]
# Log level: DEBUG, INFO, WARNING, ERROR
level = "INFO"

# Log to file
enable_file_logging = true
log_file = "logs/myconfig.log"

# Log format
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Log rotation
max_log_size = "10MB"
backup_count = 5
```

### Performance Settings

```toml
[performance]
# Parallel processing
max_workers = 4

# Timeout settings (seconds)
command_timeout = 300
download_timeout = 30

# Memory limits
max_memory_usage = "1GB"

# Compression settings
compression_threads = 2
buffer_size = "64KB"
```

### Plugin Configuration

```toml
[plugins]
# Plugin directory
plugin_dir = "src/plugins"

# Enable specific plugins
enabled_plugins = [
    "sample",
    "custom_exporter"
]

# Plugin-specific settings
[plugins.custom_exporter]
export_format = "json"
include_metadata = true
```

### Backup Validation

```toml
[validation]
# Enable backup verification
enable_verification = true

# Checksum algorithm
checksum_algorithm = "sha256"

# Verify file integrity
verify_file_integrity = true

# Maximum verification time (seconds)
max_verification_time = 60
```

### Network Settings

```toml
[network]
# Proxy settings
http_proxy = ""
https_proxy = ""

# Timeout settings
connect_timeout = 10
read_timeout = 30

# User agent for downloads
user_agent = "MyConfig/2.0"
```

## Configuration Examples

### Enterprise Configuration

```toml
# Enterprise-grade configuration
interactive = false
enable_defaults = true
enable_launchagents = true

[templates.variables]
company_name = "Enterprise Corp"
compliance_standard = "SOX, HIPAA"
backup_policy = "Daily incremental, weekly full"

[security]
skip_sensitive = true
exclude_patterns = [
    ".*\\.key$",
    ".*\\.p12$",
    ".*credential.*",
    ".*password.*"
]

[export]
default_compression = "gzip"
compression_level = 9
max_archive_size = 500

[logging]
level = "INFO"
enable_file_logging = true
```

### Developer Configuration

```toml
# Developer-focused configuration
interactive = true
enable_homebrew = true
enable_vscode = true
enable_npm = true
enable_pipx = true

[templates.variables]
department = "Engineering"
environment = "development"

[export]
include_dev_tools = true
compression_level = 6

[logging]
level = "DEBUG"
```

### Minimal Configuration

```toml
# Minimal configuration for basic use
interactive = true
enable_homebrew = true
enable_vscode = false
enable_defaults = false

[export]
compression_level = 1
max_archive_size = 100

[logging]
level = "WARNING"
```

## Configuration Validation

### Validate Configuration

```bash
# Check configuration syntax
myconfig config validate

# Show current configuration
myconfig config show

# Show effective configuration (with overrides)
myconfig config show --effective
```

### Common Configuration Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid TOML syntax` | Malformed config file | Check TOML syntax |
| `Unknown configuration key` | Typo in key name | Check documentation |
| `Invalid path` | File path doesn't exist | Verify file paths |
| `Permission denied` | Insufficient permissions | Check file permissions |

### Configuration Testing

```bash
# Test configuration with dry run
myconfig --dry-run export

# Validate specific profile
myconfig profile use test-profile
myconfig config validate
```

## Migration Guide

### Upgrading Configuration

When upgrading MyConfig versions:

1. **Backup Current Config**
   ```bash
   cp config/config.toml config/config.toml.backup
   ```

2. **Check New Options**
   ```bash
   myconfig config show-defaults > config/new-options.toml
   ```

3. **Merge Changes**
   ```bash
   # Review and merge new options
   vim config/config.toml
   ```

4. **Validate Configuration**
   ```bash
   myconfig config validate
   ```

For specific migration instructions, see the version-specific documentation in the [CHANGELOG.md](../CHANGELOG.md) file.