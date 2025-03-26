from pathlib import Path
import pandas as pd
import numpy as np
import logging
from src.common.stats import adf_test

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, root_dir:Path):
        """Initialize DataLoader object."""
        self.root_dir = root_dir    
        self.ETH = None
        self.BTC = None
        self.LTC = None
        self.final_data = None
        self.train = None
        self.test = None

    def load_data(self):
        """Load dataset from CSV, JSON, or other sources."""
        logger.info("Loading data...")
        self.ETH = pd.read_csv(f"{self.root_dir}\\data\\final\\ETH.csv", index_col="Date", parse_dates=True)
        self.BTC = pd.read_csv(f"{self.root_dir}\\data\\final\\BTC.csv", index_col="Date", parse_dates=True)
        self.LTC = pd.read_csv(f"{self.root_dir}\\data\\final\\LTC.csv", index_col="Date", parse_dates=True)
        logger.info("Data loaded successfully.")

    def merge_selected_data(self):
        """Handle missing values, encode categorical features, normalize data."""
        pass

    def set_time_range(self, start_date:str, end_date:str):
        """Set time range for dataset."""
        self.final_data = self.final_data.loc[start_date:end_date]

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
        return self.train, self.test

    def train_val_split(self, cv_method:str="static", test_size:float=0.2, train_size:int=30, val_size:int=1):
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