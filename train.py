# train.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
import joblib
import re
from pathlib import Path

DATA_PATH = Path("data/mental_disorders_reddit.csv")

def clean_text(s: str) -> str:
    s = str(s).lower()
    s = re.sub(r'[^a-z\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"CSV not found at {DATA_PATH.resolve()}")

    df = pd.read_csv(DATA_PATH)
    df["text"] = df["title"].fillna("") + " " + df["selftext"].fillna("")
    df["clean_text"] = df["text"].apply(clean_text)

    X = df["clean_text"]
    y = df["subreddit"]  # using subreddit as label

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=5000, stop_words="english")),
        ("clf", RandomForestClassifier(n_estimators=200, random_state=42))
    ])

    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    print(f"✅ Model trained. Test accuracy: {score:.2f}")

    joblib.dump(model, "model.pkl")
    print("✅ Model saved as model.pkl")

if __name__ == "__main__":
    main()
