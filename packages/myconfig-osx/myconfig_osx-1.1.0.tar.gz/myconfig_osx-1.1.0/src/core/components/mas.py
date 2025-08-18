"""
Mac App Store applications backup/restore component
"""

from __future__ import annotations
import os
from typing import List
from core.base import BackupComponent


class MASComponent(BackupComponent):
    """Handles Mac App Store applications backup/restore"""

    def is_available(self) -> bool:
        return self.executor.which("mas")

    def is_enabled(self) -> bool:
        return self.config.enable_mas

    def export(self, output_dir: str) -> bool:
        if not self.is_enabled() or not self.is_available():
            self.logger.warning("MAS export disabled or not available")
            return False

        mas_file = os.path.join(output_dir, "mas.list")
        self.executor.run(f'mas list > "{mas_file}"', description="Export MAS app list")
        return True

    def restore(self, backup_dir: str) -> bool:
        mas_file = os.path.join(backup_dir, "mas.list")

        if not os.path.exists(mas_file):
            self.logger.warning("No MAS list found in backup")
            return False

        if not self.is_available():
            self.executor.run("brew install mas", check=False)

        self.logger.warning("Please login to App Store first")
        if self.executor.confirm("Install MAS list now?"):
            install_cmd = f'awk \'{{print $1}}\' "{mas_file}" | while read -r id; do [[ -z "$id" ]] || mas install "$id" || true; done'
            self.executor.run(install_cmd, check=False)
            return True
        return False

    def preview_export(self, output_dir: str) -> List[str]:
        if not self.is_enabled() or not self.is_available():
            return ["✗ MAS export disabled or not installed"]
        return ["✓ Mac App Store app list"]

    def preview_restore(self, backup_dir: str) -> List[str]:
        mas_file = os.path.join(backup_dir, "mas.list")
        if not os.path.exists(mas_file):
            return ["✗ No MAS app list"]

        try:
            with open(mas_file, "r") as f:
                app_count = len(f.readlines())
            return [f"✓ Mac App Store: {app_count} apps"]
        except Exception as e:
            self.logger.debug(f"Failed to parse MAS list: {e}")
            return ["✓ Mac App Store app list"]
