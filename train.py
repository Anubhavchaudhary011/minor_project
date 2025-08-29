import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
import joblib
import re

# Load dataset
df = pd.read_csv(r"C:\Users\DELL\Downloads\mental_health_ai\archive\mental_disorders_reddit.csv")

# Combine title + selftext
df["text"] = df["title"].fillna("") + " " + df["selftext"].fillna("")

# Clean text
def clean_text(s: str) -> str:
    s = str(s).lower()
    s = re.sub(r'[^a-z\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

df["clean_text"] = df["text"].apply(clean_text)

# Features & target
X = df["clean_text"]
y = df["subreddit"]  # subreddit = label

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build pipeline
model = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=5000, stop_words='english')),
    ('clf', RandomForestClassifier(n_estimators=200, random_state=42))
])

# Train
model.fit(X_train, y_train)

# Evaluate
score = model.score(X_test, y_test)
print(f"✅ Model trained with Random Forest. Test accuracy: {score:.2f}")

# Save model
joblib.dump(model, "model.pkl")
print("✅ Model saved as model.pkl")
