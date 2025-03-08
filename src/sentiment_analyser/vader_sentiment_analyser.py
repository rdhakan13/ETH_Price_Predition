import nltk
import pandas as pd
import time
import logging
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from src.sentiment_analyser.base import SentimentAnalyser
import swifter

logger = logging.getLogger(__name__)


class VaderSentimentAnalyser(SentimentAnalyser):
    def __init__(self, df: pd.DataFrame):
        super().__init__(df)
        nltk.download("vader_lexicon", quiet=True)
        self.analyzer = SentimentIntensityAnalyzer()

    def analyse_sentiment(self, column_name: str) -> pd.DataFrame:
        if column_name not in self.df.columns:
            raise ValueError(f"Column '{column_name}' not found in DataFrame")
        logger.info("Analyzing sentiment using VADER...")
        start_time = time.time()
        self.df["D_VADER_Score"] = self.df[column_name].swifter.apply(
            lambda text: self.analyzer.polarity_scores(str(text))["compound"]
        )
        self.df["D_VADER_Sent"] = self.df["D_VADER_Score"].swifter.apply(
            self.determine_sentiment
        )
        end_time = time.time()
        logger.info("Sentiment analysis complete")
        logger.info(f"Time taken: {end_time - start_time}")
        return self.df

    def determine_sentiment(self, input_var: float) -> int:
        if not isinstance(input_var, float):
            raise ValueError("Input must be a float")
        if input_var >= 0.05:
            return 1
        elif input_var <= -0.05:
            return -1
        else:
            return 0
