#! /bin/python3

import configparser
from   sys          import argv
from   request      import spotify_requests


def main(APP_FILE: str):
    config = configparser.ConfigParser()
    config.read(APP_FILE)
    APP = {
        "CLIENT_ID": config["CLIENT"]["CLIENT_ID"],
        "CLIENT_SECRET": config["CLIENT"]["CLIENT_SECRET"],
        "SCOPE": config["CLIENT"]["SCOPE"],
        "HOST": config["SERVER"]["HOST"],
        "PORT": config["SERVER"]["PORT"]
    }
    api = spotify_requests(APP)
    api.get_liked()

if __name__ == "__main__":
    APP_FILE = argv[1]
    main(APP_FILE)


