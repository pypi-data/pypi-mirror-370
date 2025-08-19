import logging
import sys
from logging.handlers import RotatingFileHandler

# ANSI-Farbcodes
RESET = "\033[0m"
GRAY = "\033[90m"
RED = "\033[31m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
WHITE = "\033[97m"


class ColoredFormatter(logging.Formatter):
    """
    Formatter that adds color for console output.
    """

    LEVEL_COLORS = {
        logging.DEBUG: GRAY,
        logging.INFO: WHITE,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: RED + MAGENTA,
    }

    def __init__(self):
        super().__init__()
        self.base_fmt = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        self.detailed_fmt = "%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d:%(funcName)s | %(message)s"
        self.datefmt = "%m-%d-%Y %H:%M:%S"

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, WHITE)
        if record.levelno >= logging.WARNING:
            fmt = self.detailed_fmt
        else:
            fmt = self.base_fmt

        formatter = logging.Formatter(fmt, self.datefmt)
        msg = formatter.format(record)

        parts = msg.split(" | ")
        if len(parts) >= 4:
            parts[0] = CYAN + parts[0] + RESET  # Zeit
            parts[1] = BLUE + parts[1] + RESET  # Logger Name
            parts[2] = color + parts[2] + RESET  # Level
            # Nachricht selbst farbig bei Warning/Error/Critical
            if record.levelno >= logging.WARNING:
                parts[4] = color + parts[4] + RESET
            if record.levelno == logging.DEBUG:
                parts[3] = GRAY + parts[3] + RESET
        msg = " | ".join(parts)
        return msg


import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[90m",  # Grau
        "INFO": "\033[0m",  # Normal
        "WARNING": "\033[93m",  # Gelb
        "ERROR": "\033[91m",  # Rot
        "CRITICAL": "\033[95m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


def get_logger(
    name,
    log_level=logging.DEBUG,
    log_dir="logs",
    max_bytes=5000 * 1024,
    backup_count=30,
    use_colors=True,
):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger_var = logging.getLogger(name)
    logger_var.setLevel(logging.DEBUG)

    if not logger_var.handlers:
        # Console Handler
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(log_level)
        if use_colors:
            stdout_handler.setFormatter(
                ColoredFormatter(
                    "%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d:%(funcName)s | %(message)s",
                    "%m-%d-%Y %H:%M:%S",
                )
            )
        else:
            stdout_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d:%(funcName)s | %(message)s",
                    "%m-%d-%Y %H:%M:%S",
                )
            )

        # Dateiname pro Tag
        today_str = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"{today_str}_{name}.log")

        # File Handler mit Größenlimit (mehrere pro Tag möglich)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d:%(funcName)s | %(message)s",
                "%m-%d-%Y %H:%M:%S",
            )
        )

        logger_var.addHandler(stdout_handler)
        logger_var.addHandler(file_handler)

    return logger_var


if __name__ == "__main__":
    logger = get_logger("colorTest")
    logger.debug("Debug message.")
    logger.info("Info message.")
    logger.warning("Warning message.")
    logger.error("Error message.")
    logger.critical("Critical message.")
