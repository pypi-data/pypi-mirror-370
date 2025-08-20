"""
Backup components for different macOS tools and configurations
"""

from myconfig.core.base import BackupComponent
from myconfig.core.components.homebrew import HomebrewComponent
from myconfig.core.components.mas import MASComponent
from myconfig.core.components.vscode import VSCodeComponent
from myconfig.core.components.dotfiles import DotfilesComponent
from myconfig.core.components.defaults import DefaultsComponent
from myconfig.core.components.launchagents import LaunchAgentsComponent
from myconfig.core.components.applications import ApplicationsComponent

__all__ = [
    "BackupComponent",
    "HomebrewComponent",
    "MASComponent",
    "VSCodeComponent", 
    "DotfilesComponent",
    "DefaultsComponent",
    "LaunchAgentsComponent",
    "ApplicationsComponent",
]
