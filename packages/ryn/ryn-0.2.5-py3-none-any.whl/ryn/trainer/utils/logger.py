import logging
import os
from datetime import datetime


def get_logger(name="trainer", log_dir="logs"):
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(
        log_dir, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        fh = logging.FileHandler(log_path)
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger, log_path
