import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from src.preprocessing.data_cleaner import DataCleaner


@pytest.fixture
def dummy_data():
    return pd.DataFrame({
        "Date": pd.date_range(start="2022-01-01", periods=3),
        "value": [1, np.nan, 3],
        "to_drop": [10, 20, 30]
    })


@pytest.fixture
def cleaner(tmp_path):
    return DataCleaner(root_dir=str(tmp_path), ticker="ETHUSD", source=["oklink", "bitinfocharts", "etherscan"])


@patch("pandas.read_csv")
def test_read_data_success(mock_read_csv, cleaner, dummy_data):
    mock_read_csv.return_value = dummy_data
    cleaner.read_data()
    assert cleaner.etherscan is not None
    assert cleaner.oklink is not None
    assert cleaner.bitinfocharts is not None


@pytest.mark.parametrize("source, ticker", [
    (["oklink"], "ETHUSD"),
    (["bitinfocharts"], "ETHUSD"),
    (["etherscan"], "ETHUSD"),
])
def test_read_data_file_not_found(cleaner, source, ticker):
    cleaner.source = source
    cleaner.ticker = ticker
    with patch("src.preprocessing.data_cleaner.pd.read_csv", side_effect=FileNotFoundError), \
         patch("src.preprocessing.data_cleaner.logger") as mock_logger:
        with pytest.raises(FileNotFoundError):
            cleaner.read_data()
        mock_logger.error.assert_called_with("File not found")


def test_identify_nan(cleaner, dummy_data):
    cleaner.etherscan = dummy_data.copy()
    cleaner.oklink = dummy_data.copy()
    cleaner.bitinfocharts = dummy_data.copy()
    cleaner.identify_nan()
    assert cleaner.etherscan.isna().sum().sum() > 0


def test_interpolate_clean_data_time_method(cleaner, dummy_data):
    df_with_nans = dummy_data.copy()
    cleaner.cleaned_data = df_with_nans.copy()
    cleaner.interpolate_clean_data(method="time")
    assert cleaner.cleaned_data.isna().sum().sum() == 0


def test_interpolate_invalid_method(cleaner, dummy_data):
    cleaner.cleaned_data = dummy_data.copy()
    with pytest.raises(NotImplementedError):
        cleaner.interpolate_clean_data(method="invalid")


def test_interpolate_no_data(cleaner):
    cleaner.cleaned_data = None
    with patch("src.preprocessing.data_cleaner.logger") as mock_logger:
        cleaner.interpolate_clean_data(method="linear")
        mock_logger.error.assert_called_with("No data to interpolate")


def test_drop_columns_valid(cleaner, dummy_data):
    cleaner.etherscan = dummy_data.copy()
    cleaner.drop_columns(source="etherscan", columns=["to_drop"])
    assert "to_drop" not in cleaner.etherscan.columns


def test_drop_columns_invalid_source(cleaner):
    with pytest.raises(ValueError):
        cleaner.drop_columns(source="invalid", columns=["col"])


def test_drop_columns_nonexistent_column(cleaner, dummy_data):
    cleaner.oklink = dummy_data.copy()
    # Should not raise since column won't be selected for dropping
    cleaner.drop_columns(source="oklink", columns=["non_existent"])
    assert "value" in cleaner.oklink.columns


def test_standardise_columns(cleaner, dummy_data):
    column_map = {"value": "v"}
    cleaner.etherscan = dummy_data.copy()
    cleaner.standardise_columns("etherscan", column_map)
    assert "v" in cleaner.etherscan.columns


def test_standardise_invalid_source(cleaner):
    with patch("src.preprocessing.data_cleaner.logger") as mock_logger:
        cleaner.standardise_columns("invalid", {})
        mock_logger.error.assert_called_with("Invalid source")


def test_merge_sources(cleaner, dummy_data):
    cleaner.etherscan = dummy_data.copy()
    cleaner.oklink = dummy_data.copy().rename(columns={"value": "value2"})
    cleaner.bitinfocharts = dummy_data.copy().rename(columns={"value": "value3"})
    cleaner.merge_sources()
    assert cleaner.cleaned_data.shape[0] == 3
    assert "value2" in cleaner.cleaned_data.columns
    assert "value3" in cleaner.cleaned_data.columns

