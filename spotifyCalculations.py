from numpy import genfromtxt, fromstring
from collections import Counter

def average_song_length(data):
    s = 0
    for i in data:
        s += float(data[i][6]) #sum
    return s / len(data) #divide to average

def average_song_length_formatted(data):
    m, s = divmod(average_song_length(data), 60) #format
    return str(int(m)).zfill(2) + ":" + str(int(s)).zfill(2)

def average_song_listened(data):
    s = 0
    for i in data:
        s += percent_listened(data[i])
    return s / len(data) #divide to average

def average_song_completion_listened(data):
    return str(format(average_song_listened(data),".2f")) + "%" #format percentage as readable string

def most_played_artists(data):
    artists = []
    for line in data:
        if percent_listened(line) > 50:
            artists.append(line[1])

    highest_occuring_artists = Counter(artists).most_common()
    highest_occurence = highest_occuring_artists[0][1]
    artists = []

    for artist in highest_occuring_artists:
        if artist[1] != highest_occurence:
            break
        if artist[1] not in artists:
            artists.append(artist[0])

    return artists

def most_played_artist_by_amount_listened(data):
    artists = most_played_artists(data)

    most_played_artist = artists[0]
    by_length = average_song_completion_for_artist(data, artists[0])

    for artist in artists:
        avg_song_comp = average_song_completion_for_artist(data, artist)
        if by_length <= avg_song_comp:
            by_length = avg_song_comp
            most_played_artist = artist

    return most_played_artist

def average_song_completion_for_artist(data, artist):
    sum_percent_listened = 0
    song_list = get_songs(data, artist)

    if len(song_list) == 0 or song_list == [ [] ]:
        print("NO SONGS BY GIVEN ARIST '" + artist + "'!")
        return None

    for line in song_list:
        sum_percent_listened += percent_listened(line)

    return sum_percent_listened / len(song_list)

def percent_listened(line):
    return ( float(line[5]) / float(line[6]) ) * 100

def get_songs(data, artist):
    songs = [ [] ]
    for line in data:
        if artist == line[1]:
            songs.append(line)
    songs.remove( [] )
    return songs

def main():
    d = genfromtxt('data.csv', delimiter=',', dtype=None, encoding="UTF-8")
    print(most_played_artist_by_amount_listened(d))

if __name__ == "__main__":
    main()
