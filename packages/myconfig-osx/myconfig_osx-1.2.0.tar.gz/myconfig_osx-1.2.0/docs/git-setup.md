# Git Setup and Hooks

## 📋 Table of Contents

- [Git Configuration](#git-configuration)
- [Pre-commit Hooks](#pre-commit-hooks)
- [Development Workflow](#development-workflow)
- [Branch Management](#branch-management)
- [Code Quality Checks](#code-quality-checks)
- [Release Process](#release-process)

## Git Configuration

### Initial Setup

Configure Git for MyConfig development:

```bash
# Clone the repository
git clone https://github.com/kehr/myconfig.git
cd myconfig

# Configure Git user information
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Set up upstream tracking
git remote add upstream https://github.com/kehr/myconfig.git

# Configure push behavior
git config push.default simple
git config push.autoSetupRemote true
```

### Git Hooks Setup

MyConfig includes pre-commit hooks for code quality assurance:

```bash
# Install pre-commit hooks
cp .git/hooks/pre-commit.sample .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Or use the provided hook
cp contrib/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Repository Configuration

Configure repository-specific settings:

```bash
# Set line ending handling
git config core.autocrlf input
git config core.eol lf

# Enable file mode checking
git config core.filemode true

# Configure merge strategy
git config merge.tool vimdiff
git config merge.conflictstyle diff3
```

For detailed git workflow and contribution guidelines, see [CONTRIBUTING.md](../CONTRIBUTING.md).
