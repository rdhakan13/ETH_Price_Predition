import pytest
import pandas as pd
from unittest.mock import patch
from src.sentiment_analyser.vader_sentiment_analyser import VaderSentimentAnalyser


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "headline": [
            "Stocks rally as investors cheer economic recovery.",
            "Market crashes amid recession fears.",
            "Investors wait and watch."
        ]
    })


def test_initialization(sample_df):
    analyser = VaderSentimentAnalyser(sample_df)
    assert hasattr(analyser, "analyzer")
    assert isinstance(analyser.df, pd.DataFrame)

def test_initialization_invalid_input():
    with pytest.raises(ValueError, match="Input must be a pandas DataFrame"):
        VaderSentimentAnalyser("not a dataframe")

def test_analyse_sentiment_success(sample_df):
    analyser = VaderSentimentAnalyser(sample_df)
    result_df = analyser.analyse_sentiment("headline")
    assert "D_VADER_Score" in result_df.columns
    assert "D_VADER_Sent" in result_df.columns
    assert all(isinstance(score, float) for score in result_df["D_VADER_Score"])
    assert all(sent in [-1, 0, 1] for sent in result_df["D_VADER_Sent"])


def test_analyse_sentiment_column_not_found(sample_df):
    analyser = VaderSentimentAnalyser(sample_df)
    with pytest.raises(ValueError, match="Column 'invalid_column' not found in DataFrame"):
        analyser.analyse_sentiment("invalid_column")


@pytest.mark.parametrize("score,expected", [
    (0.1, 1),
    (-0.1, -1),
    (0.0, 0),
    (0.05, 1),
    (-0.05, -1),
])
def test_determine_sentiment_valid(score, expected, sample_df):
    analyser = VaderSentimentAnalyser(sample_df)
    assert analyser.determine_sentiment(score) == expected


@pytest.mark.parametrize("invalid_input", ["text", None, True, [], {}])
def test_determine_sentiment_invalid_type(invalid_input, sample_df):
    analyser = VaderSentimentAnalyser(sample_df)
    with pytest.raises(ValueError, match="Input must be a float"):
        analyser.determine_sentiment(invalid_input)
