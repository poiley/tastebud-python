import requests, json, time, os, datetime
import authentication

URL_BASE = "https://api.spotify.com/v1/"

def read_data(headers):
    url = URL_BASE + "me/tracks"
    response = requests.get(url, headers=headers, params={"limit": 50})
    response_as_text = "{}"
    if response.status_code != 204:
        response_as_text = response.text

    return response.status_code, json.loads(response_as_text)

def get_features(headers, song_id):
    url = URL_BASE + "audio-features/" + song_id
    response = requests.get(url, headers=headers)
    return json.loads(response.text)

def get_track_id(headers, track_name):
    url = URL_BASE + "search?q=" + track_name.replace(" ", "%20") + "&type=track"
    response = requests.get(url, headers=headers)
    try:
        return json.loads(response.text)["tracks"]["items"][0]["id"]
    except IndexError, KeyError:
        return ""

def get_track_ids(headers, tracks):
    ids = []
    if tracks:
        for track in tracks:
            ids.append(get_track_id(headers, track))
    return ids

def get_artist_id(headers, artist):
    url = URL_BASE + "search?q=" + artist.replace(" ", "%20") + "&type=artist"
    response = requests.get(url, headers=headers)
    try:
        return json.loads(response.text)["artists"]["items"][0]["id"]
    except IndexError:
        return ""

def get_artist_ids(headers, artist_names):
    ids = []
    if artist_names:
        for artist in artist_names:
            ids.append(get_artist_id(headers, artist))
    return ids

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
             'Access-Control-Allow-Origin': '*',
             'Content-Type': 'application/json',
             'Authorization': 'Bearer '+get_token(), }

def get_playlist_name(artist, trait):
    return trait + " " + artist + " - TasteBud, " + datetime.datetime.now().strftime('%B %d, %Y')

def get_saved_tracks():
    headers = get_header()
    url = "https://api.spotify.com/v1/me/tracks"
    data = json.loads(requests.get(url, headers=headers).text)

    tracks = { "Tracks": [] }
    track_index = 0
    while("next" in data.keys()):
        for track in data["items"]:
            track = track["track"]

            tracks["Tracks"].append({ "Name": track["name"],
                                      "Artist": track["artists"][0]["name"],
                                      "Album": track["album"]["name"],
                                      "ID": track["id"],
                                      "features": get_features(headers, track["id"]),
                                      "listens": 0 })
            track_index += 1
            if track_index % 100 == 0:
                print(str(track_index) + " songs queried!")

        url = data["next"]
        if url == None:
            break
        data = json.loads(requests.get(url, headers=headers).text)

        if "Retry-After" in data.keys():
            print("Rate limited! Trying again in " + str(data["Retry-After"]) + " seconds.")
            time.sleep(data["Retry-After"])

    return tracks

def get_reccomendations_with_algo(query):
    headers = get_header()
    seeds = { "artists": get_artist_ids(headers, query["artists"]),
              "tracks": get_track_ids(headers, query["tracks"]),
              "genres":  query["genres"] }
    input_time_signature = query["signature"]
    input_number_of_responses = query["limit"]
    input_key = query["key"]
    input_traits = query["traits"]

    keysInNumberFormat = { "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11 }

    query_params = {
        "seed_tracks": ','.join(seeds["tracks"]),
        "seed_genres": ','.join(seeds["genres"]),
        "seed_artists": ','.join(seeds["artists"]),
        "target_time_signature": input_time_signature,
        "target_key": None,
        "target_mode": None,
        "mode_control": None,
        "limit": input_number_of_responses
    }

    if query_params["mode_control"] != 0 and query_params["mode_control"] != None:
        query_params["mode_control"] = query["mode_control"]
        query_params["target_key"] = keysInNumberFormat[input_key]
        query_params["target_mode"] = query["target_mode"]

    with open('traits.json') as trait_file:
        trait_db = json.load(trait_file)

    for trait_str in input_traits:
        trait = trait_db[trait_str]
        for lookup_str in trait["attributes"].keys():
            type = trait["attributes"][lookup_str]["type"]
            query_params.update({ type + "_" + lookup_str: trait["attributes"][lookup_str]["value"] })

    data = get_recomendation_objects(headers, query_params)

    ids = []
    if "tracks" in data.keys():
        for track in data["tracks"]:
            if "id" in track.keys():
                ids.append(track["id"])

    return ids

def add_songs_to_playlist(headers, username, playlist_id, track_ids):
    response = requests.post("https://api.spotify.com/v1/users/"+username+"/playlists/"+playlist_id+"/tracks",
                             headers=headers,
                             data=json.dumps({ "uris": track_ids }))

def get_playlist_from_ids(ids, artist, trait):
    headers = get_header()

    if(len(ids) == 0):
        return ""

    title = get_playlist_name(artist, trait)

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
