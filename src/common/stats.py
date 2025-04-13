import logging
from ensure import ensure_annotations
import pandas as pd
from statsmodels.tsa.stattools import adfuller, grangercausalitytests
from arch.unitroot import PhillipsPerron

logger = logging.getLogger(__name__)

class StationarityTests:
    is_stationary: bool
    result: dict

@ensure_annotations
def adf_test(series: pd.DataFrame, alpha:float=0.05)->StationarityTests:
    """
    Perform Augmented Dickey-Fuller test on a time series.

    Parameters:
        series (pd.DataFrame): The time series to be tested.
        alpha (float): The significance level.

    Returns:
        ADF: A named tuple containing the test result and whether the series is stationary.
    """
    try:
        result = adfuller(series)
    except ValueError as e:
        logger.error(f"Error in ADF test: {e}")
        raise ValueError("ADF test failed. Please check the input series.")
    is_stationary = result[1] < alpha
    stationarity_result = StationarityTests()
    stationarity_result.is_stationary = is_stationary
    stationarity_result.result = {
        "ADF Statistic": result[0],
        "p-value": result[1],
        "Critical Values": result[4],
    }
    return stationarity_result

@ensure_annotations
def pp_test(series: pd.DataFrame, alpha:float=0.05)->StationarityTests:
    """
    Perform Phillips-Perron test on a time series.

    Parameters:
        series (pd.DataFrame): The time series to be tested.
        alpha (float): The significance level.

    Returns:
        dict: A dictionary containing the test result.
    """
    try:
        pp_test = PhillipsPerron(series)
    except ValueError as e:
        logger.error(f"Error in PP test: {e}")
        raise ValueError("PP test failed. Please check the input series.")
    
    is_stationary = pp_test.pvalue < alpha
    stationarity_result = StationarityTests()
    stationarity_result.is_stationary = is_stationary
    stationarity_result.result = {
        "PP Statistic": pp_test.stat,
        "p-value": pp_test.pvalue,
        "Critical Values": pp_test.critical_values,
    }
    return stationarity_result

@ensure_annotations
def grangers_causality_test(df:pd.DataFrame, target_col:str, max_lag:int=5, alpha:float=0.05)->dict:
    """
    Perform Granger's Causality test for each column in a DataFrame against a specified target column.
    
    Parameters:
        df (pd.DataFrame): The DataFrame containing the target and feature columns.
        target_col (str): The target column to test against.
        max_lag (int): The maximum number of lags to consider.
        significance (float): The significance level for the test.
    
    Returns:
        dict: A dictionary containing the test results.
    """
    results = {}
    for col in df.columns:
        if col == target_col:
            continue 
        
        try:
            test_result = grangercausalitytests(df[[target_col, col]].dropna(), max_lag, verbose=False)
        except Exception as e:
            logger.error(f"Error in Granger's Causality test for {col}: {e}")
            raise ValueError(f"Granger's Causality test failed for {col}. Please check the input data.")
        
        p_values = {lag: test_result[lag][0]['ssr_chi2test'][1] for lag in range(1, max_lag + 1)}
        
        significant_lags = [lag for lag, p in p_values.items() if p < alpha]
        
        results[col] = {
            'Causal': len(significant_lags) > 0, 
            'Significant Lags': significant_lags
            }
    
    return results