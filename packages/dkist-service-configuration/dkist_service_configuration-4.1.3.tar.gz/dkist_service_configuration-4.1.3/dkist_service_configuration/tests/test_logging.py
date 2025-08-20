"""Tests for the logging module"""

import logging

import pytest

from dkist_service_configuration.logging import format_log_level_from_record
from dkist_service_configuration.logging import logger

std_logger = logging.getLogger(__name__)


def test_log_levels():
    logger.trace("trace")
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")


def test_log_levels_std_logger():
    std_logger.debug("debug")
    std_logger.info("info")
    std_logger.warning("warning")
    std_logger.error("error")


@pytest.mark.parametrize(
    "level, expected",
    [
        ("TRACE", 5),
        ("DEBUG", 10),
        ("INFO", 20),
        ("SUCCESS", 25),
        ("WARNING", 30),
        ("ERROR", 40),
        ("CRITICAL", 50),
        ("FOO", 20),
    ],
)
def test_format_log_level_from_record(level: str | int, expected: str | int):
    """Test the format_log_level_from_record function"""
    record = logging.LogRecord(
        name="test",
        level=logging.DEBUG,
        pathname="test.py",
        lineno=1,
        msg="test",
        args=None,
        exc_info=None,
    )
    assert format_log_level_from_record(record) == "DEBUG"
