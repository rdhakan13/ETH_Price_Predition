import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.preprocessing.data_loader import DataLoader
import numpy as np
from collections import namedtuple

StationarityResult = namedtuple('StationarityResult', ['is_stationary', 'p_value'])

mock_data = [
    {
        "Date": "2020-01-01",
        "News Headline": "Hong Kong Fintech Innovation Lab Led with Blockchain And AI - Forbes",
        "Publisher": "Forbes",
        "D_VADER_Score": 0.3818,
        "D_VADER_Sent": 1,
        "D_FINBERT_ConScore": 0.590740085,
        "D_FINBERT_Sent": 0,
        "D_CRYPTOBERT_ConScore": 0.518976152,
        "D_CRYPTOBERT_Sent": 0
    },
    {
        "Date": "2020-01-02",
        "News Headline": "Decentralized Electricity Could be Blockchain's Trojan Horse - Cointelegraph",
        "Publisher": "Cointelegraph",
        "D_VADER_Score": 0.0,
        "D_VADER_Sent": 0,
        "D_FINBERT_ConScore": 0.927920163,
        "D_FINBERT_Sent": 0,
        "D_CRYPTOBERT_ConScore": 0.949832797,
        "D_CRYPTOBERT_Sent": 0
    },
    {
        "Date": "2020-01-03",
        "News Headline": "Ethereum cryptocurrency value dropped due to wallet security vulnerability - Inquirer.net",
        "Publisher": "Inquirer.net",
        "D_VADER_Score": 0.4404,
        "D_VADER_Sent": 1,
        "D_FINBERT_ConScore": 0.967869937,
        "D_FINBERT_Sent": -1,
        "D_CRYPTOBERT_ConScore": 0.948679328,
        "D_CRYPTOBERT_Sent": 0
    },
    {
        "Date": "2020-01-05",
        "News Headline": "Ambrosus: Digitalising the Global Trade with Blockchain - Open Access Government",
        "Publisher": "Open Access Government",
        "D_VADER_Score": 0.0,
        "D_VADER_Sent": 0,
        "D_FINBERT_ConScore": 0.852425814,
        "D_FINBERT_Sent": 0,
        "D_CRYPTOBERT_ConScore": 0.549529016,
        "D_CRYPTOBERT_Sent": 1
    }
]

@pytest.fixture
def data_loader():
    return DataLoader(root_dir=Path("test_data"))

@pytest.fixture
def mock_final_data(data_loader):
    # Create a mock dataframe with a datetime index for testing
    data_loader.final_data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=5, freq='D'),
        'ETH_Open': np.random.randn(5),
        'ETH_Close': np.random.randn(5)
    }).set_index('Date')
    return data_loader.final_data


# Test initialization of DataLoader
def test_initialization(data_loader):
    assert data_loader.root_dir == Path("test_data")
    assert data_loader.ETH is None
    assert data_loader.BTC is None
    assert data_loader.LTC is None
    assert data_loader.sentiment_analysis is None
    assert data_loader.final_data is None
    assert data_loader.train is None
    assert data_loader.test is None
    assert data_loader.val is None

# Test loading data
@patch('pandas.read_csv')
def test_load_data(mock_read_csv, data_loader):
    # Mock the CSV loading
    mock_read_csv.return_value = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=5, freq='D'),
        'Open': np.random.randn(5),
        'Close': np.random.randn(5)
    }).set_index('Date')
    
    data_loader.load_data()
    
    # Check that data was loaded
    assert data_loader.ETH is not None
    assert data_loader.BTC is not None
    assert data_loader.LTC is not None
    assert data_loader.sentiment_analysis is not None
    assert data_loader.final_data is not None

# Test merging selected data
def test_merge_selected_data(data_loader, mock_final_data):
    data_loader.BTC = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=5, freq='D'),
        'Open': np.random.randn(5),
        'Close': np.random.randn(5)
    }).set_index('Date')

    data_loader.LTC = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=5, freq='D'),
        'Open': np.random.randn(5),
        'Close': np.random.randn(5)
    }).set_index('Date')

    df = pd.DataFrame(mock_data)
    df["Date"] = pd.to_datetime(df["Date"])

    data_loader.sentiment_analysis = df.set_index('Date')
    
    data_loader.merge_selected_data(["BTC","LTC", "sentiment_analysis"])
    
    assert 'BTC_Open' in data_loader.final_data.columns
    assert 'BTC_Close' in data_loader.final_data.columns
    assert 'LTC_Open' in data_loader.final_data.columns
    assert 'LTC_Close' in data_loader.final_data.columns
    assert 'D_VADER_AvgScr_Ex' in data_loader.final_data.columns
    assert 'D_VADER_Sent_AvgEx' in data_loader.final_data.columns

