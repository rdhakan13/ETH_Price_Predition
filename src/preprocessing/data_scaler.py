from sklearn.preprocessing import MinMaxScaler, StandardScaler, QuantileTransformer
import numpy as np
import pandas as pd
import logging
from scipy.stats import rankdata

logger = logging.getLogger(__name__)


class DataScaler:
    def __init__(self, scaling_methods: dict, target_columns: list):
        """
        Initialize the data scaler with target columns and scaling methods.

        Parameters:
            scaling_methods(dict): Dictionary of target columns and scaling methods.
            target_columns(list): List of target columns to scale.

        Attributes:
            target_columns(list): List of target columns to scale.
            scaling_methods(dict): Dictionary of target columns and scaling methods.
            scalers(dict): Dictionary to hold scalers for each target column.
            minmax_scalers(dict): Store Min-Max scalers for final step.
        """
        self.target_columns = target_columns
        self.scaling_methods = scaling_methods
        self.scalers = {}  # Dictionary to hold scalers for each target column
        self.minmax_scalers = {}  # Store Min-Max scalers for final step

    def fit(self, df: pd.DataFrame):
        """
        Fit the scalers to the target columns in the DataFrame.

        Parameters:
            df(pd.DataFrame): The DataFrame to fit the scalers to.

        Returns:
            None
        """
        for col in self.target_columns:
            if col not in df.columns:
                continue  # Skip missing columns
            method = self.scaling_methods.get(col, None)

            if method == "minmax":
                scaler = MinMaxScaler()
            elif method == "standard":
                scaler = StandardScaler()
            elif method == "log":
                scaler = "log"  # Log transformation doesn't require fitting
            elif method == "quantile":
                scaler = QuantileTransformer(
                    output_distribution="normal", n_quantiles=min(len(df), 1000)
                )
            elif method == "rank_minmax":
                scaler = MinMaxScaler()
            else:
                raise ValueError(f"Unknown scaling method for {col}: {method}")

            # Fit scaler if required
            if method in ["minmax", "standard", "quantile", "rank_minmax"]:
                scaler.fit(df[[col]])  # Keep as DataFrame to preserve feature names

            self.scalers[col] = scaler

            # Fit Min-Max scaler for final step
            minmax_scaler = MinMaxScaler()
            transformed_col = self._apply_transformation(
                df[[col]], scaler, method
            )  # Keep as DataFrame
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
        for col in df.columns:  # Iterate only over existing columns
            scaler = self.scalers.get(col, None)
            minmax_scaler = self.minmax_scalers.get(col, None)
            method = self.scaling_methods.get(col, None)

            if scaler is None or minmax_scaler is None:
                continue  # Skip missing columns

            transformed = self._apply_transformation(
                df[[col]], scaler, method
            )  # Keep as DataFrame
            df_scaled[col] = minmax_scaler.transform(transformed)  # Keep as DataFrame

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
        for col in df_scaled.columns:  # Iterate only over existing columns
            scaler = self.scalers.get(col, None)
            minmax_scaler = self.minmax_scalers.get(col, None)
            method = self.scaling_methods.get(col, None)

            if scaler is None or minmax_scaler is None:
                continue  # Skip missing columns

            # Reverse Min-Max Scaling
            unscaled = minmax_scaler.inverse_transform(
                df_scaled[[col]]
            )  # Keep as DataFrame

            # Reverse primary transformation
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
            transformed = np.log1p(col_values)  # Log transformation
        elif method in ["minmax", "standard", "quantile"]:
            transformed = pd.DataFrame(
                scaler.transform(col_values), columns=col_values.columns
            )
        elif method == "rank_minmax":
            ranked = rankdata(col_values) / len(col_values)
            transformed = pd.DataFrame(
                scaler.transform(pd.DataFrame(ranked, columns=col_values.columns)),
                columns=col_values.columns,
            )  # Rank + MinMax Scaling
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
        elif method in ["minmax", "standard", "quantile"]:
            return pd.DataFrame(
                scaler.inverse_transform(transformed_values),
                columns=transformed_values.columns,
            )
        elif method == "rank_minmax":
            ranked_reversed = scaler.inverse_transform(transformed_values)
            return pd.DataFrame(
                np.interp(
                    ranked_reversed,
                    (0, 1),
                    (transformed_values.min(), transformed_values.max()),
                ),
                columns=transformed_values.columns,
            )
        else:
            raise ValueError(f"Unknown scaling method: {method}")
