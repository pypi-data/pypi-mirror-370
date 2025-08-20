"""
Configuration management for MyConfig
"""

from __future__ import annotations
import os
import logging

# Handle TOML library imports
try:
    import tomllib  # py311+
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        raise ImportError("tomli library required: pip install tomli")

from typing import Dict, Any, List
from dataclasses import dataclass, replace, field


@dataclass(frozen=True)
class AppConfig:
    """Application configuration with immutable settings"""

    interactive: bool = True
    dry_run: bool = False
    verbose: bool = False
    quiet: bool = False
    enable_npm: bool = False
    enable_pip_user: bool = False
    enable_pipx: bool = False
    enable_defaults: bool = True
    enable_vscode: bool = True
    enable_launchagents: bool = True
    enable_mas: bool = True
    enable_incremental: bool = False
    base_backup_dir: str = ""
    defaults_domains_file: str = "config/defaults/domains.txt"
    defaults_exclude_file: str = "config/defaults/exclude.txt"
    # Applications scanning/export
    enable_applications: bool = True
    applications_default: Dict[str, List[str]] = field(default_factory=dict)
    # CLI tools configuration support
    cli_tools_default: Dict[str, List[str]] = field(default_factory=dict)

    def update(self, **kwargs) -> AppConfig:
        """Create a new config with updated values"""
        return replace(self, **kwargs)


class ConfigManager:
    """Manages configuration loading, validation and updates"""

    def __init__(self, config_path: str = "./config/config.toml"):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)

    def load(self) -> AppConfig:
        """Load configuration from TOML file"""
        data = self._parse_toml(self.config_path)

        def _to_bool(val, default: bool) -> bool:
            if isinstance(val, bool):
                return val
            try:
                return str(val).lower() == "true"
            except Exception:
                return default

        def get_bool(key: str, default: bool) -> bool:
            return _to_bool(data.get(key, default), default)

        def get_str(key: str, default: str) -> str:
            return str(data.get(key, default))

        # Nested: applications
        apps_cfg = data.get("applications", {}) if isinstance(data, dict) else {}
        enable_apps = _to_bool(apps_cfg.get("enable", True), True)
        known_map = apps_cfg.get("default", {}) if isinstance(apps_cfg, dict) else {}
        # Ensure structure Dict[str, List[str]]
        if not isinstance(known_map, dict):
            known_map = {}
        else:
            cleaned_known: Dict[str, List[str]] = {}
            for k, v in known_map.items():
                if isinstance(v, list):
                    cleaned_known[str(k)] = [str(p) for p in v]
                elif isinstance(v, str):
                    cleaned_known[str(k)] = [v]
            known_map = cleaned_known

        # Nested: cli_tools
        cli_tools_cfg = data.get("cli_tools", {}) if isinstance(data, dict) else {}
        cli_tools_map = cli_tools_cfg.get("default", {}) if isinstance(cli_tools_cfg, dict) else {}
        # Ensure structure Dict[str, List[str]]
        if not isinstance(cli_tools_map, dict):
            cli_tools_map = {}
        else:
            cleaned_cli_tools: Dict[str, List[str]] = {}
            for k, v in cli_tools_map.items():
                if isinstance(v, list):
                    cleaned_cli_tools[str(k)] = [str(p) for p in v]
                elif isinstance(v, str):
                    cleaned_cli_tools[str(k)] = [v]
            cli_tools_map = cleaned_cli_tools

        return AppConfig(
            interactive=get_bool("interactive", True),
            enable_npm=get_bool("enable_npm", False),
            enable_pip_user=get_bool("enable_pip_user", False),
            enable_pipx=get_bool("enable_pipx", False),
            enable_defaults=get_bool("enable_defaults", True),
            enable_vscode=get_bool("enable_vscode", True),
            enable_launchagents=get_bool("enable_launchagents", True),
            enable_mas=get_bool("enable_mas", True),
            enable_incremental=get_bool("enable_incremental", False),
            base_backup_dir=get_str("base_backup_dir", ""),
            defaults_domains_file=get_str(
                "defaults_domains_file", "config/defaults/domains.txt"
            ),
            defaults_exclude_file=get_str(
                "defaults_exclude_file", "config/defaults/exclude.txt"
            ),
            enable_applications=enable_apps,
            applications_default=known_map,
            cli_tools_default=cli_tools_map,
        )

    def _parse_toml(self, path: str) -> Dict[str, Any]:
        """Parse TOML configuration file"""
        if not os.path.exists(path):
            self.logger.warning(f"Config file not found: {path}, using defaults")
            return {}

        try:
            with open(path, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to parse TOML config: {e}, using fallback")
            return self._fallback_parse(path)

    def _fallback_parse(self, path: str) -> Dict[str, Any]:
        """Fallback parser for simple key=value format"""
        data = {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    data[key.strip()] = value.strip().strip("\"'")
        except Exception as e:
            self.logger.error(f"Failed to parse config file: {e}")
        return data
