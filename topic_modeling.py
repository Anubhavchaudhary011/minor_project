import os
import json
import re
import pandas as pd
import numpy as np
import torch

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    DataCollatorWithPadding,
    TrainingArguments,
    Trainer,
)

import evaluate


# ============================================================
# CONFIG
# ============================================================
DATA_PATH = Path("mental_disorders_reddit.csv")
OUT_DIR = Path("models/distilroberta-mental-health")
MODEL_NAME = "distilroberta-base"   # ✅ Best for CPU


# ============================================================
# CLEAN TEXT
# ============================================================
def clean_text(t):
    t = str(t).lower()
    t = re.sub(r"http\S+|www\S+", " ", t)
    t = re.sub(r"[^a-z\s]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


# ============================================================
# LOAD DATA
# ============================================================
print("Loading CSV...")
df = pd.read_csv(DATA_PATH)
print(f"Loaded {len(df)} rows.")

print(" Cleaning text...")
df["title"] = df["title"].fillna("")
df["selftext"] = df["selftext"].fillna("")
df["text"] = (df["title"] + " " + df["selftext"]).apply(clean_text)

print("Normalizing labels...")
y = df["subreddit"].astype(str)
y = y.replace({
    "SuicideWatch": "suicidal",
    "suicidewatch": "suicidal",
    "SuicideHelp": "suicidal",
})

df = pd.DataFrame({"text": df["text"], "label": y})
df = df[df.text.str.len() > 0].reset_index(drop=True)


# ✅ SAMPLE 50,000 rows (best speed + accuracy)
print("Sampling 150k rows for training...")
df = df.sample(150000, random_state=42)


labels = sorted(df["label"].unique())
label2id = {l: i for i, l in enumerate(labels)}
id2label = {i: l for l, i in label2id.items()}
df["label_id"] = df["label"].map(label2id)

print(" Labels:", labels)


# ============================================================
# SPLIT
# ============================================================
print(" Splitting dataset...")
train_df, val_df = train_test_split(
    df,
    test_size=0.1,
    random_state=42,
    stratify=df["label_id"],
)

ds_train = Dataset.from_pandas(train_df[["text", "label_id"]].rename(columns={"label_id": "labels"}))
ds_val = Dataset.from_pandas(val_df[["text", "label_id"]].rename(columns={"label_id": "labels"}))


# ============================================================
# TOKENIZER
# ============================================================
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

print("Tokenizing dataset...")
def tok(batch):
    return tokenizer(batch["text"], truncation=True, max_length=256)

ds_train = ds_train.map(tok, batched=True, remove_columns=["text"])
ds_val = ds_val.map(tok, batched=True, remove_columns=["text"])
collator = DataCollatorWithPadding(tokenizer)


# ============================================================
# MODEL
# ============================================================
print(" Loading model...")
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(labels),
    id2label=id2label,
    label2id=label2id,
)


# ============================================================
# CLASS WEIGHTS
# ============================================================
print("Computing class weights...")
cw = compute_class_weight("balanced", classes=np.arange(len(labels)), y=df["label_id"].values)
cw = torch.tensor(cw).float()


class WeightedTrainer(Trainer):
    def __init__(self, class_weights=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels = inputs["labels"]
        outputs = model(**{k: v for k, v in inputs.items() if k != "labels"})
        logits = outputs.logits
        loss_fn = torch.nn.CrossEntropyLoss(weight=self.class_weights.to(logits.device))
        loss = loss_fn(logits, labels)
        return (loss, outputs) if return_outputs else loss


# ============================================================
# METRICS
# ============================================================
print(" Loading metrics...")
metric_acc = evaluate.load("accuracy")
metric_f1 = evaluate.load("f1")

def compute_metrics(eval_pred):
    logits, y = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": metric_acc.compute(predictions=preds, references=y)["accuracy"],
        "f1_macro": metric_f1.compute(predictions=preds, references=y, average="macro")["f1"],
    }


# ============================================================
# TRAINING SETTINGS
# ============================================================
args = TrainingArguments(
    output_dir=str(OUT_DIR),
    learning_rate=3e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    num_train_epochs=3,     # ✅ ~2.5 hours → 90% accuracy possible
    warmup_ratio=0.05,
    weight_decay=0.01,
    fp16=False,              # CPU only
    logging_steps=200,
    eval_strategy="epoch",
    save_strategy="epoch",
    report_to="none",
)


# ============================================================
# TRAIN
# ============================================================
trainer = WeightedTrainer(
    model=model,
    args=args,
    train_dataset=ds_train,
    eval_dataset=ds_val,
    tokenizer=tokenizer,
    data_collator=collator,
    compute_metrics=compute_metrics,
    class_weights=cw,
)

print(" Starting training...")
trainer.train()

trainer.save_model(OUT_DIR)
tokenizer.save_pretrained(OUT_DIR)

print(" Training complete.")
