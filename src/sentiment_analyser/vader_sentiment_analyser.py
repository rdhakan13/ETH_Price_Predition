import nltk
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from src.sentiment_analyser.base import SentimentAnalyser

class VaderSentimentAnalyser(SentimentAnalyser):
    def __init__(self, df:pd.DataFrame):
        super().__init__(df)
        nltk.download('vader_lexicon', quiet=True)
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyse_sentiment(self, column_name:str)->pd.DataFrame:
        if column_name not in self.df.columns:
            raise ValueError(f"Column '{column_name}' not found in DataFrame")
        
        self.df['D_VADER_Score'] = self.df[column_name].apply(
            lambda text: self.analyzer.polarity_scores(str(text))['compound']
        )
        
        self.df['D_VADER_Sent'] = self.df['D_VADER_Score'].apply(self.determine_sentiment)
        
        return self.df
    
    def determine_sentiment(self, input_var:float)->int:
        if not isinstance(input_var, float):
            raise ValueError("Input must be a float")
        if input_var >= 0.05:
            return 1
        elif input_var <= -0.05:
            return -1
        else:
            return 0