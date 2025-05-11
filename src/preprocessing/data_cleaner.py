import pandas as pd
import logging
import numpy as np
from src.common.utils import make_directory

logger = logging.getLogger(__name__)


class DataCleaner:
    def __init__(self, root_dir: str, ticker: str, source: list[str]):
        """
        Initialize the data cleaner.

        Parameters:
            root_dir (str): Root directory of the project.
            ticker (str): Ticker of the cryptocurrency.
            source (list): List of sources of the data.
        """
        self.root_dir = root_dir
        self.ticker = ticker
        self.source = source
        self.etherscan: pd.DataFrame = None
        self.oklink: pd.DataFrame = None
        self.bitinfocharts: pd.DataFrame = None
        self.cleaned_data: pd.DataFrame = None

    def read_data(self) -> None:
        """
        Read data from processed folder.

        Returns:
            None
        """
        logger.info("Reading data")
        if "oklink" in self.source:
            try:
                self.oklink = pd.read_csv(
                    f"{self.root_dir}\\data\\processed\\{self.ticker[:3]}_data\\{self.ticker[:3]}_oklink.csv"
                )
            except FileNotFoundError as e:
                logger.error("File not found")
                raise e
        if "bitinfocharts" in self.source:
            try:
                self.bitinfocharts = pd.read_csv(
                    f"{self.root_dir}\\data\\processed\\{self.ticker[:3]}_data\\{self.ticker[:3]}_bitinfocharts.csv"
                )
            except FileNotFoundError as e:
                logger.error("File not found")
                raise e
        if self.ticker[:3] == "ETH" and "etherscan" in self.source:
            try:
                self.etherscan = pd.read_csv(
                    f"{self.root_dir}\\data\\processed\\{self.ticker[:3]}_data\\{self.ticker[:3]}_etherscan.csv"
                )
            except FileNotFoundError as e:
                logger.error("File not found")
                raise e
        if self.etherscan is None or self.oklink is None or self.bitinfocharts is None:
            logger.info("No data read.")
        else:
            logger.info("Data read successfully")

    def identify_nan(self) -> None:
        """
        Identify NaN values in the data.

        Returns:
            None
        """
        logger.info("Identifying NaN values")
        if self.etherscan is not None:
            self.etherscan.replace(np.nan, 0, inplace=True)
            self.etherscan.replace(0, np.nan, inplace=True)
        if self.oklink is not None:
            self.oklink.replace(np.nan, 0, inplace=True)
            self.oklink.replace(0, np.nan, inplace=True)
        if self.bitinfocharts is not None:
            self.bitinfocharts.replace(np.nan, 0, inplace=True)
            self.bitinfocharts.replace(0, np.nan, inplace=True)
        logger.info("NaN values identified")

    def interpolate_clean_data(self, method: str) -> None:
        """
        Interpolate NaN values in the data.

        Parameters:
            method (str): Method to use for interpolation.

        Returns:
            None
        """
        logger.info("Interpolating NaN values using method: " + method)
        if self.cleaned_data is not None:
            if method == "time":
                self.cleaned_data["Date"] = pd.to_datetime(self.cleaned_data["Date"])
                self.cleaned_data = self.cleaned_data.set_index("Date")
            try:
                self.cleaned_data.interpolate(method=method, inplace=True)
                logger.info("NaN values interpolated")
            except NotImplementedError as e:
                logger.error("Invalid method")
                raise e
        else:
            logger.error("No data to interpolate")

    def drop_columns(self, source: str, columns: list[str]) -> None:
        """
        Drop columns from the data.

        Parameters:
            source (str): Source of the data.
            columns (list): Columns to drop.

        Returns:
            None
        """
        logger.info("Dropping columns")
        if source not in ["etherscan", "oklink", "bitinfocharts"]:
            raise ValueError("Invalid source")
        if source == "etherscan":
            columns_to_drop = [col for col in columns if col in self.etherscan.columns]
            try:
                self.etherscan.drop(columns=columns_to_drop, inplace=True)
            except KeyError as e:
                logger.error("Column not found")
                raise e
        if source == "oklink":
            try:
                columns_to_drop = [col for col in columns if col in self.oklink.columns]
                self.oklink.drop(columns=columns_to_drop, inplace=True)
            except KeyError as e:
                logger.error("Column not found")
                raise e
        if source == "bitinfocharts":
            try:
                columns_to_drop = [
                    col for col in columns if col in self.bitinfocharts.columns
                ]
                self.bitinfocharts.drop(columns=columns, inplace=True)
            except KeyError as e:
                logger.error("Column not found")
                raise e
        logger.info("Columns dropped")

    def standardise_columns(self, source: str, column_mapping: dict[str, str]) -> None:
        """
        Standardise columns in the data.

        Parameters:
            source (str): Source of the data.
            column_mapping (dict): Mapping of columns to standardise.

        Returns:
            None
        """
        logger.info("Standardising columns")
        if source == "etherscan":
            self.etherscan.rename(columns=column_mapping, inplace=True)
        elif source == "oklink":
            self.oklink.rename(columns=column_mapping, inplace=True)
        elif source == "bitinfocharts":
            self.bitinfocharts.rename(columns=column_mapping, inplace=True)
        else:
            logger.error("Invalid source")
        logger.info("Columns standardised")

    def merge_sources(self, on: str = "Date") -> None:
        """
        Merge data from different sources.

        Parameters:
            on (str): Column to merge on.

        Returns:
            None
        """
        for i, source in enumerate(self.source):
            if i == 0:
                if source == "etherscan":
                    self.cleaned_data = self.etherscan
                elif source == "oklink":
                    self.cleaned_data = self.oklink
                elif source == "bitinfocharts":
                    self.cleaned_data = self.bitinfocharts
                else:
                    logger.error("Invalid source")
            else:
                if source == "etherscan":
                    self.cleaned_data = pd.merge(
                        self.cleaned_data, self.etherscan, on=on
                    )
                elif source == "oklink":
                    self.cleaned_data = pd.merge(self.cleaned_data, self.oklink, on=on)
                elif source == "bitinfocharts":
                    self.cleaned_data = pd.merge(
                        self.cleaned_data, self.bitinfocharts, on=on
                    )
                else:
                    logger.error("Invalid source")
        logger.info("Data merged")

    def save_clean_data(self, directory: str) -> None:
        """
        Save cleaned data to a CSV file.

        Returns:
            None
        """
        if directory is None:
            directory = f"{self.root_dir}\\data\\final"
        make_directory(directory)
        self.cleaned_data.to_csv(f"{directory}\\{self.ticker[:3]}.csv")
