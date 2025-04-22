import pandas as pd
import logging
from src.sentiment_analyser.vader_sentiment_analyser import VaderSentimentAnalyser
import swifter
import numpy as np

logger = logging.getLogger(__name__)


class FeatureGenerator:
    def __init__(self, input_data: pd.DataFrame, data_tag: str):
        self.input_data = input_data
        if not isinstance(self.input_data, pd.DataFrame):
            raise ValueError("input_data must be a pandas DataFrame.")
        self.transformed_data = pd.DataFrame()
        self.data_tag = data_tag
        if data_tag not in ["sentiment", "price"]:
            raise ValueError("data_tag must be either 'sentiment' or 'price'.")

    def generate_features(self) -> pd.DataFrame:
        """
        Generate features based on the input data.

        Returns:
            pd.DataFrame: Transformed data.
        """
        if self.data_tag == "sentiment":
            self._generate_sentinment_features()
        elif self.data_tag == "price":
            self._generate_price_features()
        return self.transformed_data

    def _generate_sentinment_features(self) -> None:
        """
        Generate sentiment features based on the input data

        Returns:
            None
        """
        vsa = VaderSentimentAnalyser(self.input_data)
        for col in self.input_data.columns:
            if "Score" in col:
                col_prefix = "_".join(col.split("_")[:2])
                col_score_In = col_prefix + "_AvgScr_In"
                col_sent_In = col_prefix + "_Sent_AvgIn"
                col_score_Ex = col_prefix + "_AvgScr_Ex"
                col_sent_Ex = col_prefix + "_Sent_AvgEx"
                dropped_neutrals = self.input_data.reset_index().rename(
                    columns={"index": "Date"}
                )
                dropped_neutrals = dropped_neutrals.drop(
                    dropped_neutrals[dropped_neutrals[col_prefix + "_Sent"] == 0].index
                )
                if "VADER" in col:
                    AvgScr_In = self.input_data.pivot_table(
                        values=col, index=["Date"], aggfunc="mean"
                    )
                    AvgScr_In[col_score_In] = AvgScr_In[col]
                    AvgScr_Ex = dropped_neutrals.pivot_table(
                        values=col, index=["Date"], aggfunc="mean"
                    )
                    AvgScr_Ex[col_score_Ex] = AvgScr_Ex[col]

                if "BERT" in col:
                    self.input_data[col_score_In] = (
                        self.input_data[col] * self.input_data[col_prefix + "_Sent"]
                    )
                    dropped_neutrals[col_score_Ex] = (
                        dropped_neutrals[col] * dropped_neutrals[col_prefix + "_Sent"]
                    )
                    AvgScr_In = self.input_data.pivot_table(
                        values=col_score_In, index=["Date"], aggfunc="mean"
                    )
                    AvgScr_Ex = dropped_neutrals.pivot_table(
                        values=col_score_Ex, index=["Date"], aggfunc="mean"
                    )

                self.transformed_data[col_score_In] = AvgScr_In[col_score_In]
                self.transformed_data[col_sent_In] = self.transformed_data[
                    col_score_In
                ].swifter.apply(vsa.determine_sentiment)
                self.transformed_data[col_score_Ex] = AvgScr_Ex[col_score_Ex]
                self.transformed_data[col_sent_Ex] = self.transformed_data[
                    col_score_Ex
                ].swifter.apply(vsa.determine_sentiment)

    def _generate_price_features(self) -> None:
        """
        Generate price features based on the input data

        Returns:
            None
        """
        self.transformed_data = self.input_data
        prefix = self.transformed_data.columns[0].split("_")[0]
        columns = [
            col
            for col in self.transformed_data.columns
            if ("YF_Op" in col)
            or ("YF_Hi" in col)
            or ("YF_Lo" in col)
            or ("YF_Cls" in col)
        ]
        self.transformed_data[prefix + "_D_AvgPrc"] = self.transformed_data[
            columns
        ].mean(axis=1)
        if prefix == "ETH":
            self.transformed_data["ETH_D_PrcDir"] = np.sign(
                self.transformed_data["ETH_D_AvgPrc"].diff()
            )
            self.transformed_data = self.transformed_data[
                ["ETH_D_PrcDir"]
                + [
                    col
                    for col in self.transformed_data.columns
                    if col not in ["ETH_D_PrcDir"]
                ]
            ]
        self.transformed_data = self.transformed_data[
            [prefix + "_D_AvgPrc"]
            + [
                col
                for col in self.transformed_data.columns
                if col != (prefix + "_D_AvgPrc")
            ]
        ]
        return self.transformed_data
