import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.model_selection import train_test_split
import re

# Load dataset
print("Loading dataset...")
df = pd.read_csv(r"C:\Users\DELL\Downloads\mental_health_ai\archive\mental_disorders_reddit.csv")

# Combine title + selftext
df["text"] = df["title"].fillna("") + " " + df["selftext"].fillna("")

# Clean text function (same as train.py)
def clean_text(s: str) -> str:
    s = str(s).lower()
    s = re.sub(r'[^a-z\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

df["clean_text"] = df["text"].apply(clean_text)

# Features & target
X = df["clean_text"]
y = df["subreddit"]  # subreddit = label

# Split data (same split as training)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Load trained model
print("Loading trained model...")
model = joblib.load("model.pkl")

# Make predictions on test set
print("Making predictions...")
y_pred = model.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"\n{'='*60}")
print(f"Model Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"{'='*60}\n")

# Generate classification report
print("Classification Report:")
print(classification_report(y_test, y_pred))

# Generate confusion matrix
print("\nGenerating confusion matrix...")
cm = confusion_matrix(y_test, y_pred)

# Get class labels
classes = model.classes_

# Plot confusion matrix
plt.figure(figsize=(12, 10))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=classes, yticklabels=classes,
            cbar_kws={'label': 'Count'})
plt.title('Confusion Matrix - Mental Health Classification', fontsize=16, pad=20)
plt.xlabel('Predicted Label', fontsize=12)
plt.ylabel('True Label', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()

# Save the plot
plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
print("✓ Confusion matrix saved as 'confusion_matrix.png'")

# Show the plot
plt.show()

# Print per-class accuracy
print("\nPer-Class Accuracy:")
print("="*60)
for i, class_name in enumerate(classes):
    class_accuracy = cm[i, i] / cm[i, :].sum() if cm[i, :].sum() > 0 else 0
    print(f"{class_name:20s}: {class_accuracy:.4f} ({class_accuracy*100:.2f}%)")
print("="*60)

# Print confusion pairs (most confused classes)
print("\nMost Confused Class Pairs (Top 10):")
print("="*60)
confused_pairs = []
for i in range(len(classes)):
    for j in range(len(classes)):
        if i != j and cm[i, j] > 0:
            confused_pairs.append((classes[i], classes[j], cm[i, j]))

confused_pairs.sort(key=lambda x: x[2], reverse=True)
for true_class, pred_class, count in confused_pairs[:10]:
    print(f"{true_class:20s} → {pred_class:20s}: {count} times")
print("="*60)