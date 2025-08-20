from __future__ import annotations
import os, shutil, logging
from myconfig.logger import log_section, log_separator, log_success
try:
    from importlib import resources as importlib_resources  # py3.9+
except Exception:  # pragma: no cover
    import importlib_resources  # type: ignore

def profile_list():
    logger = logging.getLogger(__name__)
    log_section(logger, "Available profiles")
    log_separator(logger)
    # Local project profiles first
    prof_dir = "myconfig/config/profiles"
    names = []
    if os.path.isdir(prof_dir):
        names.extend([p for p in os.listdir(prof_dir) if p.endswith(".toml")])
    else:
        try:
            res_dir = importlib_resources.files("myconfig").joinpath("config/profiles")
            for p in res_dir.iterdir():
                if p.name.endswith(".toml"):
                    names.append(p.name)
        except Exception:
            pass
    for p in sorted(set(names)):
        logger.info(p)

def profile_use(name: str):
    src = f"myconfig/config/profiles/{name}.toml"
    logger = logging.getLogger(__name__)
    if not os.path.exists(src): 
        # try packaged
        try:
            res = importlib_resources.files("myconfig").joinpath(f"config/profiles/{name}.toml")
            if res.is_file():
                with importlib_resources.as_file(res) as p:
                    src = str(p)
        except Exception:
            pass
        if not os.path.exists(src):
            logger.error(f"Not found: ./config/profiles/{name}.toml")
            return
    shutil.copyfile(src, "myconfig/config/config.toml")
    log_success(logger, f"Applied: {src} → myconfig/config/config.toml")

def profile_save(name: str):
    dst = f"myconfig/config/profiles/{name}.toml"
    logger = logging.getLogger(__name__)
    shutil.copyfile("myconfig/config/config.toml", dst)
    log_success(logger, f"Saved current config as: {dst}")
