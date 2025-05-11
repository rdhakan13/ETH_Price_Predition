import os
import pandas as pd
from src.common.utils import get_root_directory, timeit
from src.common.logger import get_logger
from src.common.config_loader import ConfigLoader
from src.data.yahoo_finance import YahooFinance
from src.data.oklink import OkLink
from src.data.bitinfocharts import BitInfoCharts
from src.data.etherscan import EtherScan
from src.data.google_news import GoogleNews

logger = get_logger(os.environ.get("LOG_LEVEL"), __name__)
root_dir = str(get_root_directory()) + "\\temp"

config_loader = ConfigLoader()
config = config_loader.define_process_raw_data()
active = config.get("active", False)
tickers = config.get("tickers", False)
sources = config.get("sources", [{}])


@timeit
def process_raw_data() -> None:
    """
    Process raw data from Yahoo Finance, BitInfoCharts, OkLink, EtherScan, and Google News.
    """
    source_list = [source.get("name") for source in sources]
    try:
        ETH_data = pd.read_csv(
            f"{root_dir}\\data\\raw\\ETH_data\\ETH-USD_price_data.csv"
        )

        ETH_data["Date"] = pd.to_datetime(ETH_data["Date"])

        date_range = pd.date_range(
            start=ETH_data["Date"].iat[0], end=ETH_data["Date"].iat[-1]
        )
    except KeyError:
        logger.error("Column not found, switching to different reading mode...")
        ETH_data = pd.read_csv(
            f"{root_dir}\\data\\raw\\ETH_data\\ETH-USD_price_data.csv"
        )
        ETH_data = ETH_data.rename(columns={"Price": "Date"})
        ETH_data = ETH_data.iloc[2:]
        ETH_data["Date"] = pd.to_datetime(ETH_data["Date"])
        date_range = pd.date_range(
            start=ETH_data["Date"].iat[0], end=ETH_data["Date"].iat[-1]
        )
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e

    for ticker in tickers:
        yf = YahooFinance(ticker=ticker, root_dir=root_dir)
        data_yf = yf.get_processed_data(date_range=date_range)

        for source in source_list:
            if source == "OkLink":
                ol = OkLink(root_dir=root_dir, ticker=ticker[:3])
                ol.process_raw_data(data_yf=data_yf, date_range=date_range)
                ol.save_processed_data()
            elif source == "BitInfoCharts":
                bic = BitInfoCharts(root_dir=root_dir, ticker=ticker[:3])
                bic.process_raw_data(data_yf=data_yf, date_range=date_range)
                bic.save_processed_data()
            else:
                if ticker[:3] == "ETH" and source == "EtherScan":
                    es = EtherScan(ticker=ticker[:3], root_dir=root_dir)
                    es.process_raw_data(data_yf=data_yf, date_range=date_range)
                    es.save_processed_data()

    if "GoogleNews" in source_list:
        gn = GoogleNews(root_dir=root_dir)
        gn.process_raw_data()
        gn.save_processed_data()


if __name__ == "__main__":
    if active:
        logger.info("Starting raw data processing...")
        process_raw_data()
        logger.info("Raw data processing completed.")
