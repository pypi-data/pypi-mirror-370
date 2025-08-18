# Plugin Development Guide

## 📋 Table of Contents

- [Plugin System Overview](#plugin-system-overview)
- [Plugin Architecture](#plugin-architecture)
- [Creating Your First Plugin](#creating-your-first-plugin)
- [Plugin API Reference](#plugin-api-reference)
- [Advanced Plugin Features](#advanced-plugin-features)
- [Testing and Debugging](#testing-and-debugging)
- [Publishing Plugins](#publishing-plugins)

## Plugin System Overview

MyConfig features a powerful plugin system that allows you to extend functionality without modifying the core codebase. Plugins can add new commands, backup components, or integrate with external services.

### Plugin Capabilities

- **Custom Commands**: Add new CLI commands
- **Backup Components**: Create new backup/restore components
- **Data Processors**: Transform backup data
- **External Integrations**: Connect with cloud services, APIs
- **Custom Templates**: Add new template generators
- **Validation Hooks**: Add custom validation logic

### Plugin Types

| Plugin Type | Purpose | Example Use Cases |
|-------------|---------|-------------------|
| **Command** | Add CLI commands | Custom export formats, cloud sync |
| **Component** | Backup/restore components | Database backups, custom configs |
| **Processor** | Data transformation | Encryption, compression, filtering |
| **Template** | Custom file generation | Corporate templates, reports |
| **Hook** | Event handlers | Pre/post backup actions, notifications |

## Plugin Architecture

### Plugin Structure

```
src/plugins/
├── __init__.py              # Plugin registry
├── sample.py                # Example plugin
└── custom_plugin/           # Complex plugin package
    ├── __init__.py
    ├── plugin.py           # Main plugin code
    ├── components.py       # Custom components
    ├── templates/          # Plugin templates
    │   └── report.template
    └── config.toml         # Plugin configuration
```

### Plugin Lifecycle

1. **Discovery**: MyConfig scans the plugin directory
2. **Registration**: Plugins register their components
3. **Initialization**: Plugin setup and configuration
4. **Execution**: Plugin methods called during operations
5. **Cleanup**: Plugin teardown and resource cleanup

### Plugin Interface

All plugins must implement the base plugin interface:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BasePlugin(ABC):
    """Base class for all MyConfig plugins."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"plugin.{self.__class__.__name__}")
    
    @abstractmethod
    def get_name(self) -> str:
        """Return plugin name."""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Return plugin version."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return plugin description."""
        pass
    
    def initialize(self) -> bool:
        """Initialize plugin. Return True if successful."""
        return True
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass
```

## Creating Your First Plugin

### Step 1: Basic Plugin Structure

Create a new file `src/plugins/hello_world.py`:

```python
import logging
from typing import Dict, Any
from ..core.base import BasePlugin

class HelloWorldPlugin(BasePlugin):
    """A simple hello world plugin."""
    
    def get_name(self) -> str:
        return "hello-world"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_description(self) -> str:
        return "A simple hello world plugin for demonstration"
    
    def initialize(self) -> bool:
        self.logger.info("HelloWorld plugin initialized")
        return True
    
    def register_commands(self, subparsers):
        """Register CLI commands."""
        parser = subparsers.add_parser(
            'hello',
            help='Say hello from plugin'
        )
        parser.add_argument(
            '--name',
            default='World',
            help='Name to greet'
        )
        parser.set_defaults(func=self.handle_hello)
    
    def handle_hello(self, args):
        """Handle the hello command."""
        print(f"Hello, {args.name}! This is from a MyConfig plugin.")
        self.logger.info(f"Greeted {args.name}")

# Register the plugin
def register():
    """Plugin registration function."""
    return HelloWorldPlugin
```

### Step 2: Test Your Plugin

```bash
# The plugin should now be available
myconfig hello --name "Developer"

# Expected output:
# Hello, Developer! This is from a MyConfig plugin.
```

### Step 3: Add Configuration

Create `src/plugins/hello_world.toml`:

```toml
[plugin]
name = "hello-world"
version = "1.0.0"
author = "Your Name"
email = "your.email@example.com"
description = "A simple hello world plugin"

[plugin.dependencies]
# Plugin dependencies
required_packages = []
minimum_myconfig_version = "2.0"

[plugin.config]
# Default configuration
default_greeting = "Hello"
enable_logging = true
```

## Plugin API Reference

### Core Plugin Classes

#### BasePlugin

Base class for all plugins:

```python
class BasePlugin:
    def __init__(self, config: Dict[str, Any])
    def get_name(self) -> str
    def get_version(self) -> str
    def get_description(self) -> str
    def initialize(self) -> bool
    def cleanup(self) -> None
```

#### CommandPlugin

For plugins that add CLI commands:

```python
class CommandPlugin(BasePlugin):
    @abstractmethod
    def register_commands(self, subparsers):
        """Register CLI commands with argparse subparsers."""
        pass
```

#### ComponentPlugin

For plugins that add backup/restore components:

```python
class ComponentPlugin(BasePlugin):
    @abstractmethod
    def get_component_class(self):
        """Return the backup component class."""
        pass
```

### Plugin Services

#### Configuration Service

Access MyConfig configuration:

```python
def access_config(self):
    # Access main configuration
    main_config = self.get_main_config()
    
    # Access plugin-specific configuration
    plugin_config = self.get_plugin_config()
    
    # Get configuration value with default
    value = self.get_config_value('setting_name', default_value)
```

#### Logging Service

Plugin logging:

```python
def setup_logging(self):
    # Plugin logger (automatically namespaced)
    self.logger.info("Plugin operation")
    self.logger.warning("Plugin warning")
    self.logger.error("Plugin error")
    
    # Custom log levels
    self.logger.debug("Debug information")
```

#### File Service

File operations:

```python
def file_operations(self):
    # Safe file operations
    content = self.read_file_safe(filepath)
    self.write_file_safe(filepath, content)
    
    # Backup file operations
    self.backup_file(source, destination)
    self.restore_file(backup, target)
```

## Advanced Plugin Features

### Custom Backup Components

Create a plugin that adds a new backup component:

```python
from ..core.base import BackupComponent
from ..core.executor import CommandExecutor

class DatabaseComponent(BackupComponent):
    """Backup database configurations."""
    
    def __init__(self, config, executor: CommandExecutor):
        super().__init__("database", config, executor)
    
    def can_backup(self) -> bool:
        """Check if database tools are available."""
        return self.executor.which("pg_dump") or self.executor.which("mysqldump")
    
    def backup(self, output_dir: str) -> bool:
        """Backup database configurations."""
        try:
            # PostgreSQL
            if self.executor.which("pg_dump"):
                self._backup_postgresql(output_dir)
            
            # MySQL  
            if self.executor.which("mysqldump"):
                self._backup_mysql(output_dir)
            
            return True
        except Exception as e:
            self.logger.error(f"Database backup failed: {e}")
            return False
    
    def restore(self, backup_dir: str) -> bool:
        """Restore database configurations."""
        # Implementation for restore
        pass
    
    def _backup_postgresql(self, output_dir: str):
        """Backup PostgreSQL configuration."""
        pg_config = self.executor.run_output("pg_config --sysconfdir")
        if pg_config:
            config_file = f"{pg_config.strip()}/postgresql.conf"
            if os.path.exists(config_file):
                self.executor.run(f"cp {config_file} {output_dir}/postgresql.conf")

class DatabasePlugin(ComponentPlugin):
    def get_component_class(self):
        return DatabaseComponent
```

### Template Plugins

Add custom template generators:

```python
class ReportTemplatePlugin(BasePlugin):
    """Generate custom backup reports."""
    
    def generate_security_report(self, backup_dir: str) -> str:
        """Generate security compliance report."""
        template_path = os.path.join(
            os.path.dirname(__file__), 
            "templates", 
            "security_report.template"
        )
        
        context = self._build_security_context(backup_dir)
        
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Simple template substitution
        for key, value in context.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
        
        return template
    
    def _build_security_context(self, backup_dir: str) -> Dict[str, Any]:
        """Build context for security report."""
        return {
            'scan_date': datetime.now().isoformat(),
            'backup_dir': backup_dir,
            'sensitive_files_excluded': self._count_excluded_files(backup_dir),
            'integrity_status': self._check_integrity(backup_dir)
        }
```

### Event Hook Plugins

Handle MyConfig events:

```python
class NotificationPlugin(BasePlugin):
    """Send notifications for MyConfig events."""
    
    def on_backup_start(self, backup_dir: str):
        """Called when backup starts."""
        self._send_notification(
            "Backup Started",
            f"MyConfig backup started to {backup_dir}"
        )
    
    def on_backup_complete(self, backup_dir: str, success: bool):
        """Called when backup completes."""
        status = "successfully" if success else "with errors"
        self._send_notification(
            "Backup Complete",
            f"MyConfig backup completed {status}"
        )
    
    def on_restore_start(self, backup_dir: str):
        """Called when restore starts."""
        self._send_notification(
            "Restore Started", 
            f"MyConfig restore started from {backup_dir}"
        )
    
    def _send_notification(self, title: str, message: str):
        """Send notification via configured method."""
        method = self.get_config_value('notification_method', 'console')
        
        if method == 'email':
            self._send_email(title, message)
        elif method == 'slack':
            self._send_slack(title, message)
        elif method == 'webhook':
            self._send_webhook(title, message)
        else:
            print(f"[NOTIFICATION] {title}: {message}")
```

## Testing and Debugging

### Plugin Testing Framework

Create tests for your plugins:

```python
import unittest
from unittest.mock import Mock, patch
from src.plugins.hello_world import HelloWorldPlugin

class TestHelloWorldPlugin(unittest.TestCase):
    
    def setUp(self):
        self.config = {'test': True}
        self.plugin = HelloWorldPlugin(self.config)
    
    def test_plugin_initialization(self):
        """Test plugin initializes correctly."""
        self.assertTrue(self.plugin.initialize())
        self.assertEqual(self.plugin.get_name(), "hello-world")
    
    def test_hello_command(self):
        """Test hello command functionality."""
        with patch('builtins.print') as mock_print:
            args = Mock()
            args.name = "Test"
            
            self.plugin.handle_hello(args)
            
            mock_print.assert_called_with(
                "Hello, Test! This is from a MyConfig plugin."
            )
    
    def test_plugin_config(self):
        """Test plugin configuration."""
        self.assertIsNotNone(self.plugin.config)
        self.assertTrue(self.plugin.config.get('test'))

if __name__ == '__main__':
    unittest.main()
```

### Debugging Plugins

Enable debug logging for plugins:

```bash
# Enable debug logging
export MYCONFIG_LOG_LEVEL=DEBUG

# Run with specific plugin debugging
myconfig --debug-plugins hello

# Check plugin logs
tail -f logs/plugin.hello-world.log
```

### Plugin Development Tools

```bash
# List installed plugins
myconfig plugins list

# Show plugin information
myconfig plugins info hello-world

# Validate plugin
myconfig plugins validate hello-world

# Reload plugins (development mode)
myconfig plugins reload
```

## Publishing Plugins

### Plugin Packaging

Structure your plugin for distribution:

```
my-plugin/
├── setup.py                 # Python package setup
├── README.md               # Plugin documentation
├── LICENSE                 # Plugin license
├── requirements.txt        # Plugin dependencies
├── src/
│   └── myconfig_hello/     # Plugin package
│       ├── __init__.py
│       ├── plugin.py       # Main plugin code
│       ├── config.toml     # Plugin configuration
│       └── templates/      # Plugin templates
└── tests/                  # Plugin tests
    └── test_plugin.py
```

### Setup.py Example

```python
from setuptools import setup, find_packages

setup(
    name="myconfig-hello-world",
    version="1.0.0",
    description="Hello World plugin for MyConfig",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "myconfig>=2.0.0",
    ],
    entry_points={
        "myconfig.plugins": [
            "hello-world = myconfig_hello.plugin:HelloWorldPlugin",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
```

### Plugin Distribution

1. **PyPI Publishing**:
   ```bash
   # Build package
   python setup.py sdist bdist_wheel
   
   # Upload to PyPI
   twine upload dist/*
   ```

2. **Git Repository**:
   ```bash
   # Install from Git
   pip install git+https://github.com/user/myconfig-plugin.git
   ```

3. **Local Installation**:
   ```bash
   # Install locally
   pip install -e .
   ```

### Plugin Registry

Register your plugin in the MyConfig community registry:

```json
{
    "name": "hello-world",
    "version": "1.0.0",
    "author": "Your Name",
    "description": "Hello World plugin for MyConfig",
    "repository": "https://github.com/user/myconfig-hello-world",
    "category": "demo",
    "tags": ["example", "demo", "hello-world"],
    "minimum_myconfig_version": "2.0.0",
    "installation": "pip install myconfig-hello-world"
}
```

## Plugin Best Practices

### Design Guidelines

1. **Single Responsibility**: Each plugin should have a clear, focused purpose
2. **Minimal Dependencies**: Avoid heavy dependencies unless necessary
3. **Error Handling**: Implement robust error handling and logging
4. **Configuration**: Make plugins configurable for different use cases
5. **Documentation**: Provide clear documentation and examples

### Performance Considerations

1. **Lazy Loading**: Load resources only when needed
2. **Caching**: Cache expensive operations
3. **Async Operations**: Use async for I/O bound operations
4. **Resource Cleanup**: Always clean up resources in cleanup method

### Security Best Practices

1. **Input Validation**: Validate all plugin inputs
2. **Privilege Escalation**: Don't request unnecessary permissions
3. **Sensitive Data**: Handle sensitive data carefully
4. **Code Injection**: Sanitize any dynamically executed code

For more information about the MyConfig architecture and core APIs, see the [Configuration Reference](configuration.md) and [Usage Guide](usage.md).