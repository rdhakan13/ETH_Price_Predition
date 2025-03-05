import pandas as pd
import numpy as np
from src.common.utils import get_root_directory
from src.common.logger import get_logger
from src.preprocessing.data_cleaner import DataCleaner

root_dir = str(get_root_directory())
logger = get_logger("INFO", __name__)
input_data = {"ETH-USD": 
         {"etherscan":["Adj Close", "AddressCount", "BlockReward","Ethersupply2", 
                    "BlockDifficulty", "NetworkHash", "TxGrowth", "Uncles",
                    "TransactionFee"], 
          "oklink":['Open','High','Low','Close','Adj Close','Volume',
                    'ETH Gas price','ETH total supply','ETH daily transaction fee',
                    'Gas utilization rate of ETH','ETH daily new contracts',
                    'ETH average daily block size',
                    'ETH average computing power of the entire network',
                    'ETH average daily transaction fee',
                    'ETH mining difficulty','ETH number of daily active addresses']}, 
         "BTC-USD": 
         {"oklink":['Adj Close','BTC total supply','BTC total addresses',
                    'BTC full node data size'],
          "bitinfocharts":['Open','High','Low','Close','Adj Close','Volume',
                          'Transactions','Block Size','Difficulty',
                          'Active Addressses']}, 
         "LTC-USD": 
         {"oklink":['Adj Close','LTC total supply','LTC total addresses',
                    'LTC full node data size'],
          "bitinfocharts":['Open','High','Low','Close','Adj Close','Volume',
                          'Transactions','Block Size','Difficulty',
                          'Active Addressses']}
          }

column_mapping = {'Open': 'YF_Op', 'High': 'YF_Hi', 'Low': 'YF_Lo', 
             'Close':'YF_Cls', 'Volume':'YF_Vol', 
             'AverageDailyTransactionFee':'ES_AvgTransFee',
             'AvgGasPrice':'ES_AvgGasPrc','BlockCountRewards': 'ES_BlkCnt', 
             'BlockSize':'ES_BlkSz', 'BlockTime':'ES_BlkTm', 
             'DailyActiveEthAddress':'ES_ActAdd',
             'deployed contracts':'ES_DepCon','GasLimit':'ES_GasLmt',
             'GasUsed': 'ES_GasUsd', 'verified contracts':"ES_VerCon",
             'ETH market cap': 'OL_MktCap',
             "Number of new addresses added per day on ETH":"OL_NewAdd",
             "ETH number of daily transactions on the chain":"OL_ChnTrans",
             "ETH daily transaction volume on the chain":"OL_ChnVol",
             'BTC average daily transaction fee':'OL_AvgTransFee',
             'BTC mining difficulty': 'OL_MinDif', 
             'BTC average daily block size':'OL_BlkSz',
             'BTC number of daily active addresses':'OL_ActAdd',
             'BTC market cap': 'OL_MktCap',
             "Number of new addresses added per day on BTC":"OL_NewAdd",
             "BTC number of daily transactions on the chain":"OL_ChnTrans", 
             "BTC daily transaction volume on the chain":"OL_ChnVol", 
             'BTC average computing power of the entire network':'OL_AvgComPwr',
             "Hashrate":"BIC_HshRt",'LTC average daily transaction fee':'OL_AvgTransFee',
             'LTC mining difficulty': 'OL_MinDif', 
             'LTC average daily block size':'OL_BlkSz', 
             'LTC number of daily active addresses':'OL_ActAdd',
             'LTC market cap': 'OL_MktCap',
             "Number of new addresses added per day on LTC":"OL_NewAdd", 
             "LTC number of daily transactions on the chain":"OL_ChnTrans", 
             "LTC daily transaction volume on the chain":"OL_ChnVol", 
             'LTC average computing power of the entire network':"OL_AvgComPwr" }

