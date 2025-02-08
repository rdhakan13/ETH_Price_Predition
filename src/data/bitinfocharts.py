import os
import re
import random
import logging
import requests 
import pandas as pd
from time import sleep
from fastcore.all import *
from bs4 import BeautifulSoup
from fastprogress import progress_bar

class BitInfoCharts:
   
    def __init__(self, ticker, root_dir:str=None):
        """
        Initializes the BitInfoCharts class for downloading and processing data from Bitinfocharts.

        Args:
            ticker (str): The ticker symbol for the cryptocurrency (e.g., 'BTC', 'ETH').
            root_dir (str): The root directory of the project.

        Attributes:
            ticker (str): The ticker symbol for the cryptocurrency.
            root_dir (str): The root directory of the project.
            raw_dir (str): The directory containing raw Bitinfocharts data.
            raw_data (DataFrame): The raw data.
            processed_dir (str): The directory to save processed data.
            processed_data (DataFrame): The processed data.
            url (str): The base URL for Bitinfocharts.
            chart_dict_list (list): A list of dictionaries containing chart URLs and names.
        """
        self.ticker = ticker
        self.root_dir = str(root_dir)
        self.raw_dir = f"{self.root_dir}\\data\\raw\\{self.ticker[:3]}_data\\bitinfocharts"
        self.raw_data = None
        self.processed_dir = f"{self.root_dir}\\data\\processed\\{self.ticker[:3]}_data"
        self.processed_data = None
        self.url = 'https://bitinfocharts.com'
        self.chart_dict_list = [{'url': 'https://bitinfocharts.com/comparison/bitcoin-transactions.html', 'name': 'transactions'},
                {'url': 'https://bitinfocharts.com/comparison/size-btc.html', 'name': 'block_size'},
                {'url': 'https://bitinfocharts.com/comparison/bitcoin-difficulty.html', 'name': 'difficulty'},
                {'url': 'https://bitinfocharts.com/comparison/bitcoin-hashrate.html', 'name': 'hashrate'},
                {'url': 'https://bitinfocharts.com/comparison/bitcoin-transactionfees.html', 'name': 'av_transaction_size'},
                {'url': 'https://bitinfocharts.com/comparison/bitcoin-size.html', 'name': 'block_size'},
                {'url': 'https://bitinfocharts.com/comparison/bitcoin-activeaddresses.html', 'name': 'active_addresses'},
                ]

    @staticmethod
    def _parse_strlist(sl):
        """
        Parses a string list into a list of strings.

        Args:
            StrList (str): The string list to parse.

        Returns:
            list: A list of strings.
        """
        clean = re.sub("[\[\],\s]","",sl)

        splitted = re.split("[\'\"]",clean)

        values_only = [s for s in splitted if s != '']

        return values_only

    def _get_bitinfochart_graph_values(self, url, var_name):
        """
        Extracts graph values from the Bitinfocharts website for a given URL and variable name.

        This method sends a GET request to the specified URL, parses the HTML response to extract
        the JavaScript data containing the graph values, and processes the data into a pandas DataFrame.

        Args:
            url (str): The URL of the Bitinfocharts page to scrape.
            var_name (str): The variable name to use for the DataFrame column.

        Returns:
            DataFrame: A pandas DataFrame containing the extracted date and value pairs.
        """
        dataList = []
        sleep(random.uniform(0, 1.0))

        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')

        scripts = soup.find_all('script')
        for script in scripts:
            if 'd = new Dygraph(document.getElementById("container")' in script.text:
                StrList = script.text
                StrList = '[[' + StrList.split('[[')[-1]
                StrList = StrList.split(']]')[0] +']]'
                StrList = StrList.replace("new Date(", '').replace(')','')
                dataList = self._parse_strlist(StrList)

        date = []
        value = []
        for each in dataList:
            if (dataList.index(each) % 2) == 0:
                date.append(each)
            else:
                value.append(each)

        df = pd.DataFrame(list(zip(date, value)), columns=["date",var_name])
        return df

    @staticmethod
    def _merge_dfs(df_list):
        """
        Merges a list of DataFrames on the 'date' column.

        Args:
            df_list (list): A list of DataFrames to merge.

        Returns:
            DataFrame: A merged DataFrame.
        """
        df_merged = None
        for i in range(len(df_list)-1):
          if i == 0:
            df_merged = df_list[i].merge(df_list[i+1], on='date', how='outer')
          else:
            df_merged = df_merged.merge(df_list[i+1], on='date', how='outer')

        return df_merged
    
    def get_raw_data(self):
        """
        Downloads raw data from Bitinfocharts for the specified ticker.

        This method sends a GET request to the Bitinfocharts URL, parses the HTML response to extract
        relevant coin information, and constructs URLs for different charts. The extracted data is stored
        in a list of dictionaries, each containing the full name, coin symbol, and chart details.

        Returns:
            None
        """
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')

        coin_dict_list = []

        logging.info(f"Downloading Bitinfocharts data for {self.ticker}.")

        for span in soup.find_all('span'):
          if 's_coins' in str(span.get('class')):
            name = span.get('title').lower()
            coin = span.get('data-coin')
            if coin.upper() in [self.ticker[:3]]:
                coin_dict_list.append({'full_name': name,'coin': coin})

        for coin_dict in coin_dict_list:
          coin_dict['scrape_details'] = []
          for chart_dict in self.chart_dict_list:
            temp_dict = chart_dict.copy()
            url = temp_dict['url']
            url = url.replace('bitcoin', coin_dict['full_name'])
            url = url.replace('btc', coin_dict['coin'])
            url = url.replace(' ', '%20')
            temp_dict['url'] = url
            coin_dict['scrape_details'].append(temp_dict)

        coin_merged_df_list = []

        for coin_dict in progress_bar(coin_dict_list[:4]):
          print(f"Processing - {coin_dict['full_name']}")
          coin_df_list = []
          for page in progress_bar(coin_dict['scrape_details']):
            try:
              coin_df_list.append(self._get_bitinfochart_graph_values(url=page['url'], var_name=page['name']))
            except Exception as e:
              empty_df = pd.DataFrame()
              empty_df['full_name'] = coin_dict['full_name']
              empty_df['coin'] = coin_dict['coin']
              coin_df_list.append(pd.DataFrame)
              print(f"Error with {coin_dict['full_name']}: {e}")

          self.raw_data = self._merge_dfs(coin_df_list)
          self.raw_data['full_name'] = coin_dict['full_name']
          self.raw_data['coin'] = coin_dict['coin']

          coin_merged_df_list.append(self.raw_data)

        logging.info(f"Data downloaded successfully for {self.ticker}.")
      
    def save_raw_data(self):
        """
        Saves the raw data to a CSV file in the raw data directory.

        This method checks if the raw data directory exists, and if not, creates it.
        It then saves the raw data DataFrame to a CSV file named after the ticker symbol.

        Returns:
            None
        """
        if not os.path.exists(self.raw_dir):
            os.makedirs(self.raw_dir)

        self.raw_data.to_csv(f"{self.raw_dir}\\{self.ticker[:3]}.csv")

        logging.info(f"Data saved to {self.raw_dir}.")

    def process_raw_data(self, data_yf:pd.DataFrame=None, date_range:pd.date_range=None):
        """
        Processes raw data from Bitinfocharts and merges it with Yahoo Finance data.

        This method reads the raw data CSV file, converts the 'date' column to datetime,
        reindexes the data to match the provided date range, renames columns, and merges
        the processed data with the Yahoo Finance data.

        Args:
            data_yf (pd.DataFrame): The Yahoo Finance data to merge with.
            date_range (pd.date_range): The date range to reindex the data.

        Returns:
            None
        """
        logging.info(f"Processing raw data from {self.ticker[:3]} for Bitinfocharts.")

        data_bic = pd.read_csv(f"{self.raw_dir}\\{self.ticker[:3]}.csv")
        data_bic['date'] = pd.to_datetime(data_bic['date'])
        data_bic = data_bic.set_index('date').reindex(date_range).reset_index()
        data_bic.rename(columns={'index': 'Date','transactions':'Transactions','block_size_x':'Block Size','difficulty':'Difficulty',
                            'hashrate':'Hashrate','active_addresses':'Active Addressses'}, inplace=True)
        data_bic.drop(columns=['Unnamed: 0','block_size_y','av_transaction_size','full_name','coin'], inplace=True)
        self.processed_data = data_yf.merge(data_bic, on='Date', how='outer')

        logging.info(f"Data processed successfully for {self.ticker[:3]} from Bitinfocharts.")

    def save_processed_data(self):
        """
        Saves the processed data to a CSV file in the processed data directory.

        This method checks if the processed data directory exists, and if not, creates it.
        It then saves the processed data DataFrame to a CSV file named after the ticker symbol.

        Returns:
            None
        """
        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)

        self.processed_data.to_csv(f"{self.processed_dir}\\{self.ticker[:3]}_bitinfocharts.csv", index=False)

        logging.info(f"Data saved successfully to {self.processed_dir}.")
