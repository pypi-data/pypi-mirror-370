import emoji
import re
import spacy
import subprocess
import sys
from spacy.language import Language

def clean_input(text: str) -> str:
    """
    Clean and normalize input text for sentiment analysis.
    
    Performs text preprocessing including lowercasing, URL removal, email removal,
    and emoji conversion to text descriptions for better analysis accuracy.
    
    Args:
        text (str): Raw input text to be cleaned
        
    Returns:
        str: Cleaned and normalized text ready for analysis
    """
    text = text.lower()
    text = re.sub(r'http\S+|www\.\S+', '', text)
    text = re.sub(r'\w+@\w+\.com', '', text)
    text = emoji.demojize(text)
    return text.strip()
    
def require_spacy_model(name: str = "en_core_web_sm") -> Language:
    """
    Load a spaCy language model, downloading if necessary.
    
    Attempts to load the specified spaCy model and automatically downloads
    it if not already installed on the system.
    
    Args:
        name (str, optional): Name of the spaCy model to load. 
                            Defaults to "en_core_web_sm".
        
    Returns:
        Language: Loaded spaCy language processing pipeline
        
    Raises:
        subprocess.CalledProcessError: If model download fails
        OSError: If model cannot be loaded after download attempt
    """
    try:
        return spacy.load(name)
    except OSError:
        print(f"Downloading spaCy model: {name}...")
        subprocess.run([sys.executable, "-m", "spacy", "download", name], check=True)
        return spacy.load(name)
