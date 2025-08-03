import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from src.preprocessing.feature_generator import FeatureGenerator

@pytest.fixture
def sample_sentiment_data():
    return pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-01', '2024-01-02'],
        'D_VADER_Score': [0.2, 0.1, 0.3],
        'D_VADER_Sent': [1, 0, -1],
        'D_BERT_Score': [0.5, 0.0, -0.2],
        'D_BERT_Sent': [1, 0, -1]
    }).set_index('Date')

@pytest.fixture
def sample_price_data():
    return pd.DataFrame({
        'ETH_YF_Op': [100, 105, 110],
        'ETH_YF_Hi': [110, 115, 120],
        'ETH_YF_Lo': [90, 95, 100],
        'ETH_YF_Cls': [105, 110, 115]
    })

def test_invalid_input_data_type():
    with pytest.raises(ValueError, match="input_data must be a pandas DataFrame"):
        FeatureGenerator("invalid", "sentiment")

def test_invalid_data_tag():
    df = pd.DataFrame()
    with pytest.raises(ValueError, match="data_tag must be either 'sentiment' or 'price'"):
        FeatureGenerator(df, "invalid_tag")

def test_valid_initialization(sample_sentiment_data):
    fg = FeatureGenerator(sample_sentiment_data, "sentiment")
    assert isinstance(fg.input_data, pd.DataFrame)
    assert fg.transformed_data.empty
    assert fg.data_tag == "sentiment"

def test_generate_price_features(sample_price_data):
    fg = FeatureGenerator(sample_price_data, "price")
    result = fg.generate_features()

    assert "ETH_D_AvgPrc" in result.columns
    assert "ETH_D_PrcDir" in result.columns
    assert result.shape[0] == 3
    assert isinstance(result, pd.DataFrame)

def test_generate_price_features_column_order(sample_price_data):
    fg = FeatureGenerator(sample_price_data, "price")
    result = fg.generate_features()
    assert result.columns[0] == "ETH_D_AvgPrc"
    assert result.columns[1] == "ETH_D_PrcDir"

# @patch("src.preprocessing.feature_generator.VaderSentimentAnalyser")
# def test_generate_sentiment_features(mock_vsa_class, sample_sentiment_data):
#     mock_vsa = MagicMock()
#     mock_vsa.determine_sentiment.side_effect = lambda x: 1 if float(x) > 0 else -1
#     mock_vsa_class.return_value = mock_vsa

#     fg = FeatureGenerator(sample_sentiment_data, "sentiment")
#     result = fg.generate_features()

#     expected_cols = [
#         'D_VADER_AvgScr_In', 'D_VADER_Sent_AvgIn',
#         'D_VADER_AvgScr_Ex', 'D_VADER_Sent_AvgEx',
#         'D_BERT_AvgScr_In', 'D_BERT_Sent_AvgIn',
#         'D_BERT_AvgScr_Ex', 'D_BERT_Sent_AvgEx'
#     ]

#     for col in expected_cols:
#         assert col in result.columns

#     assert isinstance(result, pd.DataFrame)

# @patch("src.preprocessing.feature_generator.VaderSentimentAnalyser")
def test_sentiment_empty_result_if_no_scores():
    df = pd.DataFrame({'Date': ['2024-01-01'], 'Other_Col': [0.5]}).set_index('Date')
    fg = FeatureGenerator(df, "sentiment")
    result = fg.generate_features()

    assert result.empty

# @patch("src.preprocessing.feature_generator.VaderSentimentAnalyser")
# def test_generate_features_dispatch_sentiment(mock_vsa_class, sample_sentiment_data):
#     mock_vsa = MagicMock()
#     mock_vsa.determine_sentiment.return_value = 1
#     mock_vsa_class.return_value = mock_vsa

#     fg = FeatureGenerator(sample_sentiment_data, "sentiment")
#     result = fg.generate_features()
#     assert not result.empty

def test_generate_features_dispatch_price(sample_price_data):
    fg = FeatureGenerator(sample_price_data, "price")
    result = fg.generate_features()
    assert "ETH_D_AvgPrc" in result.columns
