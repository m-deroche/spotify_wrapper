import random
import re
from json import dump
from time import sleep
from spotify_requests import SpotifyRequests


class SpotifyClient(SpotifyRequests):
    PAGE_SIZE = 50
    PLAYLIST_ADD_SIZE = 100
    POLL_SECONDS = 2

    def __init__(self, app: dict):
        super().__init__(app)
        self.market = app.get("MARKET", "FR")

    def paginate(self, endpoint: str, params=None):
        offset = 0

        while True:
            page = self.get(endpoint, {
                **(params or {}),
                "limit": self.PAGE_SIZE,
                "offset": offset
            })
            yield from page["items"]
            offset += len(page["items"])
            print(f"Fetched: {offset}/{page['total']}", end="\r")

            if not page["next"]:
                print()
                return

    def get_username(self):
        me = self.get("/me")
        return me["display_name"] or me["id"]

    def get_liked(self):
        liked = []

        for item in self.paginate("/me/tracks", {"market": self.market}):
            track = item["track"]
            if track:
                liked.append({
                    "id": track["id"],
                    "uri": track["uri"],
                    "track_name": track["name"],
                    "artists": [artist["name"] for artist in track["artists"]]
                })

        print(f"Fetched liked tracks: {len(liked)}")
        return liked

    def get_liked_uris(self):
        return [track["uri"] for track in self.get_liked()]

    def reverse_liked(self):
        uris = self.get_liked_uris()[::-1]
        playlist_id = self.post("/me/playlists", {"name": "reverse"})["id"]

        for i in range(0, len(uris), self.PLAYLIST_ADD_SIZE):
            self.post(f"/playlists/{playlist_id}/items",
                      {"uris": uris[i:i + self.PLAYLIST_ADD_SIZE]})
            print(f"Added tracks: {min(i + self.PLAYLIST_ADD_SIZE, len(uris))}/{len(uris)}",
                  end="\r")

        print(f"\nReversed {len(uris)} liked tracks to reverse playlist")
        return uris

    def play_next(self):
        self.post("/me/player/next")

    def random_queue(self, n=25):
        # Playing Shuffle by Tshegue triggers the custom shuffle
        trigger_uri = "spotify:track:2EYde8YgCxW4yYtzdgvN7y"
        liked_uris = self.get_liked_uris()

        if not liked_uris:
            print("No liked tracks to queue")
            return

        print("Waiting to add random tracks to queue")
        try:
            while True:
                # item is null during ads or when nothing is loaded
                item = self.get("/me/player").get("item") or {}

                if item.get("uri") == trigger_uri:
                    uris = random.sample(liked_uris, min(n, len(liked_uris)))

                    for i, uri in enumerate(uris):
                        self.post("/me/player/queue", params={"uri": uri})

                        if i == 0:
                            self.play_next()

                    print(f"Added {len(uris)} random tracks to queue")

                sleep(self.POLL_SECONDS)
        except KeyboardInterrupt:
            pass
        print("Stopped random tracks listener to queue")

    def save_liked(self):
        username = re.sub(r"[^\w -]", "_", self.get_username())
        filename = f"{username}_liked_tracks.json"
        liked = self.get_liked()

        with open(filename, "w", encoding="utf8") as f:
            dump(liked, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(liked)} tracks to {filename}")

    def get_user_playlists(self):
        """Get all playlists for the current user"""
        playlists = []

        for item in self.paginate("/me/playlists"):
            # Spotify renamed tracks to items in February 2026, for newer apps
            count = item.get("items") or item["tracks"]
            playlists.append({
                "id": item["id"],
                "name": item["name"],
                "tracks_count": count["total"]
            })

        print(f"Fetched playlists: {len(playlists)}")
        return playlists
