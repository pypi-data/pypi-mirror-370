"""
VS Code extensions backup/restore component
"""

from __future__ import annotations
import os
from typing import List
from core.base import BackupComponent


class VSCodeComponent(BackupComponent):
    """Handles VS Code extensions backup/restore"""

    def is_available(self) -> bool:
        return self.executor.which("code")

    def is_enabled(self) -> bool:
        return self.config.enable_vscode

    def export(self, output_dir: str) -> bool:
        if not self.is_enabled() or not self.is_available():
            self.logger.warning("VS Code export disabled or not available")
            return False

        extensions_file = os.path.join(output_dir, "vscode_extensions.txt")
        self.executor.run(
            f'code --list-extensions > "{extensions_file}"',
            description="Export VS Code extensions",
        )
        return True

    def restore(self, backup_dir: str) -> bool:
        extensions_file = os.path.join(backup_dir, "vscode_extensions.txt")

        if not os.path.exists(extensions_file):
            self.logger.warning("No VS Code extensions found in backup")
            return False

        if not self.is_available():
            self.logger.warning("VS Code not available")
            return False

        if self.executor.confirm("Start installing VS Code extensions?"):
            install_cmd = f'while read -r ext; do [[ -z "$ext" ]] || code --install-extension "$ext" || true; done < "{extensions_file}"'
            self.executor.run(install_cmd, check=False)
            return True
        return False

    def preview_export(self, output_dir: str) -> List[str]:
        if not self.is_enabled() or not self.is_available():
            return ["✗ VS Code export disabled or not installed"]
        return ["✓ VS Code extension list"]

    def preview_restore(self, backup_dir: str) -> List[str]:
        extensions_file = os.path.join(backup_dir, "vscode_extensions.txt")
        if not os.path.exists(extensions_file):
            return ["✗ No VS Code extensions"]
        return ["✓ VS Code extensions"]
