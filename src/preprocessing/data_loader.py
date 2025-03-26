from pathlib import Path
import pandas as pd
import numpy as np
import logging
from src.common.stats import adf_test
from src.preprocessing.feature_generator import FeatureGenerator

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, root_dir:Path):
        """Initialize DataLoader object."""
        self.root_dir = root_dir    
        self.ETH = None
        self.BTC = None
        self.LTC = None
        self.sentiment_analysis = None
        self.final_data = None
        self.train = None
        self.test = None

    def load_data(self):
        """
        Load data from CSV files.

        Returns:
            None
        """
        logger.info("Loading data...")
        self.ETH = pd.read_csv(f"{self.root_dir}\\data\\final\\ETH.csv", index_col="Date", parse_dates=True)
        self.BTC = pd.read_csv(f"{self.root_dir}\\data\\final\\BTC.csv", index_col="Date", parse_dates=True)
        self.LTC = pd.read_csv(f"{self.root_dir}\\data\\final\\LTC.csv", index_col="Date", parse_dates=True)
        self.sentiment_analysis = pd.read_csv(f"{self.root_dir}\\data\\final\\sentiment_analysis.csv", index_col="Date", parse_dates=True)
        self.ETH.columns = [f"ETH_{col}" for col in self.ETH.columns]
        self.final_data = self.ETH
        logger.info("Data loaded successfully.")

    def merge_selected_data(self, selected_data:list=["ETH"]):
        """Handle missing values, encode categorical features, normalize data."""
        logger.info("Merging selected data...")
        if selected_data is None:
            raise ValueError("selected_data cannot be None.")
        if "BTC" in selected_data:
            self.BTC.columns = [f"BTC_{col}" for col in self.BTC.columns]
            self.final_data = self.final_data.merge(self.BTC, how="outer", on="Date")
        if "LTC" in selected_data:
            self.LTC.columns = [f"LTC_{col}" for col in self.LTC.columns]
            self.final_data = self.final_data.merge(self.LTC, how="outer", on="Date")
        if "sentiment_analysis" in selected_data:
            FG = FeatureGenerator(self.sentiment_analysis, "sentiment")
            sentiment_features = FG.generate_features()
            self.final_data = self.final_data.merge(sentiment_features, how="outer", on="Date")
        logger.info("Data merged successfully.")

    def set_time_range(self, start_date:str, end_date:str):
        """
        Set time range for dataset.
        
        Parameters:
            start_date (str): Start date in "YYYY-MM-DD" format.
            end_date (str): End date in "YYYY-MM-DD" format.

        Returns:
            None
        """
        if start_date > end_date:
            raise ValueError("start_date must be before end_date.")
        if start_date < self.final_data.index.min() or start_date is None:
            logger.warning("start_date is before the earliest date in the dataset, setting to the earliest date.")
            start_date = self.final_data.index.min()
        if end_date > self.final_data.index.max() or end_date is None:
            logger.warning("end_date is after the latest date in the dataset, setting to the latest date.")
            end_date = self.final_data.index.max()
        self.final_data = self.final_data.loc[start_date:end_date]
        logger.info(f"Time range set to {start_date} to {end_date}.")

    def make_stationary(self, alpha=0.05, max_diffs=5):
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
                is_stationary, _ = adf_test(series)
                
                if is_stationary:
                    break
                
                series = series.diff().dropna() 
                diff_count += 1
            
            self.final_data[col] = series
            diff_counts[col] = diff_count
            logger.info(f"{col} differenced {diff_count} times to achieve stationarity.")

    def lag_features(self, exclude_cols:list, lag:int=1):
        """
        Add lagged features to the dataset.

        Parameters:
            exclude_cols (list): Columns to exclude from lagging.
            lag (int): Number of lags to apply.
        
        Returns:
            None
        """
        columns_to_lag = [col for col in self.final_data.columns if col not in exclude_cols]
        self.final_data[columns_to_lag] = self.final_data[columns_to_lag].shift(lag)
        self.final_data.dropna(inplace=True)
        logger.info(f"Lagged features by {lag} day(s).")

    def select_features(self, features:list):
        """
        Select features to include in the model.
        
        Parameters:
            features (list): List of feature names to include.

        Returns:
            None
        """
        if features is None:
            features = self.final_data.columns
        self.final_data = self.final_data[features]
        logger.info(f"Selected features: {features}.")

    def test_train_split(self, test_size:float=0.2):
        """
        Split dataset into training and test sets.
        
        Parameters:
            test_size (float): Proportion of the dataset to include in the test split.
        
        Returns:
            None
        """
        if not (0 < test_size < 1):
            raise ValueError("test_size must be a float between 0 and 1.")
        test_count = int(len(self.final_data) * test_size)  # Calculate number of test samples
        self.train = self.final_data[:-test_count]
        self.test = self.final_data[-test_count:]
        logger
        return self.train, self.test

    def train_val_split(self, cv_method:str="static", train_size:int=30, val_size:int=):
        """Split dataset into training and test sets for cross-validation."""
        n_samples = len(self.train)

        if cv_method == "rolling":
            for start in range(n_samples - train_size - val_size + 1):
                train_idx = np.arange(start, start + train_size)
                val_idx = np.arange(start + train_size, start + train_size + val_size)
                yield self.train[train_idx], self.train[val_idx]

        elif cv_method == "expanding":
            for end in range(train_size, n_samples - val_size + 1):
                train_idx = np.arange(0, end)
                val_idx = np.arange(end, end + val_size)
                yield self.train[train_idx], self.train[val_idx]

        elif cv_method == "static":
            train_idx = np.arange(0, n_samples - val_size)
            val_idx = np.arange(n_samples - val_size, n_samples)
            yield self.train[train_idx], self.train[val_idx]

        else:
            raise ValueError("cv_method must be 'rolling', 'expanding', or 'static'.")