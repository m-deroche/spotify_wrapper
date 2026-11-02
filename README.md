# Simple Spotify API wrapper

This is an updated version of a Spotify API wrapper. Your desired endpoints go in the **spotify_wrapper.py** file, on top of the request handling in **spotify_requests.py**.

## Features

- Fetches all liked tracks from a user's library
- Creates a reverse-ordered playlist of liked tracks
- Adds random tracks from the user's library to the playback queue
- Saves liked tracks to JSON files for offline access
- Handles Spotify API rate limiting gracefully
- Manages authentication tokens with automatic refresh

## Requirements

- Python 3.9+
- A web browser for the Spotify login
- Flask server for handling OAuth callback

## Setup

### Creating a Virtual Environment

To avoid conflicts with system packages, it's recommended to use a virtual environment:

```bash
# Create a virtual environment
python3 -m venv spotify_env

# Activate the virtual environment
# On macOS/Linux:
source spotify_env/bin/activate
# On Windows:
spotify_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Spotify Developer Setup

1. Create a Spotify Developer App at https://developer.spotify.com/dashboard
2. Add your Client ID and Client Secret to the `app.ini` file
3. Set the redirect URI to `http://127.0.0.1:5000/callback`

## Usage

Run the application:
```bash
python main.py
```

The wrapper will:
1. Authenticate with Spotify using OAuth 2.0 in your default browser, or reuse your saved session
2. Fetch your liked tracks
3. Save them to a JSON file named after your username
4. Display API statistics

## Configuration

Edit `app.ini` to customize:
- Client credentials (required)
- Market used when fetching liked tracks (optional, defaults to FR)
- Server settings (optional)

## Authentication Flow

The first run opens the Spotify login page in your default browser. A Flask server listens for the OAuth callback and stops once authentication is done.

The refresh token is then saved to `.spotify_token` (ignored by git, readable only by your user), so later runs don't need the browser. Delete this file to log in again. Changing `SCOPE` also triggers a new login.
