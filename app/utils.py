# spotify/utils.py

import base64, time, requests
from django.conf import settings
import time

TOKEN_FILE = "spotify_token.json"

def _read_token():
    import json
    try:
        with open(TOKEN_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def _write_token(data):
    import json
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f)

def get_access_token():
    tok = _read_token()
    if not tok or tok["expires_at"] <= int(time.time()):
        # Refresh
        auth_header = base64.b64encode(f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()).decode()
        resp = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth_header}"},
            data={
                "grant_type": "refresh_token",
                "refresh_token": tok.get("refresh_token")
            }
        ).json()
        tok.update({
            "access_token": resp["access_token"],
            "expires_at": int(time.time()) + resp["expires_in"]
        })
        _write_token(tok)
    return tok["access_token"]

# def spotify_get(path, **params):
#     token = get_access_token()
#     return requests.get(
#         f"https://api.spotify.com/v1/{path}",
#         headers={"Authorization": f"Bearer {token}"},
#         params=params
#     ).json()

# def spotify_post(path, **kwargs):
#     token = get_access_token()
#     return requests.put(
#         f"https://api.spotify.com/v1/{path}",
#         headers={"Authorization": f"Bearer {token}"},
#         json=kwargs.get("json", {})
#     ).json() if kwargs.get("method","PUT") == "PUT" else requests.post(
#         f"https://api.spotify.com/v1/{path}",
#         headers={"Authorization": f"Bearer {token}"},
#         json=kwargs.get("json", {})
#     ).json()


def spotify_get(path, **params):
    token = get_access_token()
    resp = requests.get(
        f"https://api.spotify.com/v1/{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params
    )
    if resp.status_code == 204:
        return None
    resp.raise_for_status()
    return resp.json()

def spotify_post(path, method="PUT", json=None):
    token = get_access_token()
    if method.upper() == "PUT":
        resp = requests.put(
            f"https://api.spotify.com/v1/{path}",
            headers={"Authorization": f"Bearer {token}"},
            json=json or {}
        )
    else:
        resp = requests.post(
            f"https://api.spotify.com/v1/{path}",
            headers={"Authorization": f"Bearer {token}"},
            json=json or {}
        )
    if resp.status_code == 204:
        return None
    resp.raise_for_status()
    return resp.json()
