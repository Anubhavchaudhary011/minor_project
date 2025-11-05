import argparse
import joblib
import re
from preprocess import clean_text
from sentiment import vader_sentiment

def is_factual_statement(text, vader_scores):
    """
    Fact detection using sentiment neutrality, linguistic patterns, and disorder keyword exclusion
    """
    print("\n=== FACT DETECTION DEBUG ===")
    
    neu_value = float(vader_scores.get("neu", 0))
    compound = float(vader_scores.get("compound", 0))
    pos_value = float(vader_scores.get("pos", 0))
    neg_value = float(vader_scores.get("neg", 0))
    
    print(f"Neutral: {neu_value}, Compound: {compound}, Pos: {pos_value}, Neg: {neg_value}")
    
    text_lower = text.lower().strip()
    word_count = len(text_lower.split())
    print(f"Text: '{text_lower}' | Word count: {word_count}")
    
    # 1️⃣ Too short text → consider as fact
    if word_count < 3:
        print("✓ CHECK 1 PASSED: Short text (<3 words)")
        return True

    # 2️⃣ Emotional / disorder keywords → cannot be fact
    emotional_keywords = [
        r'\b(feel|feeling|felt|emotion)',
        r'\b(sad|happy|angry|scared|worried|anxious|depressed|stressed)',
        r'\b(hate|love|fear|hope|wish)',
        r'\b(can\'?t|cannot|struggling|suffering|pain|hurt)',
        r'\b(want to die|suicide|kill myself|self harm)',
        r'\b(therapy|therapist|medication|diagnosis)',
        r'\b(lonely|alone|isolated|worthless|hopeless)',
        # OCD-specific
        r'\b(checking|washing|repeating|counting|ritual|compulsion|obsession)\b'
    ]
    for pattern in emotional_keywords:
        if re.search(pattern, text_lower):
            print(f"✗ CHECK FAILED: Emotional/disorder keyword found: {pattern}")
            return False

    # 3️⃣ Strong neutrality + low compound → likely fact
    if neu_value >= 0.85 and abs(compound) <= 0.15:
        print("✓ CHECK 2 PASSED: High neutrality + low compound")
        return True

    # 4️⃣ Balanced sentiment → likely fact
    if pos_value < 0.15 and neg_value < 0.15:
        print("✓ CHECK 3 PASSED: Balanced sentiment (no strong emotion)")
        return True

    # 5️⃣ Factual patterns
    factual_indicators = [
        r'\b(today|yesterday|tomorrow|this (morning|evening|afternoon))\b',
        r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
        r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
        r'\b(is|are|was|were)\s+(a|an|the)?\s*\w+\b',
        r'\b\d+\s*(plus|minus|times|divided by|equals?)\s*\d+\b',
        r'\b(the (sky|sun|moon|earth|water|ocean|mountain|river))\b',
        r'\b(means?|refers? to|defined as|known as)\b',
    ]
    for i, pattern in enumerate(factual_indicators):
        if re.search(pattern, text_lower):
            print(f"✓ CHECK 4 PASSED: Pattern {i+1} matched: {pattern}")
            return True

    # 6️⃣ Default neutrality threshold
    if neu_value >= 0.75:
        print("✓ CHECK 6 PASSED: Neutrality >= 0.75")
        return True

    print("✗ ALL CHECKS FAILED: Not detected as factual")
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', required=True, help='Path to model.pkl')
    parser.add_argument('--text', required=True, help='Text to analyze')
    args = parser.parse_args()

    print("="*60)
    print("MENTAL HEALTH NLP - PREDICTION SCRIPT")
    print("="*60)

    # Clean text
    text_cleaned = clean_text(args.text)

    # VADER sentiment
    sent = vader_sentiment(args.text)

    print(f"\nInput text: {args.text}")
    print(f"Cleaned text: {text_cleaned}")
    print(f"VADER sentiment: {sent}")

    # Fact detection
    is_fact = is_factual_statement(args.text, sent)
    print(f"\n{'='*60}")
    print(f"IS FACTUAL: {is_fact}")
    print(f"{'='*60}")

    if is_fact:
        pred = "Fact"
        score = 1.0
        print(f"\n✓ RESULT: Detected as factual statement")
    else:
        # Load model and predict
        print("\nLoading model for classification...")
        model = joblib.load(args.model_path)
        pred = model.predict([text_cleaned])[0]
        proba = model.predict_proba([text_cleaned])[0]
        score = float(proba.max())

        # Show top 3 predictions
        classes = model.classes_
        top_3_idx = proba.argsort()[-3:][::-1]
        print("\nTop 3 predictions:")
        for idx in top_3_idx:
            print(f"  {classes[idx]}: {proba[idx]:.4f}")

    print(f"\n{'='*60}")
    print(f"FINAL PREDICTION: {pred}")
    print(f"CONFIDENCE: {score:.4f}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
