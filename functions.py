import requests, json, time, os, datetime
import authentication

URL_BASE = "https://api.spotify.com/v1/"

def read_data(headers):
    url = URL_BASE + "me/tracks"
    response = requests.get(url, headers=headers)
    response_as_text = "{}"
    if response.status_code != 204:
        response_as_text = response.text

    return response.status_code, json.loads(response_as_text)

def get_features(headers, song_id):
    url = URL_BASE + "audio-features/" + song_id
    response = requests.get(url, headers=headers)
    return json.loads(response.text)

def get_artist_id(headers, artist):
    url = URL_BASE + "search?q=" + (artist.replace(" ", "%20")) + "&type=artist"
    response = requests.get(url, headers=headers)
    return json.loads(response.text)["artists"]["items"][0]["id"]

def get_recomendations_url(headers, params):
    url = URL_BASE + "recommendations"
    return requests.get(url, headers=headers, params=params).url

def get_recomendation_objects(headers, params):
    url = get_recomendations_url(headers, params)
    response = requests.get(url, headers=headers)
    return json.loads(response.text)

def get_token():
    authentication.refresh()
    auth = json.load(open("authentication.json", 'r'))
    return auth["user-token"]

def get_header():
    return { 'Accept': 'application/json',
             'Content-Type': 'application/json',
             'Authorization': 'Bearer '+get_token(), }

def get_saved_tracks():
    headers     = get_header()
    code, data  = read_data(headers)

    tracks = { "Tracks": [] }
    for track in data["items"]:
        track = track["track"]

        tracks["Tracks"].append({ "Name": track["name"],
                                  "Artist": track["artists"][0]["name"],
                                  "Album": track["album"]["name"],
                                  "ID": track["id"],
                                  "features": get_features(headers, track["id"]),
                                  "listens": 0 })
    return tracks

def get_artist_ids(header, artist_names):
    ids = []
    for artist in artist_names:
        ids.append(get_artist_id(header, artist))
    return ids

def get_reccomendations_with_algo(query):
    headers = get_header()
    seeds = { "artists": query["artists"],
              "tracks": query["tracks"],
              "genres":  query["genres"] }
    input_time_signature = query["signature"]
    input_number_of_responses = query["limit"]
    input_key = query["key"]
    input_traits = query["traits"]

    artist_ids = get_artist_ids(headers, seeds["artists"])
    keysInNumberFormat = { "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11 }

    query_params = {
        "limit": input_number_of_responses,
        "seed_tracks": ','.join(seeds["tracks"]),
        "seed_genres": ','.join(seeds["genres"]),
        "seed_artists": ','.join(artist_ids),
        "target_time_signature": input_time_signature,
        "target_key": keysInNumberFormat[input_key],
        "target_mode": query["mode"],
        "mode_control": query["mode_control"]
    }

    with open('traits.json') as trait_file:
        trait_db = json.load(trait_file)

    for trait_str in input_traits:
        trait = trait_db[trait_str]
        for lookup_str in trait["attributes"].keys():
            type = trait["attributes"][lookup_str]["type"]
            query_params.update({ type + "_" + lookup_str: trait["attributes"][lookup_str]["value"] })

    data = get_recomendation_objects(headers, query_params)

    ids = []
    for track in data["tracks"]:
        ids.append(track["id"])

    return ids

def add_songs_to_playlist(headers, username, playlist_id, track_ids):
    response = requests.post("https://api.spotify.com/v1/users/"+username+"/playlists/"+playlist_id+"/tracks",
                             headers=headers,
                             data=json.dumps({ "uris": track_ids }))

def get_playlist_from_ids(ids):
    headers = get_header()
    session = requests.Session()

    if(len(ids) == 0):
        return ""

    title = "Tastemkr - " + datetime.datetime.now().strftime('%B %d, %Y')

    username = json.loads(requests.get("https://api.spotify.com/v1/me", headers=headers).text)["uri"].split(":")[2]

    url = "https://api.spotify.com/v1/users/" + username + "/playlists"

    playlist_data = json.loads(requests.post(url, headers=headers, data=json.dumps({ "name": title })).text)
    playlist_id = playlist_data["id"]
    playlist_url = playlist_data["href"]

    for i in range(0, len(ids)):
        ids[i] = "spotify:track:" + ids[i]

    add_songs_to_playlist(headers, username, playlist_id, ids)

    return { "url": json.loads(requests.get(playlist_url, headers=headers).text)["external_urls"]["spotify"] }

if __name__ == "__main__":
    main()
