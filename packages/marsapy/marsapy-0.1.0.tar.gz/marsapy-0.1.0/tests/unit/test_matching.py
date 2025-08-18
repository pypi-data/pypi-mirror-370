from marsa.config import AspectConfig, AspectData
from marsa.matching import match_aspect_phrases, AspectMatch
from tests.fixtures.constants import ASPECT_CONFIG

# ---------- Regular Tests ----------

def test_match_aspect_phrases_basic():
    # Arrange
    text = "I love the camera but hate the battery life"
    
    # Act
    aspects, _ = match_aspect_phrases(text, ASPECT_CONFIG)
    
    # Assert
    assert len(aspects) == 2
    assert all(isinstance(aspect, AspectMatch) for aspect in aspects)
    
    # Check first match (camera)
    camera_match = next(a for a in aspects if a.text == "camera")
    assert camera_match.text == "camera"
    assert camera_match.aspect == "camera"
    assert camera_match.start == 11
    assert camera_match.end == 17
    assert camera_match.token_start == 3
    assert camera_match.token_end == 4
    assert camera_match.category == "hardware"
    
    # Check second match (battery)
    battery_match = next(a for a in aspects if a.text == "battery")
    assert battery_match.text == "battery"
    assert battery_match.aspect == "battery"
    assert battery_match.start == 31
    assert battery_match.end == 38
    assert battery_match.token_start == 7
    assert battery_match.token_end == 8
    assert battery_match.category == "hardware"

def test_match_aspect_phrases_returns_doc():
    # Arrange
    text = "I love the camera but hate the battery life"
    
    # Act
    _, doc = match_aspect_phrases(text, ASPECT_CONFIG)
    
    # Assert
    assert doc is not None
    assert hasattr(doc, 'text')
    assert doc.text == text
    assert len(doc) > 0

def test_match_aspect_phrases_no_matches():
    # Arrange
    text = "This is a simple sentence with no relevant terms"
    
    # Act
    aspects, doc = match_aspect_phrases(text, ASPECT_CONFIG)
    
    # Assert
    assert len(aspects) == 0
    assert doc is not None
    assert doc.text == text

def test_match_aspect_phrases_multiple_same_term():
    # Arrange
    text = "The camera quality is good, but the camera settings are confusing"
    
    # Act
    aspects, _ = match_aspect_phrases(text, ASPECT_CONFIG)
    
    # Assert
    assert len(aspects) == 2
    assert all(aspect.text == "camera" for aspect in aspects)
    assert all(aspect.aspect == "camera" for aspect in aspects)
    assert all(aspect.category == "hardware" for aspect in aspects)
    assert aspects[0].start != aspects[1].start
    assert aspects[0].end != aspects[1].end

def test_match_aspect_phrases_case_insensitive():
    # Arrange
    text = "I love the CAMERA but hate the Battery life"
    
    # Act
    aspects, _ = match_aspect_phrases(text, ASPECT_CONFIG)
    
    # Assert
    assert len(aspects) == 2
    
    camera_match = next(aspect for aspect in aspects if aspect.text.lower() == "camera")
    battery_match = next(aspect for aspect in aspects if aspect.text.lower() == "battery")
    
    assert camera_match.aspect == "camera"
    assert battery_match.aspect == "battery"
    assert camera_match.category == "hardware"
    assert battery_match.category == "hardware"

def test_match_aspect_phrases_no_phrases_uses_aspect_names():
    # Arrange
    config = AspectConfig(
        aspects={
            'camera': AspectData(category="hardware"),
            'battery': AspectData(category="hardware"),
            'screen': AspectData(category="interface")
        }
    )
    text = "The camera and screen are great"
    
    # Act
    aspects, _ = match_aspect_phrases(text, config)
    
    # Assert
    assert len(aspects) == 2
    assert all(aspect.category is not None for aspect in aspects)
    
    for aspect in aspects:
        assert aspect.text == aspect.aspect
    
    terms_found = [aspect.text for aspect in aspects]
    aspects_found = [aspect.aspect for aspect in aspects]
    assert "camera" in terms_found
    assert "screen" in terms_found
    assert "camera" in aspects_found
    assert "screen" in aspects_found

def test_match_aspect_phrases_mixed_phrases_and_names():
    # Arrange
    config = AspectConfig(
        aspects={
            'camera': AspectData(
                phrases=["camera", "photo", "picture"],
                category="hardware"
            ),
            'battery': AspectData(category="hardware"),
            'screen': AspectData(
                phrases=["display", "monitor"],
                category="interface"
            )
        }
    )
    text = "The photo quality is good, battery lasts long, and display is bright"
    
    # Act
    aspects, _ = match_aspect_phrases(text, config)
    
    # Assert
    assert len(aspects) == 3
    
    matched_texts = [aspect.text for aspect in aspects]
    
    assert "photo" in matched_texts
    assert "battery" in matched_texts
    assert "display" in matched_texts
    
    photo_match = next(a for a in aspects if a.text == "photo")
    battery_match = next(a for a in aspects if a.text == "battery") 
    display_match = next(a for a in aspects if a.text == "display")
    
    assert photo_match.aspect == "camera"
    assert battery_match.aspect == "battery" 
    assert display_match.aspect == "screen"

# ---------- Edge Cases ----------

def test_match_aspect_phrases_empty_text():
    # Arrange
    text = ""
    
    # Act
    aspects, doc = match_aspect_phrases(text, ASPECT_CONFIG)
    
    # Assert
    assert len(aspects) == 0
    assert doc is not None
    assert doc.text == ""

def test_match_aspect_phrases_whitespace_only():
    # Arrange
    text = "   \n\t  "
    
    # Act
    aspects, doc = match_aspect_phrases(text, ASPECT_CONFIG)
    
    # Assert
    assert len(aspects) == 0
    assert doc is not None

def test_match_aspect_phrases_punctuation_handling():
    # Arrange
    text = "The camera, battery, and display work well!"
    
    # Act
    aspects, _ = match_aspect_phrases(text, ASPECT_CONFIG)
    
    # Assert
    assert len(aspects) == 3
    terms_found = [aspect.text for aspect in aspects]
    assert "camera" in terms_found
    assert "battery" in terms_found  
    assert "display" in terms_found

def test_match_aspect_phrases_partial_word_no_match():
    # Arrange
    text = "The cameras and batteries are working"
    
    # Act
    aspects, _ = match_aspect_phrases(text, ASPECT_CONFIG)
    
    # Assert
    assert len(aspects) == 0

def test_match_aspect_phrases_empty_config():
    # Arrange
    config = AspectConfig(aspects={})
    text = "The camera and battery are good"
    
    # Act
    aspects, doc = match_aspect_phrases(text, config)
    
    # Assert
    assert len(aspects) == 0
    assert doc is not None