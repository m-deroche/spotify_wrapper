import requests
from time import sleep, time
from auth import Token


class SpotifyRequests:
    SPOTIFY_API = "https://api.spotify.com/v1"

    def __init__(self, app: dict):
        self.stats = {
            "api_requests": 0,
            "limits_reached": 0,
            "first_request_time": None,
            "last_limit_time": None,
            "limit_deltas": []
        }
        self.token = Token(app)

    def record_limit(self):
        now = time()
        self.stats["limits_reached"] += 1

        if self.stats["last_limit_time"] is not None:
            self.stats["limit_deltas"].append(now - self.stats["last_limit_time"])

        self.stats["last_limit_time"] = now

    def request(self, method: str, endpoint: str, params=None, data=None) -> dict:
        if self.stats["first_request_time"] is None:
            self.stats["first_request_time"] = time()

        while True:
            # The token can expire during a long rate limit wait
            headers = {"Authorization": self.token.get_token()}
            r = requests.request(method,
                                 f"{self.SPOTIFY_API}{endpoint}",
                                 headers=headers,
                                 params=params,
                                 json=data,
                                 timeout=10)
            self.stats["api_requests"] += 1

            if r.status_code != 429:
                break

            self.record_limit()

            # Handle Retry-After header (could be string or int)
            try:
                retry_after = int(r.headers.get("Retry-After", 1))
            except (ValueError, TypeError):
                retry_after = 1

            print(f"Rate limit hit. Retrying after {retry_after} seconds")
            sleep(retry_after)

        r.raise_for_status()

        if "application/json" in r.headers.get("Content-Type", ""):
            return r.json()

        return {}

    def get(self, endpoint: str, params=None) -> dict:
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint: str, data=None, params=None) -> dict:
        return self.request("POST", endpoint, params=params, data=data)
