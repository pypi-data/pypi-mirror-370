"""
Configuration management for MyConfig
"""

from __future__ import annotations
import os
import logging
import tomllib
from typing import Dict, Any
from dataclasses import dataclass, replace


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

        def get_bool(key: str, default: bool) -> bool:
            return str(data.get(key, default)).lower() == "true"

        def get_str(key: str, default: str) -> str:
            return str(data.get(key, default))

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
