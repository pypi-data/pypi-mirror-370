"""
LaunchAgents backup/restore component
"""

from __future__ import annotations
import os
from typing import List
from core.base import BackupComponent


class LaunchAgentsComponent(BackupComponent):
    """Handles LaunchAgents backup/restore"""

    def is_available(self) -> bool:
        return True  # Always available on macOS

    def is_enabled(self) -> bool:
        return self.config.enable_launchagents

    def export(self, output_dir: str) -> bool:
        if not self.is_enabled():
            return False

        launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
        if not os.path.isdir(launch_agents_dir):
            self.logger.warning("No LaunchAgents directory found")
            return False

        # Create LaunchAgents backup directory
        backup_la_dir = os.path.join(output_dir, "LaunchAgents")
        os.makedirs(backup_la_dir, exist_ok=True)

        # Copy plist files
        self.executor.run(
            f'cp -a "{launch_agents_dir}"/*.plist "{backup_la_dir}/" 2>/dev/null || true',
            check=False,
            description="Backup LaunchAgents",
        )
        return True

    def restore(self, backup_dir: str) -> bool:
        backup_la_dir = os.path.join(backup_dir, "LaunchAgents")

        if not os.path.isdir(backup_la_dir):
            self.logger.warning("No LaunchAgents found in backup")
            return False

        # Create LaunchAgents directory
        launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
        self.executor.run(f'mkdir -p "{launch_agents_dir}"', check=False)

        # Copy plist files
        self.executor.run(
            f'cp -a "{backup_la_dir}"/*.plist "{launch_agents_dir}/" 2>/dev/null || true',
            check=False,
        )

        if self.executor.confirm("Load LaunchAgents?"):
            load_cmd = f'find "{launch_agents_dir}" -name "*.plist" -print0 | while IFS= read -r -d "" f; do launchctl load -w "$f" 2>/dev/null || true; done'
            self.executor.run(load_cmd, check=False)
            return True
        return False

    def preview_export(self, output_dir: str) -> List[str]:
        if not self.is_enabled():
            return ["✗ LaunchAgents export disabled"]

        launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
        if os.path.isdir(launch_agents_dir):
            plist_files = [
                f for f in os.listdir(launch_agents_dir) if f.endswith(".plist")
            ]
            return [f"✓ LaunchAgents ({len(plist_files)} files)"]
        return ["✗ No LaunchAgents"]

    def preview_restore(self, backup_dir: str) -> List[str]:
        backup_la_dir = os.path.join(backup_dir, "LaunchAgents")
        if os.path.isdir(backup_la_dir):
            agent_files = [f for f in os.listdir(backup_la_dir) if f.endswith(".plist")]
            return [f"✓ LaunchAgents: {len(agent_files)} services"]
        return ["✗ No LaunchAgents"]
