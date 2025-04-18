import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.common.stats import adf_test, pp_test, grangers_causality_test, StationarityTests

# Sample test data
data = {
    'A': [1, 2, 3, 4, 5],
    'B': [2, 3, 4, 5, 6],
    'C': [5, 4, 3, 2, 1]
}

df = pd.DataFrame(data)

@patch('src.common.stats.adfuller')
def test_adf_test(mock_adfuller):
    mock_adfuller.return_value = (1.23, 0.03, 3, 100, {'1%': -2.5, '5%': -1.5, '10%': -1.0})
    result: StationarityTests = adf_test(df[['A']], alpha=0.05)
    assert isinstance(result, StationarityTests)
    assert result.is_stationary is True
    assert result.result["ADF Statistic"] == 1.23
    assert result.result["p-value"] == 0.03
    assert result.result["Critical Values"] == {'1%': -2.5, '5%': -1.5, '10%': -1.0}


@patch('src.common.stats.PhillipsPerron')
def test_pp_test(mock_pp):
    mock_pp.return_value.pvalue = 0.03
    mock_pp.return_value.stat = 1.5
    mock_pp.return_value.critical_values = {'1%': -3.0, '5%': -2.0, '10%': -1.5}
    result: StationarityTests = pp_test(df[['A']], alpha=0.05)
    assert isinstance(result, StationarityTests)
    assert result.is_stationary is True
    assert result.result["PP Statistic"] == 1.5
    assert result.result["p-value"] == 0.03
    assert result.result["Critical Values"] == {'1%': -3.0, '5%': -2.0, '10%': -1.5}
