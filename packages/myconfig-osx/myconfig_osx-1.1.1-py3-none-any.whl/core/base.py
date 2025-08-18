"""
Base classes for backup components
"""

from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from typing import List
from core.executor import CommandExecutor


class BackupComponent(ABC):
    """Abstract base class for backup components"""

    def __init__(self, executor: CommandExecutor):
        self.executor = executor
        self.config = executor.config
        self.logger = logging.getLogger(self.__class__.__module__ + "." + self.__class__.__name__)

    @property
    def name(self) -> str:
        """Component name for logging"""
        return self.__class__.__name__

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this component is available on the system"""
        pass

    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if this component is enabled in config"""
        pass

    @abstractmethod
    def export(self, output_dir: str) -> bool:
        """Export component data to output directory"""
        pass

    @abstractmethod
    def restore(self, backup_dir: str) -> bool:
        """Restore component data from backup directory"""
        pass

    @abstractmethod
    def preview_export(self, output_dir: str) -> List[str]:
        """Preview what would be exported"""
        pass

    @abstractmethod
    def preview_restore(self, backup_dir: str) -> List[str]:
        """Preview what would be restored"""
        pass

    def can_export(self) -> bool:
        """Check if component can export (both available and enabled)"""
        return self.is_available() and self.is_enabled()

    def log_operation(self, operation: str, success: bool) -> None:
        """Log operation result"""
        if success:
            self.logger.info(f"✓ {operation} completed")
        else:
            self.logger.warning(f"✗ {operation} failed")
