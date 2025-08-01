import requests

from   json import dump
from   auth import token


class spotify_requests:
    SPOTIFY_API = "https://api.spotify.com/v1"

    def __init__(self, APP):
        self.token = token(APP)

    def get(self, endpoint: str, PARAMS={}) -> dict:
        HEADERS = { "Authorization": self.token.get_token() }

        try:
            r = requests.get(f"{self.SPOTIFY_API}{endpoint}",
                             headers=HEADERS,
                             params=PARAMS,
                             timeout=10)
            r.raise_for_status()
        except Exception as e:
            print(f"Failed to GET {endpoint}\n" \
                  f"params={PARAMS}\n"          \
                  f"headers={HEADERS}\n"        \
                  f"Exception: {e}")
            raise

        return r.json()

    def post(self, endpoint: str, DATA={}) -> dict:
        HEADERS = { "Authorization": self.token.get_token() }

        try:
            r = requests.post(f"{self.SPOTIFY_API}/{endpoint}",
                              headers=HEADERS,
                              data=DATA,
                              timeout=10)
            r.raise_for_status()
        except Exception as e:
            r = r.json()

            print(f"Failed to POST {endpoint}\n" \
                  f"data={DATA}\n"               \
                  f"headers={HEADERS}\n"         \
                  f"Exception: {e}")
            raise


        return r.json()

    def get_username(self):
        return self.get("/me")["display_name"]

    def get_liked(self):
        def get_page(limit, offset):
            r = self.get("/me/tracks", {
                "market": "FR",
                "limit": limit,
                "offset": offset
            })
            return r

        username = self.get_username()
        json = []
        step = 50
        offset = 0
        r = get_page(1, offset)
        tracks_number = r["total"]
        print(tracks_number)

        while tracks_number >= step:
            r = get_page(step, offset)

            for item in r["items"]:
                json.append({
                    "id": item["track"]["id"],
                    "track_name": item["track"]["name"],
                    "artists": [ artist["name"] for artist in item["track"]["artists"] ]
                })

            offset += step
            tracks_number -= step
            print(f"Fetched liked tracks: {offset}")

        r = get_page(step, offset)

        for item in r["items"]:
            json.append({
                "id": item["track"]["id"],
                "track_name": item["track"]["name"],
                "artists": [ artist["name"] for artist in item["track"]["artists"] ]
            })

        print(f"Fetched likes tracks: {offset + len(r['items'])}")
        print(f"Liked tracks: {len(json)}")


        with open(f"{username}_liked_tracks.json", "w", encoding="utf8") as f:
            dump(json, f, indent=4, ensure_ascii=False)


