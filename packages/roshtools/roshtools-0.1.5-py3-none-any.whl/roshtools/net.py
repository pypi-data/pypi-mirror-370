import requests

def get_json(url: str):
    """Fetch JSON from a URL (simple wrapper)."""
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()
