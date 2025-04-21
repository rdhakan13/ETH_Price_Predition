import os
import logging
import pandas as pd
from src.common.utils import make_directory

logger = logging.getLogger(__name__)


class EtherScan:
    def __init__(self, ticker: str, root_dir: str):
        """
        Initializes the EtherScan class for cleaning and processing data from Etherscan.

        Parameters:
            ticker (str): The ticker symbol for the cryptocurrency (e.g., 'ETH').
            root_dir (str): The root directory of the project.

        Attributes:
            ticker (str): The ticker symbol for the cryptocurrency.
            root_dir (str): The root directory of the project.
            raw_dir (str): The directory containing raw Etherscan data.
            processed_dir (str): The directory to save processed data.
            processed_data (DataFrame): The processed data.
        """
        if ticker is None or ticker == "" or not isinstance(ticker, str):
            raise ValueError("Ticker symbol must be a non-empty string")
        self.ticker = ticker
        if (
            root_dir is None
            or root_dir == ""
            or not isinstance(root_dir, str)
        ):
            raise ValueError("Root directory must be a non-empty string")
        self.ticker = ticker
        self.root_dir = root_dir
        self.raw_dir = f"{self.root_dir}\\data\\raw\\ETH_data\\etherscan\\"
        self.processsed_dir = f"{self.root_dir}\\data\\processed\\ETH_data"
        self.processed_data = None

    def process_raw_data(
        self, data_yf: pd.DataFrame, date_range: pd.date_range)-> None:
        """
        Processes raw data files from Etherscan and merges them with Yahoo Finance data.

        This method reads raw CSV files from the raw data directory, processes each file to extract
        relevant columns, converts date formats, reindexes the data to match the provided date range,
        and merges the processed data with the Yahoo Finance data.

        Parameters:
            data_yf (pd.DataFrame): The Yahoo Finance data to merge with.
            date_range (pd.date_range): The date range to reindex the data.

        Returns:
            None
        """
        if data_yf is None or not isinstance(data_yf, pd.DataFrame):
            raise ValueError("data_yf must be a DataFrame")

        if date_range is None:
            raise ValueError("date_range must be a pd.date_range object")
        
        logger.info("Processing raw data from etherscan.")

        for file in os.listdir(self.raw_dir):
            column_name = " ".join(file.split("-")[1:])[:-4]
            filepath = self.raw_dir + file
            data_etherscan = pd.read_csv(filepath)
            print(data_etherscan.columns)
            data_etherscan["Date(UTC)"] = pd.to_datetime(data_etherscan["Date(UTC)"])
            data_etherscan = (
                data_etherscan.set_index("Date(UTC)").reindex(date_range).reset_index()
            )
            data_etherscan.rename(columns={"index": "Date"}, inplace=True)

            if file == "export-AverageDailyTransactionFee.csv":
                current_column = data_etherscan.columns[3]
                data_etherscan.rename(
                    columns={current_column: column_name}, inplace=True
                )
                data_etherscan = data_etherscan.iloc[:, [0, 3]]

            elif file == "export-DailyActiveEthAddress.csv":
                current_column = data_etherscan.columns[1]
                data_etherscan.rename(
                    columns={current_column: column_name}, inplace=True
                )
                data_etherscan = data_etherscan.iloc[:, [0, 1]]

            else:
                current_column = data_etherscan.columns[2]
                data_etherscan.rename(
                    columns={current_column: column_name}, inplace=True
                )
                data_etherscan = data_etherscan.iloc[:, [0, 2]]

            self.processed_data = data_yf.merge(data_etherscan, on="Date", how="outer")

        logger.info("Data processed successfully for etherscan.")

    def save_processed_data(self)-> None:
        """
        Saves the processed data to a CSV file in the processed data directory.

        This method checks if the processed data directory exists, and if not, creates it.
        It then saves the processed data DataFrame to a CSV file named after the ticker symbol.

        Returns:
            None
        """
        make_directory(self.processsed_dir)

        self.processed_data.to_csv(
            f"{self.processsed_dir}\\{self.ticker[:3]}_etherscan.csv"
        )

        logger.info(f"Data saved to {self.processsed_dir}.")
