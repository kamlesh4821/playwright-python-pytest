from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

from pythonjsonlogger import jsonlogger


def get_logger(name: str) -> logging.Logger:
    """Return a structured JSON logger for the given module name.

    Console handler: WARNING and above.
    File handler: DEBUG and above, written to logs/run_YYYYMMDD_HHMMSS.log.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"run_{timestamp}.log"

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger
