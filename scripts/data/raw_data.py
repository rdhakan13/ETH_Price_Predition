import time
import pandas as pd
from src.common.utils import get_root_directory, split_dates_by_year
from src.common.logger import get_logger
from src.data.yahoo_finance import YahooFinance
from src.data.bitinfocharts import BitInfoCharts
from src.data.google_news import GoogleNews

tickers = ['BTC-USD','ETH-USD','LTC-USD']
keywords = ['cryptocurrency','blockchain','bitcoin','ethereum','litecoin']
root_dir = str(get_root_directory())+"\\temp"
logger = get_logger("INFO", __name__)

if __name__ == "__main__":

    start_time = time.time()

    for ticker in tickers:
        yf = YahooFinance(ticker, root_dir)
        yf.get_raw_data()
        yf.save_raw_data()
        bic = BitInfoCharts(ticker, root_dir)
        bic.get_raw_data()
        bic.save_raw_data()

    try:
        data = pd.read_csv(f"{root_dir}\\data\\raw\\ETH_data\\ETH-USD_price_data.csv")
    except FileNotFoundError as e:
        logger.error("File not found")
        raise e
    
    try:
        date_format = "%d/%m/%Y" 
        data["Date"] = pd.to_datetime(data["Date"], format=date_format)
    except KeyError as e:
        logger.error("Column not found")
        raise e

    all_dates = sorted(data["Date"].tolist())

    date_tuples = [(date.year,date.month,date.day) for date in all_dates]

    dates_list = split_dates_by_year(date_tuples)

    for index, year in enumerate(dates_list):
        gn = GoogleNews(root_dir)
        gn.get_raw_data(year[0][0], keywords, dates_list[index])
        gn.save_raw_data()

    end_time = time.time()
    total_runtime = end_time - start_time
    logger.info(f"TOTAL RUNTIME: {total_runtime}s")
    
    
        