if __name__ == "__main__":

    for ticker in list(input_data.keys()):
        dc = DataCleaner(root_dir, ticker, source=list(input_data[ticker].keys()))
        dc.read_data()
        dc.identify_nan()
        for source in list(input_data[ticker].keys()):
            dc.drop_columns(source=source, columns=input_data[ticker][source])
            dc.standardise_columns(source=source, column_mapping=column_mapping)
        dc.merge_sources()
        dc.interpolate_clean_data(method="time")
        cleaned_data = dc.get_clean_data()
        cleaned_data = cleaned_data.loc[:"2024-04-01"]
        cleaned_data['D_AvgPrc'] = cleaned_data[['YF_Op', 'YF_Hi', 'YF_Lo','YF_Cls']].mean(axis=1)
        cleaned_data.to_csv(f"{root_dir}\\temp\\{ticker[:3]}_1.csv")
        logger.info(f"Data for {ticker[:3]} cleaned and saved to {root_dir}\\temp\\{ticker[:3]}_1.csv")


    # eth_etherscan = pd.read_csv(f"{root_dir}\\data\\processed\\ETH_data\\ETH_etherscan.csv")
    # eth_ol = pd.read_csv(f"{root_dir}\\data\\processed\\ETH_data\\ETH_oklink.csv")
    # eth_etherscan.replace(np.nan, 0, inplace=True)
    # eth_etherscan.replace(0, np.nan, inplace=True)
    # eth_ol.replace(np.nan, 0, inplace=True)
    # eth_ol.replace(0, np.nan, inplace=True)
    # eth_etherscan.drop(columns=[], inplace=True)
    # columns={'Open': 'YF_Op', 'High': 'YF_Hi', 'Low': 'YF_Lo', 
    #          'Close':'YF_Cls', 'Volume':'YF_Vol', 
    #          'AverageDailyTransactionFee':'ES_AvgTransFee',
    #          'AvgGasPrice':'ES_AvgGasPrc','BlockCountRewards': 'ES_BlkCnt', 
    #          'BlockSize':'ES_BlkSz', 'BlockTime':'ES_BlkTm', 
    #          'DailyActiveEthAddress':'ES_ActAdd',
    #          'deployed contracts':'ES_DepCon','GasLimit':'ES_GasLmt',
    #          'GasUsed': 'ES_GasUsd', 'verified contracts':"ES_VerCon"}
    # eth_etherscan.rename(columns=columns, inplace=True)
    # eth_ol.drop(columns= ['Open','High','Low','Close','Adj Close','Volume',
    #                       'ETH Gas price','ETH total supply',
    #                       'ETH daily transaction fee',
    #                       'Gas utilization rate of ETH',
    #                       'ETH daily new contracts',
    #                       'ETH average daily block size',
    #                       'ETH average computing power of the entire network',
    #                       'ETH average daily transaction fee',
    #                       'ETH mining difficulty',
    #                       'ETH number of daily active addresses'],
    #                       inplace=True)
    # columns = {'ETH market cap': 'OL_MktCap',
    #            "Number of new addresses added per day on ETH":"OL_NewAdd", 
    #            "ETH number of daily transactions on the chain":"OL_ChnTrans", 
    #            "ETH daily transaction volume on the chain":"OL_ChnVol"}
    # eth_ol.rename(columns=columns, inplace=True)
    # eth = pd.merge(eth_etherscan, eth_ol, on="Date")
    # eth['Date'] = pd.to_datetime(eth['Date'])
    # eth = eth.set_index('Date')
    # eth.interpolate(method="time", inplace =True)
    # eth['D_AvgPrc'] = eth[['YF_Op', 'YF_Hi', 'YF_Lo','YF_Cls']].mean(axis=1)
    # eth_filtered = eth.loc[:"2024-04-01"]
    # eth_filtered.to_csv(f"{root_dir}\\data\\final\\ETH.csv")
    
    # btc_bic = pd.read_csv(f"{root_dir}\\data\\processed\\BTC_data\\BTC_bitinfocharts.csv")
    # btc_ol = pd.read_csv(f"{root_dir}\\data\\processed\\BTC_data\\BTC_oklink.csv")
    # btc_bic.replace(np.nan, 0, inplace=True)
    # btc_bic.replace(0, np.nan, inplace=True)
    # btc_ol.replace(np.nan, 0, inplace=True)
    # btc_ol.replace(0, np.nan, inplace=True)
    # btc_ol.drop(columns=['Adj Close','BTC total supply','BTC total addresses',
    #                      'BTC full node data size'], inplace=True)
    # columns={'Open': 'YF_Op', 'High': 'YF_Hi', 'Low': 'YF_Lo', 'Close':'YF_Cls',
    #          'Volume':'YF_Vol', 'BTC average daily transaction fee':'OL_AvgTransFee',
    #          'BTC mining difficulty': 'OL_MinDif', 
    #          'BTC average daily block size':'OL_BlkSz', 'BlockTime':'ES_BlkTm',
    #          'BTC number of daily active addresses':'OL_ActAdd',
    #          'BTC market cap': 'OL_MktCap',
    #          "Number of new addresses added per day on BTC":"OL_NewAdd",
    #          "BTC number of daily transactions on the chain":"OL_ChnTrans", 
    #          "BTC daily transaction volume on the chain":"OL_ChnVol", 
    #          'BTC average computing power of the entire network':'OL_AvgComPwr'}
    # btc_ol.rename(columns=columns, inplace=True)
    # btc_bic.drop(columns=['Open','High','Low','Close','Adj Close','Volume',
    #                       'Transactions','Block Size','Difficulty',
    #                       'Active Addressses'], inplace=True)
    # btc_bic.rename(columns={"Hashrate":"BIC_HshRt"}, inplace=True)
    # btc = pd.merge(btc_ol, btc_bic, on="Date")
    # btc['Date'] = pd.to_datetime(btc['Date'])
    # btc = btc.set_index('Date')
    # btc.interpolate(method="time", inplace=True)
    # btc['D_AvgPrc'] = btc[['YF_Op', 'YF_Hi', 'YF_Lo','YF_Cls']].mean(axis=1)
    # btc_filtered = btc.loc[:"2024-04-01"]
    # btc_filtered.to_csv(f"{root_dir}\\data\\final\\BTC.csv")

    # ltc_bic = pd.read_csv(f"{root_dir}\\data\\processed\\LTC_data\\LTC_bitinfocharts.csv")
    # ltc_ol = pd.read_csv(f"{root_dir}\\data\\processed\\LTC_data\\LTC_oklink.csv")
    # ltc_bic.replace(np.nan, 0, inplace=True)
    # ltc_bic.replace(0, np.nan, inplace=True)
    # ltc_ol.replace(np.nan, 0, inplace=True)
    # ltc_ol.replace(0, np.nan, inplace=True)
    # ltc_ol.drop(columns=['Adj Close','LTC total supply','LTC total addresses',
    #                      'LTC full node data size'], inplace=True)
    # columns={'Open': 'YF_Op', 'High': 'YF_Hi', 'Low': 'YF_Lo', 'Close':'YF_Cls',
    #          'Volume':'YF_Vol', 'LTC average daily transaction fee':'OL_AvgTransFee',
    #          'LTC mining difficulty': 'OL_MinDif', 
    #          'LTC average daily block size':'OL_BlkSz', 
    #          'LTC number of daily active addresses':'OL_ActAdd',
    #          'LTC market cap': 'OL_MktCap',
    #          "Number of new addresses added per day on LTC":"OL_NewAdd", 
    #          "LTC number of daily transactions on the chain":"OL_ChnTrans", 
    #          "LTC daily transaction volume on the chain":"OL_ChnVol", 
    #          'LTC average computing power of the entire network':"OL_AvgComPwr"}
    # ltc_ol.rename(columns=columns, inplace=True)
    # ltc_bic.drop(columns=['Open','High','Low','Close','Adj Close','Volume',
    #                       'Transactions','Block Size','Difficulty',
    #                       'Active Addressses'], inplace=True)
    # ltc_bic.rename(columns={"Hashrate":"BIC_HshRt"}, inplace=True)
    # ltc = pd.merge(ltc_ol, ltc_bic, on="Date")
    # ltc["Date"] = pd.to_datetime(ltc["Date"])
    # ltc = ltc.set_index('Date')
    # ltc['D_AvgPrc'] = ltc[['YF_Op', 'YF_Hi', 'YF_Lo','YF_Cls']].mean(axis=1)
    # ltc_filtered = ltc.loc[:"2024-04-01"]
    # ltc_filtered.interpolate(method="time", inplace=True)
    # ltc_filtered.to_csv(f"{root_dir}\\data\\final\\LTC.csv")
