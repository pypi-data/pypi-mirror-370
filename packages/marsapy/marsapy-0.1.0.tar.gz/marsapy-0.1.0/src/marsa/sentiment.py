import torch
from marsa.matching import AspectMatch
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dataclasses import dataclass
from transformers import logging
from transformers import pipeline
from spacy.tokens import Doc

@dataclass 
class AspectSentiment:
    """
    Result of sentiment analysis for a single detected aspect.
    
    Contains the aspect match information along with the predicted sentiment,
    confidence score, and contextual information used for the prediction.
    
    Attributes:
        aspect_match (AspectMatch): The original aspect match with position data
        sentiment (str): Predicted sentiment label ('positive', 'negative', or 'neutral')
        confidence (float | None): Confidence score for the sentiment prediction (0.0-1.0)
        context_used (str | None): The contextual text used for sentiment analysis
    """
    aspect_match: AspectMatch
    sentiment: str
    confidence: float | None = None
    context_used: str | None = None
    
@dataclass
class AspectSentimentResult:
    """
    Complete sentiment analysis result for a single text input.
    
    Contains the original text and all aspect-sentiment pairs detected
    and analyzed within that text.
    
    Attributes:
        text (str): The original input text that was analyzed
        aspects (list[AspectSentiment]): List of all detected aspects with their sentiments
    """
    text: str
    aspects: list[AspectSentiment]
    
