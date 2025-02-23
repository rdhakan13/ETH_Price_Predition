import logging
import logging.config
import os
from datetime import datetime
from typing import Any, Optional

format_file: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
format_console: str = "%(asctime)s - %(log_color)s%(levelname)s%(reset)s - %(message)s"

date_format: str = "%Y-%m-%d %H:%M:%S"

filename = f"logs/log_{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.log"

debug_color:str = "cyan"
info_color:str = "green"
warning_color:str = "yellow"
error_color:str = "red"
critical_color:str = "bold_red"

def log_config_for_level(log_level:str)->dict(str, Any):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "file": {
                "()":"logging.Formatter",
                "format": format_file,
                "datefmt": date_format
            },
            "console": {
                "format": format_console,
                "datefmt": date_format,
                "()": "colorlog.ColoredFormatter",
                "log_colors": {
                    "DEBUG": debug_color,
                    "INFO": info_color,
                    "WARNING": warning_color,
                    "ERROR": error_color,
                    "CRITICAL": critical_color
                }
            }
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "formatter": "file",
                "filename": filename,
                "mode": "a"
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console"
            }
        },
        "root": {
            "": {
                "handlers": ["file", "console"],
                "level": log_level
            }
        }
    }
   

def setup_logger(log_level:str)->None:
    log_config = log_config_for_level(log_level)
    logging.config.dictConfig(log_config)
    logger = logging.getLogger()