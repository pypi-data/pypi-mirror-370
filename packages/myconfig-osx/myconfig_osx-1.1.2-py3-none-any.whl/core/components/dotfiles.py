"""
Dotfiles and configuration files backup/restore component
"""

from __future__ import annotations
import os
import tempfile
from typing import List
from core.base import BackupComponent


class DotfilesComponent(BackupComponent):
    """Handles dotfiles and configuration files backup/restore"""

    DOT_LIST = [
        "~/.zshrc",
        "~/.zprofile",
        "~/.bashrc",
        "~/.bash_profile",
        "~/.profile",
        "~/.gitconfig",
        "~/.gitignore_global",
        "~/.vimrc",
        "~/.ideavimrc",
        "~/.wezterm.lua",
        "~/.tmux.conf",
        "~/.config/tmux",
        "~/.config/wezterm",
        "~/.config/kitty",
        "~/.config/nvim",
        "~/.config/alacritty",
        "~/.config/karabiner",
        "~/.config/starship.toml",
        "~/.config/iterm2",
        "~/.ssh/config",  # Config only, no private keys
        # JetBrains / Xcode / Services / Fonts (optional)
        "~/Library/Preferences/com.googlecode.iterm2.plist",
        "~/Library/Preferences/IdeaVim",
        "~/Library/Application Support/JetBrains",
        "~/Library/Preferences/IntelliJIdea*",
        "~/Library/Developer/Xcode/UserData",
        "~/Library/Services",
        "~/Library/Fonts",
        # VSCode user settings
        "~/Library/Application Support/Code/User/settings.json",
        "~/Library/Application Support/Code/User/keybindings.json",
        "~/Library/Application Support/Code/User/snippets",
    ]

    def is_available(self) -> bool:
        return True  # Always available

    def is_enabled(self) -> bool:
        return True  # Always enabled

    def export(self, output_dir: str) -> bool:
        safe_dotfiles = self._get_secure_dotfile_list()

        if not safe_dotfiles:
            self.logger.warning("No safe dotfiles found")
            return False

        with tempfile.TemporaryDirectory() as tmp:
            # Copy files to temp directory
            for pattern in safe_dotfiles:
                src = os.path.expanduser(pattern)
                if os.path.exists(src):
                    # Create relative path structure in temp
                    rel_path = os.path.relpath(src, os.path.expanduser("~"))
                    dest = os.path.join(tmp, rel_path)
                    os.makedirs(os.path.dirname(dest), exist_ok=True)

                    # Use rsync to copy excluding sensitive files
                    cmd = f'rsync -a --exclude "*.key" --exclude "known_hosts" --exclude "authorized_keys" "{src}" "{dest}" 2>/dev/null || true'
                    self.executor.run(cmd, check=False, description=f"Copy {pattern}")

            # Create tar archive
            dotfiles_archive = os.path.join(output_dir, "dotfiles.tar.gz")
            cmd = f'tar -czf "{dotfiles_archive}" -C "{tmp}" . || true'
            self.executor.run(cmd, check=False, description="Compress dotfiles")

        return True

    def restore(self, backup_dir: str) -> bool:
        dotfiles_archive = os.path.join(backup_dir, "dotfiles.tar.gz")

        if not os.path.exists(dotfiles_archive):
            self.logger.warning("No dotfiles archive found in backup")
            return False

        if self.executor.confirm("Overwrite existing files (auto backup)?"):
            with tempfile.TemporaryDirectory() as tmp:
                # Extract archive
                self.executor.run(
                    f'tar -xzf "{dotfiles_archive}" -C "{tmp}"', check=False
                )

                # Backup existing files and restore
                home = os.path.expanduser("~")
                restore_cmd = f"""
                cd "{tmp}"
                find . -type f -print0 | while IFS= read -r -d "" item; do
                    dst="{home}/${{item#./}}"
                    [[ -e "$dst" ]] && cp -a "$dst" "${{dst}}.bak.$(date +%Y%m%d%H%M%S)"
                done
                rsync -av "{tmp}/" "{home}/"
                """
                self.executor.run(restore_cmd, check=False)
                return True
        return False

    def preview_export(self, output_dir: str) -> List[str]:
        safe_dotfiles = self._get_secure_dotfile_list()
        if safe_dotfiles:
            return [
                f"✓ Dotfiles and config files:",
                *[f"    - {dot}" for dot in safe_dotfiles[:5]],
                (
                    f"    ... total {len(safe_dotfiles)} config files"
                    if len(safe_dotfiles) > 5
                    else ""
                ),
            ]
        return ["✗ No dotfiles found"]

    def preview_restore(self, backup_dir: str) -> List[str]:
        dotfiles_archive = os.path.join(backup_dir, "dotfiles.tar.gz")
        if os.path.exists(dotfiles_archive):
            size = os.path.getsize(dotfiles_archive)
            return [f"✓ Dotfiles archive ({size} bytes)"]
        return ["✗ No dotfiles backup"]

    def _get_secure_dotfile_list(self) -> List[str]:
        """Get security-filtered dotfiles list"""
        safe_dotfiles = []
        skipped_files = []

        for pattern in self.DOT_LIST:
            expanded = os.path.expanduser(pattern)
            if os.path.exists(expanded):
                if not self._is_sensitive_file(expanded):
                    safe_dotfiles.append(pattern)
                else:
                    skipped_files.append(pattern)

        if skipped_files:
            self.logger.info(
                f"Skipped {len(skipped_files)} sensitive files for security"
            )
            for skip in skipped_files:
                self.logger.debug(f"  Skipped: {skip}")

        return safe_dotfiles

    def _is_sensitive_file(self, file_path: str) -> bool:
        """Check if file contains sensitive information"""
        sensitive_patterns = [
            "private_key",
            "id_rsa",
            "id_dsa", 
            "id_ecdsa",
            "id_ed25519",
            ".pem",
            ".key",
            ".p12",
            ".pfx",
            "password",
            "secret",
            "token",
            "auth",
            "known_hosts",
            "authorized_keys",
            "keychain",
            ".keychain",
        ]
        return any(pattern in file_path for pattern in sensitive_patterns)
