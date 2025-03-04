import pandas as pd
from transformers import pipeline
from src.sentiment_analyser.base import SentimentAnalyser

class FinbertSentimentAnalyzer(SentimentAnalyser):
    def __init__(self, df:pd.DataFrame):
        super().__init__(df)
        self.analyzer = pipeline("text-classification", model="ProsusAI/finbert")
    
    def analyse_sentiment(self, column_name:str)->pd.DataFrame:
        if column_name not in self.df.columns:
            raise ValueError(f"Column '{column_name}' not found in df")
        
        results = self.df[column_name].astype(str).apply(self.analyzer)
        
        self.df['D_FinBERT_Score'] = results.apply(lambda x: x[0]['score'])
        self.df['D_FinBERT_Sent'] = results.apply(lambda x: x[0]['label'])
        
        return self.df