# Security Features

## 📋 Table of Contents

- [Security Principles](#security-principles)
- [Sensitive File Protection](#sensitive-file-protection)
- [Backup Integrity](#backup-integrity)
- [Permission Management](#permission-management)
- [Best Practices](#best-practices)
- [Security Configuration](#security-configuration)

## Security Principles

MyConfig is designed with security as a primary concern, implementing multiple layers of protection to ensure your system configurations and sensitive data remain secure during backup and restore operations.

### Core Security Features

- **Automatic Sensitive File Detection**: Intelligently identifies and excludes sensitive files
- **Permission Preservation**: Maintains correct file permissions during restore
- **Integrity Verification**: Validates backup completeness and authenticity
- **Secure Exclusion Lists**: Configurable patterns to exclude sensitive content
- **Safe Restore Process**: Creates backups before overwriting existing files

## Sensitive File Protection

### Automatic Exclusion

MyConfig automatically excludes files and directories that commonly contain sensitive information:

#### File Patterns
```regex
# SSH Keys and Certificates
.*\.key$
.*\.pem$
.*\.p12$
.*\.crt$
.*\.cert$

# Password and Credential Files
.*password.*
.*credential.*
.*secret.*
.*token.*
.*auth.*

# Database Files
.*\.db$
.*\.sqlite$
.*\.sqlite3$

# Cache and Temporary Files
.*cache.*
.*tmp.*
.*temp.*
```

#### Directory Exclusions
```
# Security Directories
.ssh/
.gnupg/
.aws/
.gcloud/
.azure/

# Application Data
Library/Keychains/
Library/Cookies/
Library/Caches/
Library/Application Support/MobileSync/

# Development Secrets
.env
.env.local
.env.production
```

### Custom Exclusion Configuration

Configure additional exclusions in `config/config.toml`:

```toml
[security]
# Enable automatic sensitive file detection
skip_sensitive = true

# Additional regex patterns to exclude
exclude_patterns = [
    ".*\\.key$",
    ".*\\.pem$", 
    ".*password.*",
    ".*secret.*",
    "company-secrets/.*",
    ".*-credentials\\.json$"
]

# Directories to always exclude
exclude_directories = [
    ".ssh",
    ".gnupg", 
    ".aws",
    "secrets/",
    "private-keys/"
]
```

### Verification Process

Before each backup, MyConfig:

1. **Scans** all target files against exclusion patterns
2. **Reports** any potentially sensitive files found
3. **Prompts** for user confirmation (in interactive mode)
4. **Logs** all exclusion decisions for audit purposes

Example output:
```
🔒 Security scan completed
▸ Excluded 15 sensitive files
▸ Skipped .ssh/ directory (3 files)
▸ Excluded password.txt (credential file)
▸ Safe to proceed with backup
```

## Backup Integrity

### Verification Mechanisms

MyConfig implements multiple integrity checks:

#### File Verification
- **Checksum Validation**: SHA-256 checksums for all backed up files
- **Size Verification**: File size consistency checks
- **Permission Tracking**: Original file permissions recorded and verified

#### Backup Manifest
Every backup includes a detailed manifest (`MANIFEST.json`) containing:

```json
{
    "version": "2.0",
    "timestamp": "2024-01-15T10:30:45Z",
    "hostname": "MacBook-Pro.local",
    "components": {
        "homebrew": {
            "files": ["Brewfile", "HOMEBREW_VERSION.txt"],
            "checksums": {
                "Brewfile": "sha256:abc123...",
                "HOMEBREW_VERSION.txt": "sha256:def456..."
            }
        }
    },
    "integrity_check": "passed",
    "excluded_files": 15
}
```

#### Restore Verification
During restore, MyConfig:

1. **Validates** backup integrity before starting
2. **Verifies** file checksums match manifest
3. **Checks** available disk space
4. **Creates** safety backups of existing files

### Integrity Commands

```bash
# Verify backup integrity
myconfig verify backup-directory

# Show backup manifest
myconfig manifest backup-directory

# Check backup completeness
myconfig check backup-directory
```

## Permission Management

### File Permission Preservation

MyConfig carefully handles file permissions:

#### During Export
- **Records** original permissions in manifest
- **Preserves** special permissions (setuid, setgid)
- **Maintains** ownership information where possible

#### During Restore
- **Restores** original permissions exactly
- **Handles** permission conflicts gracefully
- **Warns** about permission changes

### Permission Security

```bash
# Sensitive files are never made world-readable
chmod 600 ~/.ssh/config     # Preserved as 600
chmod 644 ~/.bashrc         # Preserved as 644  
chmod 755 ~/bin/script      # Preserved as 755
```

### macOS-Specific Considerations

```bash
# Extended attributes preserved
xattr -l file.txt           # Backed up with extended attributes

# Quarantine attributes handled
xattr -d com.apple.quarantine app.dmg

# Code signing preserved for applications
codesign -v /Applications/App.app
```

## Best Practices

### Backup Security

1. **Regular Review**: Periodically review exclusion patterns
2. **Audit Logs**: Check backup logs for excluded files
3. **Secure Storage**: Store backups in encrypted locations
4. **Access Control**: Limit backup access to authorized users

### Restore Safety

1. **Verify Before Restore**: Always verify backup integrity first
2. **Backup Current State**: Create safety backup before restore
3. **Test Restores**: Test restore process in safe environment
4. **Incremental Restore**: Restore components individually when possible

### Network Security

1. **Secure Transfers**: Use encrypted channels for backup transfers
2. **VPN Usage**: Transfer backups over VPN when possible
3. **Integrity Checks**: Verify checksums after network transfers

## Security Configuration

### Enterprise Security Profile

```toml
# config/profiles/enterprise-secure.toml
[profile]
name = "Enterprise Secure"
description = "Maximum security configuration"

[security]
skip_sensitive = true
strict_mode = true

exclude_patterns = [
    ".*\\.key$",
    ".*\\.pem$",
    ".*\\.p12$",
    ".*password.*",
    ".*credential.*",
    ".*secret.*",
    ".*token.*",
    ".*private.*",
    "company-confidential/.*",
    ".*-secrets\\..*"
]

exclude_directories = [
    ".ssh",
    ".gnupg",
    ".aws", 
    ".gcloud",
    ".azure",
    "secrets/",
    "private/",
    "confidential/"
]

[verification]
enable_strict_checksums = true
require_manifest_signature = true
enable_audit_logging = true
```

### Development Security Profile

```toml
# config/profiles/dev-secure.toml
[profile] 
name = "Development Secure"
description = "Balanced security for development"

[security]
skip_sensitive = true
allow_dev_secrets = false

exclude_patterns = [
    ".*\\.key$",
    ".*\\.pem$",
    ".*password.*",
    "\\.env$",
    "\\.env\\..*",
    ".*credentials\\.json$"
]

exclude_directories = [
    ".ssh",
    ".gnupg",
    "node_modules/.env",
    ".vscode/secrets/"
]
```

## Security Monitoring

### Audit Logging

MyConfig logs security-relevant events:

```bash
# View security audit log
tail -f logs/security.log

# Example log entries
2024-01-15 10:30:45 [SECURITY] Excluded sensitive file: ~/.ssh/id_rsa
2024-01-15 10:30:46 [SECURITY] Backup integrity verified: SHA256 match
2024-01-15 10:30:47 [SECURITY] Permission preserved: ~/.bashrc (644)
```

### Security Alerts

Configure alerts for security events:

```toml
[security.alerts]
# Alert on sensitive file detection
alert_on_sensitive_files = true

# Alert on permission changes
alert_on_permission_changes = true

# Alert on integrity failures
alert_on_integrity_failure = true

# Notification methods
email_alerts = "admin@company.com"
log_alerts = true
```

### Security Reports

Generate security compliance reports:

```bash
# Generate security report
myconfig security report backup-directory

# Example output:
Security Report - backup-2024-01-15
=====================================
✓ No sensitive files included
✓ All file permissions preserved  
✓ Backup integrity verified
✓ Manifest signature valid
⚠ 3 files excluded due to security patterns
ℹ Review excluded files in security.log
```

## Compliance Considerations

### Regulatory Compliance

MyConfig supports compliance with:

- **SOX (Sarbanes-Oxley)**: Audit trails and integrity verification
- **GDPR**: Personal data exclusion patterns
- **HIPAA**: Healthcare data protection
- **PCI DSS**: Payment card data security

### Documentation Requirements

Maintain security documentation:

```bash
# Generate compliance documentation
myconfig compliance export backup-directory

# Creates compliance report with:
# - Security controls applied
# - Files excluded and reasons
# - Integrity verification results
# - Audit trail documentation
```

For additional security configuration and advanced features, refer to the [Configuration Reference](configuration.md).