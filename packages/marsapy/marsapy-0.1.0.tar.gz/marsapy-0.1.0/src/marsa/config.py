import json
import yaml
from dataclasses import dataclass
from pathlib import Path
   
@dataclass 
class AspectData:
    """
    Data container for aspect configuration information.
    
    Stores the phrases associated with an aspect and its optional category
    for aspect-based sentiment analysis configuration.
    
    Attributes:
        phrases (list[str] | None): List of phrase patterns to match for this aspect.
                                   If None, the aspect name itself is used as the phrase.
        category (str | None): Optional category classification for grouping aspects
                              (e.g., 'hardware', 'software', 'service').
    """
    phrases: list[str] | None = None
    category: str | None = None
     
@dataclass
class AspectConfig:
    """
    Configuration container for all aspects in the sentiment analysis system.
    
    Holds the complete aspect configuration loaded from YAML or JSON files,
    mapping aspect names to their associated data (phrases and categories).
    
    Attributes:
        aspects (dict[str, AspectData]): Dictionary mapping aspect names to their
                                       configuration data including phrases and categories.
    """
    aspects: dict[str, AspectData]
    
def create_aspect_config(file_path: str) -> AspectConfig:
    """
    Creates an AspectConfig dataclass from a YAML or JSON configuration file.
    
    Parses aspect definitions including optional phrases and categories from
    the configuration file and returns a structured AspectConfig object.
    
    Args:
        file_path (str): Path to the configuration file (.yaml/.yml or .json)
    
    Returns:
        AspectConfig: Configured aspects with phrases and categories
        
    Raises:
        FileNotFoundError: If the configuration file doesn't exist
        NameError: If the file extension isn't .yaml/.yml or .json
        yaml.YAMLError: If YAML parsing fails
        json.JSONDecodeError: If JSON parsing fails
    """
    path = Path(file_path).resolve()
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if path.suffix not in ('.yaml', '.yml', '.json'):
        raise NameError('Expected YAML (.yaml, .yml) or JSON (.json) extension.')
    
    with path.open('r', encoding='utf-8') as fp:
        if path.suffix in ('.yaml', '.yml'):
            data = yaml.safe_load(fp)
        else: # .json
            data = json.load(fp)

    aspects = {
        aspect_name: AspectData(
            phrases=aspect_data.get('phrases'),
            category=aspect_data.get('category')
        )
        for aspect_name, aspect_data in data.get('aspects', {}).items()
    }
    
    return AspectConfig(aspects=aspects)