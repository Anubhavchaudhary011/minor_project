import os
import re
import joblib
import torch
from pathlib import Path
from typing import Dict, Any

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from preprocess import clean_text
from sentiment import vader_sentiment


def _is_hf_model_dir(path: str) -> bool:
    p = Path(path)
    return p.is_dir() and (p / "config.json").exists()


def _predict_hf(model_dir: str, text: str):
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.eval()
    inputs = tokenizer([text], padding=True, truncation=True, max_length=256, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=1)[0].tolist()
    pred_id = int(torch.argmax(logits))
    id2label = model.config.id2label or {i: str(i) for i in range(len(probs))}
    return {"label": id2label.get(pred_id), "confidence": float(max(probs)), "probs": probs}


def _predict_sklearn(path: str, text: str):
    model = joblib.load(path)
    pred = model.predict([text])[0]
    confidence = None
    try:
        confidence = float(max(model.predict_proba([text])[0]))
    except:
        pass
    return {"label": str(pred), "confidence": confidence}


def is_factual_statement(text: str, vader_scores: Dict[str, float]) -> bool:
    text_lower = text.lower().strip()
    wc = len(text_lower.split())

    # emotion signals -> NOT factual
    emotional_words = [
        r"\bfeel\b", r"\bworried\b", r"\banxious\b", r"\bdepressed\b",
        r"\bstressed\b", r"\bsuicide\b", r"\bhurt\b", r"\bpain\b"
    ]
    for p in emotional_words:
        if re.search(p, text_lower):
            return False

    # short → factual
    if wc <= 2:
        return True

    neu = vader_scores.get("neu", 0)
    comp = abs(vader_scores.get("compound", 0))

    # neutral tone → factual
    if neu >= 0.90 and comp <= 0.10:
        return True

    return False


def run_prediction(model_path: str, raw_text: str):
    cleaned = clean_text(raw_text)
    sentiment_scores = vader_sentiment(raw_text)

    if is_factual_statement(raw_text, sentiment_scores):
        return {
            "is_factual": True,
            "prediction": {"label": "fact", "confidence": None},
            "sentiment": sentiment_scores
        }

    if _is_hf_model_dir(model_path):
        pred = _predict_hf(model_path, cleaned)
    else:
        pred = _predict_sklearn(model_path, cleaned)

    return {"is_factual": False, "prediction": pred, "sentiment": sentiment_scores}
