import re

def clean_text(t: str) -> str:
    if not isinstance(t, str):
        t = str(t)
    t = t.lower()
    t = re.sub(r'[^a-z\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t