def test_merge_selected_data_invalid_type(data_loader):
    with pytest.raises(ValueError):
        data_loader.merge_selected_data("BTC")

def test_merge_selected_data_none_type(data_loader, mock_final_data):
    before = data_loader.final_data.copy()  
    data_loader.merge_selected_data()
    pd.testing.assert_frame_equal(data_loader.final_data, before)

# Test setting time range
def test_set_time_range_valid(data_loader,mock_final_data):
    data_loader.set_time_range("2020-01-02", "2020-01-04")
    assert data_loader.final_data.shape[0] == 3

def test_set_time_range_invalid_dates(data_loader):
    with pytest.raises(ValueError):
        data_loader.set_time_range("2020-01-04", "2020-01-02")

def test_set_time_range_value_error_on_invalid_date(data_loader,mock_final_data):
    with patch('pandas.to_datetime') as mock_to_datetime:
        mock_to_datetime.side_effect = ValueError("Invalid date format")
        with pytest.raises(ValueError, match="Invalid date format"):
            data_loader.set_time_range("invalid-start-date", "2025-12-31")

def test_start_date_before_min(data_loader,mock_final_data):
    with patch('src.preprocessing.data_loader.logger') as mock_logger:
        data_loader.set_time_range("2019-12-31", "2020-01-05")
        mock_logger.warning.assert_called_with("start_date is before the earliest date in the dataset, setting to the earliest date.")
        assert data_loader.final_data.index.min() == pd.to_datetime("2020-01-01")
        
def test_end_date_after_max(data_loader,mock_final_data):
    with patch('src.preprocessing.data_loader.logger') as mock_logger:
        data_loader.set_time_range("2020-01-01", "2025-12-31")
        mock_logger.warning.assert_called_with("end_date is after the latest date in the dataset, setting to the latest date.")
        assert data_loader.final_data.index.max() == pd.to_datetime("2020-01-05")

def test_start_date_none(data_loader,mock_final_data):
    with patch('src.preprocessing.data_loader.logger') as mock_logger:
        data_loader.set_time_range(None, "2020-01-05")
        mock_logger.warning.assert_called_with("start_date is before the earliest date in the dataset, setting to the earliest date.")
        assert data_loader.final_data.index.min() == pd.to_datetime("2020-01-01")
        
def test_end_date_none(data_loader,mock_final_data):
    with patch('src.preprocessing.data_loader.logger') as mock_logger:
        data_loader.set_time_range("2020-01-01", None)
        mock_logger.warning.assert_called_with("end_date is after the latest date in the dataset, setting to the latest date.")
        assert data_loader.final_data.index.max() == pd.to_datetime("2020-01-05")

@patch('src.preprocessing.data_loader.adf_test')
def test_make_stationary(mock_adf_test, data_loader, mock_final_data):
    mock_adf_test.return_value = StationarityResult(True, 0.01)
    data_loader.make_stationary()
    mock_adf_test.assert_called()
    assert not data_loader.final_data.isna().any().any()

def test_lag_features(data_loader, mock_final_data):
    data_loader.lag_features(exclude_cols=['ETH_Close'], lag=1)
    assert 'ETH_Open' in data_loader.final_data.columns
    assert data_loader.final_data['ETH_Open'].isna().sum() == 0

def test_lag_features_invalid_lag(data_loader,mock_final_data):
    with pytest.raises(ValueError):
        data_loader.lag_features(exclude_cols=['ETH_Close'], lag=0)

def test_lag_features_none_lag(data_loader,mock_final_data):
    data_loader.lag_features(exclude_cols=['ETH_Close'], lag=None)
    assert data_loader.final_data.index.min()==pd.to_datetime("2020-01-01")

# Test feature selection
def test_select_features(data_loader, mock_final_data):
    data_loader.select_features(['ETH_Open'])
    assert 'ETH_Open' in data_loader.final_data.columns
    assert 'ETH_Close' not in data_loader.final_data.columns

def test_select_features_none(data_loader, mock_final_data):
    data_loader.select_features()
    assert 'ETH_Open' in data_loader.final_data.columns
    assert 'ETH_Close' in data_loader.final_data.columns

def test_select_features_invalid(data_loader, mock_final_data):
    with pytest.raises(KeyError):
        data_loader.select_features(['Non_Existing_Column'])

def test_data_split_test_train(data_loader, mock_final_data):
    train, test = data_loader.data_split(split_type="test_train", split_size=0.2)
    assert len(train) == 4
    assert len(test) == 1

def test_data_split_invalid_split_type(data_loader):
    with pytest.raises(ValueError):
        data_loader.data_split(split_type="invalid_type", split_size=0.2)

def test_data_split_invalid_size(data_loader):
    with pytest.raises(ValueError):
        data_loader.data_split(split_type="test_train", split_size=1.5)