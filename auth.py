import random
import requests
import string
from base64 import b64encode
from flask import Flask, request
from time import time
from urllib.parse import urlencode
import threading
import time as time_module


class token:
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    AUTH_URL = "https://accounts.spotify.com/authorize"

    def __init__(self, APP: dict):
        self.end_date = 0
        self.CODE = None
        self.refresh_token = None
        self.CLIENT_ID = APP["CLIENT_ID"]
        self.CLIENT_SECRET = APP["CLIENT_SECRET"]
        self.SCOPE = APP["SCOPE"]
        self.HOST = APP["HOST"]
        self.PORT = APP["PORT"]
        self.STATE = ''.join(random.choices(
            string.ascii_uppercase + string.digits,
            k=16))
        self.CALLBACK = f"http://{self.HOST}:{self.PORT}/callback"
        
        # Use threading instead of multiprocessing to avoid pickling issues
        self.auth_completed = threading.Event()
        self.app = Flask(__name__)
        self.app.route("/callback")(self.call_back)
        
        # Start the Flask server in a separate thread
        self.server_thread = threading.Thread(target=self.app.run, 
                                             kwargs={
                                                 "host": self.HOST,
                                                 "port": self.PORT,
                                                 "debug": False
                                             })
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Wait a moment for server to start
        time_module.sleep(0.5)
        
        self.auth_user()
        self.get_new_token()

    def auth_user(self):
        PARAMS = {
            "response_type": "code",
            "client_id": self.CLIENT_ID,
            "scope": self.SCOPE,
            "redirect_uri": self.CALLBACK,
            "state": self.STATE
        }
        
        # Use a simple web browser approach with a timeout
        import webbrowser
        import time as time_lib
        
        print("Please authenticate with Spotify in your browser...")
        print(f"Opening authentication URL: {token.AUTH_URL}?{urlencode(PARAMS)}")
        webbrowser.open(f"{token.AUTH_URL}?{urlencode(PARAMS)}")
        
        # Wait up to 2 minutes for the user to complete authentication
        timeout = 120
        start_time = time_lib.time()
        while not self.auth_completed.is_set() and (time_lib.time() - start_time) < timeout:
            time_lib.sleep(1)
            
        if not self.auth_completed.is_set():
            raise Exception("Authentication timed out. Please try again.")

    def call_back(self):
        STATE = request.args['state']

        if STATE != self.STATE:
            raise Exception("Cross Site Forgery attempt")

        self.CODE = request.args['code']
        self.STATE = STATE
        self.auth_completed.set()
        return {"message": "Authentication complete. You can close this window."}, 200

    def encoded_client(self):
        client = f"{self.CLIENT_ID}:{self.CLIENT_SECRET}".encode("ascii")
        return b64encode(client).decode("ascii")

    def get_new_token(self):
        if not self.CODE:
            # Wait for authentication to complete (should already be done)
            self.auth_completed.wait()

        HEADERS = {
            "Authorization": f"Basic {self.encoded_client()}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        DATA = {
            "grant_type": "authorization_code",
            "code": self.CODE,
            "redirect_uri": self.CALLBACK
        }

        if self.refresh_token:
            del DATA["code"]
            del DATA["redirect_uri"]
            DATA["grant_type"] = "refresh_token"
            DATA["refresh_token"] = self.refresh_token

        r = requests.post(token.TOKEN_URL,
                          data=DATA,
                          headers=HEADERS,
                          timeout=10)
        r.raise_for_status()
        r = r.json()
        self.end_date = time() + r["expires_in"]
        self.token = r
        self.refresh_token = r.get("refresh_token", None)

    def update_if_expired(self):
        if time() > self.end_date:
            print("Fetching a new token")
            self.get_new_token()

    def get_token(self) -> str:
        self.update_if_expired()
        return f"{self.token['token_type']} {self.token['access_token']}"
