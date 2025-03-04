import pandas as pd
import time
import logging
import swifter
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from src.sentiment_analyser.base import SentimentAnalyser
import torch

logger = logging.getLogger(__name__)

class BertSentimentAnalyser(SentimentAnalyser):
    def __init__(self, df:pd.DataFrame, model_name:str):
        super().__init__(df)
        self.device = 0 if torch.cuda.is_available() else -1
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.analyzer = pipeline("sentiment-analysis", model=self.model, tokenizer=self.tokenizer, device=self.device)
    
    def analyse_sentiment(self, column_name:str)->pd.DataFrame:
        if column_name not in self.df.columns:
            raise ValueError(f"Column '{column_name}' not found in df")
        logger.info(f"Analyzing sentiment using {self._model_name()}...")
        start_time = time.time()
        results = self.df[column_name].astype(str).swifter.apply(self.analyzer)
        self.df[f'D_{self._model_name()}_ConScore'] = results.swifter.apply(lambda x: x[0]['score'])
        self.df[f'D_{self._model_name()}_Sent'] = results.swifter.apply(lambda x: self.determine_sentiment(x[0]['label']))
        self.df[f'D_{self._model_name()}_Score'] = self.df[f'D_{self._model_name()}_ConScore']*self.df[f'D_{self._model_name()}_Sent']
        end_time = time.time()
        logging.info("Sentiment analysis complete")
        logger.info(f"Time taken: {end_time - start_time}")
        return self.df
    
    def determine_sentiment(self, input_var:str)->int:
        if not isinstance(input_var, str):
            raise ValueError("Input must be a string")
        if input_var.lower() in ["positive","bullish"]:
            return 1
        elif input_var.lower() in ["negative","bearish"]:
            return -1
        elif input_var.lower() == "neutral":
            return 0
        else:
            raise ValueError(f"Unknown sentiment label: {input_var}")
    
    def _model_name(self)->str:
        return str(self.model_name.split("/")[-1].upper())