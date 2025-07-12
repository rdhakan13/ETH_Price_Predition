import os
import logging
import pandas as pd
import yfinance as yf
from src.common.utils import make_directory

logger = logging.getLogger(__name__)


class YahooFinance:
    def __init__(self, ticker: str, root_dir: str):
        """
        Initializes the YahooFinance class with the given ticker symbol.

        Parameters:
            ticker (str): The ticker symbol for which to download data.
            root_dir (str): The root directory of the project.
        """
        if ticker is None or ticker == "" or not isinstance(ticker, str):
            raise ValueError("Ticker symbol must be a non-empty string")
        self.ticker = ticker
        if root_dir is None or root_dir == "" or not isinstance(root_dir, str):
            raise ValueError("Root directory must be a non-empty string")
        self.root_dir = str(root_dir)
        self.raw_dir = str(os.path.join(self.root_dir,'data','raw',f"{self.ticker[:3]}_data"))
        self.raw_data: pd.DataFrame = None
        self.processed_data: pd.DataFrame = None

    def get_raw_data(self, period: str = "max", interval: str = "1d") -> None:
        """
        Downloads historical data for the given ticker symbol from Yahoo Finance and saves it to the raw data directory.

        Parameters:
            period (str): The period for which to download data (default: 'max').
                          Valid periods are '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', and 'max'.
            interval (str): The interval for the data (default: '1d').
                            Valid intervals are '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', and '3mo'.

        Returns:
            None
        """
        logger.info(f"Downloading Yahoo Finance data for {self.ticker}")

        try:
            self.raw_data = yf.download(
                tickers=self.ticker, period=period, interval=interval
            )

            logger.info(f"Data downloaded successfully for {self.ticker}.")
        except Exception as e:
            logger.error(f"Error downloading data for {self.ticker}: {e}")
            raise e

    def save_raw_data(self) -> None:
        """
        Saves the raw data to a CSV file in the raw data directory.

        This method checks if the raw data directory exists, and if not, creates it.
        It then saves the raw data DataFrame to a CSV file named after the ticker symbol.

        Returns:
            None
        """
        make_directory(self.raw_dir)

        self.raw_data.to_csv(str(os.path.join(self.raw_dir,f"{self.ticker}_price_data.csv")))

        logger.info(f"Data saved to {self.raw_dir}")

    def _process_raw_data(self, date_range: pd.date_range) -> pd.DataFrame:
        """
        Processes the raw data and reindexes it to match the provided date range.

        This method reads the raw data CSV file, converts the 'Date' column to datetime,
        reindexes the data to match the provided date range, and returns the processed data.

        Parameters:
            date_range (pd.date_range): The date range to reindex the data.

        Returns:
            pd.DataFrame: The processed data.
        """
        try:
            self.processed_data = pd.read_csv(
                str(os.path.join(self.root_dir,'data','raw',f"{self.ticker[:3]}_data",f"{self.ticker[:3]}-USD_price_data.csv"))
            )
            self.processed_data["Date"] = pd.to_datetime(self.processed_data["Date"])
            self.processed_data = (
                self.processed_data.set_index("Date").reindex(date_range).reset_index()
            )
            self.processed_data.rename(columns={"index": "Date"}, inplace=True)
            return self.processed_data
        except KeyError:
            logger.error("Column not found, switching to different reading mode...")
            self.processed_data = pd.read_csv(
                str(os.path.join(self.root_dir,'data','raw'f"{self.ticker[:3]}_data",f"{self.ticker[:3]}-USD_price_data.csv"))
            )
            self.processed_data.rename(columns={"Price": "Date"}, inplace=True)
            self.processed_data = self.processed_data.iloc[2:]
            self.processed_data["Date"] = pd.to_datetime(self.processed_data["Date"])
            self.processed_data = (
                self.processed_data.set_index("Date").reindex(date_range).reset_index()
            )
            self.processed_data.rename(columns={"index": "Date"}, inplace=True)
            return self.processed_data
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise e

    def get_processed_data(self, date_range: pd.date_range = None) -> pd.DataFrame:
        """
        Processes the raw data and returns the processed data.

        This method processes the raw data by reindexing it to match the provided date range
        and returns the processed data as a pandas DataFrame.

        Parameters:
            date_range (pd.date_range): The date range for which to process the data.

        Returns:
            pd.DataFrame: The processed data.
        """

        logger.info(f"Processing raw data for {self.ticker} from Yahoo Finance.")

        self.processed_data = self._process_raw_data(date_range)

        logger.info(
            f"Data processed successfully for {self.ticker} from Yahoo Finance."
        )
        return self.processed_data
