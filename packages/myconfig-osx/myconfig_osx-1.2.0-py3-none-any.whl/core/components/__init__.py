"""
Backup components for different macOS tools and configurations
"""

from core.base import BackupComponent
from core.components.homebrew import HomebrewComponent
from core.components.mas import MASComponent
from core.components.vscode import VSCodeComponent
from core.components.dotfiles import DotfilesComponent
from core.components.defaults import DefaultsComponent
from core.components.launchagents import LaunchAgentsComponent

__all__ = [
    "BackupComponent",
    "HomebrewComponent",
    "MASComponent",
    "VSCodeComponent", 
    "DotfilesComponent",
    "DefaultsComponent",
    "LaunchAgentsComponent",
]
