import sys, json
import spotipy.util as util

scope = 'user-library-read user-read-currently-playing user-read-playback-state'

def refresh():
    data = json.load(open('authentication.json', 'r'))

    token = util.prompt_for_user_token( data["username"],
                                        scope,
                                        client_id     = data["client-ID"],
                                        client_secret = data["client-secret"],
                                        redirect_uri  = data["redirect-URI"] )

    data['user-token'] = token

    json.dump(data, open("authentication.json", "w"), indent = 4)

    print("New token registered.")
    print(token[:47]+"...")
    print("Check `authentication.json` for more info.\n")
