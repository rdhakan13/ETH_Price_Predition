import mlflow
import os
import shutil
import pandas as pd

class MLflowTracker:
    def __init__(self, tracking_ui:str="sqlite:///mlflow.db", 
                 experiment_name:str="default_experiment", run_name:str=None):
        """
        Initialize the MLflow tracking class.
        
        :param experiment_name: Name of the MLflow experiment.
        :param run_name: Optional name for the MLflow run.
        """
        mlflow.set_tracking_uri(tracking_ui)
        mlflow.set_experiment(experiment_name)
        self.run = mlflow.start_run(run_name=run_name)
        
    def log_params(self, params: dict):
        """Log multiple parameters to MLflow."""
        mlflow.log_params(params)
        
    def log_metrics(self, metrics: dict):
        """Log multiple metrics to MLflow."""
        mlflow.log_metrics(metrics)
        
    def log_dataset(self, dataset, dataset_name:str="dataset.csv"):
        """
        Log a dataset as an artifact in MLflow.
        
        :param dataset: The dataset to be logged. Assumed to be a pandas DataFrame.
        :param dataset_name: The filename to store the dataset.
        """
        temp_dir = "mlflow_temp"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, dataset_name)
        dataset.to_csv(file_path, index=False)
        mlflow.log_artifact(file_path)
        shutil.rmtree(temp_dir)  # Clean up temp directory
        
    def end_run(self):
        """End the MLflow run."""
        mlflow.end_run()