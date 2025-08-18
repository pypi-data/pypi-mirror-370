from __future__ import annotations
import os, sys, subprocess, shlex, time, json, pathlib, logging
from logger import log_success

# Handle TOML library imports
try:
    import tomllib  # py311+
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        raise ImportError("tomli library required: pip install tomli")

# Colors
T1="\033[1m"; DIM="\033[2m"; RED="\033[31m"; GREEN="\033[32m"; YELLOW="\033[33m"; BLUE="\033[34m"; RST="\033[0m"
def color(c: str, s: str) -> str: return f"{c}{s}{RST}" if sys.stdout.isatty() else s

def which(cmd: str) -> bool:
    return subprocess.call(f"command -v {shlex.quote(cmd)} >/dev/null 2>&1", shell=True)==0

# AppConfig and configuration loading moved to src/core/config.py

def run(cmd: str, cfg, check: bool=True, description: str=""):
    logger = logging.getLogger(__name__)
    
    if cfg.dry_run:
        logger.info(f"{T1}[DRY-RUN]{RST} {cmd}")
        return True

    if cfg.verbose:
        if description:
            logger.info(f"▸ {description}")
        logger.info(f"{DIM}$ {cmd}{RST}")

    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        if check:
            logger.error(f"Command failed: {cmd}")
            logger.error(f"Exit code: {e.returncode}")
        return False

def run_out(cmd: str) -> str:
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""

def ts() -> str:
    return time.strftime("%Y%m%d-%H%M%S")

def host() -> str:
    hostname = subprocess.run("hostname", capture_output=True, text=True, shell=True).stdout.strip()
    return hostname or "unknown"

def verify_backup(srcdir: str) -> bool:
    logger = logging.getLogger(__name__)
    if not os.path.isdir(srcdir):
        logger.error(f"Backup directory does not exist: {srcdir}")
        return False
    
    # Check for essential files
    required_files = ["ENVIRONMENT.txt"]
    for f in required_files:
        if not os.path.exists(os.path.join(srcdir, f)):
            logger.warning(f"Missing backup file: {f}")
    
    return True

def create_backup_manifest(outdir: str, components: list) -> dict:
    """Create backup manifest with metadata"""
    manifest = {
        "timestamp": time.time(),
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hostname": host(),
        "components": components,
        "version": "2.0"
    }
    
    manifest_path = os.path.join(outdir, "MANIFEST.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    return manifest

class ProgressTracker:
    def __init__(self, total_steps: int = 0):
        self.current = 0
        self.total = total_steps
        self.logger = logging.getLogger(__name__)
    
    def update(self, message: str):
        self.current += 1
        if self.total > 0:
            self.logger.info(f"[{self.current}/{self.total}] {message}")
        else:
            self.logger.info(f"▸ {message}")

# Inline to avoid circular import with core module
DOT_LIST = [
    "~/.zshrc","~/.zprofile","~/.bashrc","~/.bash_profile","~/.profile",
    "~/.gitconfig","~/.gitignore_global","~/.vimrc","~/.ideavimrc",
    "~/.config/iterm2","~/.config/git","~/.config/nvim","~/.config/tmux","~/.tmux.conf"
]

def get_secure_dotfile_list() -> list[str]:
    """Return list of dotfiles, filtering out sensitive files"""
    logger = logging.getLogger(__name__)
    secure_list = []
    
    # Sensitive file patterns to exclude
    sensitive_patterns = [
        ".ssh/", ".aws/", ".gnupg/", "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
        "known_hosts", "authorized_keys", ".netrc", ".env", "secret", "password",
        "private_key", "key.pem", ".p12", ".pfx", "wallet.dat", "keychain",
        "credentials", "token", "api_key"
    ]
    
    for dotfile in DOT_LIST:
        path = os.path.expanduser(dotfile)
        if not os.path.exists(path):
            continue
            
        # Check if path contains sensitive patterns
        is_sensitive = any(pattern.lower() in path.lower() for pattern in sensitive_patterns)
        if is_sensitive:
            logger.warning(f"Skipping sensitive file: {dotfile}")
            continue
            
        secure_list.append(dotfile)
    
    return secure_list