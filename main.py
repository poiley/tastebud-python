import requests, json, time, os, datetime
import spotifyAuth, spotifyCalculations

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

def read_data(headers, params):
    response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers, params=params)
    return response.status_code, json.loads(response.text)

def read_genre(headers, params, uri):
    response = requests.get("https://api.spotify.com/v1/albums/"+uri, headers=headers, params=params)
    return response.status_code, json.loads(response.text)

def write_data(now_playing, verbose=False):
    if (now_playing.progress / 1000) >= (now_playing.length / 1000 - 1):
        now_playing.progress = now_playing.length

    output =    now_playing.song    + "," + \
                now_playing.artist  + "," + \
                now_playing.album   + "," + \
                now_playing.genre   + "," + \
                now_playing.uri     + "," + \
                str(now_playing.progress / 1000)  + "," + \
                str(now_playing.length / 1000) + "," + \
                str(datetime.datetime.now().strftime('%w %H:%M:%S'))

    if now_playing.song != get_last_line().split(",")[0]: #if the latest song in the list is NOT the one playing
        open("data.csv", "a").write("\n"+output+"\n")
    else:
        lines = open("data.csv", "r").readlines()
        lines[-1] = output
        open("data.csv", 'w').writelines(lines)

def get_last_line():
    return open('data.csv', 'r').read().splitlines()[-1]

def sanitize_data(data):
    lines = open("data.csv","r").read().splitlines()

    index_first_correct_line = 0
    dataFile = open("data.csv","w")
    for line in lines:
        if spotifyCalculations.percent_listened(line.split(",")) > 25:
            if line is not lines[0 + index_first_correct_line]: #for every valid line except the first, put a "\n" before the data
                dataFile.write("\n")
            dataFile.write(line)
        else:
            if line is lines[0]: #if the first line is not properly formatted, add one to the index so as to start formatting correctly
                index_first_correct_line += 1
            print("REMOVING:\t"+line)

    dataFile.close()

def get_song_data(data, headers=None, params=None):
    now_playing = Bunch(song=None)
    now_playing.song        = str(data["item"]["name"]).replace(",", "")
    now_playing.album       = str(data["item"]["album"]["name"]).replace(",", "")
    now_playing.artist      = str(data["item"]["artists"][0]["name"]).replace(",", "")
    now_playing.uri         = data["item"]["uri"]
    now_playing.length      = data["item"]["duration_ms"]
    now_playing.progress    = data["progress_ms"]
    now_playing.genre       = ""
    now_playing.start_time  = datetime.datetime.now().strftime("%w %H:%M:%S")

    if headers is not None and params is not None:
        genre_data = read_genre(headers, params, data["item"]["album"]["id"])[1]["genres"]
        if genre_data:
            now_playing.genre = genre_data[0].replace(",", "")

    return now_playing

def get_token():
    spotifyAuth.refresh()
    auth = json.load(open("authentication.json", 'r'))
    return auth["user-token"]

def main():
    headers     = { 'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer '+get_token(), }
    params      = ( ('market', 'US'), )

    code, data = read_data(headers, params)
    now_playing = get_song_data(data, headers, params)

    #time of day, average beat per minute, if it's on a playlist, genre, etc.
    try:
        while(True):
            code, data = read_data(headers, params)

            if code == 401:
                headers = { 'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer '+get_token(), }
                continue

            now_playing = get_song_data(data, headers, params)

            os.system("cls")

            print_album(now_playing)

            write_data(now_playing)
    except KeyboardInterrupt:
        sanitize_data(data)

def print_album(now_playing):
    m, s     = divmod(now_playing.length/1000, 60)
    length   = str(int(m)).zfill(2)+":"+str(int(s)).zfill(2)

    m, s     = divmod(now_playing.progress/1000, 60)
    progress = str(int(m)).zfill(2)+":"+str(int(s)).zfill(2)

    print(" ____________________ ")
    print("|                    |")
    print("|     ;;;;;;;;;;;;   |")
    print("|     ;          ;   |\tSong:\t"+now_playing.song)
    print("|     ;          ;   |\tAlbum:\t"+now_playing.album)
    print("|     ;          ;   |\tArtist:\t"+now_playing.artist)
    print("|     ;          ;   |")
    print("|     ;          ;   |")
    print("|     ;          ;   |")
    print("|  ,;;;       ,;;;   |\t" + progress + " / " + length)
    print("|  `;;'       `;;'   |")
    print("|                    |")
    print("|____________________|")

if __name__ == "__main__":
    main()
