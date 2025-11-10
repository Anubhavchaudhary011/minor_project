import argparse
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from preprocess import clean_text
from evaluate_utils import load_from_csv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True)
    ap.add_argument('--n_topics', type=int, default=5)
    ap.add_argument('--max_features', type=int, default=5000)
    args = ap.parse_args()

    df = load_from_csv(args.data)
    texts = [clean_text(t) for t in df["text"]]

    vect = CountVectorizer(max_features=args.max_features, stop_words="english")
    X = vect.fit_transform(texts)

    lda = LatentDirichletAllocation(n_components=args.n_topics, random_state=42)
    lda.fit(X)

    terms = vect.get_feature_names_out()
    for i, comp in enumerate(lda.components_):
        words = [terms[j] for j in comp.argsort()[-10:]]
        print(f"Topic {i}: {', '.join(words)}")


if __name__ == "__main__":
    main()
