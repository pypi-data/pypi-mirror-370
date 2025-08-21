# coding: utf-8

import logging
import logging.config
import inspect


CONSOLE_LOGGER_NAME = "ConsoleLogger"
DEFAULT_LOGGER_NAME = CONSOLE_LOGGER_NAME


class LogsCustomConfig(object):
    default_logger: str


def init_logging(config: dict = None) -> None:
    if config:
        logging.config.dictConfig(config)
    LogsCustomConfig.default_logger = config.get("default_logger", DEFAULT_LOGGER_NAME)


def get_caller_name(idx: int = 2) -> str:
    stk = inspect.stack()
    
    if len(stk) < idx:
        frm = inspect.stack()[2]
        mod = inspect.getmodule(frm[0])
        return mod.__name__
    
    return __name__


# Method used to log
# Log engine is configured throught the config.yaml application file
# Users can add different logger to different outputs or different formats
# To log a msg just use log("msg")
# You can add parameters to configure where and how to log
# params:
#   - logger_name: Logger configured in config, for exemple : "ConsoleLogger"
#           default: "ConsoleLogger"
#   - logger_level: Logger Debug Level. Can be : "DEBUG", "INFO", "ERROR", "WARNING", "CRITICAL" or ints or lowercases
#           default: "info"
#   - *args and **kwargs forwarded to python logger engine

def log(msg: str, *args, **kwargs) -> None:
    logger_name = LogsCustomConfig.default_logger
    logger_level = "info"

    if "logger_name" in kwargs.keys():
        logger_name = kwargs["logger_name"]
        del kwargs["logger_name"]
    if "logger_level" in kwargs.keys():
        logger_level = kwargs["logger_level"]
        del kwargs["logger_level"]
        
    logger = logging.getLogger(logger_name)

    logger_func = logger.info
    if logger_level in [0, "DEBUG", "debug"]:
        logger_func = logger.debug
    elif logger_level in [1, "INFO", "info"]:
        logger_func = logger.info
    elif logger_level in [2, "WARNING", "warning"]:
        logger_func = logger.warning
    elif logger_level in [3, "ERROR", "error"]:
        logger_func = logger.error
    elif logger_level in [4, "CRITICAL", "critical"]:
        logger_func = logger.critical

    logger_func(msg, *args, **kwargs)
