import os
import logging
import pandas as pd
from tqdm import tqdm
from gnews import GNews
from datetime import datetime, timedelta
from src.utils import get_root_directory

root_dir = get_root_directory()

class google_news_api:
    def __init__(self):
        self.date_tuples = None

    def get_period(self):
        logging.info("Getting period for Google News API")
        
        ETH_data = pd.read_csv("{root_dir}\\data\\raw\\ETH_data\\ETH-USD_price_data.csv".format(root_dir=root_dir))
        ETH_data['Date'] = pd.to_datetime(ETH_data['Date'])
        all_dates = sorted(ETH_data['Date'].tolist())
        self.date_tuples = [(date.year,date.month,date.day) for date in all_dates]
        
    def split_dates_by_year(self):
        """Split dates by year for batch processing"""
        year_dict = {}
        for date_tuple in self.date_tuples:
            year = date_tuple[0]
            if year not in year_dict:
                year_dict[year] = []
            year_dict[year].append(date_tuple)
        return list(year_dict.values())

    def extract_gnews_headlines(year, dates_list):
        """Extract Google News headlines"""
        keywords = ['cryptocurrency','blockchain','bitcoin','ethereum','litecoin']
        data = []
        year = str(year)

        for i in tqdm(range(len(dates_list))):
            if i == (len(dates_list)-1):
                date_obj = datetime(year=dates_list[i][0], month=dates_list[i][1], day=dates_list[i][2])
                next_day = date_obj + timedelta(days=1)
                next_day_tuple = (next_day.year, next_day.month, next_day.day)
                google_news = GNews(language='en', start_date=dates_list[i], end_date=next_day_tuple)
            else:
                google_news = GNews(language='en', start_date=dates_list[i], end_date=dates_list[i+1])
            for keyword in keywords:
                data.extend(google_news.get_news(keyword))

        data_df = pd.json_normalize(data)
        output_dir = f"{root_dir}\\data\\raw\\Google_News_Headlines_data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        data_df.to_csv("{output_dir}\\google_news_headlines_data_{year}.csv".format(output_dir=output_dir,year=year))

