import argparse, joblib, pandas as pd
from sklearn.metrics import classification_report
from .preprocess import clean_text

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model_path', required=True)
    ap.add_argument('--data', required=True, help='CSV with text,label columns')
    args = ap.parse_args()

    pipe = joblib.load(args.model_path)
    df = pd.read_csv(args.data)
    X = df['text'].astype(str).tolist()
    y = df['label'].astype(int).tolist()
    preds = pipe.predict(X)
    print(classification_report(y, preds, digits=3))

if __name__ == '__main__':
    main()
