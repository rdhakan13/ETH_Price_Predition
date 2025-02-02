import os
import yfinance as yf

root_path = Path(__file__).resolve()
while root_path != root_path.parent:
    if (root_path / '.git').exists():
        break
    root_path = root_path.parent
print(root_path)

tickers = ['BTC-USD','ETH-USD','LTC-USD']

class RawDataAPI:
    def __init__(self, root_path, ticker):
        self.root_path = root_path
        self.ticker = ticker

    def get_coin_price_data(self, ticker:str, period:str='max', interval:str='1d'):
        data = yf.download(tickers=ticker, period=period, interval=interval)
        output_dir = "{root_path}\\raw\\{coin}_data".format(root_path=self.root_path,coin=ticker[:3])
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        data.to_csv("{output_dir}\\{ticker}_price_data.csv".format(output_dir=output_dir,ticker=ticker))

    