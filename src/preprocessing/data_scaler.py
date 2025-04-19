from sklearn.preprocessing import MinMaxScaler, StandardScaler
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataScaler:
    def __init__(self, scaling_methods: dict, columns: list):
        """
        Initialize the data scaler with target columns and scaling methods.

        Parameters:
            scaling_methods(dict): Dictionary of target columns and scaling methods.
            columns(list): List of target columns to scale.

        Attributes:
            columns(list): List of target columns to scale.
            scaling_methods(dict): Dictionary of target columns and scaling methods.
            scalers(dict): Dictionary to hold scalers for each target column.
            minmax_scalers(dict): Store Min-Max scalers for final step.
        """
        self.columns = columns
        self.scaling_methods = scaling_methods
        self.scalers = {}
        self.minmax_scalers = {}

    def fit(self, df: pd.DataFrame):
        """
        Fit the scalers to the target columns in the DataFrame.

        Parameters:
            df(pd.DataFrame): The DataFrame to fit the scalers to.

        Returns:
            None
        """
        for col in self.columns:
            if col not in df.columns:
                continue
            method = self.scaling_methods.get(col, None)

            if method == "minmax":
                scaler = MinMaxScaler()
            elif method == "standard":
                scaler = StandardScaler()
            elif method == "log":
                scaler = "log"
            else:
                raise ValueError(f"Unknown scaling method for {col}: {method}")

            if method in ["minmax", "standard"]:
                scaler.fit(df[[col]])

            self.scalers[col] = scaler

            minmax_scaler = MinMaxScaler()
            transformed_col = self._apply_transformation(
                df[[col]], scaler, method
            )
            minmax_scaler.fit(transformed_col)
            self.minmax_scalers[col] = minmax_scaler

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the DataFrame using the fitted scalers.

        Parameters:
            df(pd.DataFrame): The DataFrame to transform.

        Returns:
            pd.DataFrame: The transformed DataFrame.
        """
        df_scaled = df.copy()
        for col in df.columns:
            scaler = self.scalers.get(col, None)
            minmax_scaler = self.minmax_scalers.get(col, None)
            method = self.scaling_methods.get(col, None)

            if scaler is None or minmax_scaler is None:
                continue

            transformed = self._apply_transformation(
                df[[col]], scaler, method
            )
            df_scaled[col] = minmax_scaler.transform(transformed)

        return df_scaled

    def inverse_transform(self, df_scaled: pd.DataFrame) -> pd.DataFrame:
        """
        Inverse transform the DataFrame using the fitted scalers.

        Parameters:
            df_scaled(pd.DataFrame): The DataFrame to inverse transform.

        Returns:
            pd.DataFrame: The inverse transformed DataFrame.
        """
        df_original = df_scaled.copy()
        for col in df_scaled.columns:
            scaler = self.scalers.get(col, None)
            minmax_scaler = self.minmax_scalers.get(col, None)
            method = self.scaling_methods.get(col, None)

            if scaler is None or minmax_scaler is None:
                continue

            unscaled = minmax_scaler.inverse_transform(
                df_scaled[[col]]
            )

            df_original[col] = self._reverse_transformation(
                pd.DataFrame(unscaled, columns=[col]), scaler, method
            )

        return df_original

    @staticmethod
    def _apply_transformation(col_values: pd.DataFrame, scaler, method) -> pd.DataFrame:
        """
        Apply the transformation to the DataFrame column values.

        Parameters:
            col_values(pd.DataFrame): The DataFrame column values to transform.
            scaler: The fitted scaler object.
            method(str): The scaling method to apply.

        Returns:
            pd.DataFrame: The transformed DataFrame column values.
        """
        if method == "log":
            transformed = np.log1p(col_values)
        elif method in ["minmax", "standard"]:
            transformed = pd.DataFrame(
                scaler.transform(col_values), columns=col_values.columns
            )
        else:
            raise ValueError(f"Unknown scaling method: {method}")

        return transformed

    @staticmethod
    def _reverse_transformation(
        transformed_values: pd.DataFrame, scaler, method
    ) -> pd.DataFrame:
        """
        Reverse the transformation of the DataFrame column values.

        Parameters:
            transformed_values(pd.DataFrame): The transformed DataFrame column values.
            scaler: The fitted scaler object.
            method(str): The scaling method to reverse.

        Returns:
            pd.DataFrame: The inverse transformed DataFrame column values.
        """
        if method == "log":
            return np.expm1(transformed_values)
        elif method in ["minmax", "standard"]:
            return pd.DataFrame(
                scaler.inverse_transform(transformed_values),
                columns=transformed_values.columns,
            )
        else:
            raise ValueError(f"Unknown scaling method: {method}")
