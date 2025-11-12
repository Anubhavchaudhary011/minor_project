from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

_nltk_ready = False
_analyzer = None

def _ensure():
    global _nltk_ready, _analyzer
    if not _nltk_ready:
        nltk.download('vader_lexicon', quiet=True)
        _analyzer = SentimentIntensityAnalyzer()
        _nltk_ready = True

def vader_sentiment(text: str):
    _ensure()
    return _analyzer.polarity_scores(text or "")
