import argparse
import joblib
from preprocess import clean_text
from sentiment import vader_sentiment

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', required=True, help='Path to model.pkl')
    parser.add_argument('--text', required=True, help='Text to analyze')
    args = parser.parse_args()

    # Load model
    model = joblib.load(args.model_path)

    # Clean text
    text_cleaned = clean_text(args.text)

    # Predict
    pred = model.predict([text_cleaned])[0]

    # Confidence
    score = float(model.predict_proba([text_cleaned])[0].max())

    # VADER sentiment
    sent = vader_sentiment(args.text)

    print("Input text:", args.text)
    print("Cleaned text:", text_cleaned)
    print("Predicted label:", pred)
    print("Confidence:", score)
    print("VADER sentiment:", sent)

if __name__ == "__main__":
    main()
