import praw
import os
import pandas as pd
import re

# -----------------------------------------------------
# ✅ SAME CLEANING USED IN YOUR TRAINING PIPELINE
# -----------------------------------------------------
def clean_text(t):
    t = str(t).lower()
    t = re.sub(r"http\S+|www\S+", " ", t)
    t = re.sub(r"[^a-z\s]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


# -----------------------------------------------------
# ✅ REDDIT API CLIENT
# -----------------------------------------------------
def get_reddit_client():
    return praw.Reddit(
        client_id="j56k86jHKRBnMyEi6ZO43g",               # ✅ Your client_id
        client_secret="_Bj_-md71r1o7LY42t8McZFCfAp4wQ",   # ✅ Your secret
        user_agent="script:mental_health_app:v1.0 (by u/OkMonk5420)"
    )


# -----------------------------------------------------
# ✅ FETCH POSTS FROM ANY SUBREDDIT
# -----------------------------------------------------
def fetch_subreddit_posts(subreddit_name, limit=50):
    reddit = get_reddit_client()
    subreddit = reddit.subreddit(subreddit_name)

    posts_data = []

    for post in subreddit.hot(limit=limit):
        title = clean_text(post.title)
        body = clean_text(post.selftext)

        combined = f"{title} {body}".strip()

        if len(combined) < 5:
            continue

        posts_data.append({
            "id": post.id,
            "title": title,
            "body": body,
            "text": combined,
            "url": f"https://reddit.com{post.permalink}"
        })

    df = pd.DataFrame(posts_data)
    return df


# -----------------------------------------------------
# ✅ TEST
# -----------------------------------------------------
if __name__ == "__main__":
    print("Fetching posts from r/depression ...")
    df = fetch_subreddit_posts("depression", limit=10)
    print(df.head())
    df.to_csv("sample_depression_posts.csv", index=False)
    print("Saved sample_depression_posts.csv")
