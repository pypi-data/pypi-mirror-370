from __future__ import annotations
import os, shutil, logging
from logger import log_section, log_separator, log_success

def profile_list():
    logger = logging.getLogger(__name__)
    log_section(logger, "Available profiles")
    log_separator(logger)
    for p in sorted(os.listdir("./config/profiles")):
        if p.endswith(".toml"): 
            logger.info(p)

def profile_use(name: str):
    src = f"./config/profiles/{name}.toml"
    logger = logging.getLogger(__name__)
    if not os.path.exists(src): 
        logger.error(f"Not found: {src}")
        return
    shutil.copyfile(src, "./config/config.toml")
    log_success(logger, f"Applied: {src} → ./config/config.toml")

def profile_save(name: str):
    dst = f"./config/profiles/{name}.toml"
    logger = logging.getLogger(__name__)
    shutil.copyfile("./config/config.toml", dst)
    log_success(logger, f"Saved current config as: {dst}")
