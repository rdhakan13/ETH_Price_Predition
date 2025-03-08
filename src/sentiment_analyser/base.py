from abc import abstractmethod
from typing import Any
import pandas as pd


class SentimentAnalyser:
    def __init__(self, df: pd.DataFrame):
        """Initialise Sentiment Analyser."""
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        self.df = df

    @abstractmethod
    def analyse_sentiment(self, column_name: str) -> pd.DataFrame:
        """
        Analyze the sentiment of a given headline.

        Parameters:
            column_name (str): The name of the column containing the text data.

        Returns:
            pd.DataFrame: The original dataframe with the sentiment score and sentiment category.
        """
        pass

    @abstractmethod
    def determine_sentiment(self, input_var: Any) -> int:
        """
        Determine sentiment category based on given inputs.

        Parameters:
            input (Any): The input to determine the sentiment category.

        Returns:
            int: The sentiment category.
        """
        pass
