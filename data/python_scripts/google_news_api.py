import os
import json
import pandas as pd
from tqdm import tqdm
from gnews import GNews
from datetime import datetime, timedelta

# parent directory set
parent_dir = os.path.dirname(os.getcwd())
ETH_data = pd.read_csv("{parent_dir}\\raw_data\\ETH-USD_price_data.csv".format(parent_dir=parent_dir))
ETH_data['Date'] = pd.to_datetime(ETH_data['Date'])

# start and end dates of the dataset
data_start_date = (ETH_data['Date'].iat[0].year, ETH_data['Date'].iat[0].month, ETH_data['Date'].iat[0].day)
data_end_date = (ETH_data['Date'].iat[-1].year, ETH_data['Date'].iat[-1].month, ETH_data['Date'].iat[-1].day)

# list of years in the dataset
list_of_years = list(range(ETH_data['Date'].iat[0].year, ETH_data['Date'].iat[-1].year+1))

# list of dates in the dataset
iter_dates = sorted(ETH_data['Date'].tolist())
# list of tuples of dates in the dataset
date_tuples = [(date.year,date.month,date.day) for date in iter_dates]

# function to split dates by year for batch processing
def split_dates_by_year(date_tuples):
    year_dict = {}
    for date_tuple in date_tuples:
        year = date_tuple[0]
        if year not in year_dict:
            year_dict[year] = []
        year_dict[year].append(date_tuple)
    return list(year_dict.values())

# function to extract Google News headlines
def extract_gnews_headlines(year, iter_dates_list):
    keywords = ['cryptocurrency','blockchain','bitcoin','ethereum','litecoin']
    data = []
    year = str(year)
    for i in tqdm(range(len(iter_dates_list))):
        if i == (len(iter_dates_list)-1):
            date_obj = datetime(year=iter_dates_list[i][0], month=iter_dates_list[i][1], day=iter_dates_list[i][2])
            next_day = date_obj + timedelta(days=1)
            next_day_tuple = (next_day.year, next_day.month, next_day.day)
            google_news = GNews(language='en', start_date=iter_dates_list[i], end_date=next_day_tuple)
        else:
            google_news = GNews(language='en', start_date=iter_dates_list[i], end_date=iter_dates_list[i+1])
        for keyword in keywords:
            data.extend(google_news.get_news(keyword))
    data_df = pd.json_normalize(data)
    data_df.to_csv("{parent_dir}\\raw_data\\Google_News_Headlines_data\\google_news_headlines_data_{year}.csv".format(parent_dir=parent_dir,year=year))

# split dates by year
iter_dates_list = split_dates_by_year(date_tuples)

# extract Google News headlines
for index, year in enumerate(iter_dates_list):
    extract_gnews_headlines(year, iter_dates_list[index])
