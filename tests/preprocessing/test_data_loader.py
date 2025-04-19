import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.preprocessing.data_loader import DataLoader
import numpy as np

@pytest.fixture
def data_loader():
    return DataLoader(root_dir=Path("test_data"))

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
def test_merge_selected_data(data_loader):
    data_loader.ETH = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=5, freq='D'),
        'ETH_Open': np.random.randn(5),
        'ETH_Close': np.random.randn(5)
    }).set_index('Date')

    data_loader.BTC = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=5, freq='D'),
        'BTC_Open': np.random.randn(5),
        'BTC_Close': np.random.randn(5)
    }).set_index('Date')
    
    data_loader.merge_selected_data(["BTC"])
    
    assert 'BTC_Open' in data_loader.final_data.columns
    assert 'BTC_Close' in data_loader.final_data.columns

def test_merge_selected_data_invalid_type(data_loader):
    with pytest.raises(ValueError):
        data_loader.merge_selected_data("BTC")

# Test setting time range
def test_set_time_range_valid(data_loader):
    data_loader.final_data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=5, freq='D'),
        'ETH_Open': np.random.randn(5),
        'ETH_Close': np.random.randn(5)
    }).set_index('Date')
    
    data_loader.set_time_range("2020-01-02", "2020-01-04")
    assert data_loader.final_data.shape[0] == 3

def test_set_time_range_invalid_dates(data_loader):
    with pytest.raises(ValueError):
        data_loader.set_time_range("2020-01-04", "2020-01-02")

# Test make stationary
@patch('src.common.stats.adf_test')
def test_make_stationary(mock_adf_test, data_loader):
    mock_adf_test.return_value = (True, 0.01)
    
    data_loader.final_data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=5, freq='D'),
        'ETH_Open': np.random.randn(5),
        'ETH_Close': np.random.randn(5)
    }).set_index('Date')
    
    data_loader.make_stationary()
    
    # Ensure that make_stationary was called on each column
    mock_adf_test.assert_called()
    assert not data_loader.final_data.isna().any().any()

# Test lag features
def test_lag_features(data_loader):
    data_loader.final_data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=5, freq='D'),
        'ETH_Open': np.random.randn(5),
        'ETH_Close': np.random.randn(5)
    }).set_index('Date')
    
    data_loader.lag_features(exclude_cols=['ETH_Close'], lag=1)
    
    assert 'ETH_Open' in data_loader.final_data.columns
    assert data_loader.final_data['ETH_Open'].isna().sum() == 0

def test_lag_features_invalid_lag(data_loader):
    with pytest.raises(ValueError):
        data_loader.lag_features(exclude_cols=['ETH_Close'], lag=0)

# Test feature selection
def test_select_features(data_loader):
    data_loader.final_data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=5, freq='D'),
        'ETH_Open': np.random.randn(5),
        'ETH_Close': np.random.randn(5)
    }).set_index('Date')
    
    data_loader.select_features(['ETH_Open'])
    
    assert 'ETH_Open' in data_loader.final_data.columns
    assert 'ETH_Close' not in data_loader.final_data.columns

def test_select_features_invalid(data_loader):
    data_loader.final_data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=5, freq='D'),
        'ETH_Open': np.random.randn(5),
        'ETH_Close': np.random.randn(5)
    }).set_index('Date')
    
    with pytest.raises(KeyError):
        data_loader.select_features(['Non_Existing_Column'])

# Test data split
def test_data_split_test_train(data_loader):
    data_loader.final_data = pd.DataFrame({
        'Date': pd.date_range('2020-01-01', periods=10, freq='D'),
        'ETH_Open': np.random.randn(10),
        'ETH_Close': np.random.randn(10)
    }).set_index('Date')
    
    train, test = data_loader.data_split(split_type="test_train", split_size=0.2)
    
    assert len(train) == 8
    assert len(test) == 2

def test_data_split_invalid_split_type(data_loader):
    with pytest.raises(ValueError):
        data_loader.data_split(split_type="invalid_type", split_size=0.2)

def test_data_split_invalid_size(data_loader):
    with pytest.raises(ValueError):
        data_loader.data_split(split_type="test_train", split_size=1.5)