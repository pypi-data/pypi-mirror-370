"""
Backup management and orchestration
"""

from __future__ import annotations
import os
import logging
from core.config import AppConfig
from core.executor import CommandExecutor
from core.components import (
    HomebrewComponent,
    MASComponent,
    VSCodeComponent,
    DotfilesComponent,
    DefaultsComponent,
    LaunchAgentsComponent,
)
from logger import log_section, log_separator, log_success
from utils import create_backup_manifest, ts, host
from template_engine import ExportTemplateRenderer, create_template_context


class BackupManager:
    """Manages the overall backup and restore process"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.executor = CommandExecutor(config)
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.components = [
            HomebrewComponent(self.executor),
            MASComponent(self.executor),
            VSCodeComponent(self.executor),
            DotfilesComponent(self.executor),
            DefaultsComponent(self.executor),
            LaunchAgentsComponent(self.executor),
        ]

    def export(self, output_dir: str, compress: bool = False) -> bool:
        """Export all enabled components"""
        temp_dir = output_dir
        if compress:
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix="myconfig_export_")
        
        os.makedirs(temp_dir, exist_ok=True)

        log_section(self.logger, f"Exporting to: {output_dir}")
        log_separator(self.logger)

        success_count = 0
        total_count = 0

        # Export environment info
        self._export_environment(temp_dir)
        success_count += 1

        # Export each component
        for component in self.components:
            if component.is_enabled() and component.is_available():
                total_count += 1
                if component.export(temp_dir):
                    success_count += 1
                    self.logger.info(f"✓ {component.name} exported")
                else:
                    self.logger.warning(f"✗ {component.name} export failed")

        # Create backup manifest and README using templates
        component_names = [comp.name for comp in self.components if comp.is_enabled()]
        create_backup_manifest(temp_dir, component_names)
        self._create_templated_files(temp_dir)
        
        # Handle compression if requested
        if compress:
            self._create_compressed_backup(temp_dir, output_dir)
            # Clean up temp directory
            import shutil
            shutil.rmtree(temp_dir)
        
        log_separator(self.logger)
        log_success(
            self.logger, f"Export completed: {success_count} components exported"
        )
        return success_count > 0

    def restore(self, backup_dir: str) -> bool:
        """Restore all available components from backup"""
        if not os.path.isdir(backup_dir):
            self.logger.error(f"Backup directory does not exist: {backup_dir}")
            return False

        log_section(self.logger, f"Restoring from backup: {backup_dir}")
        log_separator(self.logger)

        success_count = 0

        # Restore each component
        for component in self.components:
            if component.restore(backup_dir):
                success_count += 1
                self.logger.info(f"✓ {component.name} restored")

        log_separator(self.logger)
        log_success(
            self.logger, f"Restore completed: {success_count} components restored"
        )
        return success_count > 0

    def preview_export(self, output_dir: str) -> None:
        """Preview what would be exported"""
        log_section(self.logger, f"Preview export operation → {output_dir}")
        log_separator(self.logger)

        self.logger.info("Content to be exported:")
        self.logger.info("  ✓ Environment info (ENVIRONMENT.txt)")

        for component in self.components:
            if component.is_enabled():
                for line in component.preview_export(output_dir):
                    self.logger.info(f"  {line}")

        log_separator(self.logger)
        log_success(
            self.logger,
            "Preview completed. Use 'myconfig export' to perform actual export",
        )

    def preview_restore(self, backup_dir: str) -> None:
        """Preview what would be restored"""
        if not os.path.isdir(backup_dir):
            self.logger.error(f"Backup directory does not exist: {backup_dir}")
            return

        log_section(self.logger, f"Preview restore operation ← {backup_dir}")
        log_separator(self.logger)

        self.logger.info("Backup content analysis:")

        for component in self.components:
            for line in component.preview_restore(backup_dir):
                self.logger.info(f"  {line}")

        log_separator(self.logger)
        log_success(
            self.logger,
            "Preview completed. Use 'myconfig restore' to perform actual restore",
        )

    def _export_environment(self, output_dir: str) -> None:
        """Export environment information using template"""
        from utils import ts, host
        from template_engine import TemplateEngine
        
        try:
            # Gather environment data
            rc, sw_vers = self.executor.run_output("sw_vers || true")
            rc, xcode_path = self.executor.run_output("xcode-select -p || true")
            
            # Create template context
            env_context = {
                'export_time': ts(),
                'hostname': host(),
                'sw_vers': sw_vers.strip(),
                'xcode_path': xcode_path.strip()
            }
            
            # Use template engine
            engine = TemplateEngine()
            env_file = os.path.join(output_dir, "ENVIRONMENT.txt")
            engine.render_to_file("ENVIRONMENT.txt.template", env_context, env_file)
            
        except Exception as e:
            self.logger.warning(f"Template-based environment export failed: {e}")
            # Fallback to simple version
            self._export_environment_fallback(output_dir)

    def _export_environment_fallback(self, output_dir: str) -> None:
        """Fallback environment export without templates"""
        from utils import ts, host

        env_file = os.path.join(output_dir, "ENVIRONMENT.txt")
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(f"export_time: {ts()}\nhost: {host()}\n\n")

            rc, sw = self.executor.run_output("sw_vers || true")
            f.write("sw_vers:\n" + sw + "\n")

            rc, xcp = self.executor.run_output("xcode-select -p || true")
            f.write("xcode-select -p:\n" + xcp + "\n")

    def _create_templated_files(self, output_dir: str) -> None:
        """Create templated files (README.md, etc.) using template engine"""
        try:
            # Create template context from exported files
            context = create_template_context(output_dir)
            
            # Use template renderer to create README
            renderer = ExportTemplateRenderer()
            renderer.create_readme(output_dir, context)
            
        except Exception as e:
            self.logger.warning(f"Template generation failed: {e}")
            # Fallback to simple README
            self._create_simple_readme(output_dir)

    def _create_simple_readme(self, output_dir: str) -> None:
        """Create a simple fallback README if template fails"""
        readme_file = os.path.join(output_dir, "README.md")
        
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write("# MyConfig Export\n\n")
            f.write(f"Export Time: {ts()}\n")
            f.write(f"Hostname: {host()}\n\n")
            f.write("This directory contains a MyConfig backup.\n")
            f.write("Use 'myconfig restore <this-directory>' to restore.\n")
        
        self.logger.info("Created simple README.md")

    def _create_compressed_backup(self, temp_dir: str, output_path: str) -> None:
        """Create compressed backup archive"""
        import tarfile
        
        # Ensure output_path has .tar.gz extension
        if not output_path.endswith('.tar.gz'):
            output_path = output_path + '.tar.gz'
        
        self.logger.info(f"Creating compressed backup: {output_path}")
        
        with tarfile.open(output_path, 'w:gz') as tar:
            # Add all files from temp directory
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                tar.add(item_path, arcname=item)
        
        # Show final archive size
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        self.logger.info(f"Compressed backup created: {size_mb:.1f} MB")

    def unpack(self, archive_path: str, output_dir: str = None) -> str:
        """Unpack a compressed backup archive"""
        import tarfile
        import tempfile
        
        if not os.path.exists(archive_path):
            self.logger.error(f"Archive not found: {archive_path}")
            return None
        
        if output_dir is None:
            # Create temp directory for extraction
            output_dir = tempfile.mkdtemp(prefix="myconfig_unpack_")
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        log_section(self.logger, f"Unpacking archive: {archive_path}")
        log_separator(self.logger)
        
        try:
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(output_dir)
            
            # Verify extraction
            if os.path.exists(os.path.join(output_dir, "MANIFEST.json")):
                log_success(self.logger, f"Archive unpacked to: {output_dir}")
                return output_dir
            else:
                self.logger.error("Invalid backup archive - missing MANIFEST.json")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to unpack archive: {e}")
            return None
