# rust_crate_pipeline/utils/logging_utils.py
import logging
import os
import time
from typing import Optional


def configure_logging(log_level: int = logging.INFO, log_dir: Optional[str] = None) -> logging.Logger:
    """
    Configure global logging with file and console handlers (canonical for the whole repo).
    Args:
        log_level: Logging level (default: INFO)
        log_dir: Directory for log files (defaults to current directory)
    Returns:
        Root logger instance
    """
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler
    log_file = None
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(
            log_dir,
            (f"pipeline_{time.strftime('%Y%m%d-%H%M%S')}.log"),
        )
    else:
        log_file = f"pipeline_{time.strftime('%Y%m%d-%H%M%S')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    # Set noisy libraries to WARNING
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests_cache").setLevel(logging.WARNING)
    logging.getLogger("llama_cpp").setLevel(logging.WARNING)

    logger.info(f"Logging initialized - file: {log_file}")
    return logger
