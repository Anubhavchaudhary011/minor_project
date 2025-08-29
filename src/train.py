import argparse, joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

from .data_ingest import load_from_csv
from .preprocess import clean_text

ALGOS = {
    'svm': LinearSVC,
    'rf': RandomForestClassifier,
    'mlp': MLPClassifier,
}

def build_pipeline(algo: str):
    if algo == 'svm':
        clf = LinearSVC()
    elif algo == 'rf':
        clf = RandomForestClassifier(n_estimators=300, random_state=42)
    elif algo == 'mlp':
        clf = MLPClassifier(hidden_layer_sizes=(128,), max_iter=200, random_state=42)
    else:
        raise ValueError(f'Unknown algo {algo}')
    pipe = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=20000, ngram_range=(1,2), stop_words='english', preprocessor=clean_text)),
        ('clf', clf),
    ])
    return pipe

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True, help='CSV with text,label columns')
    ap.add_argument('--model_path', required=True, help='Where to save the trained model')
    ap.add_argument('--algo', choices=list(ALGOS.keys()), default='svm')
    args = ap.parse_args()

    df = load_from_csv(args.data)
    if 'label' not in df.columns:
        raise ValueError("Training requires a 'label' column (0/1)")
    X = df['text'].astype(str).tolist()
    y = df['label'].astype(int).tolist()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    pipe = build_pipeline(args.algo)
    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)
    print(classification_report(y_test, preds, digits=3))

    joblib.dump(pipe, args.model_path)
    print('Saved model to', args.model_path)

if __name__ == '__main__':
    main()
