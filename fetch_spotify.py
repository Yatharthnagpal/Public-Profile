import os
import requests
import json
import base64

OUTPUT_DIR = "public"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "spotify.json")

def get_access_token(client_id, client_secret, refresh_token):
    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {b64_auth_str}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def get_spotify_data(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Check currently playing
    url = "https://api.spotify.com/v1/me/player/currently-playing"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data and data.get("is_playing") and data.get("item"):
            track = data["item"]
            return track["name"], track["artists"][0]["name"], True

    # If nothing currently playing, check recently played
    url = "https://api.spotify.com/v1/me/player/recently-played?limit=1"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data and data.get("items"):
            track = data["items"][0]["track"]
            return track["name"], track["artists"][0]["name"], False
            
    return "Nothing playing", "Spotify API", False

if __name__ == "__main__":
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    refresh_token = os.environ.get("SPOTIFY_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        title = "Setup Required"
        artist = "Add Spotify Secrets"
        is_playing = False
    else:
        try:
            access_token = get_access_token(client_id, client_secret, refresh_token)
            title, artist, is_playing = get_spotify_data(access_token)
        except Exception as e:
            print(f"Error fetching Spotify data: {e}")
            title = "Error"
            artist = "Check Action Logs"
            is_playing = False

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Truncate very long song names
    msg = str(title) + " - " + str(artist)
    if len(msg) > 40:
        msg = msg[:37] + "..."
        
    badge_data = {
        "schemaVersion": 1,
        "label": "Now Playing 🎧" if is_playing else "Recently Played 🎵",
        "message": msg,
        "color": "1DB954"
    }
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(badge_data, f, indent=2)
        
    print(f"Saved Spotify badge data to {OUTPUT_FILE}")
