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


def opendata():
    with open("data.json", "r") as f:
        data = json.load(f)
    return data

def closedata(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

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

def update_data(song_id):
    if song_id == -1:
        print("WHAT IS THAT MELODY")
        return 1
    
    curr_min = _data["tracks"][current_song_id].get("seconds_listened")
    last_lis = _data["tracks"][current_song_id].get("last_listened")
    _data["tracks"][current_song_id]["seconds_listened"] = curr_min + (current_timestamp() - last_lis)
    _data["tracks"][current_song_id]["last_listened"] = current_timestamp()

    return 0

CURRENT_SONG_URL = "https://api.spotify.com/v1/me/player/currently-playing"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

_data = opendata()
current_song_id = -1

while(1):
    try:
        r = requests.get(CURRENT_SONG_URL, headers=headers) #Tries the saved token in .env
        if r.status_code in (400,401):
            ACCESS_TOKEN = refresh_access_token(REFRESH_TOKEN)
            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}"
            }
            r = requests.get(CURRENT_SONG_URL, headers=headers)
        

        #Check for song playing
        if r.status_code == 200 and r.content:
            song = json.loads(r.content).get("item")

            #if song changed, update the data file THEN change current_song_id
            if current_song_id != song.get("id"):
                print("SONG CHANGED!")

                val = update_data(current_song_id)
                if not val:
                    print(f"Data updated correctly for id : {current_song_id}")
                else:
                    print(f"Cannot update info about id: {current_song_id}")

                #update song to track
                current_song_id = song.get("id")

            #first listen add basic info to data
            if current_song_id != -1 and current_song_id not in _data["tracks"]:
                    _data["tracks"][current_song_id] = {
                        "name" : song.get("name"),
                        "seconds_listened" : 0,
                        "first_listened" : current_timestamp(),
                        "last_listened"  : current_timestamp(),
                        "artist" : song.get("artists")[0].get("name"),
                        "album" : song.get("album", {}).get("name", "Unknown")
                    }
        elif current_song_id != -1: #switched to not playing anything
            update_data(current_song_id)
            current_song_id = -1
            print("RESET SONG ID TO -1")
        time.sleep(5)
    except KeyboardInterrupt:
        if current_song_id != -1:
            update_data(current_song_id)
        closedata(_data)
        exit()

"""
                minutes_listened = int((current_timestamp() - START_TIME) / 60 * 100) / 100
                print(f"current song \"{song.get('name')}\" \t {minutes_listened} minutes listened")
                time.sleep(5)
"""

