import os
import yaml
import logging
from typing import Any
from src.common.utils import get_root_directory, find_file

logger = logging.getLogger(__name__)


class ConfigLoader:
    def __init__(self) -> None:
        """
        Initializes the ConfigLoader class.
        Sets the config_filename attribute based on the environment variable CONFIG_FILENAME.
        If the environment variable is not set, it defaults to a template configuration file.
        """
        if os.environ.get("CONFIG_FILENAME") is None:
            self.config_filename = str(os.path.join(get_root_directory(), "configs", "pipeline_template.yml"))
        else:
            self.config_filename = find_file(os.environ.get("CONFIG_FILENAME"))
        self.config = self.load_config()

    def load_config(self) -> dict[str, Any]:
        """
        Loads the configuration file and returns the configuration as a dictionary.

        Parameters:
            None

        Returns:
            dict: The loaded configuration.
        """
        try:
            with open(self.config_filename, "r") as file:
                config = yaml.safe_load(file)
            logger.info(f"Config file loaded successfully: {self.config_filename}")
            return config
        except Exception as e:
            logger.error(f"Error loading config file {self.config_filename}: {e}")
            raise e

    def define_get_raw_data(self) -> dict[str, Any]:
        """
        Defines the configuration for the "get_raw_data" stage of the pipeline.

        Parameters:
            None

        Returns:
            dict: The configuration for the "get_raw_data" stage.
        """
        get_raw_data_config = [
            stage
            for stage in self.config.get("pipeline", {})
            if stage.get("stage") == "get_raw_data"
        ]
        if not get_raw_data_config:
            get_raw_data_config = [{}]
        else:
            if (
                get_raw_data_config[0].get("tickers") is None
                and get_raw_data_config[0].get("active") is True
            ):
                logger.error("Tickers not found in config file")
                raise ValueError("Tickers not found in config file.")
        return get_raw_data_config[0]

    def define_process_raw_data(self) -> dict[str, Any]:
        """
        Defines the configuration for the "process_raw_data" stage of the pipeline.

        Parameters:
            None

        Returns:
            dict: The configuration for the "process_raw_data" stage.
        """
        process_raw_data_config = [
            stage
            for stage in self.config.get("pipeline", {})
            if stage.get("stage") == "process_raw_data"
        ]
        if not process_raw_data_config:
            process_raw_data_config = [{}]
        else:
            if (
                process_raw_data_config[0].get("tickers") is None
                and process_raw_data_config[0].get("active") is True
            ):
                logger.error("Tickers not found in config file")
                raise ValueError("Tickers not found in config file.")
        return process_raw_data_config[0]

    def define_conduct_sentiment_analysis(self) -> dict[str, Any]:
        """
        Defines the configuration for the "conduct_sentiment_analysis" stage of the pipeline.

        Parameters:
            None

        Returns:
            dict: The configuration for the "conduct_sentiment_analysis" stage.
        """
        conduct_sentiment_analysis_config = [
            stage
            for stage in self.config.get("pipeline", {})
            if stage.get("stage") == "conduct_sentiment_analysis"
        ]
        if not conduct_sentiment_analysis_config:
            conduct_sentiment_analysis_config = [{}]
        else:
            if (
                conduct_sentiment_analysis_config[0].get("sources") is None
                and conduct_sentiment_analysis_config[0].get("active") is True
            ):
                logger.error("Sources not found in config file")
                raise ValueError("Sources not found in config file.")
        return conduct_sentiment_analysis_config[0]

    def define_compile_final_data(self) -> dict[str, Any]:
        """
        Defines the configuration for the "compile_final_data" stage of the pipeline.

        Parameters:
            None

        Returns:
            dict: The configuration for the "compile_final_data" stage.
        """
        compile_final_data_config = [
            stage
            for stage in self.config.get("pipeline", {})
            if stage.get("stage") == "compile_final_data"
        ]
        if not compile_final_data_config:
            compile_final_data_config = [{}]
        
        return compile_final_data_config[0]

    def define_column_mapping(self) -> dict[str, str]:
        """
        Defines the column mapping.

        Parameters:
            None

        Returns:
            dict: The column mapping.
        """
        column_mapping = self.config.get("column_mapping", {})
        if not column_mapping:
            logger.error("Column mapping not found in config file")
            raise ValueError("Column mapping not found in config file.")
        return column_mapping

    # TODO
    def define_run_model(self) -> None:
        pass

    # TODO
    def define_get_results(self) -> None:
        pass
