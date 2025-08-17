import random
import requests
from json import dump
from time import sleep, time
from urllib.parse import urlencode
from auth import token


class spotify_requests:
    SPOTIFY_API = "https://api.spotify.com/v1"

    def __init__(self, APP):
        self.stats = {
            "api_requests": 0,
            "limits_reached": 0,
            "first_request_time": time(),
            "limit_deltas": []
        }
        self.token = token(APP)

    def get(self, endpoint: str, PARAMS={}) -> dict:
        HEADERS = {"Authorization": self.token.get_token()}

        r = requests.get(f"{self.SPOTIFY_API}{endpoint}",
                            headers=HEADERS,
                            params=PARAMS,
                            timeout=10)

        while r.status_code == 429:
            self.stats["limits_reached"] += 1

            if self.stats["limit_deltas"] == []:
                self.stats["limit_deltas"].append(time())
            else:
                previous_error = self.stats["limit_deltas"][-1]
                self.stats["limit_deltas"].append(time() - previous_error)

            retry_after = r.headers["Retry-After"]
            sleep(retry_after)
            self.get(endpoint, PARAMS=PARAMS)

        self.stats["api_requests"] += 1
        r.raise_for_status()

        if "application/json" in r.headers.get("Content-Type", ""):
            return r.json()

        return {}

    def post(self, endpoint: str, DATA={}) -> dict:
        HEADERS = {"Authorization": self.token.get_token()}

        r = requests.post(f"{self.SPOTIFY_API}{endpoint}",
                            headers=HEADERS,
                            data=DATA,
                            timeout=10)

        while r.status_code == 429:
            self.stats["limits_reached"] += 1

            if self.stats["limit_deltas"] == []:
                self.stats["limit_deltas"].append(time())
            else:
                self.stats["limit_deltas"].append(time() - self.stats["limit_deltas"])

            retry_after = r.headers["Retry-After"]
            sleep(retry_after)

        self.stats["api_requests"] += 1
        r.raise_for_status()


        if "application/json" in r.headers.get("Content-Type", ""):
            return r.json()

        return {}
