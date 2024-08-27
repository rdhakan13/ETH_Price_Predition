import os
import pandas as pd
from tqdm import tqdm
from gnews import GNews
from datetime import datetime, timedelta

parent_dir = os.path.dirname(os.getcwd())

ETH_data = pd.read_csv("{parent_dir}\\raw_data\\ETH_data\\ETH-USD_price_data.csv".format(parent_dir=parent_dir))

ETH_data['Date'] = pd.to_datetime(ETH_data['Date'])

data_start_date = (ETH_data['Date'].iat[0].year, ETH_data['Date'].iat[0].month, ETH_data['Date'].iat[0].day)

data_end_date = (ETH_data['Date'].iat[-1].year, ETH_data['Date'].iat[-1].month, ETH_data['Date'].iat[-1].day)

all_dates = sorted(ETH_data['Date'].tolist())

date_tuples = [(date.year,date.month,date.day) for date in all_dates]

def split_dates_by_year(date_tuples):
    """Split dates by year for batch processing"""
    year_dict = {}
    for date_tuple in date_tuples:
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
    output_dir = f"{parent_dir}\\raw_data\\Google_News_Headlines_data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    data_df.to_csv("{output_dir}\\google_news_headlines_data_{year}.csv".format(output_dir=output_dir,year=year))

dates_list = split_dates_by_year(date_tuples)

for index, year in enumerate(dates_list):
    extract_gnews_headlines(year, dates_list[index])
