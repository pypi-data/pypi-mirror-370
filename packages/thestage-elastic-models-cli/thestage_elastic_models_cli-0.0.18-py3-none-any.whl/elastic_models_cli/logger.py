import functools
import logging
import os
import time

# ------------------------------------------------------------------------------------
# Levels, init main library logger
# ------------------------------------------------------------------------------------
_LOGGING_LEVELS_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}

_LOGGER_MAIN = logging.getLogger("ElasticModels")


# ------------------------------------------------------------------------------------
# Logger to split messages for main process and other ranks
# ------------------------------------------------------------------------------------
class ConditionalLogger(logging.Logger):
    _CONDITION = lambda *args: True
    _GUG = 0
    """
    Wraps logger main message methods to be called only in the main process.
    To pass message from each process `debug_all`, `info_all` etc. should be used.

    Parameters
    ----------
    logger: logging.Logger.
    """

    def __init__(self, name: str, level: int = logging.INFO) -> None:
        logging.Logger.__init__(self, name, level)

    def debug(self, msg: str, *args, **kwargs) -> None:
        if ConditionalLogger._CONDITION():
            logging.Logger.debug(self, msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        if ConditionalLogger._CONDITION():
            logging.Logger.info(self, msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        if ConditionalLogger._CONDITION():
            logging.Logger.warning(self, msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        if ConditionalLogger._CONDITION():
            logging.Logger.error(self, msg)

    def debug_all(self, msg: str) -> None:
        logging.Logger.debug(self, msg)

    def info_all(self, msg: str) -> None:
        logging.Logger.info(self, msg)

    def warning_all(self, msg: str) -> None:
        logging.Logger.warning(self, msg)

    def error_all(self, msg: str) -> None:
        logging.Logger.error(self, msg)


# ------------------------------------------------------------------------------------
# Logging utils
# ------------------------------------------------------------------------------------
def _get_std_formatter() -> logging.Formatter:
    """
    Returns logging formatter 'date time: name: level: msg'.
    """
    formatter = logging.Formatter(
        "%(asctime)s" ": %(name)s: %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    return formatter


def _get_console_handler() -> logging.StreamHandler:
    """
    Setups and returns console handler.
    """
    formatter = _get_std_formatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    return handler


def _get_file_handler(
    log_path: str = "./logs", name: str = "log", *, add_timestamp: bool = False
) -> logging.FileHandler:
    """
    Setups and returns file handler.
    """
    formatter = _get_std_formatter()
    os.makedirs(log_path, exist_ok=True)

    log_file_name = name
    if add_timestamp:
        log_file_name = f"{name}_{time.time()}"

    log_file_name = os.path.join(log_path, log_file_name)
    handler = logging.FileHandler(log_file_name)
    handler.setFormatter(formatter)
    _LOGGER_MAIN.debug("File handler created at %s", log_file_name)

    return handler


def _set_console_handler() -> None:
    """
    Set console handler with std formatter.
    """
    global _LOGGER_MAIN

    handler = _get_console_handler()
    _LOGGER_MAIN.addHandler(handler)
    _LOGGER_MAIN.debug("Console handler attached")


def _set_file_handler(
    log_path: str = "./logs", name: str = "log", *, add_timestamp: bool = False
) -> None:
    global _LOGGER_MAIN

    handler = _get_file_handler(log_path, name, add_timestamp=add_timestamp)
    _LOGGER_MAIN.addHandler(handler)
    _LOGGER_MAIN.debug("File handler attached: %s/%s", log_path, name)


def get_logger(name: str) -> logging.Logger:
    """
    Returns child logger from the Elastic Models main logger.

    Parameters
    ----------
    name: str. Best practise is to pass `__name__` of the module.

    Examples
    --------
    from elastic_models.logger import get_logger

    MYLOGGER = get_logger(__name__)
    MYLOGGER.info('Logger was initialized.')
    """
    global _LOGGER_MAIN

    return _LOGGER_MAIN.getChild(name)
    # return DistributedLogger( _LOGGER_MAIN.getChild(name) )


def set_logging_level(level: str = "INFO") -> None:
    """
    Sets logging level for library logger.

    Parameters
    ----------
    level: str. Available: DEBUG, INFO, WARNING, ERROR.

    Examples
    --------
    from elastic_models.logger import set_logging_level

    # By default Elastic Models logger has `INFO` logging level
    MYLOGGER = get_logger(__name__)
    # This message will not be printed, because `INFO` > `DEBUG`
    MYLOGGER.debug('Debug: Logger was initialized.')
    MYLOGGER.info('INFO: Logger was initialized.')

    set_logging_level('DEBUG')
    # Both messages will be printed
    MYLOGGER.debug('Debug: Logger was initialized.')
    MYLOGGER.info('INFO: Logger was initialized.')
    """
    global _LOGGER_MAIN
    global _LOGGING_LEVELS_MAP

    _LOGGER_MAIN.setLevel(_LOGGING_LEVELS_MAP[level])


def set_name(name: str) -> None:
    """ """
    global _LOGGER_MAIN

    _LOGGER_MAIN.name = name


@functools.lru_cache(None)
def warning_once(self, *args, **kwargs):
    """
    This method is identical to `logger.warning()`, but will emit the warning with the same message only once

    Note: The cache is for the function arguments, so 2 different callers using the same arguments will hit the cache.
    The assumption here is that all warning messages are unique across the code. If they aren't then need to switch to
    another type of cache that includes the caller frame information in the hashing function.
    """
    self.warning(*args, **kwargs)


_LOGGER_MAIN.warning_once = warning_once

# set default console handler globally
# logging.setLoggerClass(ConditionalLogger)
# _set_console_handler()
# set_logging_level('INFO')
