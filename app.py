from flask import Flask, request, jsonify
import joblib
from preprocess import clean_text
from sentiment import vader_sentiment

# Load trained model
model = joblib.load("model.pkl")

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ Mental Health NLP API is running!"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    text_cleaned = clean_text(text)
    pred = model.predict([text_cleaned])[0]
    score = float(model.predict_proba([text_cleaned])[0].max())
    sent = vader_sentiment(text)

    return jsonify({
        "text": text,
        "predicted_label": pred,
        "confidence": score,
        "vader_sentiment": sent
    })

if __name__ == "__main__":
    app.run(debug=True)
