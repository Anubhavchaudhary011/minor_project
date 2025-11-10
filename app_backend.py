from flask import Flask, request, jsonify
from predict import run_prediction
import praw
import os

app = Flask(__name__)

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

MODEL_PATH = "models/distilroberta-mental-health"


@app.get("/subreddit/<name>")
def get_subreddit_posts(name):
    posts = []
    subreddit = reddit.subreddit(name)

    for post in subreddit.hot(limit=10):
        posts.append({
            "id": post.id,
            "title": post.title,
            "text": post.selftext or ""
        })

    return jsonify(posts)


@app.post("/predict")
def predict_post():
    data = request.json
    text = data.get("text")

    result = run_prediction(MODEL_PATH, text)
    return jsonify(result)


app.run(debug=True)
