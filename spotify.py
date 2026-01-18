import requests
from urllib.parse import urlencode
from dotenv import load_dotenv
import os
import json
import time
import datetime
import myemail
import threading

stop_event = threading.Event()
spotify_thread = None

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
CLIENT_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
ACCESS_TOKEN = os.getenv("SPOTIFY_ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")
_data = {}
current_song_id = -1
paused = 0
time_paused = 0

def get_midnight(timestamp):
    # Convert to datetime
    dt = datetime.datetime.fromtimestamp(timestamp)
    # Get midnight of that date
    midnight_dt = datetime.datetime(dt.year, dt.month, dt.day)
    dt_str = midnight_dt.strftime("%Y-%m-%d %H:%M:%S")  # format as "2026-01-12 11:42:00"
    return dt_str

def current_timestamp():
    return datetime.datetime.now().timestamp()

def opendata():
    with open("data.json", "r") as f:
        data = json.load(f)
    return data

def closedata(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

def get_access_token():
    global CLIENT_ID
    global CLIENT_REDIRECT_URI
    global CLIENT_SECRET
    global ACCESS_TOKEN
    global REFRESH_TOKEN
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
    global CLIENT_ID
    global CLIENT_REDIRECT_URI
    global CLIENT_SECRET
    global ACCESS_TOKEN
    global REFRESH_TOKEN
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

def update_data(data, current_song_id):
    if current_song_id == -1:
        return 1
    
    #track data
    last_lis = data["tracks"][current_song_id].get("last_listened")
    new_secs = (current_timestamp() - last_lis)
    data["tracks"][current_song_id]["seconds_listened"] += new_secs
    data["tracks"][current_song_id]["last_listened"] = current_timestamp()


    #day's data
    data["dates"][get_midnight(current_timestamp())]["seconds_listened"] += new_secs
    #print(f'{data["dates"][get_midnight(current_timestamp())]["seconds_listened"] /60 } minutes listened today')

    return 0

def get_genres(artist_id):
    global ACCESS_TOKEN
    ARTIST_INFO_URL = f"https://api.spotify.com/v1/artists/{artist_id}"
    r = requests.get(ARTIST_INFO_URL, headers= {
                    "Authorization": f"Bearer {ACCESS_TOKEN}"
                }) #Tries the saved token in .env

    print(r.status_code)
    if r.status_code == 200:
        response = json.loads(r.content)
        return response.get("genres")
    return []


def new_track(_data, current_song_id,song):
            #first listen add basic info to data
                    _data["tracks"][current_song_id] = {
                        "name" : song.get("name"),
                        "seconds_listened" : 0,
                        "first_listened" : current_timestamp(),
                        "last_listened"  : current_timestamp(),
                        "artist" : song.get("artists")[0].get("name"),
                        "artist_id" : song.get("artists")[0].get("id"),
                        "genre" : get_genres(song.get("artists")[0].get("id")),
                        "album" : song.get("album", {}).get("name", "Unknown"),
                        "genre" : None,
                        "times_skipped" : 0,
                        "times_played"  : 1,
                        "track_length"  : song.get("duration_ms") / 1000

                    }
CURRENT_SONG_URL = "https://api.spotify.com/v1/me/player/currently-playing"

def skipped(track,starting_seconds,total_length):
     time_listened = track.get("seconds_listened") - starting_seconds
     #print(f' time listned = {time_listened}')
     #print(f' total_length = {total_length}')
     

     if abs(time_listened - total_length) > 15:
          print("You skipped!")
          term_helper()
          return 1
     else:
          return 0

def safe_save():
    global paused
    global _data
    global current_song_id
    global time_paused  
    if current_song_id != -1:
        update_data(_data, current_song_id)
        #print("jere2")
        if paused:
            print('jere')
            tp = current_timestamp() - time_paused
            _data["tracks"][current_song_id]["seconds_listened"] -= tp
            _data["dates"][get_midnight(current_timestamp())]["seconds_listened"] -= tp

    print(f"Data was saved at {datetime.datetime.fromtimestamp(current_timestamp())}")

    closedata(_data)

def get_todays_stats():
    x = opendata()
    return json.dumps(x["dates"][get_midnight(current_timestamp())],indent=4)
def term_helper():
    print("> ", end="", flush=True)

def spotify_loop(): 
    global CLIENT_ID
    global CLIENT_REDIRECT_URI
    global CLIENT_SECRET
    global ACCESS_TOKEN
    global REFRESH_TOKEN
    global paused
    global _data
    global current_song_id
    global time_paused    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    _data = opendata()

    last_save_time = current_timestamp()
    seconds_listened_when_track_begin = 0
    duration_s = 0
    save_please = 1
    current_day = -1
    last_notif_time = current_timestamp()

    while not stop_event.is_set():
        #autosave
        if save_please or current_timestamp() - last_save_time > 900: #15 minutes
            last_save_time = current_timestamp()
            save_please = 0
            closedata(_data)
            print(f"--> Autosaving data at {datetime.datetime.fromtimestamp(last_save_time)}")
            term_helper()
            #myemail.send_email(myemail.MY_EMAIL,"Autosave",f"Autosaving data at {datetime.datetime.fromtimestamp(last_save_time)}")

        #Hourly notifications option    
        """
        if current_timestamp() - last_notif_time > 3600: #1 hour
            last_notif_time = current_timestamp()
            myemail.send_email(myemail.MY_EMAIL,
                                "Daily Summary",
                                f"You spent {_data["dates"][current_day]["seconds_listened"]/60} minutes listening to Spotify on {current_day} (or {_data["dates"][current_day]["seconds_listened"]/60/60} hours)")
        """


        #daily notifications , will send an email summary of previous day at midnight
        if get_midnight(current_timestamp()) != current_day:
            if current_day != -1:
                myemail.send_email(myemail.MY_EMAIL,
                                "Daily Summary",
                                f"You spent {_data["dates"][current_day]["seconds_listened"]/60} minutes listening to Spotify on {current_day}")
            current_day = get_midnight(current_timestamp())

        #add day to "data/dates"
        if current_day not in _data["dates"]:
            _data["dates"][current_day] = {
                "seconds_listened" : 0
            }

        #get current song
        try:
            r = requests.get(CURRENT_SONG_URL, headers=headers) #Tries the saved token in .env
            if r.status_code in (400,401):
                ACCESS_TOKEN = refresh_access_token(REFRESH_TOKEN)
                headers = {
                    "Authorization": f"Bearer {ACCESS_TOKEN}"
                }
                r = requests.get(CURRENT_SONG_URL, headers=headers, timeout = 10)
        except Exception as e:
            print(f"Caught error with url request : {e}")
            time.sleep(1)
            continue
        except KeyboardInterrupt:
            safe_save()
            exit()   
        

        #Check for song playing

        if r.status_code == 200 and r.content:

            """" debug
            with open("recent_req.json", "w") as f:
                json.dump(json.loads(r.content), f, indent=4)
            """
            response = json.loads(r.content)
            song = json.loads(r.content).get("item")

            if not response.get("is_playing"): #pausing
                if not paused:
                    time_paused = current_timestamp()
                    print("Pausing")
                    term_helper()
                    paused = 1

            if response.get("is_playing"): #unpausing
                if paused:
                    tp = current_timestamp() - time_paused
                    if current_song_id != -1:
                        tp = current_timestamp() - time_paused
                        _data["tracks"][current_song_id]["seconds_listened"] -= tp
                        _data["dates"][get_midnight(current_timestamp())]["seconds_listened"] -= tp

                    print(f'Unpausing (after {tp} seconds)')
                    term_helper()
                    paused = 0

            #if there is a song playing and the song playing currently is not what was just playing in the previous loop
            # song changed!
            if song and current_song_id != song.get("id"): 

                #If you skip songs while paused, the time you were paused on that track is subtracted from your total time spent listening to that track
                if paused and current_song_id != -1:
                    tp = current_timestamp() - time_paused
                    _data["tracks"][current_song_id]["seconds_listened"] -= tp
                    _data["dates"][get_midnight(current_timestamp())]["seconds_listened"] -= tp

                #Updates all data about the song
                update_data(_data,current_song_id)
                
                #Perform math to check the song was completed, if not than increase the 'skip count' of the song
                if current_song_id != -1 and skipped(_data["tracks"][current_song_id],seconds_listened_when_track_begin, duration_s):
                    _data["tracks"][current_song_id]["times_skipped"] += 1



                print(f"Current Song : \"{song.get('name')}\"")
                term_helper()

                #update song to track if song swapped
                current_song_id = song.get("id")
                duration_s = song.get("duration_ms") / 1000
                if current_song_id != -1:

                    #If this is the first time listening to this song we need to add it
                    if current_song_id != -1 and current_song_id not in _data["tracks"]:
                        new_track(_data, current_song_id,song)
                    else:
                    #Since we have listened to this song before, increase the amount of times we have listened to it
                    
                        _data["tracks"][current_song_id]["times_played"] += 1

                    #Fill in data that was absent in previous version
                    try:
                        if _data["tracks"][current_song_id]["artist_id"] == None:
                            _data["tracks"][current_song_id]["artist_id"] = song.get("artists")[0].get("id")
                    except KeyError:
                        _data["tracks"][current_song_id]["artist_id"] = song.get("artists")[0].get("id")


                    #Fill in data that was absent in previous version
                    try:
                        if _data["tracks"][current_song_id]["track_length"] == None:
                            _data["tracks"][current_song_id]["track_length"] = duration_s
                    except KeyError:
                         _data["tracks"][current_song_id]["track_length"] = duration_s

                    try:
                        if _data["tracks"][current_song_id]["genre"] == None:
                            _data["tracks"][current_song_id]["genre"] = get_genres(_data["tracks"][current_song_id].get("artist_id"))
                    except KeyError:
                            _data["tracks"][current_song_id]["genre"] = get_genres(_data["tracks"][current_song_id].get("artist_id"))
                
                    #How long had we previously listened to this track? 
                    #This is saved for later to check if we listened to the entire track or if we skipped
                    seconds_listened_when_track_begin = _data["tracks"][current_song_id].get("seconds_listened")

                    #Update most recent listen of song to now
                    _data["tracks"][current_song_id]["last_listened"] = current_timestamp()


        elif current_song_id != -1: #switched to not playing anything
            update_data(_data, current_song_id)
            current_song_id = -1
            print("Nothing is playing now")
            term_helper()

        try:
            time.sleep(1)

        except KeyboardInterrupt:
            safe_save()
            exit()
    safe_save()
      

def start():
    global spotify_thread

    if spotify_thread and spotify_thread.is_alive():
        print("Spotify tracker already running")
        return

    stop_event.clear()
    spotify_thread = threading.Thread(
        target=spotify_loop,
        daemon=True
    )
    spotify_thread.start()
    print("Spotify tracker started")

def stop():
    global spotify_thread

    print("Stopping Spotify tracker...")
    stop_event.set()

    if spotify_thread:
        spotify_thread.join()

    print("Spotify tracker stopped")

