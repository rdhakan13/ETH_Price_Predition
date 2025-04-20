import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.sentiment_analyser.bert_sentiment_analyser import BertSentimentAnalyser

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "headline": [
            "Stocks are rising after strong earnings",
            "Markets crash as inflation worries grow"
        ]
    })


@pytest.fixture
def mock_pipeline_output():
    return [[{"label": "POSITIVE", "score": 0.98}], [{"label": "NEGATIVE", "score": 0.87}]]

@patch("src.sentiment_analyser.bert_sentiment_analyser.AutoTokenizer.from_pretrained")
@patch("src.sentiment_analyser.bert_sentiment_analyser.AutoModelForSequenceClassification.from_pretrained")
@patch("src.sentiment_analyser.bert_sentiment_analyser.pipeline")
@patch("src.sentiment_analyser.bert_sentiment_analyser.torch.cuda.is_available", return_value=False)
def test_initialization(mock_cuda, mock_pipeline, mock_model, mock_tokenizer, sample_df):
    mock_pipeline.return_value = MagicMock()
    analyser = BertSentimentAnalyser(sample_df, "bert-base-uncased")
    assert analyser.device == -1
    assert analyser.model_name == "bert-base-uncased"
    assert analyser.analyzer is mock_pipeline.return_value


@patch("src.sentiment_analyser.bert_sentiment_analyser.AutoTokenizer.from_pretrained")
@patch("src.sentiment_analyser.bert_sentiment_analyser.AutoModelForSequenceClassification.from_pretrained")
@patch("src.sentiment_analyser.bert_sentiment_analyser.pipeline")
@patch("src.sentiment_analyser.bert_sentiment_analyser.torch.cuda.is_available", return_value=False)
@patch("src.sentiment_analyser.bert_sentiment_analyser.swifter")
def test_analyse_sentiment_success(
    mock_swifter, mock_torch, mock_pipeline, mock_model, mock_tokenizer, sample_df, mock_pipeline_output
):
    # Setup mocks
    mock_analyzer = MagicMock()
    mock_analyzer.side_effect = mock_pipeline_output
    mock_pipeline.return_value = mock_analyzer

    mock_swifter.apply.side_effect = lambda func: sample_df["headline"].apply(func)

    analyser = BertSentimentAnalyser(sample_df.copy(), "bert-base-uncased")
    analyser.analyzer = lambda text: [{"label": "POSITIVE", "score": 0.95}] if "rising" in text else [{"label": "NEGATIVE", "score": 0.85}]
    analyser.determine_sentiment = lambda label: "POS" if label == "POSITIVE" else "NEG"

    result_df = analyser.analyse_sentiment("headline")

    assert f"D_{analyser._model_name()}_ConScore" in result_df.columns
    assert f"D_{analyser._model_name()}_Sent" in result_df.columns
    assert result_df.iloc[0][f"D_{analyser._model_name()}_Sent"] == "POS"
    assert result_df.iloc[1][f"D_{analyser._model_name()}_Sent"] == "NEG"



@patch("src.sentiment_analyser.bert_sentiment_analyser.AutoTokenizer.from_pretrained")
@patch("src.sentiment_analyser.bert_sentiment_analyser.AutoModelForSequenceClassification.from_pretrained")
@patch("src.sentiment_analyser.bert_sentiment_analyser.pipeline")
@patch("src.sentiment_analyser.bert_sentiment_analyser.torch.cuda.is_available", return_value=False)
def test_analyse_sentiment_column_not_found(mock_cuda, mock_pipeline, mock_model, mock_tokenizer, sample_df):
    analyser = BertSentimentAnalyser(sample_df, "bert-base-uncased")
    with pytest.raises(ValueError, match="Column 'missing_column' not found in df"):
        analyser.analyse_sentiment("missing_column")


def test_determine_sentiment_valid():
    analyser = BertSentimentAnalyser(pd.DataFrame(), "bert-base-uncased")
    assert analyser.determine_sentiment("positive") == 1
    assert analyser.determine_sentiment("bullish") == 1
    assert analyser.determine_sentiment("negative") == -1
    assert analyser.determine_sentiment("bearish") == -1
    assert analyser.determine_sentiment("neutral") == 0


def test_determine_sentiment_invalid_type():
    analyser = BertSentimentAnalyser(pd.DataFrame(), "bert-base-uncased")
    with pytest.raises(ValueError, match="Input must be a string"):
        analyser.determine_sentiment(123)


def test_determine_sentiment_unknown_label():
    analyser = BertSentimentAnalyser(pd.DataFrame(), "bert-base-uncased")
    with pytest.raises(ValueError, match="Unknown sentiment label: happy"):
        analyser.determine_sentiment("happy")


def test_model_name_extraction():
    analyser = BertSentimentAnalyser(pd.DataFrame(), "bert-base-uncased")
    assert analyser._model_name() == "BERT-BASE-UNCased".split("/")[-1].upper()