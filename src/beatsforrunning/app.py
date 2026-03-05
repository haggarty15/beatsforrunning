import os
from flask import Flask, request, jsonify, send_from_directory, session, redirect
from flask_cors import CORS
from dotenv import load_dotenv

from beatsforrunning.connectors.spotify import SpotifyConnector
from beatsforrunning.core.tempo import calculate_target_bpm
from beatsforrunning.core.playlist import PlaylistGenerator

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-running-key")
CORS(app)

# Use the environment variables for Spotify
SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Connector instance
spotify_conn = SpotifyConnector(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)

@app.route("/")
def serve_index():
    return app.send_static_file("index.html")

@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)

@app.route("/api/health")
def health():
    is_healthy = spotify_conn.check_health()
    return jsonify({"status": "healthy" if is_healthy else "unhealthy", "spotify": is_healthy})

@app.route("/api/recommendations", methods=["POST"])
def get_playlist():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    pace = data.get("pace") # e.g. "5:30" or 5.5
    genres = data.get("genres", ["rock"])
    distance = float(data.get("distance", 5.0))
    unit = data.get("unit", "min/km")
    
    if not pace:
        return jsonify({"error": "Pace is required"}), 400

    try:
        # 1. Calculate BPM
        bpm_range = calculate_target_bpm(pace, unit=unit)
        
        # 2. Get recommendations from Spotify
        tracks = spotify_conn.get_recommendations(
            seed_genres=genres,
            min_tempo=int(bpm_range["lower"]),
            max_tempo=int(bpm_range["upper"]),
            limit=20
        )
        
        # 3. Assemble playlist
        generator = PlaylistGenerator(distance, str(pace), unit)
        playlist = generator.assemble_playlist(tracks)
        
        return jsonify({
            "bpm_range": bpm_range,
            "playlist": playlist
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
