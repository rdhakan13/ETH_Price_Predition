import pandas as pd
from src.utils import get_root_directory
from src.data.yahoo_finance import YahooFinance
from src.data.oklink import OkLink
from src.data.bitinfocharts import BitInfoCharts
from src.data.etherscan import EtherScan
from src.data.google_news import GoogleNews

tickers = ['BTC-USD','ETH-USD','LTC-USD']
sources = ['oklink','bitinfocharts','etherscan']
root_dir = get_root_directory()

if __name__ == "__main__":

    ETH_data = pd.read_csv(f"{root_dir}\\data\\raw\\ETH_data\\ETH-USD_price_data.csv")

    ETH_data['Date'] = pd.to_datetime(ETH_data['Date'])

    date_range = pd.date_range(start=ETH_data['Date'].iat[0], end=ETH_data['Date'].iat[-1])

    for ticker in tickers:

        yf = YahooFinance(ticker=ticker, root_dir=root_dir)
        data_yf = yf.get_processed_data(date_range=date_range)

        for source in sources:
            if source == 'oklink':
                ol = OkLink(root_dir=root_dir, ticker=ticker[:3])
                ol.process_raw_data(data_yf=data_yf, date_range=date_range)
                ol.save_processed_data()
            elif source == 'bitinfocharts':
                bic = BitInfoCharts(root_dir=root_dir, ticker=ticker[:3])
                bic.process_raw_data(data_yf=data_yf, date_range=date_range)
                bic.save_processed_data()
            else:
                if ticker[:3] == 'ETH':
                    es = EtherScan(ticker=ticker[:3], root_dir=root_dir)
                    es.process_raw_data(data_yf=data_yf, date_range=date_range)
                    es.save_processed_data()

    gn = GoogleNews(root_dir=root_dir)
    gn.process_raw_data()
    gn.save_processed_data()


                    


