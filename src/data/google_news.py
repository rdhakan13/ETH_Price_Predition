import os
import logging
import pandas as pd
from tqdm import tqdm
from gnews import GNews
from datetime import datetime, timedelta

class GoogleNews:

    def __init__(self, root_dir:str=None):
        """
        Initializes the GoogleNews class.

        Args:
            root_dir (str): The root directory of the project.
        """
        self.root_dir = str(root_dir)
        self.raw_dir = f"{self.root_dir}\\data\\raw\\Google_News_Headlines_data"
        self.raw_data = None
        self.processed_dir = f"{self.root_dir}\\data\\processed\\Google_News_Headlines_data"
        self.processed_data = None
        self.final_dir = f"{self.root_dir}\\data\\final\\Google_News_Headlines_data"
        self.final_data = None
        self.year = None

    def get_raw_data(self, year, keywords:list=None, dates_list:list=None):
        """
        Extracts Google News headlines for the specified year and keywords.

        Args:
            year (int): The year for which to extract headlines.
            keywords (list): A list of keywords to search for.
            dates_list (list): A list of date tuples (year, month, day) to search within.

        Returns:
            list: A list of extracted news headlines.

        Raises:
            ValueError: If root_dir is not a non-empty string or keywords is not a list of strings.
        """
        data = []

        self.year = str(year)

        if self.root_dir is None or self.root_dir == "" or not isinstance(self.root_dir, str):
            raise ValueError("Root self.raw_dir must be a non-empty string")

        if not keywords or keywords is None or not isinstance(keywords, list):
            raise ValueError("Keywords must be a list of strings")
        
        if not dates_list or dates_list is None or not isinstance(dates_list, list):
            raise ValueError("Dates list must be a list of tuples")

        logging.info(f"Downloading Google News headlines for {self.year}.")

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

        self.raw_data = pd.json_normalize(data)

        logging.info("Data downloaded successfully for {self.year}.")
        
    def save_raw_data(self):
        """
        Saves the raw data to a CSV file in the raw data directory.

        This method checks if the raw data directory exists, and if not, creates it.
        It then saves the raw data DataFrame to a CSV file named after the year of the data.

        Returns:
            None
        """

        if not os.path.exists(self.raw_dir):
            os.makedirs(self.raw_dir)

        self.raw_data.to_csv(f"{self.raw_dir}\\google_news_headlines_data_{self.year}.csv")

        logging.info(f"Data saved to {self.raw_dir}.")

    def process_raw_data(self):
        """
        Processes raw Google News headline files and combines them into a single DataFrame.

        This method reads all CSV files in the raw data directory, processes each file to extract relevant columns,
        renames columns, converts date formats, removes duplicates, and sorts the data by date. The final combined
        DataFrame is then saved to a CSV file in the processed data directory.

        Returns:
            None
        """

        logging.info("Processing Google News Headlines raw data.")

        self.processed_data = pd.DataFrame(columns = ['Date','News Headline','Publisher'])

        for file in os.listdir(self.raw_dir):

            filepath = self.raw_dir + "\\"+ file
            data = pd.read_csv(filepath)
            data_drop = data.drop(columns=['Unnamed: 0','description','url','publisher.href'])
            data_renamed = data_drop.rename(columns={'published date':'Date','title':'News Headline','publisher.title':'Publisher'})
            data_renamed['Date'] = pd.to_datetime(data_renamed['Date'], format='%a, %d %b %Y %H:%M:%S %Z').dt.strftime('%d/%m/%Y')
            data_renamed['Date'] = pd.to_datetime(data_renamed['Date'], format='%d/%m/%Y')
            data_unique = data_renamed.drop_duplicates(subset='News Headline', keep='first')
            self.processed_data = pd.concat([self.processed_data, data_unique], ignore_index=True)
            self.processed_data = self.processed_data.sort_values(by='Date',ascending=True)

        self.processed_data = self.processed_data.drop_duplicates(subset='News Headline', keep='first')

        logging.info("Data processed successfully.")

    def save_processed_data(self):
        """
        Saves the processed data to a CSV file in the processed data directory.

        This method checks if the processed data directory exists, and if not, creates it.
        It then saves the processed data DataFrame to a CSV file.

        Returns:
            None
        """

        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)

        self.processed_data.to_csv(f"{self.processed_dir}\\google_news_headlines_data.csv", index=False)

        logging.info(f"Data saved to {self.processed_dir}.")