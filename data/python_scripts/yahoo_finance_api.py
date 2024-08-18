import os
import yfinance as yf

parent_dir = os.path.dirname(os.getcwd())

tickers = ['BTC-USD','ETH-USD','LTC-USD']

for ticker in tickers:
    data = yf.download(tickers=ticker, period='max', interval='1d')
    data.to_csv("{parent_dir}\\raw_data\\{coin}_data\\{ticker}_price_data.csv".format(parent_dir=parent_dir,coin=ticker[:3],ticker=ticker))
