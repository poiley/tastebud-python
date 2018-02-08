from numpy import genfromtxt, fromstring
from collections import Counter

def average_song_length(data):
    s = 0
    for line in data:
        s += float(line[7]) #sum
    return s / len(data) #divide to average

def average_song_length_formatted(data):
    m, s = divmod(average_song_length(data), 60) #format
    return str(int(m)).zfill(2) + ":" + str(int(s)).zfill(2)

def average_song_progress(data):
    s = 0
    for line in data:
        s += float(line[6])
    return s / len(data) #divide to average

def most_played_artists(data):
    artists = get_artists(data, 50)

    highest_occuring_artists = Counter(artists).most_common()

    if len(highest_occuring_artists) != 1:
        highest_occurence = highest_occuring_artists[0][1]
        artists = []

        for artist in highest_occuring_artists:
            if artist[1] != highest_occurence:
                break
            if artist[1] not in artists:
                artists.append(artist[0])

    return artists

def average_song_completion_for_artist(data, artist):
    sum_percent_listened = 0
    song_list = get_songs(data, artist)

    if len(song_list) == 0 or song_list == [ ]:
        print("NO SONGS BY GIVEN ARIST '" + artist + "'!")
        return None

    for song in song_list:
        sum_percent_listened += percent_listened(get_song_line(data, song))

    return sum_percent_listened / len(song_list)

def percent_listened(line):
    return ( float(line[6]) / float(line[7]) ) * 100

def get_song_line(data, song):
    for line in data:
        if line[0] == song:
            return line
    return None

def get_songs(data, artist=None):
    songs = [ ]
    for line in data:
        if percent_listened(line) > 25:
            if artist != None and artist == line[1]:
                songs.append(line[0])
            else:
                songs.append(line[0])

    return songs

def get_albums(data, artist=None):
    albums = [ ]
    for line in data:
        if artist != None and artist == line[1]:
            albums.append(line[2])
        else:
            albums.append(line[2])

    return albums

def get_artists(data, minimum_percent=None):
    artists = [ ]
    for line in data:
        if minimum_percent == None and percent_listened(line) > 25:
            artists.append(line[1])
        elif percent_listened(line) > minimum_percent:
            artists.append(line[1])

    return artists

def main():
    d = genfromtxt('data.csv', delimiter=',', dtype=None, encoding="UTF-8")
    print(average_song_completion_for_artist(d, "Childish Gambino"))

if __name__ == "__main__":
    main()