class AspectSentimentAnalyzer:
    """
    Ensemble sentiment analyzer combining VADER and BERT models.
    
    Performs aspect-based sentiment analysis using both lexicon-based (VADER)
    and transformer-based (BERT) approaches, with weighted combination and
    contextual analysis around detected aspects.
    
    The analyzer extracts context windows around aspects and uses ensemble
    prediction to provide robust sentiment classification with confidence scoring.
    
    Attributes:
        threshold (float): Sentiment score threshold for neutral classification
        context_window (int): Number of tokens before/after aspects for context
        vader_analyzer (SentimentIntensityAnalyzer): VADER sentiment analyzer instance
        bert_model: Pre-trained BERT sentiment classification pipeline
        doc (Doc | None): Current spaCy document being processed
    """
    def __init__(self, threshold: float = 0.05, context_window: int = 3) -> None:
        """
        Initialize the aspect sentiment analyzer with VADER and BERT models.
        
        Sets up both VADER (lexicon-based) and BERT (transformer-based) sentiment
        analyzers for ensemble sentiment prediction.
        
        Args:
            threshold (float, optional): Sentiment score threshold for neutral classification. 
                                    Defaults to 0.05.
            context_window (int, optional): Number of tokens before/after aspects for context. 
                                        Defaults to 3.
        """
        self.threshold = threshold
        self.context_window = context_window
        self.vader_analyzer = SentimentIntensityAnalyzer()
        logging.set_verbosity_error() # only log errors
        self.bert_model = pipeline(
            "sentiment-analysis", # alias for text-classication
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            device=0 if torch.cuda.is_available() else -1,
            top_k=True
        )
        self.doc = None
        
    def analyze_text(self, text: str, aspect_matches: list[AspectMatch], doc: Doc) -> AspectSentimentResult:
        """
        Analyze sentiment for each detected aspect in the text.
        
        Uses ensemble approach combining VADER and BERT sentiment models with
        contextual analysis around each detected aspect.
        
        Args:
            text (str): The original input text
            aspect_matches (list[AspectMatch]): List of detected aspect matches
            doc (Doc): spaCy Doc object for token-level context extraction
            
        Returns:
            AspectSentimentResult: Structured result containing aspect sentiments
        """
        self.doc = doc  
        aspect_sentiments = []
        
        for aspect in aspect_matches:
            context = self._extract_context_window(aspect)
            
            vader_scores = self.vader_analyzer.polarity_scores(context)
            vader_compound = vader_scores['compound']
            bert_results = self.bert_model(context)[0]
            bert_probs = self._extract_bert_probabilities(bert_results)
            
            sentiment, confidence = self._weighted_sentiment(bert_probs, vader_compound)
            
            aspect_sentiments.append(AspectSentiment(
                aspect_match=aspect,
                sentiment=sentiment,
                confidence=confidence,
                context_used=context
            ))
        
        return AspectSentimentResult(text=text, aspects=aspect_sentiments)
    
    def _extract_context_window(self, aspect_match: AspectMatch) -> str:
        """
        Extract contextual text around an aspect for sentiment analysis.
        
        Extracts a window of tokens before and after the detected aspect to provide
        sufficient context for accurate sentiment classification.
        
        Args:
            aspect_match (AspectMatch): The matched aspect with token positions
            
        Returns:
            str: Contextual text surrounding the aspect
        """
        start_token = max(0, aspect_match.token_start - self.context_window)
        end_token = min(len(self.doc), aspect_match.token_end + self.context_window)
        return self.doc[start_token:end_token].text
    
    def _extract_bert_probabilities(self, bert_results: dict) -> list[float]:   
        """
        Extract and normalize BERT sentiment probabilities.
        
        Converts BERT model output to standardized probability format for
        negative, neutral, and positive sentiments.
        
        Args:
            bert_results (dict): Raw BERT model output with labels and scores
            
        Returns:
            list[float]: Probabilities for [negative, neutral, positive] sentiments
        """     
        probs = [0.0, 0.0, 0.0]  # [negative, neutral, positive]
        
        for result in bert_results:
            label = result['label'].lower()
            score = result['score']
            
            if 'negative' in label or label == 'label_0':
                probs[0] = score
            elif 'neutral' in label or label == 'label_1':
                probs[1] = score
            elif 'positive' in label or label == 'label_2':
                probs[2] = score
            
        return probs
    
    def _weighted_sentiment(self, bert_probs: list[float], vader_score: float) -> tuple[str, float]:
        """
        Combine BERT and VADER predictions using weighted ensemble approach.
        
        Calculates final sentiment by weighting BERT and VADER predictions based on
        their confidence levels and agreement, with confidence adjustment for consensus.
        
        Args:
            bert_probs (list[float]): BERT probabilities [negative, neutral, positive]
            vader_score (float): VADER compound sentiment score (-1 to 1)
            
        Returns:
            tuple[str, float]: Final sentiment label and confidence score
        """
        bert_sentiment_score = (
            -1 * bert_probs[0] +   # negative
             0 * bert_probs[1] +   # neutral  
             1 * bert_probs[2]     # positive
        )
        bert_confidence = max(bert_probs)
        vader_confidence = abs(vader_score)
        total_confidence = bert_confidence + vader_confidence
        
        if total_confidence > 0:
            bert_weight = bert_confidence / total_confidence
            vader_weight = vader_confidence / total_confidence
        else:
            bert_weight = vader_weight = 0.5
        
        combined_score = (bert_weight * bert_sentiment_score) + (vader_weight * vader_score)
        
        agreement_factor = self._calculate_agreement(bert_sentiment_score, vader_score)
        final_confidence = agreement_factor * max(bert_confidence, vader_confidence)
        
        if combined_score > self.threshold:
            return "positive", final_confidence
        elif combined_score < -self.threshold:
            return "negative", final_confidence
        else:
            return "neutral", final_confidence
        
    def _calculate_agreement(self, bert_score: float, vader_score: float) -> float:
        """
        Calculate agreement factor between BERT and VADER predictions.
        
        Determines how well BERT and VADER agree on sentiment polarity to adjust
        final confidence score based on model consensus.
        
        Args:
            bert_score (float): BERT sentiment score (-1 to 1)
            vader_score (float): VADER sentiment score (-1 to 1)
            
        Returns:
            float: Agreement factor (1.0 for agreement, 0.5 for disagreement)
        """
        if (bert_score > 0 and vader_score > 0) or (bert_score < 0 and vader_score < 0):
            return 1.0  # agreement
        elif abs(bert_score) < self.threshold and abs(vader_score) < self.threshold:
            return 1.0  # both neutral
        else:
            return 0.5  # disagreement
