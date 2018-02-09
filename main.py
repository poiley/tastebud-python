import requests, json, time, os, datetime
import spotifyAuth, spotifyCalculations

URL_BASE = "https://api.spotify.com/v1/"

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

def read_data(headers, params):
    url = URL_BASE + "me/player/currently-playing"
    response = requests.get(url, headers=headers, params=params)

    response_as_text = "{}"
    if response.status_code != 204:
        response_as_text = response.text

    return response.status_code, json.loads(response_as_text)

def read_artist_data(headers, params, uri):
    url = URL_BASE + "artists/" + uri
    response = requests.get(url, headers=headers, params=params)
    return json.loads(response.text)

def read_playlist_data(headers, params, user_id, playlist_id):
    url = URL_BASE + "users/" + user_id +"/playlists/" + playlist_id
    response = requests.get(url, headers=headers, params=params)
    return json.loads(response.text)

def read_audio_analysis_data(headers, params, uri):
    url = URL_BASE + "audio-features/" + uri
    response = requests.get(url, headers=headers, params=params)
    return json.loads(response.text)

def write_data(now_playing, verbose=False):
    if (now_playing.progress / 1000) >= (now_playing.length / 1000 - 1):
        now_playing.progress = now_playing.length

    output =    now_playing.song    + "," + \
                now_playing.artist  + "," + \
                now_playing.album   + "," + \
                now_playing.genre   + "," + \
                now_playing.uri     + "," + \
                now_playing.playlist+ "," + \
                str(now_playing.progress / 1000)  + "," + \
                str(now_playing.length / 1000) + "," + \
                str(now_playing.start_time) + "," + \
                str(now_playing.tempo)

    if now_playing.song != get_last_line().split(",")[0]:
        open("data.csv", "a").write("\n"+output+"\n")
    else:
        lines = open("data.csv", "r").readlines()
        lines[-1] = output
        open("data.csv", 'w').writelines(lines)

def get_last_line():
    return open('data.csv', 'r').read().splitlines()[-1]

def sanitize_data():
    lines = open("data.csv","r").read().splitlines()

    index_first_correct_line = 0
    data_file = open("data.csv","w")
    for line in lines:
        if spotifyCalculations.percent_listened(line.split(",")) > 25:
            if line is not lines[0 + index_first_correct_line]: #for every valid line except the first, put a "\n" before the data
                data_file.write("\n")
            data_file.write(line)
        else:
            if line is lines[0]: #if the first line is not properly formatted, add one to the index so as to start formatting correctly
                index_first_correct_line += 1
            print("REMOVING:\t"+line.split(",")[0])

    data_file.close()

def get_song_data(data, headers=None, params=None):
    now_playing = Bunch(playlist="", genre = "", tempo = -1.0)

    now_playing.song     = str(data["item"]["name"]).replace(",", "")
    now_playing.album    = str(data["item"]["album"]["name"]).replace(",", "")
    now_playing.artist   = str(data["item"]["artists"][0]["name"]).replace(",", "")
    now_playing.uri      = data["item"]["uri"]
    now_playing.length   = data["item"]["duration_ms"]
    now_playing.progress = data["progress_ms"]

    start_time           = datetime.datetime.now() - datetime.timedelta(milliseconds=now_playing.progress)
    now_playing.start_time  = start_time.strftime("%w %H:%M:%S")

    if headers is not None and params is not None:
        try:
            if data["context"]["type"] == "playlist":
                user_id              = data["context"]["uri"].split(":")[2]
                playlist_id          = data["context"]["uri"].split(":")[4]
                playlist_data        = read_playlist_data(headers,
                                                          params,
                                                          user_id,
                                                          playlist_id)

                now_playing.playlist = playlist_data["name"].replace(",", "")
        except (KeyError, TypeError):
            pass

        try:
            song_id              = now_playing.uri.split(":")[2]
            audio_analysis_data  = read_audio_analysis_data(headers,
                                                            params,
                                                            song_id)

            now_playing.tempo    = float(audio_analysis_data["tempo"])
        except (KeyError, TypeError):
            pass

        try:
            artist_id            = data["item"]["artists"][0]["id"]
            artist_data          = read_artist_data(headers,
                                                    params,
                                                    artist_id)

            now_playing.genre    = artist_data["genres"][0].replace(",", "")
        except (KeyError, TypeError):
            pass

    return now_playing

def print_album(now_playing):
    m, s     = divmod(now_playing.length/1000, 60)
    length   = str(int(m)).zfill(2)+":"+str(int(s)).zfill(2)

    m, s     = divmod(now_playing.progress/1000, 60)
    progress = str(int(m)).zfill(2)+":"+str(int(s)).zfill(2)

    side_lines = "|"+ (20 * " ") +"|"
    base       = "|     ;          ;   |\t"

    song    = "Song:\t\t"   + ((now_playing.song[:27]     + '...') if len(now_playing.song)     >= 27 else now_playing.song)
    album   = "Album:\t\t"  + ((now_playing.album[:27]    + '...') if len(now_playing.album)    >= 27 else now_playing.album)
    artist  = "Artist\t\t"  + ((now_playing.artist[:27]   + '...') if len(now_playing.artist)   >= 27 else now_playing.artist)
    playlist= "Playlist:\t" + ((now_playing.playlist[:27] + '...') if len(now_playing.playlist) >= 27 else now_playing.playlist)

    print(" " + (20 * "_") + " \n" + side_lines)
    print("|     ;;;;;;;;;;;;   |")
    print(base + song + "\n" + base + album + "\n" + base + artist + "\n" + base + playlist + "\n" + base + "\n" + base)
    print("|  ,;;;       ,;;;   |\t" + progress + " / " + length)
    print("|  `;;'       `;;'   |\n" + side_lines)
    print("|" + (20 * "_") + "|")

def get_token():
    spotifyAuth.refresh()
    auth = json.load(open("authentication.json", 'r'))
    return auth["user-token"]

def get_header():
    return { 'Accept': 'application/json',
             'Content-Type': 'application/json',
             'Authorization': 'Bearer '+get_token(), }

def main():
    headers     = get_header()
    params      = ( ('market', 'US'), )

    code, data = read_data(headers, params)

    if code != 204:
        now_playing = get_song_data(data, headers, params)

    try:
        while(True):
            code, data = read_data(headers, params)

            if code != 200:
                if code == 401:
                    headers = get_header()
                elif code == 204: # nothing playing!
                    os.system("cls")
                    print("Nothing Playing.")
                    time.sleep(1)
                continue

            now_playing = get_song_data(data, headers, params)

            os.system("cls")

            print_album(now_playing)
            write_data(now_playing)
    except KeyboardInterrupt:
        sanitize_data()

if __name__ == "__main__":
    main()
