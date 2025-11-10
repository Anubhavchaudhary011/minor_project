import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("REDDIT_API_KEY")

def fetch_reddit_posts(subreddit: str):
    try:
        url = f"https://oauth.reddit.com/r/{subreddit}/hot"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "User-Agent": "MinorProjectPythonApp/1.0 (personal use by Anubhav Choudhary)"
        }

        r = requests.get(url, headers=headers)
        data = r.json()

        posts = []
        # extract post titles
        for post in data.get("data", {}).get("children", []):
            title = post["data"].get("title")
            if title:
                posts.append(title)

        return posts if posts else ["No posts found"]

    except Exception:
        return ["Error fetching Reddit posts"]
