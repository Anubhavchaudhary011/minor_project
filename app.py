import os
import random
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from predict import run_prediction
from doctor_locator import get_doctors_for_disorder

load_dotenv()

REDDIT_ACCESS_TOKEN = os.getenv("REDDIT_ACCESS_TOKEN")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "MinorProjectPythonApp/1.0")

MODEL_PATH = os.getenv("MODEL_PATH", "models/distilroberta-mental-health")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)


@app.route("/")
def root():
    return send_from_directory(STATIC_DIR, "index.html")


# ----------------------------------------------------
# FETCH POSTS FROM A SINGLE SUBREDDIT
# ----------------------------------------------------
@app.route("/api/posts/<subreddit>")
def get_posts(subreddit):
    token = REDDIT_ACCESS_TOKEN
    if not token:
        return jsonify({"error": "NO ACCESS TOKEN IN .env"}), 500

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": REDDIT_USER_AGENT
    }

    url = f"https://oauth.reddit.com/r/{subreddit}/hot?limit=10"
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return jsonify({
            "error": f"Reddit returned HTTP {r.status_code}",
            "details": r.text
        }), 500

    data = r.json()

    posts = [
        {
            "subreddit": subreddit,
            "id": item["data"].get("id"),
            "title": item["data"].get("title"),
            "text": item["data"].get("selftext") or ""
        }
        for item in data.get("data", {}).get("children", [])
    ]

    return jsonify(posts)


# ----------------------------------------------------
# RANDOM POSTS FROM r/all (GLOBAL FEED)
# ----------------------------------------------------
@app.route("/api/random-all")
def random_all():
    token = REDDIT_ACCESS_TOKEN
    if not token:
        return jsonify({"error": "NO ACCESS TOKEN IN .env"}), 500

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": REDDIT_USER_AGENT
    }

    url = "https://oauth.reddit.com/r/all/hot?limit=100"
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return jsonify({"error": f"Reddit returned HTTP {r.status_code}"}), 500

    data = r.json()

    posts = []
    for child in data.get("data", {}).get("children", []):
        d = child["data"]
        posts.append({
            "subreddit": d.get("subreddit"),
            "id": d.get("id"),
            "title": d.get("title"),
            "text": d.get("selftext") or ""
        })

    random.shuffle(posts)
    posts = posts[:15]

    return jsonify(posts)


# ----------------------------------------------------
# MIXED DEFAULT MENTAL-HEALTH SUBREDDITS (AUTO-MIX)
# ----------------------------------------------------
@app.route("/api/mixed-default")
def mixed_default():
    token = REDDIT_ACCESS_TOKEN
    if not token:
        return jsonify({"error": "NO ACCESS TOKEN IN .env"}), 500

    # ✅ Auto-mix from these subs
    default_subs = [
        "Anxiety",
        "depression",
        "bipolar",
        "mentalillness",
        "BPD",
        "schizophrenia",
        "mentalhealth"
    ]

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": REDDIT_USER_AGENT
    }

    all_posts = []

    for sub in default_subs:
        url = f"https://oauth.reddit.com/r/{sub}/hot?limit=10"
        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            continue

        data = r.json()

        for child in data.get("data", {}).get("children", []):
            d = child["data"]
            all_posts.append({
                "subreddit": sub,
                "id": d.get("id"),
                "title": d.get("title"),
                "text": d.get("selftext") or ""
            })

    random.shuffle(all_posts)

    return jsonify(all_posts[:20])


# ----------------------------------------------------
# NLP ANALYSIS
# ----------------------------------------------------
@app.post("/api/analyze")
def analyze():
    text = (request.get_json() or {}).get("text", "")
    result = run_prediction(MODEL_PATH, text)
    return jsonify(result)


# ----------------------------------------------------
# DOCTOR LOOKUP
# ----------------------------------------------------
@app.get("/api/doctors")
def doctors_api():
    label = request.args.get("label", "").lower().strip()
    city = request.args.get("city", "Delhi")

    if label == "fact" or not label:
        return jsonify([])

    valid_labels = {
        "anxiety", "depression", "schizophrenia",
        "bipolar", "mentalillness", "bpd"
    }

    if label not in valid_labels:
        return jsonify([])

    doctors = get_doctors_for_disorder(label, city)
    return jsonify(doctors)


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
