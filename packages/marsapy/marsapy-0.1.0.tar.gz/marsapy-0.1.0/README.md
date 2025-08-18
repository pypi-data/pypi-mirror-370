# MARSA
MARSA is a lightweight tool designed to streamline aspect-based sentiment analysis (ABSA) by automating the extraction and pre-labeling of aspect-sentiment pairs from review-style text. MARSA combines rule-based aspect extraction with sentiment analysis to accelerate the long process of manually labeling text data. It is especially useful for analyzing social media content such as Reddit comments and Twitter posts and mining product reviews from platforms like Amazon and Yelp.

The tool simplifies ABSA by identifying multiple aspects within a single sentence and automatically assigning initial sentiment scores using VADER. Users can define custom aspect terms and categories to tailor the analysis to their needs. MARSA also supports exporting results in JSON or CSV formats for easy manual review or use in training models. It can be accessed via command line or Python API, offering convenient ways to interact with it.

## Pipeline Architecture
MARSA uses a two-stage pipeline:
1. **Aspect Extraction**: Rule-based matching using configurable phrase dictionaries
2. **Sentiment Analysis**: VADER sentiment analyzer processes text within the specified context window around each detected aspect

## Installation
### Install with pip
```bash
pip install marsapy
```
### Install with `uv`
```bash
uv add marsapy
```
### For GPU support (optional):
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu129
uv add torch --index pytorch-cu129 --index-url https://download.pytorch.org/whl/cu129
```

## Quick Start
### Command Line
```bash
# Analyze a single text string
marsa analyze-text "Great camera but poor battery" --config config.yaml --output results.json --context-window 3
# Analyze a file of comments (short notation)
marsa analyze-file comments.txt -c config.yaml -o results.json -w 3
```
### Python API
```python
from marsa import AspectSentimentPipeline
pipeline = AspectSentimentPipeline(config_file="config.yaml", context_window=2)
results = pipeline.process_corpus(["I love the camera but don't like the battery life"])
```

## Context Window
The `--context-window` (shorthand notation: `-c`) parameter controls how many words around each aspect phrase are analyzed for sentiment. A larger context window (e.g., 5) captures more nuanced sentiment but may include irrelevant text, while a smaller window (e.g., 1-2) focuses on immediate sentiment but might miss important context.

**Example:**

- **Text**: "I love the sleek *design* but hate the poor *performance*"
- Aspect **"design"** with context window 1: Analyzes "sleek design but"
- Aspect **"design"** with context window 3: Analyzes "love the sleek design but hate the"
- Aspect **"performance"** with context window 1: Analyzes "poor performance"
- Aspect **"performance"** with context window 3: Analyzes "hate the poor performance"

## Configuration
The easiest way to configure MARSA is by using a YAML file. Create a `config.yaml` fine and define your aspects:
```yaml
aspects:
    camera:
        phrases: ["camera", "photo", "picture", "pics", "photography", "image", "snap"]
        category: "hardware"
    
    battery:
        phrases: ["battery", "power", "charge", "charging", "juice", "drain", "life"]
        category: "hardware"
    
    screen:
        phrases: ["screen", "display", "resolution", "brightness", "monitor", "lcd", "oled"]
        category: "interface"
```
You can define aspects by creating a `config.json` file as well:
```json
{
  "aspects": {
        "camera": {
            "phrases": ["camera", "photo", "picture", "pics", "photography", "image", "snap"],
            "category": "hardware"
        },
        "battery": {
            "phrases": ["battery", "power", "charge", "charging", "juice", "drain", "life"],
            "category": "hardware"
        },
        "screen": {
            "phrases": ["screen", "display", "resolution", "brightness", "monitor", "lcd", "oled"],
            "category": "interface"
        }
    }
}
```

## Sentiment Analysis
MARSA uses an ensemble approach combining VADER and BERT models for sentiment classification:
- **VADER**: Lexicon-based analyzer that handles social media text, slang, and emoticons well
- **BERT**: Twitter-RoBERTa transformer model for contextual sentiment understanding
- **Ensemble Method**: Weighted combination based on model confidence and agreement
- **Output**: Each aspect gets a sentiment label (positive/negative/neutral) and confidence score (0.0-1.0)
- **Threshold**: Scores within ±0.05 are classified as neutral
- **Confidence Interpretation**: Higher confidence scores indicate more reliable predictions; low confidence scores suggest the result may need manual review

## Output Format
MARSA outputs structured data showing detected aspects with their sentiment classifications:

```json
[
  {
    "cleaned_text": "great camera but battery life is terrible",
    "aspect_sentiments": [
      {
        "aspect": "camera",
        "category": "hardware", 
        "sentiment": "positive",
        "confidence": 0.85
      },
      {
        "aspect": "battery",
        "category": "hardware",
        "sentiment": "negative", 
        "confidence": 0.92
      }
    ]
  },
  {
    "cleaned_text": "beautiful screen display",
    "aspect_sentiments": [
      {
        "aspect": "screen",
        "category": "interface",
        "sentiment": "positive",
        "confidence": 0.95
      }
    ]
  }
]
```
