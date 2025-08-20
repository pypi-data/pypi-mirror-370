import logging
import pytest
from unittest.mock import patch, mock_open
from liveramp_automation.utils.log import LoggerUtils, MyFormatter, Logger


def test_log_info():
    Logger.info("info")


def test_log_critical():
    Logger.critical("critical")


def test_log_error():
    Logger.error("Error")


def test_log_debug():
    Logger.debug("Debug")


def test_log_warning():
    Logger.warning("warning")


def test_get_logger_returns_same_instance():
    logger_utils = LoggerUtils()
    logger1 = logger_utils.get_logger()
    logger2 = logger_utils.get_logger()
    assert logger1 == logger2


def test_configure_logging_returns_logger_instance():
    logger_utils = LoggerUtils()
    logger = logger_utils._configure_logging()
    assert isinstance(logger, logging.Logger)


def test_get_log_format_returns_my_formatter_when_scenario_included(monkeypatch):
    logger_utils = LoggerUtils()
    monkeypatch.setenv("SCENARIO_NAME", "test_scenario")
    log_format = logger_utils.get_log_format("true")
    assert isinstance(log_format, MyFormatter)
    assert "test_case_name" in log_format._fmt


def test_get_log_format_returns_default_formatter_when_scenario_not_included(monkeypatch):
    logger_utils = LoggerUtils()
    monkeypatch.delenv("SCENARIO_NAME", raising=False)
    log_format = logger_utils.get_log_format("false")
    assert isinstance(log_format, logging.Formatter)
    assert "test_case_name" not in log_format._fmt


def test_logger_utils_get_log_format_invalid_value():
    with pytest.raises(ValueError):
        LoggerUtils.get_log_format('invalid')


def test_configure_logging_file_property_not_found():
    with patch('builtins.open', mock_open(read_data="[data]")):
        logger_utils = LoggerUtils()
        logger = logger_utils._configure_logging()
        assert isinstance(logger, logging.Logger)
