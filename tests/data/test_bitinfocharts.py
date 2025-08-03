import pytest
import os
import pandas as pd
import requests
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from src.data.bitinfocharts import BitInfoCharts
from bs4 import BeautifulSoup


@pytest.fixture
def mock_root_dir():
    return str(os.path.join("C:", "test", "root"))


@pytest.fixture
def bitinfocharts_instance(mock_root_dir):
    return BitInfoCharts(ticker="BTC", root_dir=mock_root_dir)


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'date': ['2023-01-01', '2023-01-02'],
        'test_value': [100, 200]
    })


@pytest.fixture
def merged_df():
    return pd.DataFrame({
        'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'transactions': [1000, 1100, 1200],
        'block_size': [500, 550, 600],
        'full_name': ['bitcoin', 'bitcoin', 'bitcoin'],
        'coin': ['btc', 'btc', 'btc']
    })


def test_init(mock_root_dir):
    # Test with root_dir provided
    bic = BitInfoCharts(ticker="BTC", root_dir=mock_root_dir)
    assert bic.ticker == "BTC"
    assert bic.root_dir == mock_root_dir
    assert bic.raw_dir == str(os.path.join(mock_root_dir, "data", "raw", "BTC_data", "bitinfocharts"))
    assert bic.processed_dir == str(os.path.join(mock_root_dir, "data", "processed", "BTC_data"))
    assert bic.raw_data is None
    assert bic.processed_data is None
    assert bic.url == "https://bitinfocharts.com"
    assert isinstance(bic.chart_dict_list, list)
    assert len(bic.chart_dict_list) > 0


def test_parse_strlist(bitinfocharts_instance):
    # Test with normal input
    input_str = "['2023-01-01', 100, '2023-01-02', 200]"
    result = bitinfocharts_instance._parse_strlist(input_str)
    assert result == ['2023-01-01', '100', '2023-01-02', '200']

    # Test with empty input
    empty_str = "[]"
    result = bitinfocharts_instance._parse_strlist(empty_str)
    assert result == []

    # Test with mixed quotes
    mixed_quotes = "[\"2023-01-01\", '100']"
    result = bitinfocharts_instance._parse_strlist(mixed_quotes)
    assert result == ['2023-01-01', '100']


@patch('src.data.bitinfocharts.requests.get')
@patch('src.data.bitinfocharts.sleep')
def test_get_bitinfochart_graph_values(mock_sleep, mock_requests_get, bitinfocharts_instance):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.text = """
    <script>
    d = new Dygraph(document.getElementById("container"),
    [['2023-01-01',100],['2023-01-02',200]],
    { labels: [ "Date", "Value"] });
    </script>
    """
    mock_requests_get.return_value = mock_response

    # Call the method
    df = bitinfocharts_instance._get_bitinfochart_graph_values(
        url="https://test.url", var_name="test_value")

    # Check that requests.get and sleep were called
    mock_requests_get.assert_called_once_with("https://test.url")
    mock_sleep.assert_called_once()

    # Check the result
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['date', 'test_value']
    assert len(df) == 2
    assert df['date'].tolist() == ['2023-01-01', '2023-01-02']
    assert df['test_value'].tolist() == ['100', '200']


@patch('src.data.bitinfocharts.requests.get')
@patch('src.data.bitinfocharts.sleep')
def test_get_bitinfochart_graph_values_no_data(mock_sleep, mock_requests_get, bitinfocharts_instance):
    # Setup mock response with no relevant data
    mock_response = MagicMock()
    mock_response.text = "<html><body>No data here</body></html>"
    mock_requests_get.return_value = mock_response

    # Call the method - should return empty DataFrame
    df = bitinfocharts_instance._get_bitinfochart_graph_values(
        url="https://test.url", var_name="test_value")

    # Check that requests.get and sleep were called
    mock_requests_get.assert_called_once_with("https://test.url")
    mock_sleep.assert_called_once()

    # Check the result - should be an empty DataFrame with the expected columns
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['date', 'test_value']
    assert len(df) == 0


def test_merge_dfs(bitinfocharts_instance):
    # Create test DataFrames
    df1 = pd.DataFrame({'date': ['2023-01-01', '2023-01-02'], 'value1': [1, 2]})
    df2 = pd.DataFrame({'date': ['2023-01-01', '2023-01-03'], 'value2': [3, 4]})
    df3 = pd.DataFrame({'date': ['2023-01-02', '2023-01-04'], 'value3': [5, 6]})
    
    # Test with multiple DataFrames
    result = bitinfocharts_instance._merge_dfs([df1, df2, df3])
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ['date', 'value1', 'value2', 'value3']
    assert len(result) == 4  # All unique dates
    
    # Test with only one DataFrame
    result = bitinfocharts_instance._merge_dfs([df1])
    assert result is None


