import pandas as pd
from src.common.utils import get_root_directory
from src.common.logger import get_logger
from src.sentiment_analyser.bert_sentiment_analyser import BertSentimentAnalyser
from src.sentiment_analyser.vader_sentiment_analyser import VaderSentimentAnalyser

logger = get_logger("INFO", __name__)
root_dir = get_root_directory()

if __name__ == "__main__":
    processed_gn = pd.read_csv(
        f"{root_dir}\\data\\processed\\Google_News_Headlines_data\\google_news_headlines_data.csv"
    )
    processed_gn = processed_gn.astype("string")
    processed_gn["Date"] = pd.to_datetime(processed_gn["Date"])
    VSA = VaderSentimentAnalyser(processed_gn)
    processed_gn = VSA.analyse_sentiment("News Headline")
    FBA = BertSentimentAnalyser(processed_gn, model_name="ProsusAI/finbert")
    processed_gn = FBA.analyse_sentiment("News Headline")
    CBA = BertSentimentAnalyser(processed_gn, model_name="ElKulako/cryptobert")
    processed_gn = CBA.analyse_sentiment("News Headline")
    processed_gn.to_csv(f"{root_dir}\\data\\final\\sentiment_analysis.csv", index=False)
    logger.info(f"Sentiment analysis saved to {root_dir}\\data\\final\\")
