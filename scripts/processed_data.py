#%%
import os
import pandas as pd
from datetime import datetime, timedelta
# %%
coins = ['BTC','ETH','LTC']
sources = ['oklink','bitinfocharts','etherscan']
parent_dir = os.path.dirname(os.getcwd())
ETH_data = pd.read_csv("{parent_dir}\\raw_data\\ETH_data\\ETH-USD_price_data.csv".format(parent_dir=parent_dir))
ETH_data['Date'] = pd.to_datetime(ETH_data['Date'])
date_range = pd.date_range(start=ETH_data['Date'].iat[0], end=ETH_data['Date'].iat[-1])

for coin in coins:
    for source in sources:
        data_yf = pd.read_csv("{parent_dir}\\raw_data\\{coin}_data\\{coin}-USD_price_data.csv".format(parent_dir=parent_dir,coin=coin))
        data_yf['Date'] = pd.to_datetime(data_yf['Date'])
        data_yf = data_yf.set_index('Date').reindex(date_range).reset_index()
        data_yf.rename(columns={'index': 'Date'}, inplace=True)
        if source == 'oklink':
            directory = "{parent_dir}\\raw_data\\{coin}_data\\{source}\\".format(parent_dir=parent_dir, coin=coin, source=source)
            for file in os.listdir(directory):
                filepath = directory + file
                data_oklink = pd.read_csv(filepath)
                data_oklink['Time'] = pd.to_datetime(data_oklink['Time'])
                data_oklink = data_oklink.set_index('Time').reindex(date_range).reset_index()
                data_oklink.rename(columns={'index': 'Date'}, inplace=True)
                data_oklink = data_oklink.iloc[:,:2]
                data_yf = data_yf.merge(data_oklink, on='Date', how='outer')
            output_dir = "{parent_dir}\\cleaned_data\\{coin}_data".format(parent_dir=parent_dir,coin=coin)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            data_yf.to_csv("{output_dir}\\{coin}_{source}.csv".format(output_dir=output_dir,coin=coin,source=source), index=False)
        elif source == 'bitinfocharts':
            data_bic = pd.read_csv("{parent_dir}\\raw_data\\{coin}_data\\{source}\\{coin}.csv".format(parent_dir=parent_dir,coin=coin, source=source))
            data_bic['date'] = pd.to_datetime(data_bic['date'])
            data_bic = data_bic.set_index('date').reindex(date_range).reset_index()
            data_bic.rename(columns={'index': 'Date','transactions':'Transactions','block_size_x':'Block Size','difficulty':'Difficulty',
                                'hashrate':'Hashrate','active_addresses':'Active Addressses'}, inplace=True)
            data_bic.drop(columns=['Unnamed: 0','block_size_y','av_transaction_size','full_name','coin'], inplace=True)
            merged_data = data_yf.merge(data_bic, on='Date', how='outer')
            output_dir = "{parent_dir}\\cleaned_data\\{coin}_data".format(parent_dir=parent_dir,coin=coin)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            merged_data.to_csv("{output_dir}\\{coin}_{source}.csv".format(output_dir=output_dir,coin=coin, source=source), index=False)
        else:
            if coin == 'ETH':
                directory = "{parent_dir}\\raw_data\\{coin}_data\\{source}\\".format(parent_dir=parent_dir, coin=coin, source=source)
                for file in os.listdir(directory):
                    print(file)
                    column_name = ' '.join(file.split('-')[1:])[:-4]
                    filepath = directory + file
                    data_etherscan = pd.read_csv(filepath)
                    data_etherscan['Date(UTC)'] = pd.to_datetime(data_etherscan['Date(UTC)'])
                    data_etherscan = data_etherscan.set_index('Date(UTC)').reindex(date_range).reset_index()
                    data_etherscan.rename(columns={'index': 'Date'}, inplace=True)
                    if file=="export-AverageDailyTransactionFee.csv":
                        current_column = data_etherscan.columns[3]
                        data_etherscan.rename(columns={current_column: column_name}, inplace=True)
                        data_etherscan = data_etherscan.iloc[:,[0,3]]
                    elif file=="export-DailyActiveEthAddress.csv":
                        current_column = data_etherscan.columns[1]
                        data_etherscan.rename(columns={current_column: column_name}, inplace=True)
                        data_etherscan = data_etherscan.iloc[:,[0,1]]
                    else:
                        current_column = data_etherscan.columns[2]
                        data_etherscan.rename(columns={current_column: column_name}, inplace=True)
                        data_etherscan = data_etherscan.iloc[:,[0,2]]
                    # print(data_etherscan)
                    data_yf = data_yf.merge(data_etherscan, on='Date', how='outer')
                output_dir = "{parent_dir}\\cleaned_data\\{coin}_data".format(parent_dir=parent_dir,coin=coin)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                data_yf.to_csv("{output_dir}\\{coin}_{source}.csv".format(output_dir=output_dir,coin=coin, source=source), index=False)

#%%
# directory = "{parent_dir}\\raw_data\\Google_News_Headlines_data\\".format(parent_dir=parent_dir)
# final_data = pd.DataFrame(columns = ['Date','News Headline','Publisher'])

# for file in os.listdir(directory):
#     filepath = directory + file
#     data = pd.read_csv(filepath)
#     data_drop = data.drop(columns=['Unnamed: 0','description','url','publisher.href'])
#     data_renamed = data_drop.rename(columns={'published date':'Date','title':'News Headline','publisher.title':'Publisher'})
#     data_renamed['Date'] = pd.to_datetime(data_renamed['Date'], format='%a, %d %b %Y %H:%M:%S %Z').dt.strftime('%d/%m/%Y')
#     data_renamed['Date'] = pd.to_datetime(data_renamed['Date'], format='%d/%m/%Y')
#     data_unique = data_renamed.drop_duplicates(subset='News Headline', keep='first')
#     final_data = pd.concat([final_data, data_unique], ignore_index=True)
#     final_data = final_data.sort_values(by='Date',ascending=True)

# final_data_unique = final_data.drop_duplicates(subset='News Headline', keep='first')

# final_data_unique.to_csv("{parent_dir}\\cleaned_data\\Google_News_Headlines_data\\google_news_headlines_data.csv".format(parent_dir=parent_dir), index=False)
