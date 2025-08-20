"""
Standard logging configuration for which intercepts standard logger messages from imported
libraries to emit through the loguru handler.  Must be the first import on the entry point to
ensure the first execution of the standard library logger basicConfig method
"""

import logging
from sys import stderr

from loguru import logger

__all__ = ["logger"]

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class LogConfiguration(BaseSettings):
    """"""

    log_level: str = Field(default="DEBUG", validation_alias="LOGURU_LEVEL")
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    log_level_name_int_map: dict[str, int] = Field(
        default={
            "TRACE": 5,
            "DEBUG": 10,
            "INFO": 20,
            "SUCCESS": 25,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50,
        }
    )

    @property
    def log_level_int(self):
        return self.log_level_name_int_map.get(self.log_level, 20)

    @property
    def is_better_exceptions_active(self):
        return self.log_level_int <= 10


logger_config = LogConfiguration()

# Remove the default stderr handler
logger.remove()

# Add back the stderr handler with the 'diagnose' flag set
logger.add(
    stderr, level=logger_config.log_level, diagnose=logger_config.is_better_exceptions_active
)


def format_log_level_from_record(record: logging.LogRecord) -> int | str:
    """Log name to support formatting if known, otherwise use the level number"""
    log_level_int_name_map = {v: k for k, v in logger_config.log_level_name_int_map.items()}
    return log_level_int_name_map.get(record.levelno, 20)


class InterceptHandler(logging.Handler):
    """
    Handler to route stdlib logs to loguru
    """

    def emit(self, record: logging.LogRecord):
        # Retrieve context where the logging call occurred, this happens to be in the 6th frame upward
        logger_opt = logger.opt(depth=6, exception=record.exc_info)  # pragma: no cover
        logger_opt.log(
            format_log_level_from_record(record), record.getMessage()
        )  # pragma: no cover


# Configuration for stdlib logger to route messages to loguru; must be run before other imports
logging.basicConfig(handlers=[InterceptHandler()], level=logger_config.log_level_int)
