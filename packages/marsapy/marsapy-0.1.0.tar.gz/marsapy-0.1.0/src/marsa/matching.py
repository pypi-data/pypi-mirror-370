from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc
from marsa.config import AspectConfig
from dataclasses import dataclass
from marsa.utils import require_spacy_model

@dataclass
class AspectMatch:
    """
    Represents a matched aspect found in text with position information.
    
    Contains both character-level and token-level position data for extracting
    context windows and performing sentiment analysis on detected aspects.
    
    Attributes:
        text (str): The actual matched text from the input
        aspect (str): The aspect name this match represents
        start (int): Character-level start position in the original text
        end (int): Character-level end position in the original text
        token_start (int): Token-level start position for context extraction
        token_end (int): Token-level end position for context extraction
        category (str | None): Optional category of the aspect (e.g., 'hardware', 'service')
    """
    text: str       # actual text matches
    aspect: str     # the aspect it represents
    start: int
    end: int   
    token_start: int
    token_end: int    
    category: str | None = None 

def match_aspect_phrases(text: str, config: AspectConfig) -> tuple[list[AspectMatch], Doc]:
    """
    Match aspect phrases in text using spaCy's PhraseMatcher.
    
    Identifies aspects and their associated phrases within the input text based on
    the provided configuration. If no phrases are defined for an aspect, uses the
    aspect name itself as the matching phrase.
    
    Args:
        text (str): Input text to search for aspect matches
        config (AspectConfig): Configuration containing aspects and their phrases
        
    Returns:
        tuple[list[AspectMatch], Doc]]: List of matched aspects with positions and 
                                     the spaCy Doc object for context extraction
        
    Raises:
        OSError: If required spaCy model cannot be loaded
    """
    nlp = require_spacy_model("en_core_web_sm")
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    
    phrase_to_aspect = {}
    patterns = [] 
    
    for aspect_name, aspect_data in config.aspects.items():
        if aspect_data.phrases:
            for phrase in aspect_data.phrases:
                patterns.append(nlp.make_doc(phrase))
                phrase_to_aspect[phrase.lower()] = aspect_name
        else:
            # If no phrases defined, use aspect name itself as the phrase
            patterns.append(nlp.make_doc(aspect_name))
            phrase_to_aspect[aspect_name.lower()] = aspect_name
    
    if patterns:
        matcher.add('AspectTermsList', patterns)
            
    doc = nlp(text)
    matches = matcher(doc)
    
    aspects = []
    for _, start, end in matches:
        span = doc[start:end]
        aspect_name = phrase_to_aspect[span.text.lower()]
        aspect_data = config.aspects[aspect_name]

        aspects.append(AspectMatch(
            text=span.text, 
            aspect=aspect_name,
            start=span.start_char, 
            end=span.end_char,     
            token_start=start,      
            token_end=end,       
            category=aspect_data.category
        ))
    
    return aspects, doc