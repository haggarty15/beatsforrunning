import os
import requests
import base64
import urllib.parse
from typing import Any


class SpotifyConnector:
    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
    ) -> None:
        self.client_id = client_id or os.environ.get("CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.environ.get("REDIRECT_URI")
        self.token = ""

    def get_auth_url(self, state: str | None = None) -> str:
        """Generate the URL for the user to authorize the app."""
        scopes = "user-read-private playlist-modify-public playlist-modify-private"
        url = "https://accounts.spotify.com/authorize"
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": scopes,
        }
        if state:
            params["state"] = state

        query_string = "&".join([f"{k}={urllib.parse.quote(v)}" for k, v in params.items() if v])
        return f"{url}?{query_string}"

    def get_token_from_code(self, code: str) -> str:
        """Exchange authorization code for an access token."""
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_base64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "authorization_code", "code": code, "redirect_uri": self.redirect_uri}

        response = requests.post(
            "https://accounts.spotify.com/api/token", headers=headers, data=data
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]
        return self.token

    def get_token(self) -> str:
        """Fetch an access token using Client Credentials Flow (Fallback)."""
        if not self.client_id or not self.client_secret:
            raise ValueError("Spotify credentials not set")

        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_base64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}

        response = requests.post(
            "https://accounts.spotify.com/api/token", headers=headers, data=data
        )
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
                "https://api.spotify.com/v1/browse/new-releases?limit=1", headers=headers, timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def search_tracks(
        self,
        seed_genres: list[str],
        seed_artists: list[str] | None = None,
        target_bpm: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Search for tracks by genre, artist, and optional BPM keywords."""
        if not self.token:
            self.get_token()

        headers = {"Authorization": f"Bearer {self.token}"}

        # Construct query
        query_parts = []
        if seed_artists:
            query_parts.extend([f'artist:"{a}"' for a in seed_artists])
        if seed_genres:
            query_parts.extend([f'genre:"{g}"' for g in seed_genres])

        base_query = " ".join(query_parts)
        query = base_query
        if target_bpm:
            query += f" {target_bpm} bpm"

        # 1. Dual-Search Strategy
        # Strategy A: Broad Track Search (reliable for artists/genres but blind to BPM)
        # Strategy B: Playlist-based Search (reliable for BPM-curated tracks)

        all_tracks = {}
        total_spotify_matches = 0

        # --- STRATEGY A: Broad Track Search ---
        # We fetch up to 150 tracks (3 pages) to ensure variety
        for offset in [0, 50, 100]:
            params: dict[str, Any] = {
                "q": base_query,
                "type": "track",
                "limit": 50,
                "offset": offset,
            }
            resp = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
            if resp.status_code == 200:
                data = resp.json()
                tracks_data = data.get("tracks")
                if tracks_data:
                    total_spotify_matches = max(total_spotify_matches, tracks_data.get("total", 0))
                    for track in tracks_data.get("items", []):
                        if track and track.get("id") and track["id"] not in all_tracks:
                            all_tracks[track["id"]] = {
                                "id": track["id"],
                                "name": track["name"],
                                "artists": [a["name"] for a in track["artists"]]
                                if track.get("artists")
                                else [],
                                "duration_ms": track.get("duration_ms", 0),
                                "uri": track.get("uri"),
                                "popularity": track.get("popularity", 50),
                                "source": "search",
                            }
            if len(all_tracks) >= 150:
                break

        # --- STRATEGY B: Multi-BPM Playlist Discovery ---
        # If target_bpm is provided, we search for curated playlists across compatible tempos
        if target_bpm:
            target = target_bpm
            half = target // 2

            # We search for:
            # 1. Target BPM (e.g. 170)
            # 2. Key variations (+/- 10)
            # 3. Half-time variations (+/- 10) - great for a 170 stride
            search_tempos = [target, target - 10, target + 10, half, half - 10, half + 10]
            # Filter unique positives
            search_tempos = sorted(list(set([t for t in search_tempos if t > 0])), reverse=True)

            for tempo in search_tempos:
                if seed_artists and len(seed_artists) > 0:
                    bpm_query = f'"{seed_artists[0]}" {tempo} BPM'
                else:
                    bpm_query = f"{tempo} BPM"
                    if seed_genres and len(seed_genres) > 0:
                        bpm_query += f" {seed_genres[0]}"

                # Limit to 2 playlists per tempo to keep it fast
                p_params: dict[str, Any] = {"q": bpm_query, "type": "playlist", "limit": 2}
            p_resp = requests.get(
                "https://api.spotify.com/v1/search", headers=headers, params=p_params
            )
            if p_resp.status_code == 200:
                p_data = p_resp.json().get("playlists")
                if p_data:
                    playlists = p_data.get("items", [])
                    for p in playlists:
                        if not p or not p.get("tracks") or not p["tracks"].get("href"):
                            continue

                        # Get tracks from this BPM-curated playlist
                        t_resp = requests.get(p["tracks"]["href"], headers=headers)
                        if t_resp.status_code == 200:
                            t_data = t_resp.json()
                            for item in t_data.get("items", []):
                                if not item:
                                    continue
                                track = item.get("track")
                                if track and track.get("id") and track["id"] not in all_tracks:
                                    all_tracks[track["id"]] = {
                                        "id": track["id"],
                                        "name": track["name"],
                                        "artists": [a["name"] for a in track["artists"]]
                                        if track.get("artists")
                                        else [],
                                        "duration_ms": track.get("duration_ms", 0),
                                        "uri": track.get("uri"),
                                        "popularity": track.get("popularity", 80),
                                        "source": "playlist",
                                    }

        # 2. Filter Results (Strict Artist Match)
        filtered_tracks = []
        for track_id, track in all_tracks.items():
            item_artists = [a.lower().strip() for a in track["artists"]]

            if seed_artists:
                # STRICT VALIDATION: The track MUST include the artist name as a standalone match
                # This prevents "Similar Artists" from slipping through
                is_match = False
                for requested in seed_artists:
                    req_clean = requested.lower().strip()
                    if any(req_clean == found for found in item_artists):
                        is_match = True
                        break
                if not is_match:
                    continue

            filtered_tracks.append(track)

        # 3. Shuffle and Prioritize
        import random

        # First sort by popularity
        filtered_tracks = sorted(filtered_tracks, key=lambda x: x["popularity"], reverse=True)

        # We now return the count of HIGH QUALITY valid matches found for the run
        display_total = len(filtered_tracks)

        # Take up to 100 high-quality tracks and shuffle them
        candidate_pool = filtered_tracks[:100]
        random.shuffle(candidate_pool)

        return {"tracks": candidate_pool[:limit], "total_matches": display_total}

    def get_recommendations(
        self, seed_genres: list[str], min_tempo: int, max_tempo: int, limit: int = 10
    ) -> list[dict]:
        """Get recommended tracks by genre and tempo range."""
        if not self.token:
            self.get_token()

        headers = {"Authorization": f"Bearer {self.token}"}
        params: dict[str, Any] = {
            "seed_genres": ",".join(seed_genres),
            "min_tempo": min_tempo,
            "max_tempo": max_tempo,
            "limit": limit,
        }
        response = requests.get(
            "https://api.spotify.com/v1/recommendations", headers=headers, params=params
        )
        response.raise_for_status()

        data = response.json()
        tracks = []
        for track in data.get("tracks", []):
            tracks.append(
                {
                    "id": track["id"],
                    "name": track["name"],
                    "artists": [a["name"] for a in track["artists"]],
                    "duration_ms": track["duration_ms"],
                    "uri": track["uri"],
                }
            )
        return tracks

    def create_playlist(self, user_id: str, name: str, track_uris: list[str]) -> dict:
        """Create a new playlist for the user and add tracks."""
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

        # 1. Create playlist
        url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        data = {"name": name, "description": "Generated by BeatsForRunning", "public": True}
        resp = requests.post(url, headers=headers, json=data)
        resp.raise_for_status()
        playlist = resp.json()

        # 2. Add tracks
        add_url = f"https://api.spotify.com/v1/playlists/{playlist['id']}/tracks"
        requests.post(add_url, headers=headers, json={"uris": track_uris}).raise_for_status()

        return playlist

    def get_user_profile(self) -> dict:
        """Get current user's profile."""
        headers = {"Authorization": f"Bearer {self.token}"}
        resp = requests.get("https://api.spotify.com/v1/me", headers=headers)
        resp.raise_for_status()
        return resp.json()
