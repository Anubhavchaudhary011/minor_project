import joblib
import re
from sentiment import vader_sentiment


# -----------------------------------
# CLEAN TEXT
# -----------------------------------
def clean_text(t):
    t = str(t).lower()
    t = re.sub(r"http\S+|www\S+", " ", t)
    t = re.sub(r"[^a-z\s]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


# -----------------------------------
# FACTUAL STATEMENT DETECTION
# -----------------------------------
def is_factual_statement(text, vader_scores):
    text_lower = text.lower().strip()
    wc = len(text_lower.split())

    neu = float(vader_scores.get("neu", 0))
    pos = float(vader_scores.get("pos", 0))
    neg = float(vader_scores.get("neg", 0))
    compound = float(vader_scores.get("compound", 0))

    # Emotional keyword patterns → NOT factual
    emotional_keywords = [
        r'\b(feel|feeling|felt)\b',
        r'\b(sad|happy|angry|worried|anxious|depressed|stressed)\b',
        r'\b(hate|love|fear|hope)\b',
        r'\b(struggling|suffering|pain|hurt)\b',
        r'\b(suicide|kill myself|self harm)\b',
        r'\b(therapy|medication|diagnosis)\b',
        r'\b(lonely|isolated|worthless|hopeless)\b'
    ]

    for p in emotional_keywords:
        if re.search(p, text_lower):
            return False

    # Very short → treat as factual
    if wc < 3:
        return True

    # Mostly neutral → factual
    if neu >= 0.85 and abs(compound) <= 0.15:
        return True

    # Very low polarity → factual
    if pos < 0.15 and neg < 0.15:
        return True

    # Hard factual patterns
    factual_patterns = [
        r'\b(today|yesterday|tomorrow)\b',
        r'\b(monday|tuesday|wednesday|thursday|friday)\b',
        r'\b(january|february)\b',
        r'\b(is|are|was|were)\s+\w+\b',
    ]

    for p in factual_patterns:
        if re.search(p, text_lower):
            return True

    return neu >= 0.75


# -----------------------------------
# MAIN PREDICTION FUNCTION
# CALLED AUTOMATICALLY FROM app.py
# -----------------------------------
def run_prediction(model_path, text):
    cleaned = clean_text(text)
    sentiment_scores = vader_sentiment(text)

    # 1. Factual detection
    if is_factual_statement(text, sentiment_scores):
        return {
            "is_factual": True,
            "label": "fact",
            "confidence": None,
            "sentiment": sentiment_scores
        }

    # 2. Load the ML model
    model = joblib.load(model_path)

    pred = model.predict([cleaned])[0]

    # Confidence score (safe)
    try:
        proba = model.predict_proba([cleaned])[0]
        confidence = float(max(proba))
    except:
        confidence = None

    return {
        "is_factual": False,
        "label": pred,
        "confidence": confidence,
        "sentiment": sentiment_scores
    }
