from __future__ import annotations
import os, json, shlex, logging
from core import AppConfig
from utils import run, run_out, ts, host, which, verify_backup, create_backup_manifest, ProgressTracker, get_secure_dotfile_list
from logger import log_section, log_separator, log_success, confirm_action

HOME = os.path.expanduser("~")

DOT_LIST = [
    "~/.zshrc","~/.zprofile","~/.bashrc","~/.bash_profile","~/.profile",
    "~/.gitconfig","~/.gitignore_global","~/.vimrc","~/.ideavimrc",
    "~/.wezterm.lua","~/.tmux.conf","~/.config/tmux",
    "~/.config/wezterm","~/.config/kitty","~/.config/nvim","~/.config/alacritty",
    "~/.config/karabiner","~/.config/starship.toml","~/.config/iterm2",
    "~/.ssh/config",  # Config only, no private keys
    # JetBrains / Xcode / Services / Fonts (optional)
    "~/Library/Preferences/com.googlecode.iterm2.plist",
    "~/Library/Preferences/IdeaVim",
    "~/Library/Application Support/JetBrains",
    "~/Library/Preferences/IntelliJIdea*",  # patterns handled by shell via rsync
    "~/Library/Developer/Xcode/UserData",   # keybindings/snippets/themes
    "~/Library/Services",                   # Automator quick actions
    "~/Library/Fonts",                      # Custom fonts
    # VSCode user settings
    "~/Library/Application Support/Code/User/settings.json",
    "~/Library/Application Support/Code/User/keybindings.json",
    "~/Library/Application Support/Code/User/snippets",
]

def do_export(cfg: AppConfig, outdir: str|None):
    outdir = outdir or f"./backups/backup-{host()}-{ts()}"
    if os.path.exists(outdir):
        logger = logging.getLogger(__name__)
        logger.warning(f"Output directory already exists: {outdir}")
        if not confirm_action(logger, "Continue writing?", cfg.interactive): return
    os.makedirs(outdir, exist_ok=True)
    logger = logging.getLogger(__name__)
    log_section(logger, f"Exporting to: {outdir}")
    log_separator(logger)
    
    # Calculate total steps and create progress tracker
    total_steps = 1  # Environment info
    if which("brew"): total_steps += 1
    if cfg.enable_mas and which("mas"): total_steps += 1
    if cfg.enable_vscode and which("code"): total_steps += 1
    if cfg.enable_npm and which("npm"): total_steps += 1
    if cfg.enable_pipx and which("pipx"): total_steps += 1
    if cfg.enable_pip_user and which("pip"): total_steps += 1
    total_steps += 1  # dotfiles
    if cfg.enable_defaults: total_steps += 1
    if cfg.enable_launchagents: total_steps += 1
    total_steps += 2  # Manifest and verification
    
    progress = ProgressTracker(total_steps, "Export progress")

    # Environment info
    with open(os.path.join(outdir, "ENVIRONMENT.txt"), "w", encoding="utf-8") as f:
        f.write(f"export_time: {ts()}\nhost: {host()}\n\n")
        rc, sw = run_out("sw_vers || true"); f.write("sw_vers:\n"+sw+"\n")
        rc, xcp = run_out("xcode-select -p || true"); f.write("xcode-select -p:\n"+xcp+"\n")
    progress.update("Environment info saved")

    # brew
    if which("brew"):
        run(f'brew bundle dump --file="{outdir}/Brewfile" --force', cfg, check=False, description="Export Brewfile")
        run(f'brew --version > "{outdir}/HOMEBREW_VERSION.txt"', cfg, check=False)
        progress.update("Homebrew config exported")
    else: 
        logger.warning("brew not detected, skipping")

    # mas
    if cfg.enable_mas and which("mas"):
        run(f'mas list > "{outdir}/mas.list"', cfg, check=False, description="Export MAS app list")
        progress.update("Mac App Store app list exported")
    else: 
        logger.warning("Skipping MAS list export")

    # vscode
    if cfg.enable_vscode and which("code"):
        run(f'code --list-extensions > "{outdir}/vscode_extensions.txt"', cfg, check=False, description="Export VS Code extensions")
        progress.update("VS Code extension list exported")
    else: 
        logger.warning("Skipping VS Code extension export")

    # npm/pip/pipx
    if cfg.enable_npm and which("npm"):
        run(r'npm -g list --depth=0 2>/dev/null | awk -F" " "/──/ {print $2}" | cut -d"@" -f1 | sed "/^$/d" > "{}"'.format(os.path.join(outdir,"npm_globals.txt")), cfg, check=False, description="Export npm global packages")
        progress.update("npm global package list exported")
    if cfg.enable_pipx and which("pipx"):
        run(f'pipx list > "{outdir}/pipx_list.txt"', cfg, check=False, description="Export pipx package list")
        progress.update("pipx package list exported")
    if cfg.enable_pip_user and which("pip"):
        run(f'pip freeze --user > "{outdir}/pip_user_freeze.txt"', cfg, check=False, description="Export pip user packages")
        progress.update("pip user package list exported")

    # dotfiles (using security filtering)
    safe_dotfiles = get_secure_dotfile_list()
    tmp = os.path.join(outdir, "dotfiles"); os.makedirs(tmp, exist_ok=True)
    
    for pat in safe_dotfiles:
        src = os.path.expanduser(pat)
        if os.path.exists(src):
            run(f'rsync -a --exclude "*.key" --exclude "known_hosts" --exclude "authorized_keys" {shlex.quote(src)} {shlex.quote(tmp)} 2>/dev/null || true', cfg, check=False, description=f"Copy {pat}")
    
    run(f'tar -czf "{outdir}/dotfiles.tar.gz" -C "{tmp}" . || true', cfg, check=False, description="Compress dotfiles")
    run(f'rm -rf "{tmp}"', cfg, check=False)
    progress.update("dotfiles exported and compressed")

    # Curated defaults
    if cfg.enable_defaults and os.path.exists("./" + cfg.defaults_domains_file):
        defdir = os.path.join(outdir, "defaults"); os.makedirs(defdir, exist_ok=True)
        with open("./" + cfg.defaults_domains_file, "r", encoding="utf-8") as f:
            domains = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        for d in domains:
            rc,_ = run_out(f'defaults domains | grep -q "{d}"; echo $?')
            if rc==0:
                run(f'defaults export "{d}" "{defdir}/{d}.plist" || true', cfg, check=False, description=f"Export {d}")
        progress.update(f"System preferences exported ({len(domains)} domains)")

    # LaunchAgents
    la = os.path.expanduser("~/Library/LaunchAgents")
    if cfg.enable_launchagents and os.path.isdir(la):
        os.makedirs(os.path.join(outdir,"LaunchAgents"), exist_ok=True)
        run(f'cp -a "{la}"/*.plist "{outdir}/LaunchAgents/" 2>/dev/null || true', cfg, check=False, description="Backup LaunchAgents")
        progress.update("LaunchAgents backed up")

    # Create backup manifest and verification
    create_backup_manifest(outdir)
    progress.update("Backup manifest created")
    
    if verify_backup(outdir):
        progress.update("Backup verification passed")
        progress.finish()
        log_separator(logger)
        log_success(logger, f"Export completed and verified → {outdir}")
    else:
        progress.update("Backup verification failed")
        progress.finish()
        log_separator(logger)
        logger.warning(f"Export completed but verification failed → {outdir}")
        logger.warning("Recommend checking backup content or re-running export")

