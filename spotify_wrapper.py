import random
import requests
from json import dump
from time import sleep
from urllib.parse import urlencode
from auth import token
from spotify_requests import spotify_requests


class spotify_wrapper(spotify_requests):
    SPOTIFY_API = "https://api.spotify.com/v1"

    def __init__(self, APP):
        super().__init__(APP)

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
        json = []
        step = 50
        offset = 0
        r = get_page(1, offset)
        tracks_number = r["total"]
        total = tracks_number
        print(f"Total tracks: {tracks_number}")

        while tracks_number >= step:
            r = get_page(step, offset)

            for item in r["items"]:
                json.append({
                    "id": item["track"]["id"],
                    "uri": item["track"]["uri"],
                    "track_name": item["track"]["name"],
                    "artists": [artist["name"] for artist in item["track"]["artists"]]
                })

            offset += step
            tracks_number -= step
            print(f"Fetched tracks: {offset}/{total}", end="\r")

        r = get_page(step, offset)

        for item in r["items"]:
            json.append({
                "id": item["track"]["id"],
                "track_name": item["track"]["name"],
                "artists": [artist["name"] for artist in item["track"]["artists"]]
            })

        print(f"Fetched liked tracks: {offset + len(r['items'])}")
        return json

    def get_liked_uris(self):
        def get_page(limit, offset):
            r = self.get("/me/tracks", {
                "market": "FR",
                "limit": limit,
                "offset": offset
            })
            return r
        json = []
        step = 50
        offset = 0
        r = get_page(1, offset)
        tracks_number = r["total"]
        total = tracks_number
        print(f"Total tracks: {tracks_number}")

        while tracks_number >= step:
            r = get_page(step, offset)

            for item in r["items"]:
                json.append({
                    "uri": item["track"]["uri"]
                })

            offset += step
            tracks_number -= step
            print(f"Fetched tracks: {offset}/{total}", end="\r")

        r = get_page(step, offset)

        for item in r["items"]:
            json.append({
                "uri": item["track"]["uri"]
            })

        print(f"Fetched liked tracks: {offset + len(r['items'])}")
        return json

    def play_next(self):
        self.post("/me/player/next")

    def random_queue(self, n=25):
        # Playing Shuffle by Tshegue triggers the custom shuffle
        trigger_uri = "spotify:track:2EYde8YgCxW4yYtzdgvN7y"
        liked_tracks = self.get_liked_uris()
        tracks_number = len(liked_tracks)

        print("Waiting to add random tracks to queue")
        while True:
            try:
                r = self.get("/me/player")
            except BaseException:
                r = None

            if r and r["item"]["uri"] == trigger_uri:
                for i in range(n):
                    random_uri_idx = random.randint(0, tracks_number)
                    random_uri = {
                        "uri": liked_tracks[random_uri_idx]["uri"]
                    }
                    try:
                        self.post(f"/me/player/queue?{urlencode(random_uri)}")
                        sleep(0.3)
                    except BaseException:
                        break

                    if i == 0:
                        self.play_next()
                print(f"Added {n} random tracks to queue")
            sleep(1)
        print("Stop adding random tracks to queue")

    def save_liked(self):
        username = self.get_username()
        filename = f"{username}_liked_tracks.json"
        json = self.get_liked()
        with open(filename, "w", encoding="utf8") as f:
            dump(json, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(json)} tracks to {filename}")
