import re
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def clean_text(t):
    t = str(t).lower()
    t = re.sub(r"http\S+|www\S+", " ", t)
    t = re.sub(r"[^a-z\s]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()

MODEL_DIR = "models/distilroberta-mental-health"

print("✅ Loading model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()

print("✅ Loading data...")
df = pd.read_csv("mental_disorders_reddit.csv")

df["title"] = df["title"].fillna("")
df["selftext"] = df["selftext"].fillna("")
df["text"] = (df["title"] + " " + df["selftext"]).apply(clean_text)

# label normalization
y = df["subreddit"].astype(str)
y = y.replace({
    "SuicideWatch": "suicidal",
    "suicidewatch": "suicidal",
    "SuicideHelp": "suicidal",
})
df["label"] = y
df = df[df.text.str.len() > 0].reset_index()

# ✅ use same 150k sampling as training
df = df.sample(150000, random_state=42)

labels = sorted(df["label"].unique())
label2id = {l: i for i, l in enumerate(labels)}
df["label_id"] = df["label"].map(label2id)

print("✅ Creating validation set...")
_, val_df = train_test_split(
    df, test_size=0.1, random_state=42, stratify=df["label_id"]
)

# ✅ SPEED-UP: evaluate on first **2000 samples only**
val_df = val_df.sample(2000, random_state=42)

texts = val_df["text"].tolist()
true_labels = val_df["label_id"].tolist()

print("✅ Evaluating (fast mode)...")

batch_size = 32
preds = []

for i in range(0, len(texts), batch_size):
    batch = texts[i:i + batch_size]

    inputs = tokenizer(
        batch,
        padding=True,
        truncation=True,
        max_length=256,
        return_tensors="pt"
    )

    with torch.no_grad():
        logits = model(**inputs).logits

    preds.extend(torch.argmax(logits, dim=1).tolist())

acc = accuracy_score(true_labels, preds)

print(f"\n✅ FAST ACCURACY (2000 samples): {acc:.4f}\n")
print("✅ Classification Report:")
print(classification_report(true_labels, preds, target_names=labels))
