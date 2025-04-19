import os
import pytest
import pandas as pd
from unittest import mock
from datetime import datetime
from src.data.google_news import GoogleNews


@pytest.fixture
def valid_root_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def google_news_instance(valid_root_dir):
    return GoogleNews(root_dir=valid_root_dir)


def test_init_with_valid_root_dir(valid_root_dir):
    gn = GoogleNews(valid_root_dir)
    assert gn.root_dir == valid_root_dir
    assert "raw" in gn.raw_dir
    assert "processed" in gn.processed_dir
    assert "final" in gn.final_dir


def test_init_with_invalid_root_dir():
    with pytest.raises(ValueError):
        GoogleNews(root_dir=None)
    with pytest.raises(ValueError):
        GoogleNews(root_dir="")
    with pytest.raises(ValueError):
        GoogleNews(root_dir=123)


@mock.patch("src.data.google_news.GNews")
@mock.patch("src.data.google_news.pd.json_normalize")
def test_get_raw_data_success(mock_json_normalize, mock_gnews, google_news_instance):
    keywords = ["Bitcoin"]
    dates_list = [(2022, 1, 1), (2022, 1, 2)]
    mock_gnews.return_value.get_news.return_value = [{"title": "Test", "published date": "Mon, 01 Jan 2022 12:00:00 GMT", "publisher.title": "Test Publisher"}]
    mock_json_normalize.return_value = pd.DataFrame([{"title": "Test"}])
    google_news_instance.get_raw_data(2022, keywords, dates_list)
    assert isinstance(google_news_instance.raw_data, pd.DataFrame)
    assert google_news_instance.year == "2022"


def test_get_raw_data_invalid_keywords(google_news_instance):
    with pytest.raises(ValueError):
        google_news_instance.get_raw_data(2022, keywords=None, dates_list=[(2022, 1, 1)])

def test_get_raw_data_invalid_dates_list(google_news_instance):
    with pytest.raises(ValueError):
        google_news_instance.get_raw_data(2022, keywords=["crypto"], dates_list=None)


@mock.patch("src.data.google_news.make_directory")
@mock.patch("src.data.google_news.pd.DataFrame.to_csv")
def test_save_raw_data(mock_to_csv, mock_make_dir, google_news_instance):
    google_news_instance.year = "2022"
    google_news_instance.raw_data = pd.DataFrame([{"title": "Sample"}])
    google_news_instance.save_raw_data()
    mock_make_dir.assert_called_once_with(google_news_instance.raw_dir)
    mock_to_csv.assert_called_once()


@mock.patch("os.listdir")
@mock.patch("pandas.read_csv")
def test_process_raw_data(mock_read_csv, mock_listdir, google_news_instance):
    mock_listdir.return_value = ["mock_file.csv"]
    sample_data = pd.DataFrame({
        "Unnamed: 0": [0],
        "description": ["desc"],
        "url": ["url"],
        "publisher.href": ["href"],
        "published date": ["Mon, 01 Jan 2022 12:00:00 GMT"],
        "title": ["Headline"],
        "publisher.title": ["Publisher"],
    })
    mock_read_csv.return_value = sample_data
    google_news_instance.process_raw_data()
    assert isinstance(google_news_instance.processed_data, pd.DataFrame)
    assert all(col in google_news_instance.processed_data.columns for col in ["Date", "News Headline", "Publisher"])


@mock.patch("src.data.google_news.make_directory")
@mock.patch("pandas.DataFrame.to_csv")
def test_save_processed_data(mock_to_csv, mock_make_dir, google_news_instance):
    google_news_instance.processed_data = pd.DataFrame([{"Date": datetime.today(), "News Headline": "Headline", "Publisher": "Publisher"}])
    google_news_instance.save_processed_data()
    mock_make_dir.assert_called_once_with(google_news_instance.processed_dir)
    mock_to_csv.assert_called_once()
