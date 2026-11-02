#!/usr/bin/env python3

import argparse
import configparser
import sys
from spotify_wrapper import SpotifyClient
from time import time

def main(app_file: str):
    config = configparser.ConfigParser()

    if not config.read(app_file):
        sys.exit(f"Configuration file not found: {app_file}")

    app = {
        "CLIENT_ID": config["CLIENT"]["CLIENT_ID"],
        "CLIENT_SECRET": config["CLIENT"]["CLIENT_SECRET"],
        "SCOPE": config["CLIENT"]["SCOPE"],
        "MARKET": config["CLIENT"].get("MARKET", "FR"),
        "HOST": config["SERVER"]["HOST"],
        "PORT": config["SERVER"]["PORT"]
    }
    api = SpotifyClient(app)

    # Execute only the get_liked and save_liked functionality
    print("Fetching liked tracks...")
    api.save_liked()

    # Display API statistics
    api_requests = api.stats["api_requests"]
    limits_reached = api.stats["limits_reached"]
    first_request_time = api.stats["first_request_time"]
    limit_deltas = api.stats["limit_deltas"]
    requests_per_second = api_requests / (time() - first_request_time)

    if limit_deltas:
        error_deltas = sum(limit_deltas) / len(limit_deltas)
    else:
        error_deltas = -1

    print(f"Number of API calls: {api_requests}")
    print(f"Number of times API rate limit was reached: {limits_reached}")
    print(f"Average API call per second: {requests_per_second}")
    print(f"Average API call per 30 seconds: {requests_per_second * 30}")
    print(f"Average time between rate limit errors: {error_deltas}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c",
                        "--conf-file",
                        type=str,
                        default="app.ini",
                        dest="app_file",
                        help="Application configuration filepath")
    args = parser.parse_args()
    main(args.app_file)
