#! /bin/python3

import argparse
import configparser
from spotify_wrapper import spotify_wrapper
from time import time

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
    api = spotify_wrapper(APP)
    api.reverse_liked()
    #api.random_queue()
    api_requests = api.stats["api_requests"]
    limits_reached = api.stats["limits_reached"]
    first_request_time = api.stats["first_request_time"]
    limit_deltas = api.stats["limit_deltas"]
    requests_per_second = api_requests / (time() - first_request_time)

    if limits_reached != 0:
        error_deltas = sum(limit_deltas) / limits_reached
    else:
        error_deltas = -1

    print(f"Number of API calls: {api_requests}")
    print(f"Number of time API rate limit was reached: {limits_reached}")
    print(f"Average API call per second: {requests_per_second}")
    print(f"Average API call per 30 seconds: {requests_per_second * 30}")
    print(f"Average time between rate limit erros: {error_deltas}")

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
