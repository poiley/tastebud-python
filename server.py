import functions
from flask import jsonify
from flask import Flask
from flask import request
app = Flask(__name__)

@app.route("/music/playlist")
def reccomend_playist():
    input = {
        "artists": request.args.get('artists', default=[]).split(","),
        "tracks": [],
        "genres": request.args.get('genres', default=[]).split(","),
        "traits": request.args.get('traits', default=[]).split(","),
        "key": request.args.get('key'),
        "signature": request.args.get('signature'),
        "mode": request.args.get('mode'),
        "mode_control": request.args.get('modecontrol'),
        "limit": request.args.get('tracks')
    }
    reccomendations = functions.get_reccomendations_with_algo(input)
    return jsonify(functions.get_playlist_from_ids(reccomendations))

@app.route("/music/saved")
def get_saved_tracks():
    return jsonify(functions.get_saved_tracks())
