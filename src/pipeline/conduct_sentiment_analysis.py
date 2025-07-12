import os
import pandas as pd
from src.common.utils import get_root_directory, timeit, get_class
from src.common.logger import get_logger
from src.common.config_loader import ConfigLoader

logger = get_logger(os.environ.get("LOG_LEVEL"), __name__)
root_dir = str(os.path.join(str(get_root_directory()),'tmp'))

config_loader = ConfigLoader()
config = config_loader.define_conduct_sentiment_analysis()
active = config.get("active", False)
sources = config.get("sources", [{}])


@timeit
def conduct_sentiment_analysis() -> None:
    """
    Conduct sentiment analysis on the processed Google News headlines data.
    """
    try:
        processed_gn = pd.read_csv(
            str(os.path.join(root_dir,'data','processed','Google_News_Headlines_data','google_news_headlines_data.csv'))
        )
        processed_gn = processed_gn.astype("string")

        processed_gn["Date"] = pd.to_datetime(processed_gn["Date"])
    except Exception as e:
        logger.error(f"Error reading processed Google News data: {e}")
        raise e

    for analyser in config.get("sentiment_analysis", []):
        analyser_class = get_class(analyser.get("type"))
        if analyser.get("type") == "vader_sentiment_analyser":
            instance = analyser_class(processed_gn)
        else:
            instance = analyser_class(processed_gn, model_name=analyser.get("name"))
        processed_gn = instance.analyse_sentiment("News Headline")

    processed_gn.to_csv(str(os.path.join(root_dir,'data','final','sentiment_analysis.csv')), index=False)

    logger.info(f"Sentiment analysis saved to {str(os.path.join(root_dir,'data','final'))}")


if __name__ == "__main__":
    if active:
        logger.info("Starting sentiment analysis...")
        conduct_sentiment_analysis()
        logger.info("Sentiment analysis completed.")
