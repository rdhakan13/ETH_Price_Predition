import pandas as pd
import numpy as np
import logging
from src.sentiment_analyser.vader_sentiment_analyser import VaderSentimentAnalyser
import swifter

logger = logging.getLogger(__name__)


class FeatureGenerator:
    def __init__(self, input_data: pd.DataFrame, data_tag: str):
        self.input_data = input_data
        self.transformed_data = pd.DataFrame()
        self.data_tag = data_tag

    def generate_features(self)->pd.DataFrame:
        """
        Generate features based on the input data.

        Returns:
            pd.DataFrame: Transformed data.
        """
        if self.data_tag == "sentiment":
            self._generate_sentinment_features()
        return self.transformed_data.replace(np.nan, 0, inplace=True)
    
    def _generate_sentinment_features(self):
        """
        Generate sentiment features based on the input data
        
        Returns:
            None
        """
        VSA = VaderSentimentAnalyser(self.input_data)
        for col in self.input_data.columns:
            if "Score" in col:
                col_prefix = "_".join(col.split("_")[:2])
                col_score_In = col_prefix + "_AvgScr_In"
                col_sent_In = col_prefix + "_Sent_AvgIn"
                col_score_Ex = col_prefix + "_AvgScr_Ex"
                col_sent_Ex = col_prefix + "_Sent_AvgEx"
                dropped_neutrals = self.input_data.reset_index().rename(columns={"index": "Date"})
                dropped_neutrals = dropped_neutrals.drop(dropped_neutrals[dropped_neutrals[col_prefix+"_Sent"] == 0].index)
                if "VADER" in col:
                    AvgScr_In = self.input_data.pivot_table(values=col, index=["Date"], aggfunc="mean")
                    AvgScr_In[col_score_In] = AvgScr_In[col]
                    AvgScr_Ex = dropped_neutrals.pivot_table(values=col, index=["Date"], aggfunc="mean")
                    AvgScr_Ex[col_score_Ex] = AvgScr_Ex[col]

                if "BERT" in col:
                    self.input_data[col_score_In] = self.input_data[col]*self.input_data[col_prefix+"_Sent"]
                    dropped_neutrals[col_score_Ex] = dropped_neutrals[col]*dropped_neutrals[col_prefix+"_Sent"]
                    AvgScr_In = self.input_data.pivot_table(values=col_score_In, index=["Date"], aggfunc="mean")
                    AvgScr_Ex = dropped_neutrals.pivot_table(values=col_score_Ex, index=["Date"], aggfunc="mean")
                
                self.transformed_data[col_score_In] = AvgScr_In[col_score_In]
                self.transformed_data[col_sent_In] = self.transformed_data[col_score_In].swifter.apply(VSA.determine_sentiment)
                self.transformed_data[col_score_Ex] = AvgScr_Ex[col_score_Ex]
                self.transformed_data[col_sent_Ex] = self.transformed_data[col_score_Ex].swifter.apply(VSA.determine_sentiment)
