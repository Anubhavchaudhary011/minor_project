from flask import Flask, jsonify, request
import requests
from predict import run_prediction
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv("REDDIT_ACCESS_TOKEN")
USER_AGENT = os.getenv("USER_AGENT")
MODEL_PATH = "models/distilroberta-mental-health"

# ✅ GET POSTS FROM REDDIT
@app.get("/reddit/<subreddit>")
def get_posts(subreddit):
    url = f"https://oauth.reddit.com/r/{subreddit}/hot"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "User-Agent": USER_AGENT
    }

    r = requests.get(url, headers=headers).json()

    posts = []
    for c in r.get("data", {}).get("children", []):
        data = c["data"]
        posts.append({
            "id": data["id"],
            "title": data["title"],
            "text": data.get("selftext", "")
        })

    return jsonify(posts)


# ✅ RUN PREDICTION
@app.post("/analyze")
def analyze():
    text = request.json.get("text")

    result = run_prediction(MODEL_PATH, text)

    return jsonify(result)


app.run(debug=True)
