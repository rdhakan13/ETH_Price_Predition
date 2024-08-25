import os
import yfinance as yf

parent_dir = os.path.dirname(os.getcwd())

tickers = ['BTC-USD','ETH-USD','LTC-USD']

for ticker in tickers:
    data = yf.download(tickers=ticker, period='max', interval='1d')
    output_dir = "{parent_dir}\\raw_data\\{coin}_data".format(parent_dir=parent_dir,coin=ticker[:3])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    data.to_csv("{output_dir}\\{ticker}_price_data.csv".format(output_dir=output_dir,ticker=ticker))
