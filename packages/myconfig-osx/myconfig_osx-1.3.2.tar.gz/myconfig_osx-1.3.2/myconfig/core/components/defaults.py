"""
macOS system defaults backup/restore component
"""

from __future__ import annotations
import os
from typing import List
from myconfig.core.base import BackupComponent
try:
    from importlib import resources as importlib_resources  # py3.9+
except Exception:  # pragma: no cover - fallback
    import importlib_resources  # type: ignore


class DefaultsComponent(BackupComponent):
    """Handles macOS system defaults backup/restore"""

    def is_available(self) -> bool:
        return self.executor.which("defaults")

    def is_enabled(self) -> bool:
        return self.config.enable_defaults

    def export(self, output_dir: str) -> bool:
        if not self.is_enabled() or not self.is_available():
            return False

        # Load domains list (local path or packaged fallback)
        domains_file = "myconfig/" + self.config.defaults_domains_file
        domains: List[str] = []
        if os.path.exists(domains_file):
            with open(domains_file, "r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if s and not s.startswith("#"):
                        domains.append(s)
        else:
            # packaged (single source of truth)
            rel = self.config.defaults_domains_file
            res = importlib_resources.files("myconfig").joinpath(rel)
            if res.is_file():
                with importlib_resources.as_file(res) as p:
                    with open(p, "r", encoding="utf-8") as f:
                        for line in f:
                            s = line.strip()
                            if s and not s.startswith("#"):
                                domains.append(s)

        if not domains:
            self.logger.warning("No domains found in domains file")
            return False

        # Create defaults directory
        defaults_dir = os.path.join(output_dir, "defaults")
        os.makedirs(defaults_dir, exist_ok=True)

        # Export each domain
        exported_count = 0
        for domain in domains:
            rc, _ = self.executor.run_output(f'defaults domains | grep -q "{domain}"')
            if rc == 0:
                plist_file = os.path.join(defaults_dir, f"{domain}.plist")
                self.executor.run(
                    f'defaults export "{domain}" "{plist_file}" || true',
                    check=False,
                    description=f"Export {domain}",
                )
                exported_count += 1

        self.logger.info(f"Exported {exported_count} defaults domains")
        return exported_count > 0

    def restore(self, backup_dir: str) -> bool:
        defaults_dir = os.path.join(backup_dir, "defaults")

        if not os.path.isdir(defaults_dir):
            self.logger.warning("No defaults directory found in backup")
            return False

        if self.executor.confirm("Import and refresh Dock/Finder?"):
            # Import all plist files
            import_cmd = f"""
            for p in "{defaults_dir}"/*.plist; do
                [[ -e "$p" ]] || continue
                d="$(basename "$p" .plist)"
                defaults domains | grep -q "$d" && defaults export "$d" "$HOME/defaults_backup_${{d}}_$(date +%Y%m%d%H%M%S).plist" || true
                defaults import "$d" "$p" || true
            done
            killall Dock 2>/dev/null || true
            killall Finder 2>/dev/null || true
            """
            self.executor.run(import_cmd, check=False)
            return True
        return False

    def preview_export(self, output_dir: str) -> List[str]:
        if not self.is_enabled() or not self.is_available():
            return ["✗ Defaults export disabled"]

        # Try local then packaged
        domains: List[str] = []
        domains_file = "myconfig/" + self.config.defaults_domains_file
        if os.path.exists(domains_file):
            with open(domains_file, "r", encoding="utf-8") as f:
                domains = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
        else:
            rel = self.config.defaults_domains_file
            res = importlib_resources.files("myconfig").joinpath(rel)
            if res.is_file():
                with importlib_resources.as_file(res) as p:
                    with open(p, "r", encoding="utf-8") as f:
                        domains = [
                            line.strip()
                            for line in f
                            if line.strip() and not line.startswith("#")
                        ]
        if domains:
            return [
                "✓ System preferences (defaults):",
                *[f"    - {domain}" for domain in domains[:5]],
                f"    ... total {len(domains)} domains" if len(domains) > 5 else "",
            ]
        return ["✗ No defaults domains file"]

    def preview_restore(self, backup_dir: str) -> List[str]:
        defaults_dir = os.path.join(backup_dir, "defaults")
        if os.path.isdir(defaults_dir):
            plist_files = [f for f in os.listdir(defaults_dir) if f.endswith(".plist")]
            return [f"✓ System preferences: {len(plist_files)} domains"]
        return ["✗ No system preferences"]