@patch('src.data.bitinfocharts.BitInfoCharts._get_bitinfochart_graph_values')
@patch('src.data.bitinfocharts.BitInfoCharts._merge_dfs')
@patch('src.data.bitinfocharts.requests.get')
@patch('src.data.bitinfocharts.BeautifulSoup')
@patch('src.data.bitinfocharts.progress_bar')
def test_get_raw_data(mock_progress_bar, mock_bs, mock_get, mock_merge_dfs, 
                     mock_get_graph_values, bitinfocharts_instance, sample_df):
    # Setup mocks
    mock_response = MagicMock()
    mock_get.return_value = mock_response
    
    mock_span1 = MagicMock()
    mock_span1.get.side_effect = lambda x: {'class': 's_coins', 'title': 'bitcoin', 'data-coin': 'btc'}[x]
    mock_span2 = MagicMock()
    mock_span2.get.side_effect = lambda x: {'class': 'other', 'title': 'ethereum', 'data-coin': 'eth'}[x]
    
    mock_soup = MagicMock()
    mock_soup.find_all.return_value = [mock_span1, mock_span2]
    mock_bs.return_value = mock_soup
    
    mock_get_graph_values.return_value = sample_df
    mock_merged_df = pd.DataFrame({
        'date': ['2023-01-01', '2023-01-02'],
        'transactions': [100, 200],
        'block_size': [300, 400]
    })
    mock_merge_dfs.return_value = mock_merged_df
    
    mock_progress_bar.side_effect = lambda x: x
    
    # Call the method
    bitinfocharts_instance.get_raw_data()
    
    # Check that the raw_data was set correctly
    assert bitinfocharts_instance.raw_data is not None
    assert mock_merge_dfs.called
    assert mock_get_graph_values.called


@patch('src.data.bitinfocharts.make_directory')
def test_save_raw_data(mock_make_directory, bitinfocharts_instance, merged_df):
    # Setup
    bitinfocharts_instance.raw_data = merged_df
    
    # Mock open and pandas to_csv
    with patch('builtins.open', mock_open()) as mock_file:
        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            # Call the method
            bitinfocharts_instance.save_raw_data()
            
            # Check that directory was created
            mock_make_directory.assert_called_once_with(bitinfocharts_instance.raw_dir)
            
            # Check that to_csv was called with correct path
            mock_to_csv.assert_called_once()
            args, _ = mock_to_csv.call_args
            assert args[0] == str(os.path.join(bitinfocharts_instance.raw_dir, "BTC.csv"))


# @patch('pandas.read_csv')
# def test_process_raw_data(mock_read_csv, bitinfocharts_instance, merged_df):
#     # Setup
#     date_range = pd.date_range(start='2023-01-01', end='2023-01-04')
#     data_yf = pd.DataFrame({
#         'Date': date_range,
#         'Price': [100, 200, 300, 400]
#     })
    
#     mock_read_csv.return_value = merged_df
    
#     # Call the method
#     with patch('pandas.DataFrame.set_index') as mock_set_index:
#         mock_set_index.return_value.reindex.return_value.reset_index.return_value = pd.DataFrame({
#             'Date': date_range,
#             'Transactions': [1000, 1100, 1200, None],
#             'Block Size': [500, 550, 600, None],
#         })
        
#         bitinfocharts_instance.process_raw_data(data_yf=data_yf, date_range=date_range)
    
#     # Check that processed_data was set
#     assert bitinfocharts_instance.processed_data is not None
#     assert mock_read_csv.called
#     mock_read_csv.assert_called_once_with(f"{bitinfocharts_instance.raw_dir}\\BTC.csv")


@patch('src.data.bitinfocharts.make_directory')
def test_save_processed_data(mock_make_directory, bitinfocharts_instance):
    # Setup
    processed_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
    bitinfocharts_instance.processed_data = processed_df
    
    # Mock pandas to_csv
    with patch('pandas.DataFrame.to_csv') as mock_to_csv:
        # Call the method
        bitinfocharts_instance.save_processed_data()
        
        # Check that directory was created
        mock_make_directory.assert_called_once_with(bitinfocharts_instance.processed_dir)
        
        # Check that to_csv was called with correct path
        mock_to_csv.assert_called_once()
        args, kwargs = mock_to_csv.call_args
        assert args[0] == f"{bitinfocharts_instance.processed_dir}\\BTC_bitinfocharts.csv"
        assert kwargs['index'] == False


@patch('src.data.bitinfocharts.requests.get')
@patch('src.data.bitinfocharts.sleep')
def test_get_bitinfochart_graph_values_exception(mock_sleep, mock_requests_get, bitinfocharts_instance):
    # Setup mock to raise an exception
    mock_requests_get.side_effect = requests.exceptions.RequestException("Network error")
    
    # Call the method - should return empty DataFrame
    with pytest.raises(requests.exceptions.RequestException):
        bitinfocharts_instance._get_bitinfochart_graph_values(
            url="https://test.url", var_name="test_value")
    
    # Check that requests.get was called
    mock_requests_get.assert_called_once_with("https://test.url")


# @patch('src.data.bitinfocharts.BitInfoCharts._get_bitinfochart_graph_values')
# @patch('src.data.bitinfocharts.requests.get')
# @patch('src.data.bitinfocharts.BeautifulSoup')
# @patch('src.data.bitinfocharts.progress_bar')
# def test_get_raw_data_exception(mock_progress_bar, mock_bs, mock_get, 
#                               mock_get_graph_values, bitinfocharts_instance):
#     # Setup mocks
#     mock_response = MagicMock()
#     mock_get.return_value = mock_response
    
#     mock_span1 = MagicMock()
#     mock_span1.get.side_effect = lambda x: {'class': 's_coins', 'title': 'bitcoin', 'data-coin': 'btc'}[x]
    
#     mock_soup = MagicMock()
#     mock_soup.find_all.return_value = [mock_span1]
#     mock_bs.return_value = mock_soup
    
#     # Setup exception in _get_bitinfochart_graph_values
#     mock_get_graph_values.side_effect = Exception("Test error")
    
#     mock_progress_bar.side_effect = lambda x: x
    
#     # Call the method - should handle the exception
#     bitinfocharts_instance.get_raw_data()
    
#     # Even with exception, code should continue
#     assert mock_get_graph_values.called