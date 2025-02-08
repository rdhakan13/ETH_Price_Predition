import os
import logging
import pandas as pd
import yfinance as yf

class YahooFinance:

    def __init__(self, ticker:str=None, root_dir:str=None):
        """
        Initializes the YahooFinance class with the given ticker symbol.

        Args:
            ticker (str): The ticker symbol for which to download data.
            root_dir (str): The root directory of the project.

        Attributes:
            ticker (str): The ticker symbol for the cryptocurrency.
            root_dir (str): The root directory of the project.
            raw_dir (str): The directory containing raw Yahoo Finance data.
            raw_data (DataFrame): The raw data.
            processed_data (DataFrame): The processed data.
        """
        self.ticker = ticker
        self.root_dir = str(root_dir)
        self.raw_dir = f"{self.root_dir}\\data\\raw\\{self.ticker[:3]}_data"
        self.raw_data = None
        self.processed_data = None

    def get_raw_data(self, period:str='max', interval:str='1d'):
        """
        Downloads historical data for the given ticker symbol from Yahoo Finance and saves it to the raw data directory.

        Args:
            period (str): The period for which to download data (default: 'max').
                          Valid periods are '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', and 'max'.
            interval (str): The interval for the data (default: '1d').
                            Valid intervals are '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', and '3mo'.

        Returns:
            None
        """
        if self.ticker is None or self.ticker == "" or not isinstance(self.ticker, str):
            raise ValueError("Ticker symbol must be a non-empty string")

        if self.root_dir is None or self.root_dir == "" or not isinstance(self.root_dir, str):
            raise ValueError("Root directory must be a non-empty string")

        logging.info(f"Downloading Yahoo Finance data for {self.ticker}")

        self.raw_data = yf.download(tickers=self.ticker, period=period, interval=interval)

        logging.info(f"Data downloaded successfully for {self.ticker}.")

    def save_raw_data(self):
        """
        Saves the raw data to a CSV file in the raw data directory.

        This method checks if the raw data directory exists, and if not, creates it.
        It then saves the raw data DataFrame to a CSV file named after the ticker symbol.

        Returns:
            None
        """
        if not os.path.exists(self.raw_dir):
            os.makedirs(self.raw_dir)

        self.raw_data.to_csv(f"{self.raw_dir}\\{self.ticker}_price_data.csv")

        logging.info(f"Data saved to {self.raw_dir}")

    def _process_raw_data(self, date_range:pd.date_range=None):
        """
        Processes the raw data and reindexes it to match the provided date range.

        This method reads the raw data CSV file, converts the 'Date' column to datetime,
        reindexes the data to match the provided date range, and returns the processed data.

        Args:
            date_range (pd.date_range): The date range to reindex the data.

        Returns:
            pd.DataFrame: The processed data.
        """
        self.processed_data = pd.read_csv(f"{self.root_dir}\\data\\raw\\{self.ticker[:3]}_data\\{self.ticker[:3]}-USD_price_data.csv")
        self.processed_data['Date'] = pd.to_datetime(self.processed_data['Date'])
        self.processed_data = self.processed_data.set_index('Date').reindex(date_range).reset_index()
        self.processed_data.rename(columns={'index': 'Date'}, inplace=True)
        return self.processed_data
    
    def get_processed_data(self, date_range:pd.date_range=None):
        """
        Processes the raw data and returns the processed data.

        This method processes the raw data by reindexing it to match the provided date range
        and returns the processed data as a pandas DataFrame.

        Args:
            date_range (pd.date_range): The date range for which to process the data.

        Returns:
            pd.DataFrame: The processed data.
        """

        logging.info(f"Processing raw data for {self.ticker} from Yahoo Finance.")

        self.processed_data = self._process_raw_data(date_range)

        logging.info(f"Data processed successfully for {self.ticker} from Yahoo Finance.")

        return self.processed_data