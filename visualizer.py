import json
import pandas as pd
from typing import List


"""

when converted to df orient = "index"
it will look like this: (in a table)

song_id     name    seconds_listened    ...     track_length
ID1         NAME1       xxxx            ///         xxx
...
etc..


"""

def parse_that_shit(sortby):
    with open("data.json") as f:
        data = json.load(f)

    df = pd.DataFrame.from_dict(data["tracks"], orient="index")

    # Check if the column is all numbers or all strings
    if df[sortby].dtype == object:
        # Try converting to numeric, if possible
        df[sortby] = pd.to_numeric(df[sortby], errors='ignore')

    # If it's still object (string), sort alphabetically case-insensitive
    if df[sortby].dtype == object:
        df_sorted = df.sort_values(by=sortby, key=lambda x: x.str.lower())
    else:
        df_sorted = df.sort_values(by=sortby, ascending=False)

    # Update original data
    #data["tracks"] = df_sorted.to_dict(orient="index")


    with open("result.json", 'w') as f:
        json.dump(df_sorted.to_dict(orient="index"), f, indent=4)


def retrieve_info_of_artist(artist) -> None:
    with open("data.json") as f:
        data = json.load(f)

    df = pd.DataFrame.from_dict(data["tracks"],orient="index")
    filtered = df[df["artist"].str.lower().str.contains(artist)]

    with open("result.json", 'w') as f:
        json.dump(filtered.to_dict(orient="index"), f, indent=4)

def retrieve_info_of_song(song_name) -> None:
    with open("data.json") as f:
        data = json.load(f)

    df = pd.DataFrame.from_dict(data["tracks"],orient="index")
    filtered = df[df["name"].str.lower().str.contains(song_name)]

    with open("result.json", 'w') as f:
        json.dump(filtered.to_dict(orient="index"), f, indent=4)

def get_top_songs(count: int, key: str = "seconds_listened") -> List[str]:
    # Load data
    with open("data.json") as f:
        data = json.load(f)

    df = pd.DataFrame.from_dict(data["today"], orient="index")

    # Sort descending by key
    if df[key].dtype == object:
        # Try numeric first
        df[key] = pd.to_numeric(df[key], errors='ignore')
    
    if df[key].dtype == object:
        # Strings → alphabetical descending
        df_sorted = df.sort_values(by=key, key=lambda x: x.str.lower(), ascending=False)
    else:
        df_sorted = df.sort_values(by=key, ascending=False)

    # Return top 'count' track IDs
    top_tracks = df_sorted.head(count)["name"].tolist()
    return top_tracks