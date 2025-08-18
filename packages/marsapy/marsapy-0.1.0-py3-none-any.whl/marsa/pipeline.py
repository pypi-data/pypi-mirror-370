from marsa.config import create_aspect_config
from marsa.matching import match_aspect_phrases
from marsa.sentiment import AspectSentimentAnalyzer, AspectSentimentResult
from marsa.utils import clean_input

class AspectSentimentPipeline:
    """
    Complete pipeline for aspect-based sentiment analysis.
    
    Orchestrates the entire process from text input to sentiment results,
    including aspect configuration loading, text cleaning, aspect matching,
    and sentiment analysis. Provides both structured and flattened output
    formats for different use cases.
    
    The pipeline handles text preprocessing, aspect detection using spaCy's
    PhraseMatcher, and sentiment analysis using the ensemble AspectSentimentAnalyzer.
    
    Attributes:
        config (AspectConfig): Loaded aspect configuration with phrases and categories
        sentiment_analyzer (AspectSentimentAnalyzer): Configured sentiment analysis engine
    """
    
    def __init__(self, config_file: str, context_window: int = 3):
        """
        Initialize the aspect sentiment analysis pipeline.
        
        Args:
            config_file (str): Path to aspect configuration file
            context_window (int, optional): Number of tokens before/after aspects 
                                        for sentiment context. Defaults to 3.
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            NameError: If configuration file has invalid extension
        """
        self.config = create_aspect_config(config_file)
        self.sentiment_analyzer = AspectSentimentAnalyzer(context_window=context_window)
    
    def process_corpus_flat(self, comments: list[str]) -> list[dict]:
        """
        Process a list of comments and return flattened results suitable for export.
        
        Performs aspect matching and sentiment analysis on each comment, returning
        results in a dictionary format optimized for JSON/CSV export.
        
        Args:
            comments (list[str]): List of text comments to analyze
            
        Returns:
            list[dict]: List of analysis results with flattened aspect-sentiment data
        """
        results = []
        for comment in comments:
            cleaned = clean_input(comment)
            aspects, doc = match_aspect_phrases(cleaned, self.config)
            sentiment_result = self.sentiment_analyzer.analyze_text(cleaned, aspects, doc)
            results.append({
                'original_text': comment,
                'cleaned_text': cleaned,
                'aspects_found': len(aspects),
                'aspect_sentiments': [
                    {
                        'aspect': aspect.aspect_match.text,
                        'category': aspect.aspect_match.category,
                        'sentiment': aspect.sentiment,
                        'confidence': aspect.confidence,
                        'start': aspect.aspect_match.start,
                        'end': aspect.aspect_match.end
                    }
                    for aspect in sentiment_result.aspects
                ]
            })
        return results
    
    def process_corpus(self, comments: list[str]) -> list[AspectSentimentResult]:
        """
        Process a list of comments and return structured AspectSentimentResult objects.
        
        Performs aspect matching and sentiment analysis on each comment, returning
        results as structured dataclass objects for programmatic use.
        
        Args:
            comments (list[str]): List of text comments to analyze
            
        Returns:
            list[AspectSentimentResult]: List of structured sentiment analysis results
        """
        results = []
        for comment in comments:
            cleaned = clean_input(comment)
            aspects, doc = match_aspect_phrases(cleaned, self.config)
            sentiment_result = self.sentiment_analyzer.analyze_text(cleaned, aspects, doc)
            results.append(sentiment_result)
        return results