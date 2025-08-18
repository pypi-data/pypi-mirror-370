import json
import pandas as pd
from pathlib import Path

from pathlib import Path
import json
import pandas as pd

def export_for_review(results: list[dict], out_file: str) -> None:
    """
    Export sentiment analysis results to JSON or CSV format.
    
    Exports the analysis results to either JSON format (preserving full structure)
    or CSV format (flattened with one row per aspect-sentiment pair).
    
    Args:
        results (list[dict]): List of analysis results containing aspects and sentiments
        out_file (str): Output file path with .json or .csv extension
        
    Raises:
        ValueError: If file extension isn't .json or .csv
        OSError: If file cannot be written to the specified path
    """
    path = Path(out_file).resolve() 
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if path.suffix.lower() == '.json':
        with open(path, 'w') as f:
            json.dump(results, f, indent=2)
    elif path.suffix.lower() == '.csv':
        flattened = []
        for result in results:
            for aspect_sent in result['aspect_sentiments']:
                flattened.append({
                    'text': result['cleaned_text'],
                    'aspect': aspect_sent['aspect'],
                    'category': aspect_sent['category'],
                    'prelabeled_sentiment': aspect_sent['sentiment'],
                    'confidence': aspect_sent['confidence']
                })
        pd.DataFrame(flattened, columns=['text', 'aspect', 'category', 'prelabeled_sentiment', 'confidence']).to_csv(path, index=False)
    else:
        raise ValueError(f'Unsupported file extension: {path.suffix}; expected .json or .csv')