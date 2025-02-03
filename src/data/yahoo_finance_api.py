"""
Yahoo Finance API Module

This module provides a class to interact with the Yahoo Finance API to download historical data for a given ticker symbol.

Classes:
    YahooFinanceAPI: A class to download and save historical data for a given ticker symbol using the Yahoo Finance API.

Functions:
    get_root_directory: A utility function to get the root directory of the project.

Usage Example:
    from yahoo_finance_api import YahooFinanceAPI

    api = YahooFinanceAPI(ticker='ETH-USD')
    api.get_yf_data()
"""
import os
import logging
import yfinance as yf
from src.utils import get_root_directory

root_dir = get_root_directory()

class yahoo_finance_api:

    def __init__(self, ticker):
        """
        Initializes the YahooFinanceAPI class with the given ticker symbol.

        Args:
            ticker (str): The ticker symbol for which to download data.
        """
        self.ticker = ticker


    def get_yf_data(self, period:str='max', interval:str='1d'):
        """
        Downloads historical data for the given ticker symbol from Yahoo Finance and saves it to the raw data directory.
        """
        logging.info("Downloading Yahoo Finance data for {ticker}".format(ticker=self.ticker))

        data = yf.download(tickers=self.ticker, period=period, interval=interval)

        logging.info("Data downloaded successfully")

        output_dir = "{root_dir}\\data\\raw\\{coin}_data".format(root_dir=root_dir,coin=self.ticker[:3])

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        data.to_csv("{output_dir}\\{ticker}_price_data.csv".format(output_dir=output_dir,ticker=self.ticker))

        logging.info("Data saved to {output_dir}".format(output_dir=output_dir))