from src.data.yahoo_finance_api import yahoo_finance_api
# from src.data.bitinfocharts_api import bitinfocharts_api
from src.data.google_news_api import google_news_api

tickers = ['BTC-USD','ETH-USD','LTC-USD']

if __name__ == "__main__":

    for ticker in tickers:
        yf = yahoo_finance_api(ticker)
        yf.get_yf_data()

    gn = google_news_api()
    dates_list = gn.get_period()
    split_dates_by_year(date_tuples)

    for index, year in enumerate(dates_list):
        extract_gnews_headlines(year, dates_list[index])    
