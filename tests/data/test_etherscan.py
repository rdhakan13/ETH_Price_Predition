import os
import pytest
import pandas as pd
from unittest import mock
from datetime import datetime
from src.data.etherscan import EtherScan


@pytest.fixture
def valid_root_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def etherscan_instance(valid_root_dir):
    return EtherScan(ticker="ETH", root_dir=valid_root_dir)


def test_init_valid(etherscan_instance):
    assert etherscan_instance.ticker == "ETH"
    assert "raw\\ETH_data\\etherscan" in etherscan_instance.raw_dir
    assert "processed\\ETH_data" in etherscan_instance.processsed_dir


def test_init_invalid_ticker(valid_root_dir):
    with pytest.raises(ValueError):
        EtherScan(ticker=None, root_dir=valid_root_dir)
    with pytest.raises(ValueError):
        EtherScan(ticker="", root_dir=valid_root_dir)
    with pytest.raises(ValueError):
        EtherScan(ticker=123, root_dir=valid_root_dir)


def test_init_invalid_root():
    with pytest.raises(ValueError):
        EtherScan(ticker="ETH", root_dir=None)
    with pytest.raises(ValueError):
        EtherScan(ticker="ETH", root_dir="")
    with pytest.raises(ValueError):
        EtherScan(ticker="ETH", root_dir=123)


def test_process_raw_data_invalid_inputs(etherscan_instance):
    with pytest.raises(ValueError):
        etherscan_instance.process_raw_data(data_yf=None, date_range=pd.date_range("2022-01-01", "2022-01-05"))
    with pytest.raises(ValueError):
        etherscan_instance.process_raw_data(data_yf=pd.DataFrame(), date_range=None)


@mock.patch("os.listdir")
@mock.patch("pandas.read_csv")
def test_process_raw_data_all_file_types(mock_read_csv, mock_listdir, etherscan_instance):
    mock_listdir.return_value = [
        "export-AverageDailyTransactionFee.csv",
        "export-DailyActiveEthAddress.csv",
        "export-DailyBlockCount.csv"
    ]
    date_rng = pd.date_range("2022-01-01", "2022-01-05")
    dummy_yf = pd.DataFrame({"Date": date_rng, "Close": [1, 2, 3, 4, 5]})
    mock_dfs = {
        "export-AverageDailyTransactionFee.csv": pd.DataFrame({
            "Date(UTC)": date_rng,
            "Dummy": ["a", "b", "c", "d", "e"],
            "Fee Column": [10, 20, 30, 40, 50],
            "Extra Column": [1, 2, 3, 4, 5]
        }),
        "export-DailyActiveEthAddress.csv": pd.DataFrame({
            "Date(UTC)": date_rng,
            "Active Addresses": [100, 110, 120, 130, 140]
        }),
        "export-DailyBlockCount.csv": pd.DataFrame({
            "Date(UTC)": date_rng,
            "Other": [200, 210, 220, 230, 240],
            "Block Count": [300, 310, 320, 330, 340]
        })
    }
    def read_csv_side_effect(filepath):
        filename = os.path.basename(filepath.replace("\\", "/"))
        return mock_dfs[filename]

    mock_read_csv.side_effect = read_csv_side_effect
    etherscan_instance.process_raw_data(data_yf=dummy_yf, date_range=date_rng)
    assert isinstance(etherscan_instance.processed_data, pd.DataFrame)
    assert "Date" in etherscan_instance.processed_data.columns
    assert "Close" in etherscan_instance.processed_data.columns


@mock.patch("src.data.etherscan.make_directory")
@mock.patch("pandas.DataFrame.to_csv")
def test_save_processed_data(mock_to_csv, mock_make_dir, etherscan_instance):
    etherscan_instance.processed_data = pd.DataFrame({
        "Date": pd.date_range("2022-01-01", "2022-01-03"),
        "Close": [1, 2, 3]
    })
    etherscan_instance.save_processed_data()
    mock_make_dir.assert_called_once_with(etherscan_instance.processsed_dir)
    mock_to_csv.assert_called_once()
