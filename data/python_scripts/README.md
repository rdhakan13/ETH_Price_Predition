## Raw Data

### Yahoo Finance

To acquire cryptocurrency price data (Open, High, Low, Close, Adj Close & Volume), [yfinance](https://github.com/ranaroussi/yfinance), built by Ran Aroussi, was used to pull all the available price data at a daily interval for Ethereum, Bitcoin and Litecoin from [Yahoo Finance](https://finance.yahoo.com/). To install `yfinance`, ensure you have a minimum of Python 3.4 to be able to install it with `pip`:
```
pip install yfinance
```
By running `yahoo_finance_api.py`, the code will generate a CSV file for the specified `tickers` under the directory `{parent_directory}/raw_data/{ticker}_data/`.

The code in `yahoo_finance_api.py` can be ammended to pull other cryptocurrency/stock data by changing the `tickers` list.

### Google News

To acquire Google News Headlines for the time period fetched for Ethereum price data, [gnews](https://github.com/ranahaani/GNews), built by Muhammad Abdullah (ranahanni), was used to pull any news that contained the keywords: Cryptocurrency, Blockchain, Bitcoin, Ethereum and Litecoin. `gnews` can be `pip` installed as such:
```
pip install gnews
```
`google_news_api.py` uses the Ethereum data captured in the CSV file by `yahoo_finance_api.py` to establish the start and end date of news headlines that need to be obtained. `google_news_api.py` splits the entire period into distict years for batch processing such that it produces a CSV file for each year under the directory `{parent_directory}/raw_data/Google_News_Headlines_data/`. The data acquired from the API call pulls the news headline, description, Google news URL, news publisher name and website.

The code in `google_news_api.py` can be ammended to bulk download Google news headlines for any set of keywords for any specified start and end dates. 

<div style="color: red; border: 1px solid red; padding: 10px;">
  <strong>Warning:</strong> google_news_api.py may produce duplicate headlines for keywords of the same topic.
</div>

### Blockchain Data

Blockchain data is acquired from 3 separate source to be able to choose the most complete data source and patch any incomplete data points.

#### bitinfocharts.com

To acquire blockchain data, data was scraped from [bitinfocharts.com](bitinfocharts.com) by adapting the code from [bitinfochartscraper](https://github.com/logic-language/bitinfochartscraper) produced by the user logic-language. 

By running `bitinfocharts_api.py`, all available blockchain data (Transaction Count, Block Size, Difficulty, Hashrate, Average Transaction Fees & No. of Active Addresses) for Ethereum, Bitcoin and Litecoin is scraped and saved as CSV file under the directory `{parent_directory}/raw_data/{coin}_data/bitinfocharts/`.

#### OKLINK Chainhub

The blockchain data acquired for the three coins through [OKLINK Chainhub](oklink.com) is summarised in Table 2. The data was downloaded as a CSV file straight from the graphs displayed on the website. 

**Table 1: Blockchain Data Summary**

| Blockchain data            | ETH | BTC | LTC |
|----------------------------|-----|-----|-----|
| Market Capitalisation      | ✔   | ✔   | ✔   |
| Total Supply               | ✔   | ✔   | ✔   |
| Mean Block Size            | ✔   | ✔   | ✔   |
| Mean Hash Rate             | ✔   | ✔   | ✔   |
| Mean Transaction Fees      | ✔   | ✔   | ✔   |
| Mining Difficulty          | ✔   | ✔   | ✔   |
| No. of Active Addresses    | ✔   | ✔   | ✔   |
| No. of New Addresses       | ✔   | ✔   | ✔   |
| No. of Total Addresses     | ✔   | ✔   | ✔   |
| No. of Transactions        | ✔   | ✔   | ✔   |
| Total Size of Transactions | ✔   | ✔   | ✔   |
| Total Transfer Volume      | ✔   | ✔   | ✖   |
| Mean Gas Price             | ✔   | ✖   | ✖   |
| Gas Used                   | ✔   | ✖   | ✖   |
| No. of Issued Contracts    | ✔   | ✖   | ✖   |

#### Etherscan

Only Ethereum data was provided on [Etherscan](https://etherscan.io/) and as such the blockchain data that was acquired was: No. of Total Addresses, Mean Transaction Fees, Mean Gas Price, Block Count Rewards, Mean Difficulty, Block Reward, Mean Block Size, Mean Block Time, No. of Active Addresses, No. of Issued Contracts, No. of Verified Contracts, Total Supply, Mean Gas Limit, Gas Used, Mean Hash Rate, Total Uncle Count.

The data was for each of the above listed features was downloaded as a CSV straight from the graphs provided. 

## Cleaned Data

By running `merge_data.py`, the cryptocurrency price data is merged with blockchain data to create a CSV file under the directory `{parent_directory}/cleaned_data/{coin}_data/` for the respective coins.

Moreover, the Google news headlines are merged into a single CSV file under the directory `{parent_directory}/cleaned_data/Google_News_Headlines_data/`. The cleaned CSV file has no duplicates and columns containing Google news URL and publisher website are dropped. 

The time period of the final dataset ranges from 09/11/2017 to 10/08/2024. 
