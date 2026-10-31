# Simple Spotify API wrapper

This is an updated version of a Spotify API wrapper that implements your desired endpoints in the **spotify_requests.py** file.

## Features

- Fetches all liked tracks from a user's library
- Creates a reverse-ordered playlist of liked tracks
- Adds random tracks from the user's library to the playback queue
- Saves liked tracks to JSON files for offline access
- Handles Spotify API rate limiting gracefully
- Manages authentication tokens with automatic refresh

## Requirements

- Python 3.x
- One of the following web drivers (for Selenium automation):
  - Safari (built-in on macOS)
  - Chrome (if installed separately)
  - Firefox (if installed separately)
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
1. Authenticate with Spotify using OAuth 2.0 (using Safari, Chrome, or Firefox as needed)
2. Fetch your liked tracks
3. Save them to a JSON file named after your username
4. Display API statistics

## Configuration

Edit `app.ini` to customize:
- Client credentials (required)
- Server settings (optional)

## Authentication Flow

The application uses Selenium to automate the browser-based Spotify authentication flow. A Flask server listens for the OAuth callback after authentication.

On macOS, the application will attempt to use Safari first, then fall back to Chrome or Firefox if needed.
