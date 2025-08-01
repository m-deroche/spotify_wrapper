from base64 import b64encode
from flask import Flask, redirect, request, session
import os
import pickle
import random
import requests
import string
from time import time, sleep
from multiprocessing import Process
from urllib.parse import urlencode
from selenium import webdriver


class token:
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    AUTH_URL = "https://accounts.spotify.com/authorize"

    def __init__(self, APP: dict):
        self.end_date = 0
        self.CODE = None
        self.CLIENT_ID = APP["CLIENT_ID"]
        self.CLIENT_SECRET = APP["CLIENT_SECRET"]
        self.SCOPE = APP["SCOPE"]
        self.HOST = APP["HOST"]
        self.PORT = APP["PORT"]
        self.STATE = ''.join(random.choices(
            string.ascii_uppercase + string.digits,
            k=16))
        self.CALLBACK = f"http://{self.HOST}:{self.PORT}/callback"
        options = webdriver.ChromeOptions()
        options.add_argument(r'--user-data-dir=./.UserData')
        self.driver = webdriver.Chrome(options=options)
        self.app = Flask(__name__)
        self.app.route("/callback")(self.call_back)
        self.server = Process(target=self.app.run,
                              kwargs={
                                  'host': self.HOST,
                                  'port': self.PORT
                              })
        self.server.start()
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
        self.driver.get(f"{token.AUTH_URL}?{urlencode(PARAMS)}")

    def call_back(self):
        try:
            self.CODE = request.args['code']
            STATE = request.args['state']
            if STATE != self.STATE:
                raise Exception("Cross Site Forgery attempt")
            self.STATE = STATE
        except Exception as e:
            print(f"Failed to authenticate user\n"
                  f"Exception: {e}")
            raise Exception("Failed to authenticate user")
        with open(".CODE", "w") as f:
            f.write(self.CODE)

        return {"message": "user authenticated"}, 204

    def encoded_client(self):
        client = f"{self.CLIENT_ID}:{self.CLIENT_SECRET}"
        print(client)

        return base64.b64encode(client.encode("ascii")).decode("ascii")

    def get_new_token(self):
        while not self.CODE:
            try:
                with open(".CODE", "r", errors="ignore") as f:
                    self.CODE = f.read()
            except BaseException:
                pass
            sleep(1)

        self.server.terminate()
        self.server.join()
        self.driver.quit()
        os.remove(".CODE")

        DATA = {
            "grant_type": "authorization_code",
            "code": self.CODE,
            "redirect_uri": self.CALLBACK,
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET
        }

        try:
            r = requests.post(token.TOKEN_URL,
                              data=DATA,
                              timeout=10)
            r.raise_for_status()
        except Exception as e:
            print(f"Failed to retrieve token\n"
                  f"data={DATA}\n"
                  f"Exception: {e}")
            raise Exception("Failed to get new token")

        r = r.json()
        self.end_date = time() + r["expires_in"]
        self.token = r

    def update_if_expired(self):
        if time() > self.end_date:
            print("Fetching a new token")
            self.get_new_token()

    def get_token(self) -> str:
        self.update_if_expired()

        return f"{self.token['token_type']} {self.token['access_token']}"
