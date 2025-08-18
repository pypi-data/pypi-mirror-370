from __future__ import annotations
import os, logging
from core import AppConfig
from utils import run, run_out, which, verify_backup
from logger import log_section, log_separator, log_success, confirm_action

def do_restore(cfg: AppConfig, srcdir: str):
    logger = logging.getLogger(__name__)
    if not srcdir or not os.path.isdir(srcdir):
        logger.error(f"Backup directory does not exist: {srcdir}")
        return
    
    # Verify backup integrity
    logger.info("Verifying backup integrity...")
    if not verify_backup(srcdir):
        if not confirm_action(logger, "Backup verification failed, continue with restore?", cfg.interactive):
            logger.warning("Restore operation cancelled")
            return
    
    log_section(logger, f"Restoring from backup: {srcdir}")
    log_separator(logger)

    # brew
    if not which("brew"):
        log_section(logger, "Install Homebrew")
        if confirm_action(logger, "Install Homebrew?", cfg.interactive):
            run('NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"', cfg, check=False)
    brewfile = os.path.join(srcdir, "Brewfile")
    if os.path.exists(brewfile):
        if confirm_action(logger, "Execute brew bundle install?", cfg.interactive):
            run(f'brew bundle --file="{brewfile}"', cfg, check=False)

    # mas
    mlist = os.path.join(srcdir, "mas.list")
    if cfg.enable_mas and os.path.exists(mlist):
        if not which("mas"): 
            run("brew install mas", cfg, check=False)
        log_section(logger, "Restore Mac App Store apps")
        logger.warning("Please login to App Store first")
        if confirm_action(logger, "Install MAS list now?", cfg.interactive):
            run(f'awk \'{{print $1}}\' "{mlist}" | while read -r id; do [[ -z "$id" ]] || mas install "$id" || true; done', cfg, check=False)

    # dotfiles
    dotball = os.path.join(srcdir, "dotfiles.tar.gz")
    if os.path.exists(dotball):
        log_section(logger, "Restore dotfiles to $HOME")
        if confirm_action(logger, "Overwrite existing files (auto backup)?", cfg.interactive):
            run('TMP_DOT="$(mktemp -d)" && '
                f'tar -xzf "{dotball}" -C "$TMP_DOT" && '
                '(cd "$TMP_DOT" && find . -type f -print0) | while IFS= read -r -d "" item; do '
                'dst="$HOME/${item#./}"; [[ -e "$dst" ]] && cp -a "$dst" "${dst}.bak.$(date +%Y%m%d%H%M%S)"; '
                'done && rsync -av "$TMP_DOT"/ "$HOME"/ && rm -rf "$TMP_DOT"', cfg, check=False)

    # vscode
    vxt = os.path.join(srcdir, "vscode_extensions.txt")
    if cfg.enable_vscode and os.path.exists(vxt) and which("code"):
        log_section(logger, "Install VS Code extensions")
        if confirm_action(logger, "Start installing VS Code extensions?", cfg.interactive):
            run(f'while read -r ext; do [[ -z "$ext" ]] || code --install-extension "$ext" || true; done < "{vxt}"', cfg, check=False)

    # npm/pip/pipx
    if cfg.enable_npm and os.path.exists(os.path.join(srcdir,"npm_globals.txt")) and which("npm"):
        log_section(logger, "npm global packages")
        if confirm_action(logger, "Install npm global packages?", cfg.interactive):
            run(f'xargs -I{{}} npm -g install {{}} < "{os.path.join(srcdir,"npm_globals.txt")}"', cfg, check=False)
    if cfg.enable_pip_user and os.path.exists(os.path.join(srcdir,"pip_user_freeze.txt")) and which("pip"):
        log_section(logger, "pip --user packages")
        if confirm_action(logger, "pip --user install requirements?", cfg.interactive):
            run(f'pip install --user -r "{os.path.join(srcdir,"pip_user_freeze.txt")}"', cfg, check=False)

    # defaults
    defdir = os.path.join(srcdir, "defaults")
    if cfg.enable_defaults and os.path.isdir(defdir):
        log_section(logger, "Import defaults")
        if confirm_action(logger, "Import and refresh Dock/Finder?", cfg.interactive):
            run('for p in "'+defdir+'"/*.plist; do [[ -e "$p" ]] || continue; '
                'd="$(basename "$p" .plist)"; '
                'defaults domains | grep -q "$d" && defaults export "$d" "$HOME/defaults_backup_${d}_$(date +%Y%m%d%H%M%S).plist" || true; '
                'defaults import "$d" "$p" || true; '
                'done; killall Dock 2>/dev/null || true; killall Finder 2>/dev/null || true', cfg, check=False)

    # LaunchAgents
    la = os.path.join(srcdir, "LaunchAgents")
    if cfg.enable_launchagents and os.path.isdir(la):
        log_section(logger, "Restore LaunchAgents")
        run('mkdir -p "$HOME/Library/LaunchAgents"', cfg, check=False)
        run(f'cp -a "{la}"/*.plist "$HOME/Library/LaunchAgents/" 2>/dev/null || true', cfg, check=False)
        if confirm_action(logger, "Load LaunchAgents?", cfg.interactive):
            run('find "$HOME/Library/LaunchAgents" -name "*.plist" -print0 | while IFS= read -r -d "" f; do launchctl load -w "$f" 2>/dev/null || true; done', cfg, check=False)

    log_separator(logger)
    log_success(logger, "Restore completed")

