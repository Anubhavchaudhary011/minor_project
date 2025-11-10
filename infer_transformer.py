import json
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline

MODEL_DIR = Path("models/roberta-base-mental-health")

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)

pipe = TextClassificationPipeline(
    model=model,
    tokenizer=tokenizer,
    device=0  # GPU if available
)

def predict(text):
    out = pipe(text, truncation=True, max_length=256, return_all_scores=True)[0]
    out = sorted(out, key=lambda x: x["score"], reverse=True)
    return out[:3]

if __name__ == "__main__":
    print(predict("I feel extremely anxious and can't sleep."))
