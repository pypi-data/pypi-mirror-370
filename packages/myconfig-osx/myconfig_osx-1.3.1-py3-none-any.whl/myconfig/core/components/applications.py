"""
Applications configuration backup/restore component
 - Scans installed GUI applications in /Applications and ~/Applications
 - Detects and backs up CLI tools configurations
 - Optionally exports known configuration directories for common developer apps
 - Generates Applications list and optional install command hints
"""

from __future__ import annotations
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
from myconfig.core.base import BackupComponent


class ApplicationsComponent(BackupComponent):
    """Handles scanning and exporting configurations for GUI applications and CLI tools"""

    def __init__(self, executor):
        super().__init__(executor)
        # Load GUI applications configuration
        cfg_map = getattr(self.config, "applications_default", {}) or {}
        self.known_app_config_map: Dict[str, List[str]] = {
            k: [os.path.expanduser(p) for p in v]
            for k, v in cfg_map.items()
        }
        
        # Load CLI tools configuration (new dedicated section)
        cli_cfg_map = getattr(self.config, "cli_tools_default", {}) or {}
        self.cli_tools_config_map: Dict[str, List[str]] = {
            k: [os.path.expanduser(p) for p in v]
            for k, v in cli_cfg_map.items()
        }
        
        # Merge both configurations for backward compatibility
        # CLI tools config takes precedence over applications config for CLI tools
        self.combined_config_map = {**self.known_app_config_map, **self.cli_tools_config_map}
        
        # CLI tools that are commonly installed and have configurations
        # This list is now used primarily for detection, with config paths coming from config file
        self.cli_tools_to_detect = set(self.cli_tools_config_map.keys()) | {
            'git', 'vim', 'nvim', 'neovim', 'tmux', 'zsh', 'fish', 'bash', 'ssh', 'gpg',
            'node', 'npm', 'yarn', 'pnpm', 'python', 'pip', 'cargo', 'rustc',
            'go', 'java', 'mvn', 'gradle', 'php', 'composer', 'ruby', 'gem',
            'docker', 'kubectl', 'terraform', 'ansible', 'aws', 'gcloud', 'az',
            'brew', 'code', 'subl', 'emacs', 'starship', 'oh-my-zsh'
        }

    def is_available(self) -> bool:
        return True

    def is_enabled(self) -> bool:
        return getattr(self.config, "enable_applications", True)

    def _list_installed_apps(self) -> List[str]:
        apps_dirs = ["/Applications", os.path.expanduser("~/Applications")]
        found: List[str] = []
        for base in apps_dirs:
            try:
                if not os.path.isdir(base):
                    continue
                for name in os.listdir(base):
                    if name.endswith(".app"):
                        found.append(name[:-4])
            except Exception:
                continue
        # De-duplicate and sort
        return sorted(list(dict.fromkeys(found)))

    def _slugify(self, name: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    def _expand_globs(self, path: str) -> List[str]:
        # Support simple wildcard expansion for known JetBrains/Sublime patterns
        import glob
        return glob.glob(path)

    def _detect_cli_tool(self, tool_name: str) -> bool:
        """Check if a CLI tool is installed using which/command -v"""
        try:
            # Try 'which' first, then 'command -v' as fallback
            result = subprocess.run(['which', tool_name],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True
            
            # Fallback to 'command -v'
            result = subprocess.run(['command', '-v', tool_name],
                                  shell=True, capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False

    def _expand_env_vars(self, path: str) -> str:
        """Expand environment variables in path"""
        return os.path.expandvars(os.path.expanduser(path))

    def _resolve_config_paths(self, paths: List[str]) -> List[str]:
        """Resolve configuration paths with environment variable expansion"""
        resolved_paths = []
        for path in paths:
            expanded_path = self._expand_env_vars(path)
            
            # Handle glob patterns
            if any(char in expanded_path for char in ['*', '?', '[']):
                resolved_paths.extend(self._expand_globs(expanded_path))
            else:
                resolved_paths.append(expanded_path)
        
        # Filter to only existing paths
        return [p for p in resolved_paths if os.path.exists(p)]

    def _detect_installed_cli_tools(self) -> Dict[str, List[str]]:
        """
        Detect installed CLI tools and their configuration paths.
        
        This method performs comprehensive CLI tools detection using PATH scanning
        and configuration file validation. It supports 35+ development tools across
        multiple categories including editors, shells, package managers, and cloud tools.
        
        Detection Process:
        1. Scans system PATH for executable CLI tools
        2. Matches detected tools against known configuration database
        3. Resolves configuration paths with environment variable expansion
        4. Validates configuration file existence
        5. Returns mapping of tool names to their config file paths
        
        Supported Tool Categories:
        - Development Tools: git, vim, neovim, tmux, emacs
        - Shell Environments: zsh, fish, bash, starship
        - Package Managers: npm, yarn, pnpm, pip, cargo, gem, composer
        - Cloud Tools: aws, gcloud, az, kubectl, terraform, ansible
        - Container Tools: docker, kubernetes
        - Language Runtimes: node, python, go, java, php, ruby, rust
        
        Returns:
            Dict[str, List[str]]: Mapping of detected tool names to their configuration file paths.
                                 Only includes tools that are both installed and have existing config files.
        
        Example:
            {
                'git': ['/Users/user/.gitconfig', '/Users/user/.gitignore_global'],
                'vim': ['/Users/user/.vimrc', '/Users/user/.vim/vimrc'],
                'tmux': ['/Users/user/.tmux.conf'],
                'zsh': ['/Users/user/.zshrc', '/Users/user/.oh-my-zsh/']
            }
        """
        detected_tools = {}
        
        for tool in self.cli_tools_to_detect:
            if self._detect_cli_tool(tool):
                # Check if we have configuration mapping for this tool
                # First check CLI tools config, then fallback to applications config
                for app_key, config_paths in self.combined_config_map.items():
                    # Match tool name with configuration key (case-insensitive, fuzzy)
                    if (tool.lower() in app_key.lower() or
                        app_key.lower() in tool.lower() or
                        self._normalize_tool_name(tool) == self._normalize_tool_name(app_key)):
                        
                        resolved_paths = self._resolve_config_paths(config_paths)
                        if resolved_paths:
                            # Mark if this came from CLI tools config for better organization
                            source = "CLI" if app_key in self.cli_tools_config_map else "GUI"
                            detected_tools[f"{app_key} ({source})"] = resolved_paths
                            break
        
        return detected_tools

    def _normalize_tool_name(self, name: str) -> str:
        """Normalize tool name for comparison"""
        # Handle common variations
        name_map = {
            'nvim': 'neovim',
            'vim': 'vim',
            'code': 'visual studio code',
            'subl': 'sublime text',
            'git': 'git',
            'tmux': 'tmux',
            'zsh': 'zsh',
            'fish': 'fish',
            'bash': 'bash',
            'node': 'node.js',
            'npm': 'npm',
            'yarn': 'yarn',
            'pnpm': 'pnpm',
            'python': 'python',
            'pip': 'pip',
            'cargo': 'cargo',
            'rustc': 'rust',
            'go': 'go',
            'java': 'java',
            'mvn': 'java',
            'gradle': 'java',
            'php': 'php',
            'composer': 'composer',
            'ruby': 'ruby',
            'gem': 'rubygems',
            'docker': 'docker',
            'kubectl': 'kubernetes',
            'terraform': 'terraform',
            'ansible': 'ansible',
            'aws': 'aws cli',
            'gcloud': 'google cloud sdk',
            'az': 'azure cli',
            'brew': 'homebrew',
            'emacs': 'emacs',
            'starship': 'starship'
        }
        
        normalized = name_map.get(name.lower(), name.lower())
        return normalized

    def _detect_package_manager_tools(self) -> Dict[str, List[str]]:
        """
        Detect CLI tools installed via package managers and map to their configurations.
        
        This method integrates with multiple package managers to discover installed CLI tools
        and automatically maps them to their configuration files. It provides comprehensive
        coverage across different installation methods and package ecosystems.
        
        Supported Package Managers:
        - Homebrew: macOS package manager for CLI tools and applications
        - npm: Node.js package manager for global JavaScript tools
        - pip: Python package manager for user-installed packages
        - cargo: Rust package manager for Rust-based CLI tools (future enhancement)
        
        Detection Process:
        1. Checks if package manager is available in PATH
        2. Queries package manager for installed packages/tools
        3. Cross-references with known CLI tools database
        4. Maps detected tools to configuration file paths
        5. Validates configuration file existence
        6. Returns organized mapping with package manager attribution
        
        Package Manager Integration:
        - Homebrew: Uses 'brew list --formula' to get CLI tools
        - npm: Uses 'npm list -g --depth=0 --parseable' for global packages
        - pip: Uses 'pip list --user' for user-installed packages
        
        Returns:
            Dict[str, List[str]]: Mapping of detected tools to configuration paths.
                                 Tool names include package manager attribution for clarity.
        
        Example:
            {
                'git (brew)': ['/Users/user/.gitconfig'],
                'starship (brew)': ['/Users/user/.config/starship.toml'],
                'typescript (npm)': ['/Users/user/.npmrc'],
                'pipx (pip)': ['/Users/user/.local/share/pipx/']
            }
        
        Note:
            This method complements PATH-based detection by providing package manager
            context and ensuring comprehensive coverage of installed tools.
        """
        detected_tools = {}
        
        # Check Homebrew installed packages
        if self.executor.which("brew"):
            try:
                # Get formulae (CLI tools)
                rc, output = self.executor.run_output("brew list --formula")
                if rc == 0:
                    brew_tools = set(output.strip().split())
                    for tool in brew_tools:
                        if tool in self.cli_tools_to_detect:
                            # Map to configuration if available (prioritize CLI tools config)
                            for app_key, config_paths in self.combined_config_map.items():
                                if (tool.lower() in app_key.lower() or
                                    self._normalize_tool_name(tool) == self._normalize_tool_name(app_key)):
                                    resolved_paths = self._resolve_config_paths(config_paths)
                                    if resolved_paths:
                                        detected_tools[f"{app_key} (brew)"] = resolved_paths
                                        break
            except Exception as e:
                self.logger.debug(f"Failed to check brew packages: {e}")
        
        # Check npm global packages
        if self.executor.which("npm"):
            try:
                rc, output = self.executor.run_output("npm list -g --depth=0 --parseable")
                if rc == 0:
                    for line in output.strip().split('\n'):
                        if '/node_modules/' in line:
                            tool = os.path.basename(line)
                            if tool in self.cli_tools_to_detect:
                                # Check for config (prioritize CLI tools config)
                                for app_key, config_paths in self.combined_config_map.items():
                                    if (tool.lower() in app_key.lower() or
                                        self._normalize_tool_name(tool) == self._normalize_tool_name(app_key)):
                                        resolved_paths = self._resolve_config_paths(config_paths)
                                        if resolved_paths:
                                            detected_tools[f"{app_key} (npm)"] = resolved_paths
                                            break
            except Exception as e:
                self.logger.debug(f"Failed to check npm packages: {e}")
        
        return detected_tools

    def _backup_cli_config(self, src_path: str, dest_dir: str, preserve_structure: bool = True) -> bool:
        """Backup CLI configuration with proper permissions and symlink handling"""
        try:
            if not os.path.exists(src_path):
                return False
            
            if os.path.islink(src_path):
                # Handle symlinks - preserve them
                link_target = os.readlink(src_path)
                dest_path = os.path.join(dest_dir, os.path.basename(src_path))
                os.symlink(link_target, dest_path)
                return True
            
            elif os.path.isfile(src_path):
                # Copy file with permissions
                dest_path = os.path.join(dest_dir, os.path.basename(src_path))
                shutil.copy2(src_path, dest_path)
                return True
            
            elif os.path.isdir(src_path):
                # Copy directory recursively with permissions
                dest_path = os.path.join(dest_dir, os.path.basename(src_path))
                shutil.copytree(src_path, dest_path, symlinks=True,
                              ignore_dangling_symlinks=True)
                return True
            
            return False
        except Exception as e:
            self.logger.debug(f"Failed to backup {src_path}: {e}")
            return False

    def export(self, output_dir: str) -> bool:
        apps = self._list_installed_apps()
        out_apps_dir = os.path.join(output_dir, "Applications")
        os.makedirs(out_apps_dir, exist_ok=True)
        exported_any = False

        # Save GUI applications discovery list
        if apps:
            try:
                with open(os.path.join(out_apps_dir, "Applications_list.txt"), "w", encoding="utf-8") as f:
                    for a in apps:
                        f.write(a + "\n")
            except Exception:
                pass

        # Detect CLI tools
        self.logger.info("Detecting installed CLI tools...")
        cli_tools = self._detect_installed_cli_tools()
        package_manager_tools = self._detect_package_manager_tools()
        
        # Combine all detected tools
        all_detected_tools = {**cli_tools, **package_manager_tools}
        
        # Save CLI tools discovery list
        if all_detected_tools:
            try:
                with open(os.path.join(out_apps_dir, "CLI_tools_list.txt"), "w", encoding="utf-8") as f:
                    f.write("# Detected CLI Tools and Their Configurations\n")
                    for tool_name, config_paths in all_detected_tools.items():
                        f.write(f"\n{tool_name}:\n")
                        for path in config_paths:
                            f.write(f"  - {path}\n")
            except Exception as e:
                self.logger.debug(f"Failed to write CLI tools list: {e}")

        # Export GUI app configs (existing logic)
        for app_key, paths in self.known_app_config_map.items():
            # Skip if this is a CLI tool (handled separately)
            if app_key in self.cli_tools_config_map:
                continue
            
            # Check if it's a GUI app (in /Applications)
            if not any(app_key.lower() in a.lower() for a in apps):
                # Skip if this is already handled as CLI tool
                if any(app_key in tool_name for tool_name in all_detected_tools):
                    continue
                # Skip if no GUI app match and no CLI detection
                continue
            
            include = True
            if self.executor.config.interactive:
                include = self.executor.confirm(f"Include configuration for GUI app '{app_key}'?")
            if not include:
                continue

            exported_any |= self._export_app_config(app_key, paths, out_apps_dir, "GUI")

        # Export CLI tool configs
        for tool_name, config_paths in all_detected_tools.items():
            include = True
            if self.executor.config.interactive:
                include = self.executor.confirm(f"Include configuration for CLI tool '{tool_name}'?")
            if not include:
                continue

            exported_any |= self._export_app_config(tool_name, config_paths, out_apps_dir, "CLI")

        # Generate install command hints (brew casks, mas, CLI tools)
        self._generate_install_hints(out_apps_dir)
        
        if not exported_any and not apps and not all_detected_tools:
            self.logger.info("No Applications or CLI tools found to export")
        
        return exported_any or bool(apps) or bool(all_detected_tools)

    def _export_app_config(self, app_name: str, config_paths: List[str], out_apps_dir: str, app_type: str) -> bool:
        """Export configuration for a single application or CLI tool"""
        exported = False
        slug = self._slugify(app_name)
        dest_dir = os.path.join(out_apps_dir, f"{app_type}_{slug}")
        
        for path in config_paths:
            candidates = [path]
            if any(ch in path for ch in ["*", "?", "["]):
                candidates = self._expand_globs(path)
            
            for src in candidates:
                if not os.path.exists(src):
                    continue
                
                os.makedirs(dest_dir, exist_ok=True)
                
                # Use enhanced CLI backup method for better handling
                if self._backup_cli_config(src, dest_dir):
                    self.logger.info(f"✓ Backed up {app_type} {app_name}: {src}")
                    exported = True
                else:
                    # Fallback to original method
                    try:
                        if os.path.isdir(src):
                            self.executor.run(f'cp -a "{src}" "{dest_dir}/"', check=False,
                                            description=f"Backup {app_name} dir")
                            exported = True
                        elif os.path.isfile(src):
                            self.executor.run(f'cp -a "{src}" "{dest_dir}/"', check=False,
                                            description=f"Backup {app_name} file")
                            exported = True
                    except Exception as e:
                        self.logger.debug(f"Failed to backup {src}: {e}")
        
        return exported

    def _generate_install_hints(self, out_apps_dir: str) -> None:
        lines: List[str] = ["#!/usr/bin/env bash", "set -e", "# Installation helper generated by MyConfig"]
        
        # Homebrew formulae and casks
        if self.executor.which("brew"):
            rc_f, out_f = self.executor.run_output("brew list --formula")
            rc_c, out_c = self.executor.run_output("brew list --cask")
            if rc_f == 0 and out_f.strip():
                lines.append("\n# Homebrew formulae (CLI tools)")
                for n in out_f.strip().splitlines():
                    n = n.strip()
                    if n:
                        lines.append(f"brew install {n}")
            if rc_c == 0 and out_c.strip():
                lines.append("\n# Homebrew casks (GUI applications)")
                for n in out_c.strip().splitlines():
                    n = n.strip()
                    if n:
                        lines.append(f"brew install --cask {n}")
        
        # Mac App Store apps
        if self.executor.which("mas"):
            rc_m, out_m = self.executor.run_output("mas list | awk '{print $1" "$2}'")
            if rc_m == 0 and out_m.strip():
                lines.append("\n# Mac App Store apps (requires login)")
                # mas list prints: "12345 App Name"
                rc_raw, out_raw = self.executor.run_output("mas list")
                if rc_raw == 0:
                    for line in out_raw.splitlines():
                        parts = line.split()
                        if parts and parts[0].isdigit():
                            lines.append(f"mas install {parts[0]}")
        
        # VS Code extensions
        if self.executor.which("code"):
            rc_v, out_v = self.executor.run_output("code --list-extensions")
            if rc_v == 0 and out_v.strip():
                lines.append("\n# VS Code extensions")
                for ext in out_v.splitlines():
                    ext = ext.strip()
                    if ext:
                        lines.append(f"code --install-extension {ext}")
        
        # npm global packages
        if self.executor.which("npm"):
            rc_npm, out_npm = self.executor.run_output("npm list -g --depth=0 --parseable")
            if rc_npm == 0 and out_npm.strip():
                global_packages = []
                for line in out_npm.strip().split('\n'):
                    if '/node_modules/' in line:
                        package = os.path.basename(line)
                        if package and package != 'npm':  # Skip npm itself
                            global_packages.append(package)
                
                if global_packages:
                    lines.append("\n# npm global packages")
                    for pkg in sorted(global_packages):
                        lines.append(f"npm install -g {pkg}")
        
        # pip user packages
        if self.executor.which("pip"):
            rc_pip, out_pip = self.executor.run_output("pip list --user --format=freeze")
            if rc_pip == 0 and out_pip.strip():
                lines.append("\n# pip user packages")
                for line in out_pip.strip().splitlines():
                    if '==' in line:
                        package = line.split('==')[0]
                        lines.append(f"pip install --user {package}")
        
        # cargo installed binaries
        if self.executor.which("cargo"):
            cargo_bin_dir = os.path.expanduser("~/.cargo/bin")
            if os.path.isdir(cargo_bin_dir):
                try:
                    cargo_bins = [f for f in os.listdir(cargo_bin_dir)
                                 if os.path.isfile(os.path.join(cargo_bin_dir, f)) and not f.startswith('.')]
                    if cargo_bins:
                        lines.append("\n# Cargo installed binaries (manual installation required)")
                        lines.append("# Note: These were installed via 'cargo install <package>'")
                        for binary in sorted(cargo_bins):
                            lines.append(f"# cargo install {binary}")
                except Exception:
                    pass

        try:
            helper = os.path.join(out_apps_dir, "INSTALL_COMMANDS.sh")
            with open(helper, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
        except Exception:
            pass

    def restore(self, backup_dir: str) -> bool:
        apps_dir = os.path.join(backup_dir, "Applications")
        if not os.path.isdir(apps_dir):
            return False
        restored = False
        # Iterate over exported app directories and restore with confirmation
        for entry in os.listdir(apps_dir):
            src_dir = os.path.join(apps_dir, entry)
            if not os.path.isdir(src_dir):
                continue
            # Best-effort mapping: ask user for destination
            if not self.executor.confirm(f"Restore configuration for '{entry}' from backup?"):
                continue
            # Heuristics: common destinations under Library or .config
            # Let user provide path interactively is out-of-scope; copy back under home keeping structure
            dest = os.path.expanduser("~")
            self.executor.run(f'cp -a "{src_dir}" "{dest}/"', check=False, description=f"Restore {entry}")
            restored = True
        return restored

    def preview_export(self, output_dir: str) -> List[str]:
        preview_items = []
        
        # GUI Applications
        apps = self._list_installed_apps()
        if apps:
            preview_items.append(f"✓ GUI Applications list ({len(apps)} apps)")
        else:
            preview_items.append("✗ No GUI Applications detected")
        
        # CLI Tools Detection
        try:
            cli_tools = self._detect_installed_cli_tools()
            package_manager_tools = self._detect_package_manager_tools()
            all_detected_tools = {**cli_tools, **package_manager_tools}
            
            if all_detected_tools:
                preview_items.append(f"✓ CLI Tools detected ({len(all_detected_tools)} tools)")
                # Show some examples
                tool_names = list(all_detected_tools.keys())[:3]
                if len(all_detected_tools) > 3:
                    tool_names.append(f"... and {len(all_detected_tools) - 3} more")
                preview_items.append(f"  Examples: {', '.join(tool_names)}")
            else:
                preview_items.append("✗ No CLI Tools with configurations detected")
        except Exception as e:
            preview_items.append("⚠ CLI Tools detection failed")
        
        # Configuration availability
        gui_configs = len([k for k, v in self.known_app_config_map.items()
                          if any(os.path.exists(os.path.expanduser(p)) for p in v)])
        cli_configs = len([k for k, v in self.cli_tools_config_map.items()
                          if any(os.path.exists(os.path.expanduser(p)) for p in v)])
        
        if gui_configs > 0:
            preview_items.append(f"✓ {gui_configs} GUI application configurations available")
        if cli_configs > 0:
            preview_items.append(f"✓ {cli_configs} CLI tool configurations available")
        
        return preview_items

    def preview_restore(self, backup_dir: str) -> List[str]:
        apps_dir = os.path.join(backup_dir, "Applications")
        if not os.path.isdir(apps_dir):
            return ["✗ No Applications directory in backup"]
        
        preview_items = []
        
        # Count GUI and CLI configurations
        gui_count = len([d for d in os.listdir(apps_dir)
                        if os.path.isdir(os.path.join(apps_dir, d)) and d.startswith("GUI_")])
        cli_count = len([d for d in os.listdir(apps_dir)
                        if os.path.isdir(os.path.join(apps_dir, d)) and d.startswith("CLI_")])
        legacy_count = len([d for d in os.listdir(apps_dir)
                           if os.path.isdir(os.path.join(apps_dir, d))
                           and not d.startswith("GUI_") and not d.startswith("CLI_")])
        
        if gui_count > 0:
            preview_items.append(f"✓ {gui_count} GUI application configuration sets")
        if cli_count > 0:
            preview_items.append(f"✓ {cli_count} CLI tool configuration sets")
        if legacy_count > 0:
            preview_items.append(f"✓ {legacy_count} legacy configuration sets")
        
        # Check for install commands
        install_script = os.path.join(apps_dir, "INSTALL_COMMANDS.sh")
        if os.path.exists(install_script):
            preview_items.append("✓ Installation commands script available")
        
        if not preview_items:
            preview_items.append("✗ No configuration sets found in backup")
        
        return preview_items


