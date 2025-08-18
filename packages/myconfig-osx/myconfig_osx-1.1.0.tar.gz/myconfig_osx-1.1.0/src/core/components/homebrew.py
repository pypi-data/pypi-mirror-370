"""
Homebrew package management backup/restore component
"""

from __future__ import annotations
import os
from typing import List
from core.base import BackupComponent


class HomebrewComponent(BackupComponent):
    """Handles Homebrew package management backup/restore"""

    def is_available(self) -> bool:
        return self.executor.which("brew")

    def is_enabled(self) -> bool:
        return True  # Homebrew is always enabled if available

    def export(self, output_dir: str) -> bool:
        if not self.is_available():
            self.logger.warning("Homebrew not available, skipping")
            return False

        brewfile = os.path.join(output_dir, "Brewfile")
        version_file = os.path.join(output_dir, "HOMEBREW_VERSION.txt")

        self.executor.run(
            f'brew bundle dump --file="{brewfile}" --force',
            description="Export Brewfile",
        )
        self.executor.run(
            f'brew --version > "{version_file}"', description="Save Homebrew version"
        )
        return True

    def restore(self, backup_dir: str) -> bool:
        brewfile = os.path.join(backup_dir, "Brewfile")

        if not os.path.exists(brewfile):
            self.logger.warning("No Brewfile found in backup")
            return False

        if not self.is_available():
            if self.executor.confirm("Install Homebrew?"):
                install_cmd = 'NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
                self.executor.run(install_cmd, check=False)

        if self.executor.confirm("Execute brew bundle install?"):
            self.executor.run(f'brew bundle --file="{brewfile}"', check=False)
            return True
        return False

    def preview_export(self, output_dir: str) -> List[str]:
        if not self.is_available():
            return ["✗ Homebrew not installed, skipping"]
        return ["✓ Homebrew config (Brewfile)"]

    def preview_restore(self, backup_dir: str) -> List[str]:
        brewfile = os.path.join(backup_dir, "Brewfile")
        if not os.path.exists(brewfile):
            return ["✗ No Homebrew config"]

        try:
            with open(brewfile, "r") as f:
                lines = f.readlines()
            brew_count = len([l for l in lines if l.strip().startswith("brew ")])
            cask_count = len([l for l in lines if l.strip().startswith("cask ")])
            return [f"✓ Homebrew: {brew_count} packages, {cask_count} apps"]
        except Exception as e:
            self.logger.debug(f"Failed to parse Brewfile: {e}")
            return ["✓ Homebrew config file"]
