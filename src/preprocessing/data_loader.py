from pathlib import Path
import pandas as pd
import numpy as np
import logging
from src.common.stats import adf_test, StationarityTests
from src.preprocessing.feature_generator import FeatureGenerator
from typing import Optional

logger = logging.getLogger(__name__)


class DataLoader:
    def __init__(self, root_dir: Path):
        """Initialize DataLoader object."""
        self.root_dir = root_dir
        self.ETH: pd.DataFrame = None
        self.BTC: pd.DataFrame = None
        self.LTC: pd.DataFrame = None
        self.sentiment_analysis: pd.DataFrame = None
        self.final_data: pd.DataFrame = None
        self.train: pd.DataFrame = None
        self.test: pd.DataFrame = None
        self.val: pd.DataFrame = None

    def load_data(self) -> None:
        """
        Load data from CSV files.

        Returns:
            None
        """
        logger.info("Loading data...")
        self.ETH = pd.read_csv(
            f"{self.root_dir}\\data\\final\\ETH.csv", index_col="Date", parse_dates=True
        )
        self.BTC = pd.read_csv(
            f"{self.root_dir}\\data\\final\\BTC.csv", index_col="Date", parse_dates=True
        )
        self.LTC = pd.read_csv(
            f"{self.root_dir}\\data\\final\\LTC.csv", index_col="Date", parse_dates=True
        )
        self.sentiment_analysis = pd.read_csv(
            f"{self.root_dir}\\data\\final\\sentiment_analysis.csv",
            index_col="Date",
            parse_dates=True,
        )
        self.ETH.columns = [f"ETH_{col}" for col in self.ETH.columns]
        fg = FeatureGenerator(input_data=self.ETH, data_tag="price")
        price_features = fg.generate_features()
        self.final_data = price_features.dropna()
        logger.info("Data loaded successfully.")

    def merge_selected_data(self, selected_data: list[str], select_publishers: Optional[list[str]] = None) -> None:
        """Handle missing values, encode categorical features, normalize data."""
        logger.info("Merging selected data...")
        if selected_data is None:
            pass
        elif not isinstance(selected_data, list):
            raise ValueError("selected_data must be a list.")
        else:
            if "BTC" in selected_data:
                self.BTC.columns = [f"BTC_{col}" for col in self.BTC.columns]
                fg = FeatureGenerator(input_data=self.BTC, data_tag="price")
                price_features = fg.generate_features()
                self.final_data = self.final_data.merge(
                    price_features, how="outer", on="Date"
                )
            if "LTC" in selected_data:
                self.LTC.columns = [f"LTC_{col}" for col in self.LTC.columns]
                fg = FeatureGenerator(input_data=self.LTC, data_tag="price")
                price_features = fg.generate_features()
                self.final_data = self.final_data.merge(
                    price_features, how="outer", on="Date"
                )
            if "sentiment_analysis" in selected_data:
                fg = FeatureGenerator(
                    input_data=self.sentiment_analysis, data_tag="sentiment"
                )
                sentiment_features = fg.generate_features(select_publishers=select_publishers)
                self.final_data = self.final_data.merge(
                    sentiment_features.replace(np.nan, 0), how="outer", on="Date"
                )
        logger.info("Data merged successfully.")

    def set_time_range(self, start_date: str, end_date: str) -> None:
        """
        Set time range for dataset.

        Parameters:
            start_date (str): Start date in "YYYY-MM-DD" format.
            end_date (str): End date in "YYYY-MM-DD" format.

        Returns:
            None
        """
        try:
            start_date = pd.to_datetime(start_date, dayfirst=True)
            end_date = pd.to_datetime(end_date, dayfirst=True)
        except ValueError as e:
            logger.error(f"ValueError: {e}.")
            raise e
        if start_date is not None and end_date is not None and start_date > end_date:
            raise ValueError("start_date must be before end_date.")
        if start_date is None or start_date < self.final_data.index.min():
            logger.warning(
                "start_date is before the earliest date in the dataset, setting to the earliest date."
            )
            start_date = self.final_data.dropna().index.min()
        if end_date is None or end_date > self.final_data.index.max():
            logger.warning(
                "end_date is after the latest date in the dataset, setting to the latest date."
            )
            end_date = self.final_data.dropna().index.max()
        self.final_data = self.final_data.loc[start_date:end_date]
        logger.info(f"Time range set to {start_date} to {end_date}.")

    def make_stationary(self, alpha: float = 0.05, max_diffs: int = 5) -> None:
        """
        Iterates through each column in a DataFrame and differences it until it
        becomes stationary based on the Augmented Dickey-Fuller (ADF) test.

        Parameters:
            alpha: Significance level for the ADF test (default 0.05).
            max_diffs: Maximum number of differences to apply (default 5).

        Returns:
            None
        """
        diff_counts = {}

        for col in self.final_data.columns:
            series = self.final_data[col].dropna()
            diff_count = 0

            while diff_count < max_diffs:
                stationarity_result = adf_test(series)

                if stationarity_result.is_stationary:
                    break

                series = series.diff().dropna()
                diff_count += 1

            self.final_data[col] = series
            diff_counts[col] = diff_count
            logger.info(
                f"{col} differenced {diff_count} times to achieve stationarity."
            )

    def lag_features(self, lag_config:dict[str,int], target_col:str='ETH_D_AvgPrc') -> None:
        """
        Add lagged features to the dataset.

        Parameters:
            lag_config (dict): Dictionary where keys are column names and values are the number of lags to apply.
            target_col (str): The target variable.

        Returns:
            None
        """
        for col in self.final_data.columns:
            if col not in lag_config:
                logger.warning(f"Column {col} not found in lag_config, removing the column from the dataset.")
                self.final_data.drop(columns=[col], inplace=True)
        for col, n_lags in lag_config.items():
            if col not in self.final_data.columns:
                logger.warning(f"Column {col} not found in the dataset, skipping.")
                continue
            if n_lags is None or n_lags <= 0:
                logger.warning(f"No lags specified for {col}, skipping.")
                continue
            for lag in range(1, n_lags + 1):
                self.final_data[f"{col}_lag_{lag}"] = self.final_data[col].shift(lag)
            logger.info(f"Added {n_lags} lag(s) for column {col}.")
            if col != target_col:
                self.final_data.drop(columns=[col], inplace=True)

    def generate_forecast_horizon(self, target_col:str='ETH_D_AvgPrc', horizon:int=10) -> None:
        """
        Add forecast horizon features to the dataset.

        Parameters:
            target_col (str): The target variable.
            horizon (int): The number of periods to forecast.

        Returns:
            None
        """
        if horizon is None or horizon <= 0:
            logger.warning("Horizon must be a positive integer, setting to 1.")
            horizon = 1
        horizon = horizon - 1 # to account horizon 0
        if target_col not in self.final_data.columns:
            logger.error(f"Target column {target_col} not found in the dataset.")
            raise ValueError(f"Target column {target_col} not found in the dataset.")
        if horizon > 0:
            for h in range(1, horizon + 1):
                self.final_data[f"{target_col}_horizon_{h}"] = self.final_data[target_col].shift(-h)
        self.final_data = self.final_data.rename(columns={target_col: f"{target_col}_horizon_0"})
        logger.info(f"Added forecast horizon features for {horizon} periods.")

    def select_features(self, features: list[str]) -> None:
        """
        Select features to include in the model.

        Parameters:
            features (list): List of feature names to include.

        Returns:
            None
        """
        if features is None:
            features = self.final_data.columns
        try:
            self.final_data = self.final_data[features]
            logger.info(f"Selected features: {features}.")
        except KeyError as e:
            logger.error(f"KeyError: {e}.")
            raise e

    def split_data(
        self, split_type: str = "train_test", split_size: float = 0.2
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split dataset into training and test sets or training and validation sets.

        Parameters:
            split_type (str): Type of split ("test_train" or "train_val").
            split_size (float): Proportion of the dataset to include in the test/val split.

        Returns:
            tuple: Train and test/validation sets.
        """
        if not isinstance(split_size, float) or not (0 < split_size < 1):
            logger.error("test_size must be a float between 0 and 1.")
            raise ValueError("test_size must be a float between 0 and 1.")
        if split_type not in ["train_test", "train_val"]:
            logger.error("split_type must be 'test_train' or 'train_val'.")
            raise ValueError("split_type must be 'test_train' or 'train_val'.")
        elif split_type == "train_test":
            count = int(len(self.final_data) * split_size)
            self.train = self.final_data[:-count]
            self.test = self.final_data[-count:]
            return self.train, self.test
        elif split_type == "train_val" and self.train is not None:
            count = int(len(self.train) * split_size)
            self.val = self.train[-count:]
            self.train = self.train[:-count]
            return self.train, self.val
        else:
            logger.error("Please set the train data first.")
            raise ValueError("Please set the train data first.")
