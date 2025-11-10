import requests

ACCESS_TOKEN = (
    "eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpzS3dsMnlsV0VtMjVmcXhwTU40cWY4MXE2OWFFdWFyMnpL"
    "MUdhVGxjdWNZIiwidHlwIjoiSldUIn0.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNzYyODY0MzQzLjM0OTE2OCwi"
    "aWF0IjoxNzYyNzc3OTQzLjM0OTE2OCwianRpIjoiMnEwdDBmM1RIaEN1SndqWS1wTXRNbWF6Z1laTlFBIiwi"
    "Y2lkIjoiajU2azg2akhLUkJuTXlFaTZaTzQzZyIsImxpZCI6InQyX3ZrNjR5NndtIiwiYWlkIjoidDJfdms2"
    "NHk2d20iLCJhdCI6MSwibGNhIjoxNjczNzg2MjM5MDAwLCJzY3AiOiJlSnlLVmlwS1RVeFIwbEhLVEVuTks4"
    "a3NxVlRTVWNySUxDN0pMNnBVaWdVRUFBRF9fNUJ0Q2ZVIiwiZmxvIjo4fQ.nQIk6auzsLoiql1wBjj0LCeto"
    "CdD3QC4NLMSALjBOUytHOA75VvuloqTxUaSEHNjhFKzlcKv1MZ8Q3dwKgZPmeA42f0CnSsRHu_RsCJKmJua-"
    "rjZOlUCy37rE-yfgUcDcQJe_Zg4-aln8VSjeEtLbNmP1TYwlq555_5FAodguzmGfl4_fjE69Gej1oQO2kJFM"
    "5DmMaln3JkYrMqLmxdqcMCWCVTNIfhHwNT_Uz8AvzjPRY3B5YDmq99Ykna_CP8ao7ZoH3kdJLy4SUiG_Avg7"
    "bhomsilzCJDi_sFYuOf3rXlg5ckMIUCBa4sUem-1nat_KrCUhLJCTRH45pej4PS5Q"
)

USER_AGENT = "MinorProjectPythonApp/1.0"


def fetch_reddit_posts(subreddit, limit=10):
    url = f"https://oauth.reddit.com/r/{subreddit}/hot?limit={limit}"

    headers = {
        "Authorization": f"bearer {ACCESS_TOKEN}",
        "User-Agent": USER_AGENT
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {
            "error": "Failed to fetch. Token may have expired.",
            "details": response.text
        }

    posts = []
    data = response.json()

    for item in data["data"]["children"]:
        post = item["data"]
        posts.append({
            "id": post["id"],
            "title": post["title"],
            "text": post.get("selftext", "")
        })

    return posts
