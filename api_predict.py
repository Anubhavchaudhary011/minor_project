from flask import Flask, request, jsonify
import joblib
from preprocess import clean_text
from sentiment import vader_sentiment

app = Flask(__name__)
model = joblib.load("model.pkl")

@app.route("/")
def home():
    return "✅ Mental Health NLP API Running"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text")

    if not text:
        return jsonify({"error": "no text provided"}), 400

    clean = clean_text(text)
    pred = model.predict([clean])[0]
    proba = float(model.predict_proba([clean])[0].max())
    sentiment = vader_sentiment(text)

    return jsonify({
        "text": text,
        "predicted_label": pred,
        "confidence": proba,
        "vader_sentiment": sentiment
    })

if __name__ == "__main__":
    app.run(debug=True)
