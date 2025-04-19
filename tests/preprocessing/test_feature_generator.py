import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from src.preprocessing.feature_generator import FeatureGenerator

@pytest.fixture
def price_data():
    return pd.DataFrame({
        'ETH_YF_Op': [100, 110, 120],
        'ETH_YF_Hi': [110, 120, 130],
        'ETH_YF_Lo': [90, 100, 110],
        'ETH_YF_Cls': [105, 115, 125]
    })

@pytest.fixture
def sentiment_data():
    return pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=3),
        'ETH_VADER_Score': [0.2, -0.1, 0.5],
        'ETH_VADER_Sent': [1, 0, -1],
        'ETH_BERT_Score': [0.3, 0.0, -0.2],
        'ETH_BERT_Sent': [1, 0, -1]
    })

def test_invalid_input_type():
    with pytest.raises(ValueError):
        FeatureGenerator(input_data="not a dataframe", data_tag="price")

def test_invalid_data_tag(price_data):
    with pytest.raises(ValueError):
        FeatureGenerator(input_data=price_data, data_tag="invalid_tag")

def test_generate_price_features(price_data):
    fg = FeatureGenerator(input_data=price_data, data_tag="price")
    result = fg.generate_features()

    assert 'ETH_D_AvgPrc' in result.columns
    assert 'ETH_D_PrcDir' in result.columns
    assert result.shape[0] == len(price_data)

@patch("src.preprocesssing.feature_generator.swifter")
@patch("src.preprocesssing.feature_generator.VaderSentimentAnalyser")
def test_generate_sentiment_features(mock_vader, mock_swifter, sentiment_data):
    mock_analyser = MagicMock()
    mock_analyser.determine_sentiment.side_effect = lambda x: "pos" if x > 0 else "neg"
    mock_vader.return_value = mock_analyser

    mock_swifter.apply.side_effect = lambda func: sentiment_data['ETH_VADER_Score'].apply(func)

    fg = FeatureGenerator(input_data=sentiment_data, data_tag="sentiment")
    result = fg.generate_features()

    assert not result.empty
    expected_cols = [
        'ETH_VADER_AvgScr_In', 'ETH_VADER_Sent_AvgIn',
        'ETH_VADER_AvgScr_Ex', 'ETH_VADER_Sent_AvgEx',
        'ETH_BERT_AvgScr_In', 'ETH_BERT_Sent_AvgIn',
        'ETH_BERT_AvgScr_Ex', 'ETH_BERT_Sent_AvgEx'
    ]
    for col in expected_cols:
        assert col in result.columns

# Check edge case when all sentiment values are 0
@patch("src.preprocesssing.feature_generator.VaderSentimentAnalyser")
def test_sentiment_all_neutral(mock_vader, sentiment_data):
    sentiment_data['ETH_VADER_Sent'] = 0
    sentiment_data['ETH_BERT_Sent'] = 0

    mock_analyser = MagicMock()
    mock_analyser.determine_sentiment.return_value = "neutral"
    mock_vader.return_value = mock_analyser

    with patch("src.preprocesssing.feature_generator.swifter") as mock_swifter:
        mock_swifter.apply.side_effect = lambda func: sentiment_data['ETH_VADER_Score'].apply(func)
        fg = FeatureGenerator(input_data=sentiment_data, data_tag="sentiment")
        result = fg.generate_features()
        assert 'ETH_VADER_AvgScr_In' in result.columns
        assert 'ETH_VADER_Sent_AvgIn' in result.columns

