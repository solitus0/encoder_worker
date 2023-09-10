import logging
from enum import Enum

from worker.config import LOG_LEVEL, LOG_FORMAT


class BaseEnum(str, Enum):
    def __str__(self) -> str:
        return str.__str__(self)


class LogLevels(BaseEnum):
    info = "INFO"
    warn = "WARN"
    error = "ERROR"
    debug = "DEBUG"


def configure_logging():
    log_level = str(LOG_LEVEL).upper()  # cast to string
    log_levels = list(LogLevels)

    if log_level not in log_levels:
        # we use error as the default log level
        logging.basicConfig(level=LogLevels.error)
        return

    if log_level == LogLevels.debug:
        logging.basicConfig(level=log_level, format=LOG_FORMAT)
        return

    logging.basicConfig(level=log_level)
