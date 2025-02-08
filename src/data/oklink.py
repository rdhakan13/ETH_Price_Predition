import os
import pandas as pd
import logging

class OkLink:
    def __init__(self, root_dir:str=None, ticker:str=None):
        """
        Initializes the OkLink class for processing data from OkLink.

        Args:
            root_dir (str): The root directory of the project.
            ticker (str): The ticker symbol for the cryptocurrency (e.g., 'ETH').

        Attributes:
            ticker (str): The ticker symbol for the cryptocurrency.
            raw_dir (str): The directory containing raw OkLink data.
            raw_data (DataFrame): The raw data.
            processed_dir (str): The directory to save processed data.
            processed_data (DataFrame): The processed data.
        """
        self.ticker = ticker
        self.raw_dir = f"{root_dir}\\data\\raw\\{ticker}_data\\oklink"
        self.raw_data = None
        self.processed_dir = f"{root_dir}\\data\\processed\\{ticker}_data"
        self.processed_data = None

    def process_raw_data(self, data_yf:pd.DataFrame=None, date_range:pd.date_range=None):
        """
        Processes raw data files from OkLink and merges them with Yahoo Finance data.

        This method reads raw CSV files from the raw data directory, processes each file to extract
        relevant columns, converts date formats, reindexes the data to match the provided date range,
        and merges the processed data with the Yahoo Finance data.

        Args:
            data_yf (pd.DataFrame): The Yahoo Finance data to merge with.
            date_range (pd.date_range): The date range to reindex the data.

        Returns:
            None
        """
        if data_yf is None or not isinstance(data_yf, pd.DataFrame):
            raise ValueError("data_yf must be a DataFrame")
        
        if date_range is None:
            raise ValueError("date_range must be a pd.date_range object")

        logging.info(f"Processing raw data from {self.ticker} for OkLink")

        for file in os.listdir(self.raw_dir):
            filepath = self.raw_dir + "\\" + file
            data_oklink = pd.read_csv(filepath)
            data_oklink['Time'] = pd.to_datetime(data_oklink['Time'])
            data_oklink = data_oklink.set_index('Time').reindex(date_range).reset_index()
            data_oklink.rename(columns={'index': 'Date'}, inplace=True)
            data_oklink = data_oklink.iloc[:,:2]
            data_oklink = data_yf.merge(data_oklink, on='Date', how='outer')

        self.processed_data = data_oklink
        logging.info(f"Data processed successfully for {self.ticker} from OkLink")

    def save_processed_data(self):
        """
        Saves the processed data to a CSV file in the processed data directory.

        This method checks if the processed data directory exists, and if not, creates it.
        It then saves the processed data DataFrame to a CSV file named after the ticker symbol.

        Returns:
            None
        """
        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)

        self.processed_data.to_csv(f"{self.processed_dir}\\{self.ticker}_oklink.csv", index=False)

        logging.info(f"Data saved successfully to {self.processed_dir}")