def preview_restore(cfg: AppConfig, srcdir: str):
    """Preview what the restore operation will do"""
    logger = logging.getLogger(__name__)
    if not srcdir or not os.path.isdir(srcdir):
        logger.error(f"Backup directory does not exist: {srcdir}")
        return
    
    log_section(logger, f"Preview restore operation ← {srcdir}")
    log_separator(logger)
    
    # Check backup content
    logger.info("Backup content analysis:")
    
    # Check various files
    brewfile = os.path.join(srcdir, "Brewfile")
    if os.path.exists(brewfile):
        try:
            with open(brewfile, 'r') as f:
                lines = f.readlines()
            brew_count = len([l for l in lines if l.strip().startswith('brew ')])
            cask_count = len([l for l in lines if l.strip().startswith('cask ')])
            vscode_count = len([l for l in lines if l.strip().startswith('vscode ')])
            logger.info(f"  ✓ Homebrew: {brew_count} packages, {cask_count} apps, {vscode_count} VS Code extensions")
        except Exception as e:
            logger.debug(f"Failed to parse Brewfile: {e}")
            logger.info("  ✓ Homebrew config file")
    else:
        logger.warning("  ✗ No Homebrew config")
    
    mlist = os.path.join(srcdir, "mas.list")
    if os.path.exists(mlist):
        try:
            with open(mlist, 'r') as f:
                mas_apps = len(f.readlines())
            logger.info(f"  ✓ Mac App Store: {mas_apps} apps")
        except Exception as e:
            logger.debug(f"Failed to parse MAS list: {e}")
            logger.info("  ✓ Mac App Store app list")
    else:
        logger.warning("  ✗ No MAS app list")
    
    dotball = os.path.join(srcdir, "dotfiles.tar.gz")
    if os.path.exists(dotball):
        size = os.path.getsize(dotball)
        logger.info(f"  ✓ Dotfiles archive ({size} bytes)")
    else:
        logger.warning("  ✗ No dotfiles backup")
    
    defdir = os.path.join(srcdir, "defaults")
    if os.path.isdir(defdir):
        plist_files = [f for f in os.listdir(defdir) if f.endswith('.plist')]
        logger.info(f"  ✓ System preferences: {len(plist_files)} domains")
    else:
        logger.warning("  ✗ No system preferences")
    
    la = os.path.join(srcdir, "LaunchAgents")
    if os.path.isdir(la):
        agent_files = [f for f in os.listdir(la) if f.endswith('.plist')]
        logger.info(f"  ✓ LaunchAgents: {len(agent_files)} services")
    else:
        logger.warning("  ✗ No LaunchAgents")
    
    # Show environment info
    env_file = os.path.join(srcdir, "ENVIRONMENT.txt")
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info("  ✓ Source environment info:")
            for line in content.split('\n')[:3]:  # Show first 3 lines
                if line.strip():
                    logger.info(f"    {line}")
        except Exception as e:
            logger.debug(f"Failed to read environment file: {e}")
            logger.info("  ✓ Environment info file")
    
    log_separator(logger)
    log_success(logger, "Preview completed. Use 'myconfig restore' to perform actual restore")
