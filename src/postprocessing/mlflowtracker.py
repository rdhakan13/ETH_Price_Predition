import mlflow
import os
import shutil
import pandas as pd
from typing import Any


class MLflowTracker:
    def __init__(
        self,
        run_name: str,
        tracking_ui: str = "sqlite:///mlflow.db",
        experiment_name: str = "default_experiment",
    ):
        """
        Initialize the MLflow tracking class.

        Parameters:
            run_name (str): Name of the MLflow run.
            tracking_ui (str): URI for the MLflow tracking server. Default is a local SQLite database.
            experiment_name (str): Name of the MLflow experiment. Default is "default_experiment".
        """
        mlflow.set_tracking_uri(tracking_ui)
        mlflow.set_experiment(experiment_name)
        self.run = mlflow.start_run(run_name=run_name)

    def log_params(self, params: dict[str, Any]) -> None:
        """
        Log multiple parameters to MLflow.

        Parameters:
            params (dict): Dictionary of parameters to log.

        Returns:
            None
        """
        mlflow.log_params(params)

    def log_metrics(self, metrics: dict[str, Any]) -> None:
        """
        Log multiple metrics to MLflow.

        Parameters:
            metrics (dict): Dictionary of metrics to log.

        Returns:
            None
        """
        mlflow.log_metrics(metrics)

    def log_dataset(self, dataset, dataset_name: str = "dataset.csv") -> None:
        """
        Log a dataset as an artifact in MLflow.

        Parameters:
            dataset (pd.DataFrame): The dataset to log.
            dataset_name (str): Name of the dataset file. Default is "dataset.csv".

        Returns:
            None
        """
        temp_dir = "mlflow_temp"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, dataset_name)
        dataset.to_csv(file_path, index=False)
        mlflow.log_artifact(file_path)
        shutil.rmtree(temp_dir)  # Clean up temp directory

    def end_run(self) -> None:
        """
        End the MLflow run.

        Returns:
            None
        """
        mlflow.end_run()
