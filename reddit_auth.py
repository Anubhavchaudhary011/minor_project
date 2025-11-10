import os
import requests
import webbrowser
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
SECRET = os.getenv("REDDIT_SECRET")
REDIRECT_URI = os.getenv("REDDIT_REDIRECT_URI")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")
SCOPES = os.getenv("REDDIT_SCOPES")

AUTH_URL = "https://www.reddit.com/api/v1/authorize"
TOKEN_URL = "https://www.reddit.com/api/v1/access_token"


# -------------------------------------------------
# STEP 1: GET AUTHORIZATION URL
# -------------------------------------------------
def get_authorize_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "state": "random123",
        "redirect_uri": REDIRECT_URI,
        "duration": "temporary",
        "scope": SCOPES
    }
    return f"{AUTH_URL}?{urlencode(params)}"


# -------------------------------------------------
# STEP 2: EXCHANGE AUTH CODE FOR ACCESS TOKEN
# -------------------------------------------------
def get_access_token(auth_code):
    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET)

    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }

    headers = {"User-Agent": USER_AGENT}

    response = requests.post(TOKEN_URL, auth=auth, data=data, headers=headers)
    return response.json()


# -------------------------------------------------
# STEP 3: FETCH SUBREDDIT POSTS
# -------------------------------------------------
def fetch_subreddit_posts(access_token, subreddit="depression"):
    url = f"https://oauth.reddit.com/r/{subreddit}/hot"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": USER_AGENT
    }

    response = requests.get(url, headers=headers)
    return response.json()


# -------------------------------------------------
# MAIN WORKFLOW
# -------------------------------------------------
if __name__ == "__main__":
    # Step A: Ask user to authenticate
    auth_url = get_authorize_url()
    print("\nLOGIN URL (open this):")
    print(auth_url)

    webbrowser.open(auth_url)

    # Step B: User pastes code from redirect URL
    auth_code = input("\nPaste the 'code' value from the URL here: ")

    # Step C: Exchange for token
    token_data = get_access_token(auth_code)
    print("\nAccess Token Response:")
    print(token_data)

    access_token = token_data["access_token"]

    # Step D: Fetch posts
    print("\nFetching subreddit posts...")
    posts = fetch_subreddit_posts(access_token, subreddit="depression")

    print("\nPosts:\n", posts)
