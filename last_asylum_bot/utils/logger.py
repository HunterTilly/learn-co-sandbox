"""
Logging setup — writes to console and rotating file simultaneously.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def build_logger(name: str = "LastAsylumBot") -> logging.Logger:
    import config as cfg

    cfg.LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, cfg.LOG_LEVEL.upper(), logging.INFO))
    logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if cfg.LOG_TO_CONSOLE:
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(fmt)
        logger.addHandler(sh)

    if cfg.LOG_TO_FILE:
        log_file = cfg.LOG_DIR / "bot.log"
        fh = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


log = build_logger()
