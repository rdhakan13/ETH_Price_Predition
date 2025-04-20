import os
import pytest
import pandas as pd
from unittest.mock import patch, mock_open, MagicMock
from src.data.oklink import OkLink

@pytest.fixture
def instance():
    return OkLink(root_dir="test_root", ticker="ETH")

@pytest.fixture
def sample_yf_data():
    return pd.DataFrame({
        "Date": pd.date_range("2022-01-01", periods=3),
        "Close": [100, 110, 120]
    })

@pytest.mark.parametrize("bad_ticker", [None, "", 123])
def test_invalid_ticker_raises(bad_ticker):
    with pytest.raises(ValueError, match="Ticker symbol must be a non-empty string"):
        OkLink(root_dir="test", ticker=bad_ticker)

@pytest.mark.parametrize("bad_root", [None, "", 456])
def test_invalid_root_dir_raises(bad_root):
    with pytest.raises(ValueError, match="Root directory must be a non-empty string"):
        OkLink(root_dir=bad_root, ticker="ETH")

def test_valid_constructor():
    obj = OkLink(root_dir="test", ticker="ETH")
    assert obj.ticker == "ETH"
    assert obj.raw_dir == "test\\data\\raw\\ETH_data\\oklink"
    assert obj.processed_dir == "test\\data\\processed\\ETH_data"
    assert obj.raw_data is None
    assert obj.processed_data is None

def test_process_raw_data_invalid_inputs(instance):
    with pytest.raises(ValueError, match="data_yf must be a DataFrame"):
        instance.process_raw_data(data_yf=None, date_range=pd.date_range("2022-01-01", periods=2))

    with pytest.raises(ValueError, match="date_range must be a pd.date_range object"):
        instance.process_raw_data(data_yf=pd.DataFrame(), date_range=None)

@patch("os.listdir")
@patch("pandas.read_csv")
def test_process_raw_data_logic(mock_read_csv, mock_listdir, instance, sample_yf_data):
    mock_listdir.return_value = ["oklink_data.csv"]
    oklink_df = pd.DataFrame({
        "Time": pd.date_range("2022-01-01", periods=3),
        "Value": [10, 20, 30],
    })
    mock_read_csv.return_value = oklink_df
    date_range = pd.date_range("2022-01-01", periods=3)
    instance.process_raw_data(data_yf=sample_yf_data, date_range=date_range)
    assert isinstance(instance.processed_data, pd.DataFrame)
    assert "Date" in instance.processed_data.columns
    assert "Value" in instance.processed_data.columns


@patch("src.data.oklink.make_directory")
@patch("pandas.DataFrame.to_csv")
def test_save_processed_data(mock_to_csv, mock_mkdir, instance):
    instance.processed_data = pd.DataFrame({"Date": ["2022-01-01"], "Value": [1]})
    instance.save_processed_data()
    mock_mkdir.assert_called_once_with(instance.processed_dir)
    mock_to_csv.assert_called_once_with(
        f"{instance.processed_dir}\\ETH_oklink.csv", index=False
    )
