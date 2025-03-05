import logging
import logging.config
from datetime import datetime
from src.common.utils import get_root_directory

format_file: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
format_console: str = "%(asctime)s - %(name)s - %(log_color)s%(levelname)s%(reset)s - %(message)s"

date_format: str = "%Y-%m-%d %H:%M:%S"

filename = f"{get_root_directory()}\\logs\\log_{datetime.now().strftime('%Y-%m-%d')}.log"

debug_color:str = "cyan"
info_color:str = "green"
warning_color:str = "yellow"
error_color:str = "red"
critical_color:str = "bold_red"

def log_config_for_level(log_level:str)->dict:
    """
    Get log configuration for the log level.

    Parameters:
        log_level (str): Log level.

    Returns:
        dict: Log configuration.
    """
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
                "formatter": "console",
                "stream": "ext://sys.stdout"
            }
        },
        "root": {
            "handlers": ["file", "console"],
            "level": log_level
            }
        }
   

def get_logger(log_level:str, name:str)->logging.Logger:
    """
    Get logger object.
    
    Parameters:
        log_level (str): Log level.
        name (str): Name of the logger.
    
    Returns:
        logging.Logger: Logger object.
    """
    log_config = log_config_for_level(log_level)
    logging.config.dictConfig(log_config)
    return logging.getLogger(name)
