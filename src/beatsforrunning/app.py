import os
from flask import Flask, request, jsonify, send_from_directory, session, redirect
from flask_cors import CORS
from dotenv import load_dotenv

from beatsforrunning.connectors.spotify import SpotifyConnector
from beatsforrunning.core.tempo import calculate_target_bpm
from beatsforrunning.core.playlist import PlaylistGenerator

load_dotenv()

app = Flask(
    __name__,
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../static")),
    static_url_path="/static"
)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-running-key")
CORS(app)

# Use the environment variables for Spotify
SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://127.0.0.1:5000/callback")

# Connector instance
def get_spotify_conn():
    token = session.get("spotify_token")
    conn = SpotifyConnector(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, REDIRECT_URI)
    if token:
        conn.token = token
    return conn

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

@app.route("/")
def serve_index():
    # Look for index.html at the repo root
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/login")
def login():
    conn = get_spotify_conn()
    auth_url = conn.get_auth_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    print(f"Callback received with code: {code[:10]}...")
    if not code:
        return "No code provided", 400
    
    try:
        conn = get_spotify_conn()
        token = conn.get_token_from_code(code)
        session["spotify_token"] = token
        print("Token successfully retrieved and stored in session.")
        return redirect("/")
    except Exception as e:
        print(f"Error in callback: {e}")
        return f"Auth Error: {e}", 500

@app.route("/api/user")
def get_user():
    token = session.get("spotify_token")
    if not token:
        return jsonify({"authenticated": False})
    
    try:
        conn = get_spotify_conn()
        user = conn.get_user_profile()
        return jsonify({
            "authenticated": True,
            "display_name": user.get("display_name"),
            "id": user.get("id"),
            "images": user.get("images")
        })
    except Exception:
        session.pop("spotify_token", None)
        return jsonify({"authenticated": False})

@app.route("/logout")
def logout():
    session.pop("spotify_token", None)
    return redirect("/")

# Default static route will handle /static/ automatically now

@app.route("/api/health")
def health():
    conn = get_spotify_conn()
    is_healthy = conn.check_health()
    return jsonify({"status": "healthy" if is_healthy else "unhealthy", "spotify": is_healthy})

@app.route("/api/recommendations", methods=["POST"])
def get_playlist():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    pace = data.get("pace") # e.g. "5:30" or 5.5
    genres = data.get("genres", [])
    artists = data.get("artists", [])
    distance = float(data.get("distance", 5.0))
    unit = data.get("unit", "min/km")
    
    # Default to rock if nothing provided
    if not genres and not artists:
        genres = ["rock"]
    
    if not pace:
        return jsonify({"error": "Pace is required"}), 400

    try:
        conn = get_spotify_conn()
        # Ensure we have a token
        if not conn.token:
            # Fallback to client credentials if not logged in
            conn.get_token()

        # 1. Calculate BPM
        bpm_range = calculate_target_bpm(pace, unit=unit)
        
        # 2. Search for tracks on Spotify
        search_results = conn.search_tracks(
            seed_genres=genres,
            seed_artists=artists,
            target_bpm=int(bpm_range["optimal"]),
            limit=50 
        )
        
        tracks = search_results.get("tracks", [])
        total_matches = search_results.get("total_matches", 0)
        
        # Diagnostic Check: If no tracks found, find out why
        if not tracks:
            # Try searching without BPM to see if the criteria (Artist/Genre) even exist
            diag_results = conn.search_tracks(seed_genres=genres, seed_artists=artists, target_bpm=None, limit=5)
            diag_tracks = diag_results.get("tracks", [])
            
            if not diag_tracks:
                error_msg = f"We couldn't find any results for '{', '.join(artists or genres)}'. Please check the spelling or try a more common style."
                return jsonify({"error": error_msg}), 404
            else:
                error_msg = f"We found '{', '.join(artists or genres)}', but none of their songs match your target tempo of {int(bpm_range['optimal'])} BPM. Try a different pace or adding more genres."
                return jsonify({"error": error_msg}), 404

        # 3. Assemble playlist
        generator = PlaylistGenerator(distance, str(pace), unit)
        playlist = generator.assemble_playlist(tracks)
        
        # 4. Final Validation
        warning = None
        warning = warning or (playlist.get("warning"))
        if playlist["total_duration_ms"] < (playlist["target_duration_ms"] * 0.8):
            warning = "We couldn't find enough matching songs to fill your entire run. Try adding more genres or artists for a fuller playlist."

        return jsonify({
            "bpm_range": bpm_range,
            "playlist": playlist,
            "warning": warning,
            "total_matches": total_matches
        })
        
    except Exception as e:
        print(f"Error in get_playlist: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/playlist/save", methods=["POST"])
def save_playlist():
    token = session.get("spotify_token")
    if not token:
        print("Save playlist failed: Unauthorized (no token in session)")
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    track_uris = data.get("uris")
    name = data.get("name", "BeatsForRunning Playlist")
    
    print(f"Attempting to save playlist '{name}' with {len(track_uris) if track_uris else 0} tracks")
    
    if not track_uris:
        return jsonify({"error": "No tracks provided"}), 400
        
    try:
        conn = get_spotify_conn()
        user = conn.get_user_profile()
        print(f"Logged in as user: {user.get('id')}")
        playlist = conn.create_playlist(user["id"], name, track_uris)
        print(f"Playlist created successfully: {playlist.get('id')}")
        return jsonify({"success": True, "playlist_url": playlist["external_urls"]["spotify"]})
    except Exception as e:
        print(f"Error in save_playlist: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
