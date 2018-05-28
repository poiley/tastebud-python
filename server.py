import functions, json
from flask import jsonify, Flask, request
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/music/*": {"origins": "*"}})

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
    return jsonify(functions.get_playlist_from_ids(reccomendations, input["artists"][0], input["traits"][0]))

@app.route("/music/saved")
def get_saved_tracks():
    data = functions.get_saved_tracks()

    with open("saved.json", "w+") as file:
        json.dump(data, file)

    return jsonify(data)