def preview_export(cfg: AppConfig, outdir: str|None):
    """Preview what the export operation will do"""
    outdir = outdir or f"./backups/backup-{host()}-{ts()}"
    logger = logging.getLogger(__name__)
    log_section(logger, f"Preview export operation → {outdir}")
    log_separator(logger)
    
    # Show content to be exported
    logger.info("Content to be exported:")
    logger.info("  ✓ Environment info (ENVIRONMENT.txt)")
    
    if which("brew"):
        logger.info("  ✓ Homebrew config (Brewfile)")
    else:
        logger.warning("  ✗ Homebrew not installed, skipping")
    
    if cfg.enable_mas and which("mas"):
        logger.info("  ✓ Mac App Store app list")
    else:
        logger.warning("  ✗ MAS export disabled or not installed")
    
    if cfg.enable_vscode and which("code"):
        logger.info("  ✓ VS Code extension list")
    else:
        logger.warning("  ✗ VS Code export disabled or not installed")
    
    # dotfiles preview
    logger.info("  ✓ Dotfiles and config files:")
    existing_dots = []
    for pat in DOT_LIST:
        src = os.path.expanduser(pat)
        if os.path.exists(src):
            existing_dots.append(pat)
    
    for dot in existing_dots[:5]:  # Only show first 5
        logger.info(f"    - {dot}")
    if len(existing_dots) > 5:
        logger.info(f"    ... total {len(existing_dots)} config files")
    
    # defaults preview
    if cfg.enable_defaults and os.path.exists("./" + cfg.defaults_domains_file):
        logger.info("  ✓ System preferences (defaults):")
        with open("./" + cfg.defaults_domains_file, "r", encoding="utf-8") as f:
            domains = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        for domain in domains[:3]:  # Only show first 3
            logger.info(f"    - {domain}")
        if len(domains) > 3:
            logger.info(f"    ... total {len(domains)} domains")
    
    # LaunchAgents
    la = os.path.expanduser("~/Library/LaunchAgents")
    if cfg.enable_launchagents and os.path.isdir(la):
        plist_files = [f for f in os.listdir(la) if f.endswith('.plist')]
        if plist_files:
            logger.info(f"  ✓ LaunchAgents ({len(plist_files)} files)")
    
    log_separator(logger)
    log_success(logger, "Preview completed. Use 'myconfig export' to perform actual export")
