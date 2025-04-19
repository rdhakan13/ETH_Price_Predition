import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.sentiment_analyser.bert_sentiment_analyser import BertSentimentAnalyser


@pytest.fixture
def sample_df():
    return pd.DataFrame({"text": ["I love this!", "This is bad.", "Meh, it's ok."]})


@pytest.fixture
def mock_pipeline_output():
    return [
        [{"label": "POSITIVE", "score": 0.95}],
        [{"label": "NEGATIVE", "score": 0.85}],
        [{"label": "NEUTRAL", "score": 0.60}],
    ]


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
@patch("swifter.swifter.SeriesAccessor.apply", autospec=True)
def test_analyse_sentiment(
    mock_swifter_apply,
    mock_cuda,
    mock_pipeline,
    mock_model,
    mock_tokenizer,
):
    sample_df = pd.DataFrame({"text": ["I love this!", "This is bad.", "Meh, it's ok."]})
    mock_pipeline_output = [
        {'label': 'POSITIVE', 'score': 0.95},
        {'label': 'NEGATIVE', 'score': 0.85},
        {'label': 'NEUTRAL', 'score': 0.6},
    ]

    # Mock the analyzer to return dicts
    mock_analyzer = MagicMock()
    mock_analyzer.side_effect = lambda x: mock_pipeline_output[sample_df["text"].tolist().index(x)]
    mock_pipeline.return_value = mock_analyzer

    # Simulate swifter's apply method (should behave like pandas apply)
    def apply_side_effect(self, func, *args, **kwargs):
        return sample_df["text"].astype(str).apply(func)

    mock_swifter_apply.side_effect = apply_side_effect

    analyser = BertSentimentAnalyser(sample_df.copy(), "bert-base-uncased")
    analyser.analyzer = mock_analyzer
    result_df = analyser.analyse_sentiment("text")

    # Assert the final result has the expected structure
    expected = pd.DataFrame({
        "text": ["I love this!", "This is bad.", "Meh, it's ok."],
        "label": ["POSITIVE", "NEGATIVE", "NEUTRAL"],
        "score": [0.95, 0.85, 0.6]
    })
    pd.testing.assert_frame_equal(result_df.reset_index(drop=True), expected.reset_index(drop=True))



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