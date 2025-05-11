import os
import pandas as pd
import time
from src.common.utils import get_root_directory, make_directory, timeit
from src.common.logger import get_logger
from src.preprocessing.data_cleaner import DataCleaner

logger = get_logger(os.environ.get("LOG_LEVEL"), __name__)
root_dir = str(get_root_directory()) + "\\temp"
input_data = {
    "ETH-USD": {
        "etherscan": [
            "Adj Close",
            "AddressCount",
            "BlockReward",
            "Ethersupply2",
            "BlockDifficulty",
            "NetworkHash",
            "TxGrowth",
            "Uncles",
            "TransactionFee",
        ],
        "oklink": [
            "Open",
            "High",
            "Low",
            "Close",
            "Adj Close",
            "Volume",
            "ETH Gas price",
            "ETH total supply",
            "ETH daily transaction fee",
            "Gas utilization rate of ETH",
            "ETH daily new contracts",
            "ETH average daily block size",
            "ETH average computing power of the entire network",
            "ETH average daily transaction fee",
            "ETH mining difficulty",
            "ETH number of daily active addresses",
        ],
    },
    "BTC-USD": {
        "oklink": [
            "Adj Close",
            "BTC total supply",
            "BTC total addresses",
            "BTC full node data size",
        ],
        "bitinfocharts": [
            "Open",
            "High",
            "Low",
            "Close",
            "Adj Close",
            "Volume",
            "Transactions",
            "Block Size",
            "Difficulty",
            "Active Addressses",
        ],
    },
    "LTC-USD": {
        "oklink": [
            "Adj Close",
            "LTC total supply",
            "LTC total addresses",
            "LTC full node data size",
        ],
        "bitinfocharts": [
            "Open",
            "High",
            "Low",
            "Close",
            "Adj Close",
            "Volume",
            "Transactions",
            "Block Size",
            "Difficulty",
            "Active Addressses",
        ],
    },
}

column_mapping = {
    "Open": "YF_Op",
    "High": "YF_Hi",
    "Low": "YF_Lo",
    "Close": "YF_Cls",
    "Volume": "YF_Vol",
    "AverageDailyTransactionFee": "ES_AvgTransFee",
    "AvgGasPrice": "ES_AvgGasPrc",
    "BlockCountRewards": "ES_BlkCnt",
    "BlockSize": "ES_BlkSz",
    "BlockTime": "ES_BlkTm",
    "DailyActiveEthAddress": "ES_ActAdd",
    "deployed contracts": "ES_DepCon",
    "GasLimit": "ES_GasLmt",
    "GasUsed": "ES_GasUsd",
    "verified contracts": "ES_VerCon",
    "ETH market cap": "OL_MktCap",
    "Number of new addresses added per day on ETH": "OL_NewAdd",
    "ETH number of daily transactions on the chain": "OL_ChnTrans",
    "ETH daily transaction volume on the chain": "OL_ChnVol",
    "BTC average daily transaction fee": "OL_AvgTransFee",
    "BTC mining difficulty": "OL_MinDif",
    "BTC average daily block size": "OL_BlkSz",
    "BTC number of daily active addresses": "OL_ActAdd",
    "BTC market cap": "OL_MktCap",
    "Number of new addresses added per day on BTC": "OL_NewAdd",
    "BTC number of daily transactions on the chain": "OL_ChnTrans",
    "BTC daily transaction volume on the chain": "OL_ChnVol",
    "BTC average computing power of the entire network": "OL_AvgComPwr",
    "Hashrate": "BIC_HshRt",
    "LTC average daily transaction fee": "OL_AvgTransFee",
    "LTC mining difficulty": "OL_MinDif",
    "LTC average daily block size": "OL_BlkSz",
    "LTC number of daily active addresses": "OL_ActAdd",
    "LTC market cap": "OL_MktCap",
    "Number of new addresses added per day on LTC": "OL_NewAdd",
    "LTC number of daily transactions on the chain": "OL_ChnTrans",
    "LTC daily transaction volume on the chain": "OL_ChnVol",
    "LTC average computing power of the entire network": "OL_AvgComPwr",
}

directory = f"{root_dir}\\tmp\\data\\final"

if __name__ == "__main__":
    start_time = time.time()

    for ticker in list(input_data.keys()):
        dc = DataCleaner(root_dir, ticker, source=list(input_data[ticker].keys()))

        dc.read_data()

        dc.identify_nan()

        for source in list(input_data[ticker].keys()):
            dc.drop_columns(source=source, columns=input_data[ticker][source])
            dc.standardise_columns(source=source, column_mapping=column_mapping)

        dc.merge_sources()

        dc.interpolate_clean_data(method="time")

        dc.save_clean_data(directory=directory)

    end_time = time.time()

    total_runtime = end_time - start_time

    logger.info(f"TOTAL RUNTIME: {total_runtime}s")
