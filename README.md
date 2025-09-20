# :rocket: Ethereum Price Prediction using Internal and External Factors

Author: Raj Dhakan

## :page_facing_up: Abstract

Since the launch of Bitcoin (BTC) in 2008, cryptocurrencies - a decentralised digital currency - have gained popularity. They are particularly characterised by high volatility, enabling substantial short-term trading profits, but also increasing risk. This volatility differentiates crypto markets from traditional financial markets and motivates the development of predictive machine learning models to improve forecasting and reduce potential losses. This thesis focuses on Ethereum (ETH), which, unlike most cryptocurrencies, has an uncapped supply, complicating price prediction due to the everlasting interplay of supply and demand factors. Despite its prominence as the second-largest cryptocurrency, ETH remains under-researched compared to Bitcoin, with only one study exploring the effectiveness of blockchain data for price prediction - a key research gap. This project builds on the foundational work of that one study, mainly improving its methodology, but also adding a novel contribution of exploring the effectiveness of sentiment analysis of news headlines using three separate methods, namely VADER, FinBERT and CryptoBERT. As such, this thesis conducted a comparative study of machine learning models, investigating the effectiveness of internal (blockchain data) and external (public sentiment) factors in improving daily intraweek forecasts of ETH. As a precursor to the investigation, one key achievement included the development of a reliable data pipeline that fetches and cleans both blockchain data and news headlines from open sources, and also conducts feature engineering. Subsequently, the aim was achieved by setting a competitive statistical baseline model - ARIMA - followed by experimentation with three relevant machine learning models: XGBoost (ensemble), BiGRU (deep learning) and 1DCNN-BiGRU (hybrid deep learning). The models were evaluated using both percentage-based regression and classification metrics for better interpretability of risk for traders, hence improving the study’s real-world applicability. Moreover, the models were further interrogated using statistical tests and explainable methods for transparency. Regardless of the model, the experimental results disproved the initial hypothesis that both blockchain data and sentiment analysis would be effective in improving the model’s predictive performance. Though it was the case with news headlines, it is believed that this was due to a lack of features in the data that could capture the magnitude of public engagement with each news to quantify its influence factor. Nevertheless, the project generated insights that challenge conventional perceptions of feature effectiveness with full transparency and reproducibility of the work as documented in the code repository below - another key achievement.

**Keywords**: cryptocurrency, Ethereum, time-series regression, blockchain data, sentiment analysis, news headlines, ARIMA, XGBoost, deep neural networks, BiGRU, 1DCNN-BiGRU

The findings of the research in this code repository is documented in full on this [paper](reports/docs/RajDhakan_mscthesis.pdf).

## :floppy_disk: Data

