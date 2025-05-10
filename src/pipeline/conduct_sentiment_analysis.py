import os
import time
import pandas as pd
from src.common.utils import get_root_directory, timeit
from src.common.logger import get_logger
from src.common.config_loader import ConfigLoader
from src.sentiment_analyser.bert_sentiment_analyser import BertSentimentAnalyser
from src.sentiment_analyser.vader_sentiment_analyser import VaderSentimentAnalyser

logger = get_logger(os.environ.get("LOG_LEVEL"), __name__)
root_dir = str(get_root_directory()) + "\\temp"

config_loader = ConfigLoader()
config = config_loader.define_conduct_sentiment_analysis()
active = config.get("active", False)
print(config)

@timeit
def conduct_sentiment_analysis() -> None:
    """
    Conduct sentiment analysis on the processed Google News headlines data.
    """
    processed_gn = pd.read_csv(
        f"{root_dir}\\data\\processed\\Google_News_Headlines_data\\google_news_headlines_data.csv"
    )
    processed_gn = processed_gn.astype("string")

    processed_gn["Date"] = pd.to_datetime(processed_gn["Date"])

    vsa = VaderSentimentAnalyser(processed_gn)

    processed_gn = vsa.analyse_sentiment("News Headline")

    fba = BertSentimentAnalyser(processed_gn, model_name="ProsusAI/finbert")

    processed_gn = fba.analyse_sentiment("News Headline")

    cba = BertSentimentAnalyser(processed_gn, model_name="ElKulako/cryptobert")

    processed_gn = cba.analyse_sentiment("News Headline")

    processed_gn.to_csv(f"{root_dir}\\data\\final\\sentiment_analysis.csv", index=False)

    logger.info(f"Sentiment analysis saved to {root_dir}\\data\\final\\")

if __name__ == "__main__":
    if active:
        logger.info("Starting sentiment analysis...")
        conduct_sentiment_analysis()
        logger.info(f"Sentiment analysis completed.")
