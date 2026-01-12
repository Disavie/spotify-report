import requests
from urllib.parse import urlencode
from dotenv import load_dotenv
import os
import json
import time
import datetime

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
CLIENT_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
ACCESS_TOKEN = os.getenv("SPOTIFY_ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")

def current_timestamp():
    return datetime.datetime.now().timestamp()

START_TIME = current_timestamp()
minutes_listened = 0

def get_access_token():

    # Step 1: Generate Spotify login URL
    auth_params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": CLIENT_REDIRECT_URI,
        "scope": "user-read-currently-playing user-read-playback-state"
    }
    auth_url = "https://accounts.spotify.com/authorize?" + urlencode(auth_params)
    print("Open this URL in a browser and authorize the app:")
    print(auth_url)

    # Step 2: Get code from user
    code = input("Paste the 'code' parameter from the URL here: ").strip()

    # Step 3: Exchange code for access token
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": CLIENT_REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    TOKEN_URL = "https://accounts.spotify.com/api/token"
    token_response = requests.post(TOKEN_URL, data=token_data)

    # Check if token request succeeded
    if token_response.status_code != 200:
        print("Error getting access token:", token_response.text)
        exit()

    access_token = token_response.json()["access_token"]
    refresh_token = token_response.json()["refresh_token"]
    print(f'ACCESS TOKEN = {access_token}')
    print(f'refresh TOKEN = {refresh_token}')
    return [access_token,refresh_token]

def refresh_access_token(refresh_token):
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code != 200:
        raise Exception(f"Error refreshing token: {response.text}")
    return response.json()["access_token"]


CURRENT_SONG_URL = "https://api.spotify.com/v1/me/player/currently-playing"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

while(1):
    r = requests.get(CURRENT_SONG_URL, headers=headers) #Tries the saved token in .env
    if r.status_code in (400,401):
        ACCESS_TOKEN = refresh_access_token(REFRESH_TOKEN)
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }
        r = requests.get(CURRENT_SONG_URL, headers=headers)
    

    #Check for song playing
    if r.status_code == 200 and r.content:
        song = json.loads(r.content)
        minutes_listened = int((current_timestamp() - START_TIME) / 60 * 100) / 100
        print(f"current song \"{song.get('item').get('name')}\" \t {minutes_listened} minutes listened")
        time.sleep(10)



