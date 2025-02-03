import logging
import pandas as pd
from src.utils import get_root_directory, split_dates_by_year
from src.data.yahoo_finance_api import yahoo_finance_api
# from src.data.bitinfocharts_api import bitinfocharts_api
from src.data.google_news_api import google_news_api

tickers = ['BTC-USD','ETH-USD','LTC-USD']
# keywords = ['cryptocurrency','blockchain','bitcoin','ethereum','litecoin']
keywords = []
root_dir = get_root_directory()

if __name__ == "__main__":

    for ticker in tickers:
        yf = yahoo_finance_api(ticker)
        yf.get_yf_data()

    # gn = google_news_api()

    # try:
    #     data = pd.read_csv("{root_dir}\\data\\raw\\ETH_data\\test.csv".format(root_dir=root_dir))
    # except FileNotFoundError as e:
    #     logging.error("File not found")
    #     raise e
    
    # try:
    #     data["Date"] = pd.to_datetime(data["Date"])
    # except KeyError as e:
    #     logging.error("Column not found")
    #     raise e

    # all_dates = sorted(data["Date"].tolist())

    # date_tuples = [(date.year,date.month,date.day) for date in all_dates]

    # dates_list = split_dates_by_year(date_tuples)

    # print (dates_list)

    # for index, year in enumerate(dates_list):
    #     gn.get_gnews_headlines(year, keywords, dates_list[index])    
