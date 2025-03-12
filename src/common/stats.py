from statsmodels.tsa.stattools import adfuller


def adf_test(series, alpha=0.05):
    """
    Perform Augmented Dickey-Fuller (ADF) test for stationarity.

    :param series: Pandas Series to test.
    :param alpha: Significance level (default 0.05).
    :return: Boolean (True if stationary, False otherwise) and test result dictionary.
    """
    result = adfuller(series)
    p_value = result[1]
    is_stationary = p_value < alpha
    return is_stationary, {
        "ADF Statistic": result[0],
        "p-value": p_value,
        "Critical Values": result[4],
    }
