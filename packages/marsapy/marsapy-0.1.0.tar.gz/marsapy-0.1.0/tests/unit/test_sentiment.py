# Updated test_sentiment.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from marsa.sentiment import AspectSentimentAnalyzer, AspectSentiment, AspectSentimentResult
from marsa.matching import AspectMatch
from tests.fixtures.constants import EXAMPLE_CORPUS, FIRST_ASPECT_MATCH, SECOND_ASPECT_MATCH

# ---------- Setup and Fixtures ----------

@pytest.fixture
def mock_doc():
    mock_doc = MagicMock()
    mock_doc.__len__.return_value = 10

    mock_span = MagicMock()
    mock_span.text = "context around aspect"
    
    mock_doc.__getitem__.return_value = mock_span
    return mock_doc

@pytest.fixture
def analyzer():
    with patch('marsa.sentiment.pipeline') as mock_pipeline, \
         patch('marsa.sentiment.SentimentIntensityAnalyzer') as mock_vader:
        
        mock_bert = Mock()
        mock_bert.return_value = [[
            {'label': 'Negative', 'score': 0.1},
            {'label': 'Neutral', 'score': 0.2},
            {'label': 'Positive', 'score': 0.7}
        ]]
        mock_pipeline.return_value = mock_bert
        
        mock_vader_instance = Mock()
        mock_vader_instance.polarity_scores.return_value = {
            'compound': 0.5, 'pos': 0.6, 'neu': 0.3, 'neg': 0.1
        }
        mock_vader.return_value = mock_vader_instance
        
        analyzer = AspectSentimentAnalyzer()
        analyzer.bert_model = mock_bert
        analyzer.vader_analyzer = mock_vader_instance
        
        return analyzer

# ---------- Regular Tests ----------

def test_aspect_sentiment_analyzer_init():
    with patch('marsa.sentiment.pipeline'), \
         patch('marsa.sentiment.SentimentIntensityAnalyzer'):
        
        analyzer = AspectSentimentAnalyzer()
        
        assert analyzer.threshold == 0.05
        assert analyzer.context_window == 3
        assert analyzer.doc is None

def test_analyze_text_basic(analyzer, mock_doc):
    # Arrange
    text = EXAMPLE_CORPUS[0]
    aspect_matches = [FIRST_ASPECT_MATCH, SECOND_ASPECT_MATCH]
    
    # Act
    result = analyzer.analyze_text(text, aspect_matches, mock_doc)
    
    # Assert
    assert isinstance(result, AspectSentimentResult)
    assert result.text == text
    assert len(result.aspects) == 2
    assert all(isinstance(aspect, AspectSentiment) for aspect in result.aspects)
    for i, aspect in enumerate(result.aspects):
        if i == 0:
            assert aspect.aspect_match == FIRST_ASPECT_MATCH
        else:
            assert aspect.aspect_match == SECOND_ASPECT_MATCH
        
        assert aspect.sentiment in ["positive", "negative", "neutral"]
        assert isinstance(aspect.confidence, (float, type(None)))
        assert isinstance(aspect.context_used, (str, type(None)))

def test_extract_context_window(analyzer, mock_doc):
    # Arrange
    analyzer.doc = mock_doc
    analyzer.context_window = 2
    aspect_match = AspectMatch(
        text="test", 
        aspect="camera",
        start=0, 
        end=4, 
        token_start=3, 
        token_end=4, 
        category=None
    )
    
    # Act
    context = analyzer._extract_context_window(aspect_match)
    
    # Assert
    assert isinstance(context, str)
    assert context == "context around aspect"
    mock_doc.__getitem__.assert_called_once()

def test_extract_bert_probabilities(analyzer):
    # Arrange
    bert_results = [
        {'label': 'Negative', 'score': 0.1},
        {'label': 'Neutral', 'score': 0.2},
        {'label': 'Positive', 'score': 0.7}
    ]
    
    # Act
    probs = analyzer._extract_bert_probabilities(bert_results)
    
    # Assert
    assert len(probs) == 3
    assert probs[0] == 0.1  # negative
    assert probs[1] == 0.2  # neutral
    assert probs[2] == 0.7  # positive

def test_weighted_sentiment_positive(analyzer):
    # Arrange
    bert_probs = [0.1, 0.2, 0.7]  # strongly positive
    vader_score = 0.5  # positive
    
    # Act
    sentiment, confidence = analyzer._weighted_sentiment(bert_probs, vader_score)
    
    # Assert
    assert sentiment == "positive"
    assert isinstance(confidence, float)
    assert 0 <= confidence <= 1

def test_weighted_sentiment_negative(analyzer):
    # Arrange
    bert_probs = [0.8, 0.1, 0.1]  # strongly negative
    vader_score = -0.6  # negative
    
    # Act
    sentiment, confidence = analyzer._weighted_sentiment(bert_probs, vader_score)
    
    # Assert
    assert sentiment == "negative"
    assert isinstance(confidence, float)
    assert 0 <= confidence <= 1

def test_weighted_sentiment_neutral(analyzer):
    # Arrange
    bert_probs = [0.3, 0.4, 0.3]  # neutral
    vader_score = 0.02  # very low positive (below threshold)
    
    # Act
    sentiment, confidence = analyzer._weighted_sentiment(bert_probs, vader_score)
    
    # Assert
    assert sentiment == "neutral"
    assert isinstance(confidence, float)

# ---------- Edge Cases ----------

def test_analyze_text_empty_aspects(analyzer, mock_doc):
    # Arrange
    text = "Some text without aspects"
    aspect_matches = []
    
    # Act
    result = analyzer.analyze_text(text, aspect_matches, mock_doc)
    
    # Assert
    assert isinstance(result, AspectSentimentResult)
    assert result.text == text
    assert len(result.aspects) == 0

def test_extract_context_window_boundary_conditions(analyzer):
    # Arrange
    analyzer.context_window = 10
    mock_doc = MagicMock()
    mock_doc.__len__.return_value = 5
    
    mock_span = MagicMock()
    mock_span.text = "boundary context"
    mock_doc.__getitem__.return_value = mock_span
    
    analyzer.doc = mock_doc
    
    aspect_match = AspectMatch(
        text="test", 
        aspect="camera",
        start=0, 
        end=4,
        token_start=0, 
        token_end=1, 
        category=None
    )
    
    # Act
    context = analyzer._extract_context_window(aspect_match)
    
    # Assert
    assert isinstance(context, str)
    assert context == "boundary context"

def test_extract_bert_probabilities_missing_labels(analyzer):
    # Arrange
    bert_results = [
        {'label': 'Positive', 'score': 0.6},
    ]
    
    # Act
    probs = analyzer._extract_bert_probabilities(bert_results)
    
    # Assert
    assert len(probs) == 3
    assert probs[0] == 0.0  # negative (missing)
    assert probs[1] == 0.0  # neutral (missing)
    assert probs[2] == 0.6  # positive

def test_weighted_sentiment_zero_confidence(analyzer):
    # Arrange
    bert_probs = [0.0, 0.0, 0.0]  # no confidence
    vader_score = 0.0  # no sentiment
    
    # Act
    sentiment, confidence = analyzer._weighted_sentiment(bert_probs, vader_score)
    
    # Assert
    assert sentiment == "neutral"  # defaults to neutral
    assert isinstance(confidence, float)