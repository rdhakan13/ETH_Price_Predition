import os
import re
import random
import requests 
import pandas as pd
from time import sleep
from fastcore.all import *
from bs4 import BeautifulSoup
from fastprogress import progress_bar
from IPython.display import clear_output

coins = ['BTC','ETH','LTC']
parent_dir = os.path.dirname(os.getcwd())

def parse_strlist(sl):
    """Parse string list"""
    clean = re.sub("[\[\],\s]","",sl)
    splitted = re.split("[\'\"]",clean)
    values_only = [s for s in splitted if s != '']
    return values_only

def get_bitinfochart_graph_values(url, var_name):
  """Get Bitinfochart graph values"""
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
          dataList = parse_strlist(StrList)

  date = []
  value = []
  for each in dataList:
      if (dataList.index(each) % 2) == 0:
          date.append(each)
      else:
          value.append(each)

  df = pd.DataFrame(list(zip(date, value)), columns=["date",var_name])
  return df

def merge_dfs(df_list):
  """Merge dataframes"""
  df_merged = None
  for i in range(len(df_list)-1):
    if i == 0:
      df_merged = df_list[i].merge(df_list[i+1], on='date', how='outer')
    else:
      df_merged = df_merged.merge(df_list[i+1], on='date', how='outer')

  return df_merged

chart_dict_list = [{'url': 'https://bitinfocharts.com/comparison/bitcoin-transactions.html', 'name': 'transactions'},
                    {'url': 'https://bitinfocharts.com/comparison/size-btc.html', 'name': 'block_size'},
                    {'url': 'https://bitinfocharts.com/comparison/bitcoin-difficulty.html', 'name': 'difficulty'},
                    {'url': 'https://bitinfocharts.com/comparison/bitcoin-hashrate.html', 'name': 'hashrate'},
                    {'url': 'https://bitinfocharts.com/comparison/bitcoin-transactionfees.html', 'name': 'av_transaction_size'},
                    {'url': 'https://bitinfocharts.com/comparison/bitcoin-size.html', 'name': 'block_size'},
                    {'url': 'https://bitinfocharts.com/comparison/bitcoin-activeaddresses.html', 'name': 'active_addresses'},
                    ]

url = 'https://bitinfocharts.com'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

coin_dict_list = []

for span in soup.find_all('span'):
  if 's_coins' in str(span.get('class')):
    name = span.get('title').lower()
    coin = span.get('data-coin')
    if coin.upper() in coins:
        coin_dict_list.append({'full_name': name,'coin': coin})

for coin_dict in coin_dict_list:
  coin_dict['scrape_details'] = []
  for chart_dict in chart_dict_list:
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
      coin_df_list.append(get_bitinfochart_graph_values(url=page['url'], var_name=page['name']))
    except:
      empty_df = pd.DataFrame()
      empty_df['full_name'] = coin_dict['full_name']
      empty_df['coin'] = coin_dict['coin']
      coin_df_list.append(pd.DataFrame)
      print(f"Error with {coin_dict['full_name']}")

  coin_df = merge_dfs(coin_df_list)
  coin_df['full_name'] = coin_dict['full_name']
  coin_df['coin'] = coin_dict['coin']

  coin_merged_df_list.append(coin_df)

  clear_output()

  output_dir = "{parent_dir}\\raw_data\\{coin}_data\\bitinfocharts".format(parent_dir=parent_dir,coin=str(coin_dict['coin']).upper())
  if not os.path.exists(output_dir):
      os.makedirs(output_dir)

  file_path = "{output_dir}\\{coin}.csv".format(output_dir=output_dir,coin=str(coin_dict['coin']).upper())
  coin_df.to_csv(file_path)
