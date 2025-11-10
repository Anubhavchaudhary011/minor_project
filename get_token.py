import requests

CLIENT_ID = "j56k86jHKRBnMyEi6ZO43g"
CLIENT_SECRET = "_Bj_-md71r1o7LY42t8McZFCfAp4wQ"
REDIRECT_URI = "https://localhost:8080"

AUTH_CODE = "PASTE_YOUR_CODE_HERE"

response = requests.post(
    "https://www.reddit.com/api/v1/access_token",
    auth=(CLIENT_ID, CLIENT_SECRET),
    data={
        "grant_type": "authorization_code",
        "code": AUTH_CODE,
        "redirect_uri": REDIRECT_URI
    },
    headers={"User-Agent": "MentalHealthApp/1.0"}
)

print(response.json())
