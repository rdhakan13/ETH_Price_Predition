from abc import abstractmethod
import pandas as pd
from sklearn.metrics import root_mean_squared_error, mean_squared_error, mean_absolute_percentage_error, mean_absolute_error
from tabulate import tabulate
import logging

logger = logging.getLogger(__name__)


class Model:
    def __init__(self, params: dict):
        """
        Initialize the model.
        """
        self.params = params
        self.y_pred = None
        self.tbl_args = {"headers": "keys", "tablefmt": "simple", "floatfmt": ".2f"}

    @abstractmethod
    def fit(self, x_train: pd.DataFrame, y_train:pd.DataFrame):
        """
        Fit the model to the training data.
        
        Parameters:
            x_train (pd.DataFrame): The features of the training data.
            y_train (pd.DataFrame): The target variable of the training data.
        
        Returns:
            None
        """
        pass

    @abstractmethod
    def predict(self, x_test:pd.DataFrame, x_val:pd.DataFrame):
        """
        Make predictions on the test data.

        Parameters:
            x_test (pd.DataFrame): The features of the test data.

        Returns:
            None
        """
        pass
    
    def evaluate(self, y_true: pd.DataFrame)->dict:
        """
        Calculate RMSE, MSE, MAPE, and MAE between actual and predicted values.

        Parameters:
            y_true (pd.DataFrame): The actual values.

        Returns:
            dict: A dictionary containing the errors.
        """
        errors = {
            "MSE": mean_squared_error(y_true, self.y_pred),
            "RMSE": root_mean_squared_error(y_true, self.y_pred, squared=False),
            "MAE": mean_absolute_error(y_true, self.y_pred),
            "MAPE": mean_absolute_percentage_error(y_true, self.y_pred),
        }

        table = [(key, value) for key, value in errors.items()]
        logger.info(tabulate(table, **self.tbl_args))
        return errors