### Yahoo Finance
To acquire cryptocurrency price data (Open, High, Low, Close, Adj Close & Volume), [yfinance](https://github.com/ranaroussi/yfinance), built by Ran Aroussi, was used to pull all the available price data at a daily interval for Ethereum, Bitcoin and Litecoin from [Yahoo Finance](https://finance.yahoo.com/). 

### Google News
To acquire Google News Headlines for the time period fetched for Ethereum price data, [gnews](https://github.com/ranahaani/GNews), built by Muhammad Abdullah (ranahanni), was used to pull any news that contained the keywords: Cryptocurrency, Blockchain, Bitcoin, Ethereum and Litecoin. The data acquired from the API call pulls the news headline, description, Google news URL, news publisher name and website.

<div style="color: red;">
<strong>Warning:</strong> google_news_api.py may produce duplicate headlines for keywords of the same topic.
</div>

### Blockchain Data
Blockchain data is acquired from 3 separate source to be able to choose the most complete data source and patch any incomplete data points.

1. [BitInfoCharts](bitinfocharts.com) - data was scraped from  by adapting the code from [bitinfochartscraper](https://github.com/logic-language/bitinfochartscraper) produced by the user logic-language. 
2. [OKLINK Chainhub](oklink.com) - The data was downloaded as a CSV file from the graphs displayed on the website (note: the functionality of using the download button has been disabled now). 
3. [Etherscan](https://etherscan.io/) - Only Ethereum data was provided on and as such the blockchain data that was acquired was: No. of Total Addresses, Mean Transaction Fees, Mean Gas Price, Block Count Rewards, Mean Difficulty, Block Reward, Mean Block Size, Mean Block Time, No. of Active Addresses, No. of Issued Contracts, No. of Verified Contracts, Total Supply, Mean Gas Limit, Gas Used, Mean Hash Rate, Total Uncle Count.The data was for each of the above listed features was downloaded as a CSV from the graphs provided.

The blockchain data acquired for the three coins through is summarised in the below table. 

**Blockchain Data Summary**

| Blockchain data             | ETH | BTC | LTC |
|-----------------------------|-----|-----|-----|
| Mean Block Size             | ✔   | ✔   | ✔   |
| Mean Hash Rate              | ✔   | ✔   | ✔   |
| Mean Transaction Fees       | ✔   | ✔   | ✔   |
| Mining Difficulty           | ✔   | ✔   | ✔   |
| No. of Active Addresses     | ✔   | ✔   | ✔   |
| No. of New Addresses        | ✔   | ✔   | ✔   |
| No. of Total Addresses      | ✔   | ✔   | ✔   |
| No. of Transactions         | ✔   | ✔   | ✔   |
| On-chain Transaction Count  | ✔   | ✔   | ✔   |
| On-chain Transaction Volume | ✔   | ✔   | ✖   |
| Mean Gas Price              | ✔   | ✖   | ✖   |
| Gas Used                    | ✔   | ✖   | ✖   |
| Gas Limit                   | ✔   | ✖   | ✖   |
| No. of Deployed Contracts   | ✔   | ✖   | ✖   |
| No. of Verified Contracts   | ✔   | ✖   | ✖   |

## :open_file_folder: Project Structure
```
ETH_Price_Prediction/
│
├── github/                    # Directory contains unit-test CI pipeline
│
├── configs/                   # Folder to hold configs used by main.py
│
├── data/                      # Directory containing all data files
│   ├── final/                 # Data used for experiments
│   ├── processed/             # Cleaned and preprocessed data ready for modeling
│   └── raw/                   # Raw collected data
│
├── mlruns/                    # MLFlow directory to log experiments and models
│
├── notebooks/                 # Jupyter notebooks for exploration and experimenting different models
│
├── scripts/                   # Folder containing additional scripts
|   └── ec2/                   # Contains scripts for training models using GPUs in AWS EC2
│
├── reports/                   # Folder containing data for final report
│   ├── docs/                  # Contains final report documenting results of the study
|   └── figures/               # Contains figures for report and general analysis
│
├── src/                       # Source code for fetching, cleaning and using data from the pipeline
│   ├── common/                 # Utility functions
│   ├── data/                   # APIs for data collection
│   ├── pipeline/               # Pipeline scripts for different stages
│   ├── preprocessing/          # Preprocessing tasks before training
│   └── sentiment_analyser/     # Different sentiment analysers (VADER, FinBERT, CryptoBERT)
│
├── tests/                      # Unit-tests for src
│
├── .gitattributes
├── .gitignore
├── cloc_report.txt
├── LICENSE  
├── Makefile  
├── README.md  
├── main.py
├── poetry.lock
└── pyproject.toml
```

## :gear: How to Run

This project uses a `Makefile` to automate tasks related to managing a Python environment, code clean-up and running scripts.

### Prerequisites

Before using the `Makefile`, make sure you have the following installed on your system:

1. **Python**: Ensure that you have Python 3.11.7 installed.
   
2. **Make**: You need the `make` utility to execute the commands in the `Makefile`. Most Linux/macOS systems come with `make` preinstalled. On Windows, you can install `make` by downloading the wizard from [GCC for Windows](https://sourceforge.net/projects/gnuwin32/files/make/3.81/make-3.81.exe/download?use_mirror=altushost-swe&download=). Install `make` by running the wizard and copying the path of executable into PATH variable under 'Edit environmental variables for your account' in control panel. You can find the path of the executable by running `where make` in the terminal.

### Usage Instructions

The `Makefile` includes several targets:

#### Setting up Python Environment:

1. **Create a .venv**:
    This target creates a new .venv environment using the `requirements.txt` file:
    ```
    make init
    ```
2. **Install Python libraries using Poetry**:
    This target installs dependencies listed in pyproject.toml:
    ```
    make install
    ```
3. **Activate .venv**

#### Local testing & linting:

- **Linting**:

    To check linting:
    ```
    make lint-check
    ```
    To lint format
    ```
    make lint-format
    ```
    To check linting and fix issues:
    ```
    make lint-fix
    ```
- **Type check**

    To conduct a type check across `src`:
    ```
    make type-check
    ```
- **Unit tests**

    To conduct local unit tests:
    ```
    make unit-tests
    ```
- **Clean folder directory**

    To remove cache folders:
    ```
    make clean
    ```

#### Running pipeline:

To run the data pipeline to fetch and process data:
```
make run FILE=main.py LOG_LEVEL=ERROR CONFIG_FILENAME=pipeline.yml
```

Where all three variables can be configured as needed.
<!-- 
## :books: References -->
