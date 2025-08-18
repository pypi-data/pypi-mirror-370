import logging
import os
import sys
from logging import Logger

from dotenv import load_dotenv

FORMATTER = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")


def get_log_level_from_string(level: str):
    match level:
        case "ERROR":
            return logging.ERROR
        case "CRITICAL":
            return logging.CRITICAL
        case "FATAL":
            return logging.FATAL
        case "WARN":
            return logging.WARN
        case "DEBUG":
            return logging.DEBUG
        case _:
            return logging.INFO


def get_logger(name: str) -> Logger:
    """
    Returns an already existing logging.Logger or initializes new one.
    :parameter: name
    :return: initialized logger
    """

    if not logging.getLogger().hasHandlers():
        load_dotenv()
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(FORMATTER)
        logger = logging.getLogger(name)
        logger.addHandler(console_handler)
        logger.setLevel(get_log_level_from_string(os.getenv("LOGGER_LEVEL")))
        return logger
    return logging.getLogger(name)
