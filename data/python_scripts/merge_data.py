#%%
import os
import pandas as pd
# %%
coins = ['BTC']]
parent_dir = os.path.dirname(os.getcwd())
ETH_data = pd.read_csv("{parent_dir}\\raw_data\\ETH-USD_price_data.csv".format(parent_dir=parent_dir))
ETH_data['Date'] = pd.to_datetime(ETH_data['Date'])



#%%
directory = "{parent_dir}\\raw_data\\Google_News_Headlines_data\\".format(parent_dir=parent_dir)
final_data = pd.DataFrame(columns = ['Date','News Headline','Publisher'])

for file in os.listdir(directory):
    if file.endswith('.csv'):
        filepath = directory + file
    data = pd.read_csv(filepath)
    data_drop = data.drop(columns=['Unnamed: 0','description','url','publisher.href'])
    data_renamed = data_drop.rename(columns={'published date':'Date','title':'News Headline','publisher.title':'Publisher'})
    data_renamed['Date'] = pd.to_datetime(data_renamed['Date'], format='%a, %d %b %Y %H:%M:%S %Z').dt.strftime('%d/%m/%Y')
    data_renamed['Date'] = pd.to_datetime(data_renamed['Date'], format='%d/%m/%Y')
    data_unique = data_renamed.drop_duplicates(subset='News Headline', keep='first')
    final_data = pd.concat([final_data, data_unique], ignore_index=True)
    final_data = final_data.sort_values(by='Date',ascending=True)

final_data_unique = final_data.drop_duplicates(subset='News Headline', keep='first')

final_data_unique.to_csv("{parent_dir}\\cleaned_data\\Google_News_Headlines_data\\google_news_headlines_data.csv".format(parent_dir=parent_dir), index=False)
# %%
