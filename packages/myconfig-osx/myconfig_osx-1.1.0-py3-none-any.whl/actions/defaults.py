from __future__ import annotations
import os, logging
from core import AppConfig
from utils import run, run_out, ts
from logger import log_section, log_separator, log_success

def _load_list(path:str)->list[str]:
    L=[]
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            for line in f:
                s=line.strip()
                if not s or s.startswith("#"): continue
                L.append(s)
    return L

def defaults_export_all(cfg: AppConfig):
    logger = logging.getLogger(__name__)
    log_section(logger, "defaults full export")
    log_separator(logger)
    rc,out = run_out("defaults domains")
    if rc!=0: 
        logger.error("Cannot list defaults domains")
        return
    excludes = _load_list("./"+cfg.defaults_exclude_file)
    outdir = f'./backups/defaults-all-{ts()}'
    os.makedirs(outdir, exist_ok=True)
    for d in out.split():
        if any(x in d for x in excludes): 
            logger.info(f"Excluding: {d}")
            continue
        run(f'defaults export "{d}" "{outdir}/{d}.plist" || true', cfg, check=False)
    log_success(logger, f"Exported to: {outdir}")

def defaults_import_dir(cfg: AppConfig, dirpath: str):
    if not dirpath or not os.path.isdir(dirpath):
        logger = logging.getLogger(__name__)
        logger.error(f"Directory does not exist: {dirpath}")
        return
    logger = logging.getLogger(__name__)
    log_section(logger, f"Import defaults: {dirpath}")
    log_separator(logger)
    run('for p in "'+dirpath+'"/*.plist; do [[ -e "$p" ]] || continue; '
        'd="$(basename "$p" .plist)"; '
        'defaults domains | grep -q "$d" && defaults export "$d" "$HOME/defaults_backup_${d}_$(date +%Y%m%d%H%M%S).plist" || true; '
        'defaults import "$d" "$p" || true; '
        'done; killall Dock 2>/dev/null || true; killall Finder 2>/dev/null || true', cfg, check=False)
    log_success(logger, "defaults import completed")


