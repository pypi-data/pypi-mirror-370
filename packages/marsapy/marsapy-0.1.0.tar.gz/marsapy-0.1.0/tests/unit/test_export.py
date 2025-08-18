import pytest
import json
import pandas as pd
from marsa.export import export_for_review
from tests.fixtures.constants import SAMPLE_RESULTS

# ---------- Regular Tests ----------

def test_export_json_format(tmp_path):
    # Arrange
    output_file = tmp_path / "test_results.json"
    
    # Act
    export_for_review(SAMPLE_RESULTS, str(output_file))
    
    # Assert
    assert output_file.exists()
    with open(output_file) as f:
        data = json.load(f)
    assert data == SAMPLE_RESULTS

def test_export_csv_format(tmp_path):
    # Arrange
    output_file = tmp_path / "test_results.csv"
    expected_rows = [
        {
            'text': 'great camera but battery life is terrible',
            'aspect': 'camera',
            'category': 'hardware',
            'prelabeled_sentiment': 'positive',
            'confidence': 0.85
        },
        {
            'text': 'great camera but battery life is terrible',
            'aspect': 'battery',
            'category': 'hardware',
            'prelabeled_sentiment': 'negative',
            'confidence': 0.92
        },
        {
            'text': 'beautiful screen display',
            'aspect': 'screen',
            'category': 'interface',
            'prelabeled_sentiment': 'positive',
            'confidence': 0.95
        }
    ]
    
    # Act
    export_for_review(SAMPLE_RESULTS, str(output_file))
    
    # Assert
    assert output_file.exists()
    df = pd.read_csv(output_file)
    assert len(df) == 3
    assert list(df.columns) == ['text', 'aspect', 'category', 'prelabeled_sentiment', 'confidence']
    
    for i, expected in enumerate(expected_rows):
        assert df.iloc[i]['text'] == expected['text']
        assert df.iloc[i]['aspect'] == expected['aspect']
        assert df.iloc[i]['category'] == expected['category']
        assert df.iloc[i]['prelabeled_sentiment'] == expected['prelabeled_sentiment']
        assert df.iloc[i]['confidence'] == expected['confidence']

def test_export_creates_parent_directories(tmp_path):
    # Arrange
    nested_path = tmp_path / "nested" / "deep" / "directory" / "results.json"
    
    # Act
    export_for_review(SAMPLE_RESULTS, str(nested_path))
    
    # Assert
    assert nested_path.exists()
    assert nested_path.parent.exists()

def test_export_json_with_uppercase_extension(tmp_path):
    # Arrange
    output_file = tmp_path / "test_results.JSON"
    
    # Act
    export_for_review(SAMPLE_RESULTS, str(output_file))
    
    # Assert
    assert output_file.exists()
    with open(output_file) as f:
        data = json.load(f)
    assert data == SAMPLE_RESULTS

def test_export_csv_with_uppercase_extension(tmp_path):
    # Arrange
    output_file = tmp_path / "test_results.CSV"
    
    # Act
    export_for_review(SAMPLE_RESULTS, str(output_file))
    
    # Assert
    assert output_file.exists()
    df = pd.read_csv(output_file)
    assert len(df) == 3

# ---------- Edge Case Tests ----------

def test_export_empty_results_json(tmp_path):
    # Arrange
    output_file = tmp_path / "empty_results.json"
    empty_results = []
    
    # Act
    export_for_review(empty_results, str(output_file))
    
    # Assert
    assert output_file.exists()
    with open(output_file) as f:
        data = json.load(f)
    assert data == []

def test_export_empty_results_csv(tmp_path):
    # Arrange
    output_file = tmp_path / "empty_results.csv"
    empty_results = []
    
    # Act
    export_for_review(empty_results, str(output_file))
    
    # Assert
    assert output_file.exists()
    with open(output_file) as f:
        content = f.read().strip()
    expected_header = "text,aspect,category,prelabeled_sentiment,confidence"
    assert content == expected_header

def test_export_single_result_multiple_aspects(tmp_path):
    # Arrange
    output_file = tmp_path / "single_result.csv"
    single_result = [
        {
            'cleaned_text': 'camera quality is amazing but screen brightness is poor',
            'aspect_sentiments': [
                {'aspect': 'camera', 'category': 'hardware', 'sentiment': 'positive', 'confidence': 0.88},
                {'aspect': 'screen', 'category': 'interface', 'sentiment': 'negative', 'confidence': 0.91}
            ]
        }
    ]
    
    # Act
    export_for_review(single_result, str(output_file))
    
    # Assert
    assert output_file.exists()
    df = pd.read_csv(output_file)
    assert len(df) == 2
    assert all(df['text'] == 'camera quality is amazing but screen brightness is poor')

def test_export_unsupported_extension_raises_error(tmp_path):
    # Arrange
    output_file = tmp_path / "results.txt"
    
    # Act & Assert
    with pytest.raises(ValueError, match="Unsupported file extension: .txt; expected .json or .csv"):
        export_for_review(SAMPLE_RESULTS, str(output_file))

def test_export_no_extension_raises_error(tmp_path):
    # Arrange
    output_file = tmp_path / "results"
    
    # Act & Assert
    with pytest.raises(ValueError, match="Unsupported file extension: ; expected .json or .csv"):
        export_for_review(SAMPLE_RESULTS, str(output_file))