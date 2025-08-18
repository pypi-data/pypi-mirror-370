from __future__ import annotations
import os, logging
from core import AppConfig
from utils import run
from logger import log_section, log_separator, log_success

def do_diff(cfg: AppConfig, a: str, b: str):
    if not (os.path.isdir(a) and os.path.isdir(b)):
        logger = logging.getLogger(__name__)
        logger.error("Please provide two valid directories")
        return
    logger = logging.getLogger(__name__)
    log_section(logger, f"Compare: {a} ⇄ {b}")
    log_separator(logger)
    # Readable recursive comparison (ignore compressed binaries)
    run(f'diff -ruN --exclude="*.tar.gz" --exclude="*.zip" --exclude="*.log" {a} {b} || true', cfg, check=False)

def do_pack(cfg: AppConfig, srcdir: str, outfile: str|None, use_gpg: bool=False):
    if not os.path.isdir(srcdir):
        logger = logging.getLogger(__name__)
        logger.error(f"Directory does not exist: {srcdir}")
        return
    base = outfile or (srcdir.rstrip("/").split("/")[-1] + ".zip")
    logger = logging.getLogger(__name__)
    log_section(logger, f"Pack: {srcdir} → {base}")
    log_separator(logger)
    run(f'cd "{srcdir}/.." && zip -r "{base}" "{srcdir.split("/")[-1]}"', cfg, check=False)
    if use_gpg:
        if not which("gpg"):
            logger.warning("gpg not detected, skipping encryption")
            return
        run(f'gpg -c "{base}"', cfg, check=False)
        log_success(logger, f"Generated encrypted package: {base}.gpg")

def which(cmd: str)->bool:
    return os.system(f"command -v {cmd} >/dev/null 2>&1")==0
