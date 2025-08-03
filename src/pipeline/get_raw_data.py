import os
import pandas as pd
from src.common.utils import get_root_directory, split_dates_by_year, timeit
from src.common.logger import get_logger
from src.common.config_loader import ConfigLoader
from src.data.yahoo_finance import YahooFinance
from src.data.bitinfocharts import BitInfoCharts
from src.data.google_news import GoogleNews

logger = get_logger(os.environ.get("LOG_LEVEL"), __name__)
root_dir = str(os.path.join(str(get_root_directory()),'tmp'))

config_loader = ConfigLoader()
config = config_loader.define_get_raw_data()
active = config.get("active", False)
tickers = config.get("tickers", [])
sources = config.get("sources", [{"name": "YahooFinance"}])


@timeit
def get_raw_data() -> None:
    """
    Get raw data from Yahoo Finance, BitInfoCharts, and Google News.
    """
    source_list = [source.get("name") for source in sources]

    for ticker in tickers:
        if "YahooFinance" in source_list:
            yf = YahooFinance(ticker, root_dir)
            yf_params = next(
                (
                    source.get("params", {})
                    for source in sources
                    if source.get("name") == "YahooFinance"
                )
            )
            yf.get_raw_data(**yf_params)
            yf.save_raw_data()
        if "BitInfoCharts" in source_list:
            bic = BitInfoCharts(ticker, root_dir)
            bic.get_raw_data()
            bic.save_raw_data()

    if "GoogleNews" in source_list:
        gn_params = next(
            (
                source.get("params", {})
                for source in sources
                if source.get("name") == "GoogleNews"
            )
        )
        print(gn_params)

        try:
            data = pd.read_csv(
                str(os.path.join(root_dir,'data','raw','ETH_data','ETH-USD_price_data.csv'))
            )
        except FileNotFoundError as e:
            logger.error("File not found")
            raise e

        try:
            data["Date"] = pd.to_datetime(data["Date"])
        except KeyError:
            logger.error("Column not found, switching to different reading mode...")
            data = data.rename(columns={"Price": "Date"})
            data = data.iloc[2:]
            data["Date"] = pd.to_datetime(data["Date"])
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise e

        all_dates = sorted(data["Date"].tolist())

        date_tuples = [(date.year, date.month, date.day) for date in all_dates]

        dates_list = split_dates_by_year(date_tuples)

        for index, year in enumerate(dates_list):
            gn = GoogleNews(root_dir)
            gn.get_raw_data(year=year[0][0], dates_list=dates_list[index], **gn_params)
            gn.save_raw_data()


if __name__ == "__main__":
    if active:
        logger.info("Starting raw data collection...")
        get_raw_data()
        logger.info("Raw data collection completed.")
