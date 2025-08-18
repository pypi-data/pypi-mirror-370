"""
Command execution with logging and dry-run support
"""

from __future__ import annotations
import subprocess
import logging
from core.config import AppConfig
from logger import confirm_action


class CommandExecutor:
    """Handles command execution with logging and dry-run support"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def run(self, cmd: str, check: bool = True, description: str = "") -> int:
        """Execute a shell command with proper logging"""
        if self.config.dry_run:
            desc_text = f" ({description})" if description else ""
            self.logger.info(f"[dry-run]{desc_text} {cmd}")
            return 0

        if self.config.verbose:
            self.logger.debug(f"$ {cmd}")

        try:
            rc = subprocess.call(cmd, shell=True)
            if check and rc != 0:
                desc_text = f" ({description})" if description else ""
                self.logger.error(f"Command failed{desc_text} (exit code: {rc}): {cmd}")
                raise SystemExit(rc)
            return rc
        except KeyboardInterrupt:
            self.logger.warning("Operation interrupted by user")
            raise SystemExit(130)
        except Exception as e:
            self.logger.error(f"Exception occurred while executing command: {e}")
            if check:
                raise SystemExit(1)
            return 1

    def run_output(self, cmd: str) -> tuple[int, str]:
        """Execute command and return exit code and output"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, encoding="utf-8"
            )
            return result.returncode, result.stdout
        except Exception as e:
            self.logger.debug(f"Command failed: {cmd}, error: {e}")
            return 1, ""

    def which(self, cmd: str) -> bool:
        """Check if command exists"""
        return self.run_output(f"command -v {cmd} >/dev/null 2>&1")[0] == 0

    def confirm(self, prompt: str) -> bool:
        """Ask for user confirmation"""
        return confirm_action(self.logger, prompt, self.config.interactive)
