from pathlib import Path
import pandas as pd
import numpy as np
import logging
from src.common.stats import adf_test, StationarityTests
from src.preprocessing.feature_generator import FeatureGenerator

logger = logging.getLogger(__name__)


class DataLoader:
    def __init__(self, root_dir: Path):
        """Initialize DataLoader object."""
        self.root_dir = root_dir
        self.ETH = None
        self.BTC = None
        self.LTC = None
        self.sentiment_analysis = None
        self.final_data = None
        self.train = None
        self.test = None
        self.val = None

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

    def merge_selected_data(self, selected_data: list[str]) -> None:
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
                sentiment_features = fg.generate_features()
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
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
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

    def make_stationary(self, alpha=0.05, max_diffs=5) -> None:
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

    def lag_features(self, exclude_cols: list[str], lag: int = 1) -> None:
        """
        Add lagged features to the dataset.

        Parameters:
            exclude_cols (list): Columns to exclude from lagging.
            lag (int): Number of lags to apply.

        Returns:
            None
        """
        if lag is None:
            pass
        elif isinstance(lag, int) and lag > 0:
            columns_to_lag = [
                col for col in self.final_data.columns if col not in exclude_cols
            ]
            self.final_data[columns_to_lag] = self.final_data[columns_to_lag].shift(lag)
            self.final_data.dropna(inplace=True)
            logger.info(f"Lagged features by {lag} day(s).")
        else:
            logger.error("lag must be a positive integer.")
            raise ValueError("lag must be a positive integer.")

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

    def data_split(
        self, split_type: str = "test_train", split_size: float = 0.2
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
        if split_type not in ["test_train", "train_val"]:
            logger.error("split_type must be 'test_train' or 'train_val'.")
            raise ValueError("split_type must be 'test_train' or 'train_val'.")
        elif split_type == "test_train":
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

    # def train_val_split(self, cv_method:str="static", train_size:int=30, val_size:int=):
    #     """Split dataset into training and test sets for cross-validation."""
    #     n_samples = len(self.train)

    #     if cv_method == "rolling":
    #         for start in range(n_samples - train_size - val_size + 1):
    #             train_idx = np.arange(start, start + train_size)
    #             val_idx = np.arange(start + train_size, start + train_size + val_size)
    #             yield self.train[train_idx], self.train[val_idx]

    #     elif cv_method == "expanding":
    #         for end in range(train_size, n_samples - val_size + 1):
    #             train_idx = np.arange(0, end)
    #             val_idx = np.arange(end, end + val_size)
    #             yield self.train[train_idx], self.train[val_idx]

    #     elif cv_method == "static":
    #         train_idx = np.arange(0, n_samples - val_size)
    #         val_idx = np.arange(n_samples - val_size, n_samples)
    #         yield self.train[train_idx], self.train[val_idx]

    #     else:
    #         raise ValueError("cv_method must be 'rolling', 'expanding', or 'static'.")
