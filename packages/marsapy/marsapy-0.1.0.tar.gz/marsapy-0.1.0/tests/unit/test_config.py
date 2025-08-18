import pytest
from pathlib import Path
from marsa.config import AspectConfig, create_aspect_config

# ---------- Regular Tests ----------

def test_load_yaml_aspects_only_example():
    # Arrange
    path = 'tests/fixtures/test_config_only_aspects.yaml'

    # Act
    config = create_aspect_config(path)

    # Assert
    assert isinstance(config, AspectConfig)
    assert config.aspects is not None
    assert isinstance(config.aspects, dict)
    
    expected_aspects = ['camera', 'battery', 'screen']
    assert len(config.aspects) == len(expected_aspects)
    for aspect_name in expected_aspects:
        assert aspect_name in config.aspects
        assert config.aspects[aspect_name].phrases is None
        assert config.aspects[aspect_name].category is None

def test_load_yaml_no_phrases_example():
    # Arrange
    path = 'tests/fixtures/test_config_no_phrases.yaml'

    # Act
    config = create_aspect_config(path)

    # Assert
    assert isinstance(config, AspectConfig)
    assert config.aspects is not None
    assert isinstance(config.aspects, dict)
    
    expected_categories = {'camera': 'hardware', 'battery': 'hardware', 'screen': 'interface'}
    assert len(config.aspects) == len(expected_categories)
    for aspect_name, expected_category in expected_categories.items():
        assert aspect_name in config.aspects
        assert config.aspects[aspect_name].phrases is None
        assert config.aspects[aspect_name].category == expected_category

def test_load_yaml_no_categories_example():
    # Arrange
    path = 'tests/fixtures/test_config_no_categories.yaml'

    # Act
    config = create_aspect_config(path)

    # Assert
    assert isinstance(config, AspectConfig)
    assert config.aspects is not None
    assert isinstance(config.aspects, dict)
    
    expected_phrases = {
        'camera': ["camera", "photo", "picture", "pics", "photography", "image", "snap"],
        'battery': ["battery", "power", "charge", "charging", "juice", "drain", "life"],
        'screen': ["screen", "display", "resolution", "brightness", "monitor", "lcd", "oled"]
    }
    assert len(config.aspects) == len(expected_phrases)
    for aspect_name, expected_phrase_list in expected_phrases.items():
        assert aspect_name in config.aspects
        assert config.aspects[aspect_name].phrases == expected_phrase_list
        assert config.aspects[aspect_name].category is None

def test_load_yaml_full_config_example():
    # Arrange
    path = 'tests/fixtures/config.yaml'

    # Act
    config = create_aspect_config(path)

    # Assert
    assert isinstance(config, AspectConfig)
    assert config.aspects is not None
    assert isinstance(config.aspects, dict)
    
    expected_data = {
        'camera': {
            'phrases': ["camera", "photo", "picture", "pics", "photography", "image", "snap"],
            'category': 'hardware'
        },
        'battery': {
            'phrases': ["battery", "power", "charge", "charging", "juice", "drain", "life"],
            'category': 'hardware'
        },
        'screen': {
            'phrases': ["screen", "display", "resolution", "brightness", "monitor", "lcd", "oled"],
            'category': 'interface'
        }
    }
    
    assert len(config.aspects) == len(expected_data)
    for aspect_name, expected_aspect_data in expected_data.items():
        assert aspect_name in config.aspects
        assert config.aspects[aspect_name].phrases == expected_aspect_data['phrases']
        assert config.aspects[aspect_name].category == expected_aspect_data['category']

def test_load_json_aspects_only_example():
    # Arrange
    path = 'tests/fixtures/test_config_only_aspects.json'
    
    # Act
    config = create_aspect_config(path)

    # Assert
    assert isinstance(config, AspectConfig)
    assert config.aspects is not None
    assert isinstance(config.aspects, dict)
    
    expected_aspects = ['camera', 'battery', 'screen']
    assert len(config.aspects) == len(expected_aspects)
    for aspect_name in expected_aspects:
        assert aspect_name in config.aspects
        assert config.aspects[aspect_name].phrases is None
        assert config.aspects[aspect_name].category is None

def test_load_json_no_phrases_example():
    # Arrange
    path = 'tests/fixtures/test_config_no_phrases.json'
    
    # Act
    config = create_aspect_config(path)

    # Assert
    assert isinstance(config, AspectConfig)
    assert config.aspects is not None
    assert isinstance(config.aspects, dict)
    
    expected_categories = {'camera': 'hardware', 'battery': 'hardware', 'screen': 'interface'}
    assert len(config.aspects) == len(expected_categories)
    for aspect_name, expected_category in expected_categories.items():
        assert aspect_name in config.aspects
        assert config.aspects[aspect_name].phrases is None
        assert config.aspects[aspect_name].category == expected_category

def test_load_json_no_categories_example():
    # Arrange
    path = 'tests/fixtures/test_config_no_categories.json'
    
    # Act
    config = create_aspect_config(path)

    # Assert
    assert isinstance(config, AspectConfig)
    assert config.aspects is not None
    assert isinstance(config.aspects, dict)
    
    expected_phrases = {
        'camera': ["camera", "photo", "picture", "pics", "photography", "image", "snap"],
        'battery': ["battery", "power", "charge", "charging", "juice", "drain", "life"],
        'screen': ["screen", "display", "resolution", "brightness", "monitor", "lcd", "oled"]
    }
    assert len(config.aspects) == len(expected_phrases)
    for aspect_name, expected_phrase_list in expected_phrases.items():
        assert aspect_name in config.aspects
        assert config.aspects[aspect_name].phrases == expected_phrase_list
        assert config.aspects[aspect_name].category is None

def test_load_json_full_config_example():
    # Arrange
    path = 'tests/fixtures/config.json'
    
    # Act
    config = create_aspect_config(path)

    # Assert
    assert isinstance(config, AspectConfig)
    assert config.aspects is not None
    assert isinstance(config.aspects, dict)
    
    expected_data = {
        'camera': {
            'phrases': ["camera", "photo", "picture", "pics", "photography", "image", "snap"],
            'category': 'hardware'
        },
        'battery': {
            'phrases': ["battery", "power", "charge", "charging", "juice", "drain", "life"],
            'category': 'hardware'
        },
        'screen': {
            'phrases': ["screen", "display", "resolution", "brightness", "monitor", "lcd", "oled"],
            'category': 'interface'
        }
    }
    
    assert len(config.aspects) == len(expected_data)
    for aspect_name, expected_aspect_data in expected_data.items():
        assert aspect_name in config.aspects
        assert config.aspects[aspect_name].phrases == expected_aspect_data['phrases']
        assert config.aspects[aspect_name].category == expected_aspect_data['category']

# ---------- Edge Case Tests ----------

def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        create_aspect_config('tests/fixtures/nonexistent.yaml')

def test_invalid_extension_raises():
    # Arrange
    invalid_file = Path('tests/fixtures/unsupported.csv')
    
    # Act
    invalid_file.write_text('dummy content')
    
    # Assert
    with pytest.raises(NameError):
        create_aspect_config(str(invalid_file))

    invalid_file.unlink()  # cleanup

def test_empty_aspects_dict():
    empty_file = Path('tests/fixtures/empty_aspects.yaml')
    empty_file.write_text('aspects: {}')
    
    try:
        config = create_aspect_config(str(empty_file))
        assert isinstance(config, AspectConfig)
        assert config.aspects == {}
    finally:
        empty_file.unlink()