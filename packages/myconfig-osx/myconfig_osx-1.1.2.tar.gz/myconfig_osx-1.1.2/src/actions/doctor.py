from __future__ import annotations
import logging, os
from core import AppConfig, CommandExecutor
from logger import log_section, log_separator, log_success

def do_doctor(cfg: AppConfig):
    executor = CommandExecutor(cfg)
    logger = logging.getLogger(__name__)
    
    log_section(logger, "System health check")
    log_separator(logger)
    
    # Xcode
    rc, _ = executor.run_output("xcode-select -p")
    if rc == 0:
        log_success(logger, "Xcode CLT installed")
    else:
        logger.warning("Xcode CLT not installed (xcode-select --install)")
    
    # brew
    if executor.which("brew"):
        rc, v = executor.run_output("brew --version | head -n1")
        log_success(logger, v.strip())
    else: 
        logger.warning("brew not installed")
    
    # code
    if executor.which("code"):
        log_success(logger, "code command available")
    else:
        logger.warning("VS Code command 'code' not detected")
    
    # mas
    if executor.which("mas"):
        rc, acc = executor.run_output("mas account 2>/dev/null || echo 'Not logged in'")
        if "Not logged in" not in acc and acc.strip():
            log_success(logger, f"App Store logged in: {acc.strip()}")
        else:
            logger.warning("App Store not logged in")
    else: 
        logger.warning("mas not installed")
    
    # defaults domain list
    dom_file = "./config/defaults/domains.txt"
    if os.path.exists(dom_file):
        missing = 0
        with open(dom_file, "r", encoding="utf-8") as f:
            for line in f:
                d = line.strip()
                if not d or d.startswith("#"): 
                    continue
                rc, _ = executor.run_output(f'defaults domains | grep -q "{d}"')
                if rc != 0:
                    logger.warning(f"defaults domain not initialized: {d}")
                    missing += 1
        if missing == 0: 
            log_success(logger, "defaults domain list check passed")
    
    log_separator(logger)
    log_success(logger, "Health check completed")
