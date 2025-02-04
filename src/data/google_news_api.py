"""
Google News API Module

This module provides a class to interact with the Google News API to fetch news articles related to Ethereum.

Classes:
    GoogleNewsAPI: A class to fetch and process news articles using the Google News API.

Functions:
    get_root_directory: A utility function to get the root directory of the project.

Usage Example:
    from google_news_api import GoogleNewsAPI

    api = GoogleNewsAPI()
    headlines = api.get_gnews_headlines(year=2021, keywords=['Ethereum', 'cryptocurrency'], dates_list=[(2021, 1, 1), (2021, 1, 2)])
"""
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
        """
        Initializes the GoogleNewsAPI class.
        """

    def get_gnews_headlines(self, year, keywords:list=None, dates_list:list=None):
        """
        Extract Google News headlines.

        Args:
            year (int): The year for which to extract headlines.
            keywords (list): A list of keywords to search for.
            dates_list (list): A list of date tuples (year, month, day) to search within.

        Returns:
            list: A list of extracted news headlines.
        """
        data = []

        year = str(year)

        if not keywords or keywords is None or not isinstance(keywords, list):
            raise ValueError("Keywords must be a list of strings")
        
        if not dates_list or dates_list is None or not isinstance(dates_list, list):
            raise ValueError("Dates list must be a list of tuples")

        logging.info("Extracting Google News headlines for {year}".format(year=year))

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

        logging.info("Data downloaded successfully")
        
        output_dir = f"{root_dir}\\data\\raw\\Google_News_Headlines_data"

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        data_df.to_csv("{output_dir}\\google_news_headlines_data_{year}_c.csv".format(output_dir=output_dir,year=year))

        logging.info("Google News headlines saved to {output_dir}".format(output_dir=output_dir))