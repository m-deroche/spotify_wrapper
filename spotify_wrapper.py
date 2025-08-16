#! /bin/python3

import argparse
import configparser
from spotify_requests import spotify_requests


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
    #api.save_liked()
    api.random_queue()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c",
                        "--conf-file",
                        type=str,
                        default="app.ini",
                        dest="APP_FILE",
                        help="Application configuration filepath")
    args = parser.parse_args()
    main(args.APP_FILE)
