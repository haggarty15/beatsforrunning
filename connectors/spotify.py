import os
import requests
import base64

class SpotifyConnector:
    def __init__(self, client_id: str | None = None, client_secret: str | None = None) -> None:
        self.client_id = client_id or os.environ.get("SPOTIPY_CLIENT_ID") or os.environ.get("CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("SPOTIPY_CLIENT_SECRET") or os.environ.get("CLIENT_SECRET")
        self.token = ""

    def get_token(self) -> str:
        """Fetch an access token using Client Credentials Flow."""
        if not self.client_id or not self.client_secret:
            raise ValueError("Spotify credentials not set")
            
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_base64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
        
        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        
        response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
        response.raise_for_status()
        self.token = response.json()["access_token"]
        return self.token

    def check_health(self) -> bool:
        """Simple health check to verify Spotify connectivity and credentials."""
        try:
            if not self.token:
                self.get_token()
            headers = {"Authorization": f"Bearer {self.token}"}
            # Fetch a minimal resource to verify the connection
            response = requests.get(
                "https://api.spotify.com/v1/browse/new-releases?limit=1", 
                headers=headers, 
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def get_recommendations(self, seed_genres: list[str], min_tempo: int, max_tempo: int, limit: int = 10) -> list[dict]:
        """Get recommended tracks by genre and tempo range."""
        if not self.token:
            self.get_token()
            
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        params = {
            "seed_genres": ",".join(seed_genres),
            "min_tempo": min_tempo,
            "max_tempo": max_tempo,
            "limit": limit
        }
        response = requests.get("https://api.spotify.com/v1/recommendations", headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        tracks = []
        for track in data.get("tracks", []):
            tracks.append({
                "id": track["id"],
                "name": track["name"],
                "artists": [a["name"] for a in track["artists"]],
                "duration_ms": track["duration_ms"],
                "uri": track["uri"]
            })
        return tracks
