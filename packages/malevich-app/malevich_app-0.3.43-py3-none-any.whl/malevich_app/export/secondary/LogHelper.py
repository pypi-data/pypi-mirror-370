import logging
from enum import Enum
from malevich_app.export.secondary.const import LOG_SEPARATOR

log_on = True


class LogLevel(Enum):
    error = lambda logger, msg: logger.error(msg)
    warning = lambda logger, msg: logger.warning(msg)
    info = lambda logger, msg: logger.info(msg)
    debug = lambda logger, msg: logger.debug(msg)


def __log(msg, level: LogLevel=LogLevel.info, logger=logging):
    if log_on:
        level(logger, str(msg).replace('\n', LOG_SEPARATOR))


def log_info(msg, logger=logging):
    __log(msg, level=LogLevel.info, logger=logger)


def log_warn(msg, logger=logging):
    __log(msg, level=LogLevel.warning, logger=logger)


def log_error(msg, logger=logging):
    __log(msg, level=LogLevel.error, logger=logger)


def log_debug(msg, logger=logging):
    __log(msg, level=LogLevel.debug, logger=logger)
