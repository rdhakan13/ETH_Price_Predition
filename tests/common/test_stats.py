import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.common.stats import adf_test, pp_test, grangers_causality_test, StationarityTests

data = {
    'A': [1, 2, 3, 4, 5],
    'B': [2, 3, 4, 5, 6],
    'C': [5, 4, 3, 2, 1]
}

df = pd.DataFrame(data)

stationary_series = pd.DataFrame([1.2, 1.1, 1.3, 1.1, 1.2])
non_stationary_series = pd.DataFrame([1, 2, 3, 4, 5])

mock_stationary_result = (-3.5, 0.03, 0, 4, {"1%": -3.75, "5%": -3.0, "10%": -2.5}, 0)
mock_non_stationary_result = (-1.2, 0.6, 0, 4, {"1%": -3.75, "5%": -3.0, "10%": -2.5}, 0)

@patch("src.common.stats.adfuller")
def test_adf_test_stationary(mock_adf):
    mock_adf.return_value = mock_stationary_result
    result = adf_test(stationary_series)
    
    assert isinstance(result, StationarityTests)
    assert result.is_stationary is True
    assert "ADF Statistic" in result.result
    assert "p-value" in result.result
    assert "Critical Values" in result.result

@patch("src.common.stats.adfuller")
def test_adf_test_non_stationary(mock_adf):
    mock_adf.return_value = mock_non_stationary_result
    result = adf_test(non_stationary_series)
    
    assert isinstance(result, StationarityTests)
    assert result.is_stationary is False
    assert result.result["p-value"] == 0.6

@patch("src.common.stats.adfuller")
def test_adf_test_failure_raises_value_error(mock_adf):
    mock_adf.side_effect = ValueError("bad input")

    with pytest.raises(ValueError, match="ADF test failed"):
        adf_test(pd.DataFrame([]))

@patch("src.common.stats.PhillipsPerron")
def test_pp_test_stationary(mock_pp):
    mock_instance = MagicMock()
    mock_instance.pvalue = 0.03
    mock_instance.stat = -3.7
    mock_instance.critical_values = {"1%": -3.75, "5%": -3.0, "10%": -2.5}
    mock_pp.return_value = mock_instance
    result = pp_test(stationary_series)
    assert isinstance(result, StationarityTests)
    assert result.is_stationary is True
    assert result.result["p-value"] == 0.03
    assert "PP Statistic" in result.result
    assert "Critical Values" in result.result

@patch("src.common.stats.PhillipsPerron")
def test_pp_test_non_stationary(mock_pp):
    mock_instance = MagicMock()
    mock_instance.pvalue = 0.6
    mock_instance.stat = -1.2
    mock_instance.critical_values = {"1%": -3.75, "5%": -3.0, "10%": -2.5}
    mock_pp.return_value = mock_instance
    result = pp_test(non_stationary_series)
    assert isinstance(result, StationarityTests)
    assert result.is_stationary is False
    assert result.result["p-value"] == 0.6

@patch("src.common.stats.PhillipsPerron")
def test_pp_test_failure(mock_pp):
    mock_pp.side_effect = ValueError("bad input")

    with pytest.raises(ValueError, match="PP test failed"):
        pp_test(pd.Series([]))  # any invalid input

mock_result_causal = {
    1: {0: {'ssr_chi2test': (0, 0.01)}},
    2: {0: {'ssr_chi2test': (0, 0.03)}}
}

mock_result_non_causal = {
    1: {0: {'ssr_chi2test': (0, 0.6)}},
    2: {0: {'ssr_chi2test': (0, 0.8)}}
}

@patch("src.common.stats.grangercausalitytests")
def test_grangers_causality_causal(mock_granger):
    mock_granger.side_effect = [mock_result_causal, mock_result_non_causal]

    result = grangers_causality_test(df, target_col='A', max_lag=2, alpha=0.05)

    assert 'B' in result
    assert result['B']['Causal'] is True
    assert result['B']['Significant Lags'] == [1, 2]

    assert 'C' in result
    assert result['C']['Causal'] is False
    assert result['C']['Significant Lags'] == []

@patch("src.common.stats.grangercausalitytests")
def test_grangers_causality_all_non_causal(mock_granger):
    mock_granger.return_value = mock_result_non_causal
    result = grangers_causality_test(df, target_col='A', max_lag=2, alpha=0.05)
    assert all(not v['Causal'] for v in result.values())
    assert all(v['Significant Lags'] == [] for v in result.values())

@patch("src.common.stats.grangercausalitytests")
def test_grangers_causality_raises_error(mock_granger):
    mock_granger.side_effect = Exception("bad input")
    with pytest.raises(ValueError, match="Granger's Causality test failed for B"):
        grangers_causality_test(df, target_col='A', max_lag=2, alpha=0.05)