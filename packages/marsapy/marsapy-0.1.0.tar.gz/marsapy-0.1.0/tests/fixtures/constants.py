from marsa.config import AspectConfig, AspectData
from marsa.matching import AspectMatch

EXAMPLE_CORPUS = ["I love the camera but hate the battery life"]

ASPECT_CONFIG = AspectConfig(
    aspects={
        'camera': AspectData(
            phrases=["camera", "photo", "picture", "photography"],
            category="hardware"
        ),
        'battery': AspectData(
            phrases=["battery", "power", "charge", "charging", "juice", "drain"],
            category="hardware"
        ),
        'screen': AspectData(
            phrases=["screen", "display", "resolution", "brightness", "monitor"],
            category="interface"
        )
    }
)

FIRST_ASPECT_MATCH = AspectMatch(
    text="camera",
    aspect="camera",
    start=11,
    end=17,
    token_start=3,
    token_end=4,
    category="hardware"
)

SECOND_ASPECT_MATCH = AspectMatch(
    text="battery",
    aspect="battery",
    start=31,
    end=38,
    token_start=7,
    token_end=8,
    category="hardware"

)

SAMPLE_RESULTS = [
    {
        'cleaned_text': 'great camera but battery life is terrible',
        'aspect_sentiments': [
            {
                'aspect': 'camera',
                'category': 'hardware',
                'sentiment': 'positive',
                'confidence': 0.85
            },
            {
                'aspect': 'battery',
                'category': 'hardware',
                'sentiment': 'negative',
                'confidence': 0.92
            }
        ]
    },
    {
        'cleaned_text': 'beautiful screen display',
        'aspect_sentiments': [
            {
                'aspect': 'screen',
                'category': 'interface',
                'sentiment': 'positive',
                'confidence': 0.95
            }
        ]
    }
]