import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.data.yahoo_finance import YahooFinance

VALID_TICKER = "BTC-USD"
VALID_ROOT_DIR = "test_project"

@pytest.fixture
def instance():
    return YahooFinance(ticker=VALID_TICKER, root_dir=VALID_ROOT_DIR)

@pytest.mark.parametrize("bad_ticker", [None, "", 123])
def test_constructor_invalid_ticker(bad_ticker):
    with pytest.raises(ValueError, match="Ticker symbol must be a non-empty string"):
        YahooFinance(ticker=bad_ticker, root_dir=VALID_ROOT_DIR)

@pytest.mark.parametrize("bad_root", [None, "", 456])
def test_constructor_invalid_root_dir(bad_root):
    with pytest.raises(ValueError, match="Root directory must be a non-empty string"):
        YahooFinance(ticker=VALID_TICKER, root_dir=bad_root)

def test_constructor_valid_inputs():
    yf = YahooFinance(ticker=VALID_TICKER, root_dir=VALID_ROOT_DIR)
    assert yf.ticker == VALID_TICKER
    assert yf.root_dir == VALID_ROOT_DIR
    assert yf.raw_dir == str(os.path.join(VALID_ROOT_DIR, "data", "raw", f"{VALID_TICKER[:3]}_data"))
    assert yf.raw_data is None
    assert yf.processed_data is None


@patch("src.data.yahoo_finance.yf.download")
def test_get_raw_data_downloads(mock_download, instance):
    df = pd.DataFrame({"Open": [1], "Close": [2]})
    mock_download.return_value = df
    instance.get_raw_data(period="5d", interval="1h")
    mock_download.assert_called_once_with(tickers=VALID_TICKER, period="5d", interval="1h")
    pd.testing.assert_frame_equal(instance.raw_data, df)

@patch("src.data.yahoo_finance.make_directory")
@patch("pandas.DataFrame.to_csv")
def test_save_raw_data_calls_to_csv(mock_to_csv, mock_mkdir, instance):
    df = pd.DataFrame({"Open": [1], "Close": [2]})
    instance.raw_data = df
    instance.save_raw_data()
    mock_mkdir.assert_called_once_with(instance.raw_dir)
    mock_to_csv.assert_called_once_with(str(os.path.join(instance.raw_dir, f"{VALID_TICKER}_price_data.csv")))


@patch("pandas.read_csv")
def test_process_raw_data_parses_and_reindexes(mock_read_csv, instance):
    date_range = pd.date_range("2022-01-01", periods=2)

    raw_df = pd.DataFrame({
        "Date": ["2022-01-01", "2022-01-02"],
        "Open": [100, 110],
        "Close": [105, 115],
    })
    mock_read_csv.return_value = raw_df
    processed = instance._process_raw_data(date_range)
    assert isinstance(processed, pd.DataFrame)
    assert "Date" in processed.columns
    assert list(processed.columns) == ["Date", "Open", "Close"]

def test_get_processed_data_calls_internal(instance):
    date_range = pd.date_range("2023-01-01", periods=2)

    with patch.object(instance, "_process_raw_data", return_value="some_df") as mock_proc:
        result = instance.get_processed_data(date_range)
        mock_proc.assert_called_once_with(date_range)
        assert result == "some_df"
