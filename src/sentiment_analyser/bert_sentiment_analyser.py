import pandas as pd
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from src.sentiment_analyser.base import SentimentAnalyser

logger = logging.getLogger(__name__)

class BertSentimentAnalyser(SentimentAnalyser):
    def __init__(self, df:pd.DataFrame, model_name:str):
        super().__init__(df)
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.analyzer = pipeline("sentiment-analysis", model=self.model, tokenizer=self.tokenizer)
    
    def analyse_sentiment(self, column_name:str)->pd.DataFrame:
        if column_name not in self.df.columns:
            raise ValueError(f"Column '{column_name}' not found in df")
        results = self.df[column_name].astype(str).apply(self.analyzer)
        self.df[f'D_{self._column_name()}_Score'] = results.apply(lambda x: x[0]['score'])
        self.df[f'D_{self._column_name()}_Sent'] = results.apply(lambda x: self.determine_sentiment(x[0]['label']))
        return self.df
    
    def determine_sentiment(self, input_var:str)->int:
        if not isinstance(input_var, str):
            raise ValueError("Input must be a string")
        if input_var.lower() is "positive" or "bullish":
            return 1
        elif input_var.lower() is "negative" or "bearish":
            return -1
        elif input_var.lower() == "neutral":
            return 0
        else:
            raise ValueError(f"Unknown sentiment label: {input_var}")
        
    def _column_name(self)->str:
        return str(self.model_name.split("/")[-1].upper())