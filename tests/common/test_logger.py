import os
import pytest
import logging
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.common.logger import get_logger, log_config_for_level
from src.common.utils import get_root_directory


def test_log_config_for_level():
    log_level = "DEBUG"
    config = log_config_for_level(log_level)
    assert config["version"] == 1
    assert "formatters" in config
    assert "handlers" in config
    assert "root" in config
    assert config["root"]["level"] == log_level


@patch("src.common.logger.logging.config.dictConfig")
@patch("src.common.logger.logging.getLogger")
def test_get_logger(mock_get_logger, mock_dict_config):
    log_level = "INFO"
    logger_name = "test_logger"
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    logger = get_logger(log_level, logger_name)
    mock_dict_config.assert_called_once()
    mock_get_logger.assert_called_once_with(logger_name)
    assert logger == mock_logger


@patch("src.common.logger.make_directory")
@patch("src.common.logger.get_root_directory")
def test_log_file_creation(mock_get_root_directory, mock_make_directory):
    root_directory = get_root_directory()
    with patch("src.common.logger.datetime") as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = datetime.today().strftime('%Y-%m-%d')
        from src.common.logger import filename
        assert filename == str(os.path.join(str(root_directory), "logs", f"log_{datetime.today().strftime('%Y-%m-%d')}.log"))