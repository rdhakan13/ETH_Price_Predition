from src.utils import get_root_directory
import os
import logging
import yfinance as yf

parent_dir = get_root_directory()

class yahoo_finance_api:

    def __init__(self, ticker):

        self.ticker = ticker


    def get_yf_data(self):

        logging.info("Downloading Yahoo Finance data for {ticker}".format(ticker=self.ticker))

        data = yf.download(tickers=self.ticker, period='max', interval='1d')

        logging.info("Data downloaded successfully")

        output_dir = "{parent_dir}\\data\\raw\\{coin}_data".format(parent_dir=parent_dir,coin=self.ticker[:3])

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        logging.info("Saving data to {output_dir}".format(output_dir=output_dir))

        data.to_csv("{output_dir}\\{ticker}_price_data.csv".format(output_dir=output_dir,ticker=self.ticker))

        logging.info("Data saved successfully")