# Testing Guide

MyConfig includes a comprehensive test suite to ensure reliability and maintainability.

## Test Structure

```
tests/
├── __init__.py           # Test package
├── conftest.py          # Shared fixtures and configuration
├── run_tests.py         # Test runner script
├── unit/                # Unit tests
│   ├── test_config.py   # Configuration management tests
│   ├── test_executor.py # Command executor tests
│   └── test_components.py # Component tests
└── integration/         # Integration tests
    ├── test_cli.py      # CLI integration tests
    └── test_backup_manager.py # End-to-end backup tests
```

## Running Tests

### Quick Start

```bash
# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test Categories

```bash
# Unit tests only (fast)
python -m pytest tests/unit/

# Integration tests only (slower)
python -m pytest tests/integration/

# Exclude slow tests
python -m pytest -m "not slow"
```

### Using Test Runner

The test runner script provides convenient options:

```bash
# Basic usage
./tests/run_tests.py

# With coverage
./tests/run_tests.py --coverage

# Verbose output
./tests/run_tests.py --verbose

# Fast tests only
./tests/run_tests.py --fast

# Unit tests only
./tests/run_tests.py --unit

# Integration tests only
./tests/run_tests.py --integration
```

## Test Configuration

Tests are configured via `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short --cov=src --cov-report=term-missing"
markers = [
    "unit: Unit tests",
    "integration: Integration tests", 
    "slow: Slow running tests"
]
```

## Test Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0", 
    "pytest-mock>=3.10",
    # ... other dev dependencies
]
```

## Writing Tests

### Test Fixtures

Common fixtures are available in `conftest.py`:

- `temp_dir`: Temporary directory for test files
- `mock_config`: Mock AppConfig for testing
- `mock_executor`: Mock CommandExecutor
- `sample_config_file`: Sample TOML configuration
- `sample_dotfiles`: Sample dotfiles for testing

### Unit Test Example

```python
def test_config_loading(self, sample_config_file):
    """Test configuration loading from TOML."""
    manager = ConfigManager(sample_config_file)
    config = manager.load()
    
    assert config.interactive is False
    assert config.dry_run is True
```

### Integration Test Example

```python
def test_cli_doctor_command(self):
    """Test doctor command via CLI."""
    result = subprocess.run(
        [sys.executable, self.cli_path, "doctor"],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "System health check" in result.stdout
```

### Mocking External Commands

```python
@patch('subprocess.run')
def test_command_execution(self, mock_run, mock_executor):
    """Test command execution with mocked subprocess."""
    mock_run.return_value = MagicMock(returncode=0, stdout="success")
    
    result = mock_executor.run("echo test")
    assert result is True
```

## Coverage Requirements

The project aims for high test coverage:

- **Unit Tests**: >90% coverage for core modules
- **Integration Tests**: Cover critical user workflows
- **End-to-End Tests**: Verify complete backup/restore cycles

## Test Best Practices

1. **Isolation**: Each test should be independent and idempotent
2. **Mocking**: Mock external dependencies (commands, file system)
3. **Fixtures**: Use shared fixtures for common test data
4. **Descriptive Names**: Test names should clearly describe what is being tested
5. **Fast Tests**: Keep unit tests fast; mark slow tests appropriately
6. **Error Cases**: Test both success and failure scenarios

## Continuous Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Release tags

CI configuration ensures tests pass on multiple Python versions and macOS versions.

## Performance Testing

For performance-critical components:

```python
import time

def test_backup_performance(self, temp_dir):
    """Test backup completes within reasonable time."""
    start_time = time.time()
    
    # Run backup operation
    result = backup_manager.export(temp_dir)
    
    duration = time.time() - start_time
    assert duration < 30  # Should complete within 30 seconds
    assert result is True
```

## Test Data

Test fixtures and sample data are stored in `tests/fixtures/`:

- Sample configuration files
- Mock command outputs
- Test dotfiles and directories

## Debugging Tests

```bash
# Run with debugging output
python -m pytest -s -vv

# Stop on first failure
python -m pytest -x

# Run specific test
python -m pytest tests/unit/test_config.py::TestAppConfig::test_default_config

# Debug with pdb
python -m pytest --pdb
```

## Test Maintenance

- Keep tests up-to-date with code changes
- Remove obsolete tests when refactoring
- Add tests for new features and bug fixes
- Review and update fixtures regularly
