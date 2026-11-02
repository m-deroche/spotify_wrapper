import json
import os
import secrets
import threading
import webbrowser
from time import time
from urllib.parse import urlencode

import requests
from flask import Flask, request
from werkzeug.serving import make_server


class Token:
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    AUTH_URL = "https://accounts.spotify.com/authorize"
    CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".spotify_token")
    AUTH_TIMEOUT = 120
    EXPIRY_MARGIN = 60

    def __init__(self, app: dict):
        self.client_id = app["CLIENT_ID"]
        self.client_secret = app["CLIENT_SECRET"]
        self.scope = app["SCOPE"]
        self.host = app["HOST"]
        self.port = int(app["PORT"])
        self.callback = f"http://{self.host}:{self.port}/callback"
        self.auth_completed = threading.Event()
        self.state = None
        self.code = None
        self.auth_error = None
        self.token = None
        self.end_date = 0
        self.refresh_token = self.load_refresh_token()

        if self.refresh_token:
            self.refresh()
        else:
            self.login()

    def load_refresh_token(self):
        try:
            with open(self.CACHE_FILE, encoding="utf8") as f:
                cache = json.load(f)
        except (OSError, ValueError):
            return None

        # A token granted for other scopes can't be used, a new login is needed
        if cache.get("scope") != self.scope:
            return None

        return cache.get("refresh_token")

    def save_refresh_token(self):
        fd = os.open(self.CACHE_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf8") as f:
            json.dump({"scope": self.scope, "refresh_token": self.refresh_token}, f)

    def login(self):
        self.state = secrets.token_urlsafe(16)
        self.code = None
        self.auth_error = None
        self.auth_completed.clear()

        app = Flask(__name__)
        app.route("/callback")(self.call_back)
        server = make_server(self.host, self.port, app)
        threading.Thread(target=server.serve_forever, daemon=True).start()

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "scope": self.scope,
            "redirect_uri": self.callback,
            "state": self.state
        }
        url = f"{self.AUTH_URL}?{urlencode(params)}"

        try:
            print("Please authenticate with Spotify in your browser...")
            print(f"Opening authentication URL: {url}")
            webbrowser.open(url)

            if not self.auth_completed.wait(self.AUTH_TIMEOUT):
                raise TimeoutError("Authentication timed out. Please try again.")
        finally:
            server.shutdown()

        if self.auth_error:
            raise RuntimeError(f"Authentication failed: {self.auth_error}")

        self.store_token(self.post_token({
            "grant_type": "authorization_code",
            "code": self.code,
            "redirect_uri": self.callback
        }))

    def call_back(self):
        if request.args.get("state") != self.state:
            return {"message": "Invalid state."}, 400

        self.code = request.args.get("code")

        if not self.code:
            self.auth_error = request.args.get("error", "no code received")
            self.auth_completed.set()
            return {"message": f"Authentication failed: {self.auth_error}"}, 400

        self.auth_completed.set()
        return {"message": "Authentication complete. You can close this window."}, 200

    def post_token(self, data: dict):
        return requests.post(self.TOKEN_URL,
                             data=data,
                             auth=(self.client_id, self.client_secret),
                             timeout=10)

    def store_token(self, r):
        r.raise_for_status()
        self.token = r.json()
        self.end_date = time() + self.token["expires_in"]
        # Spotify only sends a refresh token when it replaces the previous one
        self.refresh_token = self.token.get("refresh_token", self.refresh_token)
        self.save_refresh_token()

    def refresh(self):
        r = self.post_token({
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        })

        if r.status_code == 400 and "invalid_grant" in r.text:
            print("Saved session is no longer valid, logging in again")
            self.refresh_token = None
            self.login()
            return

        self.store_token(r)

    def update_if_expired(self):
        if time() > self.end_date - self.EXPIRY_MARGIN:
            print("Fetching a new token")
            self.refresh()

    def get_token(self) -> str:
        self.update_if_expired()
        return f"{self.token['token_type']} {self.token['access_token']}"
