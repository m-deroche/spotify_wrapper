import random
import requests
from json import dump
from time import sleep
from urllib.parse import urlencode
from auth import token


class spotify_requests:
    SPOTIFY_API = "https://api.spotify.com/v1"

    def __init__(self, APP):
        self.token = token(APP)

    def get(self, endpoint: str, PARAMS={}) -> dict:
        HEADERS = {"Authorization": self.token.get_token()}

        try:
            r = requests.get(f"{self.SPOTIFY_API}{endpoint}",
                             headers=HEADERS,
                             params=PARAMS,
                             timeout=10)
            r.raise_for_status()
        except Exception as e:
            print(f"Failed to GET {endpoint}\n"
                  f"params={PARAMS}\n"
                  f"headers={HEADERS}\n"
                  f"Exception: {e}")
            raise Exception(f"GET status error: {e}")

        if "json" in r.headers.get("Content-Type", ""):
            return r.json()

    def post(self, endpoint: str, DATA={}) -> dict:
        HEADERS = {"Authorization": self.token.get_token()}

        try:
            r = requests.post(f"{self.SPOTIFY_API}{endpoint}",
                              headers=HEADERS,
                              data=DATA,
                              timeout=10)
            r.raise_for_status()
        except Exception as e:
            r = r.json()

            print(f"Failed to POST {endpoint}\n"
                  f"data={DATA}\n"
                  f"headers={HEADERS}\n"
                  f"Exception: {e}")
            raise Exception(f"POST status error {e}")

        if "json" in r.headers.get("Content-Type", ""):
            return r.json()
