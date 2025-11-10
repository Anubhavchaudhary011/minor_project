import os
import requests
from flask import Blueprint, jsonify
from dotenv import load_dotenv

load_dotenv()

reddit_bp = Blueprint("reddit", __name__)
REDDIT_API_KEY = os.getenv("REDDIT_API_KEY")

@reddit_bp.route("/reddit/<subreddit>", methods=["GET"])
def get_reddit_posts(subreddit):
    try:
        url = f"https://oauth.reddit.com/r/{subreddit}/hot"
        headers = {
            "Authorization": f"Bearer {REDDIT_API_KEY}",
            "User-Agent": "MinorProjectPythonApp/1.0"
        }

        response = requests.get(url, headers=headers)
        return jsonify(response.json())

    except Exception:
        return jsonify({"error": "Failed to fetch Reddit posts"}), 500
