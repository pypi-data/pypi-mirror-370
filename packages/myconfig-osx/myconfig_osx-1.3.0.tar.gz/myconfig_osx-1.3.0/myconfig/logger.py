"""
Logging configuration for MyConfig
"""
import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[34m',     # Blue  
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    # Status icons
    ICONS = {
        'DEBUG': '🔍',
        'INFO': '▸',
        'WARNING': '⚠',
        'ERROR': '✖',
        'CRITICAL': '💥',
    }
    
    def format(self, record):
        # Add color and icon based on log level
        if sys.stdout.isatty():  # Only colorize if output is a terminal
            color = self.COLORS.get(record.levelname, '')
            icon = self.ICONS.get(record.levelname, '▸')
            record.levelname = f"{color}{icon}{self.RESET}"
        else:
            record.levelname = self.ICONS.get(record.levelname, '▸')
        
        return super().format(record)


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Setup logging configuration"""
    
    # Determine log level
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = ColoredFormatter('%(levelname)s %(message)s')
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add our console handler
    root_logger.addHandler(console_handler)





# Special logging functions for compatibility
def log_section(logger: logging.Logger, message: str) -> None:
    """Log a section header"""
    if sys.stdout.isatty():
        logger.info(f"\033[1m{message}\033[0m")  # Bold
    else:
        logger.info(message)


def log_separator(logger: logging.Logger) -> None:
    """Log a separator line"""
    if sys.stdout.isatty():
        logger.info("\033[2m" + "─" * 60 + "\033[0m")  # Dim
    else:
        logger.info("─" * 60)


def log_success(logger: logging.Logger, message: str) -> None:
    """Log a success message"""
    if sys.stdout.isatty():
        logger.info(f"\033[32m✔\033[0m {message}")  # Green
    else:
        logger.info(f"✔ {message}")


def confirm_action(logger: logging.Logger, prompt: str, interactive: bool = True) -> bool:
    """Ask for user confirmation"""
    if not interactive:
        return True
    
    try:
        print(f"▸ {prompt} [y/N]: ", end="", flush=True)
        answer = input().strip().lower()
        return answer in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        print()  # New line after interrupt
        return False
