import pytest
from unittest.mock import patch, MagicMock
from beatsforrunning.app import app
import json

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-key"
    with app.test_client() as client:
        yield client

def test_serve_index(client):
    with patch('beatsforrunning.app.send_from_directory') as mock_send:
        mock_send.return_value = "Index"
        response = client.get("/")
        assert response.status_code == 200

def test_get_spotify_conn_with_token(client):
    with client.session_transaction() as sess:
        sess["spotify_token"] = "existing_token"
    
    with patch("beatsforrunning.app.SpotifyConnector") as mock_conn_class:
        mock_instance = MagicMock()
        mock_conn_class.return_value = mock_instance
        client.get("/api/user") # calls get_spotify_conn internally
        assert mock_instance.token == "existing_token"

def test_login(client):
    with patch("beatsforrunning.app.get_spotify_conn") as mock_conn_func:
        mock_conn = MagicMock()
        mock_conn.get_auth_url.return_value = "http://spotify.com/auth"
        mock_conn_func.return_value = mock_conn
        
        response = client.get("/login")
        assert response.status_code == 302
        assert response.headers["Location"] == "http://spotify.com/auth"

def test_callback_no_code(client):
    response = client.get("/callback")
    assert response.status_code == 400

def test_callback_success(client):
    with patch("beatsforrunning.app.get_spotify_conn") as mock_conn_func:
        mock_conn = MagicMock()
        mock_conn.get_token_from_code.return_value = "fake_token"
        mock_conn_func.return_value = mock_conn
        
        response = client.get("/callback?code=abc1234567890")
        assert response.status_code == 302
        with client.session_transaction() as sess:
            assert sess.get("spotify_token") == "fake_token"

def test_callback_error(client):
    with patch("beatsforrunning.app.get_spotify_conn") as mock_conn_func:
        mock_conn = MagicMock()
        mock_conn.get_token_from_code.side_effect = Exception("Auth Error")
        mock_conn_func.return_value = mock_conn
        
        response = client.get("/callback?code=abc1234567890")
        assert response.status_code == 500

def test_get_user_no_token(client):
    response = client.get("/api/user")
    data = json.loads(response.data)
    assert not data["authenticated"]

def test_get_user_with_token(client):
    with client.session_transaction() as sess:
        sess["spotify_token"] = "fake"
    
    with patch("beatsforrunning.app.get_spotify_conn") as mock_conn_func:
        mock_conn = MagicMock()
        mock_conn.get_user_profile.return_value = {"display_name": "Test User", "id": "123", "images": []}
        mock_conn_func.return_value = mock_conn
        
        response = client.get("/api/user")
        data = json.loads(response.data)
        assert data["authenticated"]
        assert data["display_name"] == "Test User"

def test_get_user_exception(client):
    with client.session_transaction() as sess:
        sess["spotify_token"] = "fake"
        
    with patch("beatsforrunning.app.get_spotify_conn") as mock_conn_func:
        mock_conn = MagicMock()
        mock_conn.get_user_profile.side_effect = Exception("API error")
        mock_conn_func.return_value = mock_conn
        
        response = client.get("/api/user")
        data = json.loads(response.data)
        assert not data["authenticated"]

def test_logout(client):
    with client.session_transaction() as sess:
        sess["spotify_token"] = "fake"
    
    response = client.get("/logout")
    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert "spotify_token" not in sess

def test_health(client):
    with patch("beatsforrunning.app.get_spotify_conn") as mock_conn_func:
        mock_conn = MagicMock()
        mock_conn.check_health.return_value = True
        mock_conn_func.return_value = mock_conn
        
        response = client.get("/api/health")
        data = json.loads(response.data)
        assert data["status"] == "healthy"

def test_recommendations_no_data(client):
    response = client.post("/api/recommendations")
    assert response.status_code == 415

def test_recommendations_no_data_json(client):
    response = client.post("/api/recommendations", json=None)
    assert response.status_code == 415

def test_recommendations_no_pace(client):
    response = client.post("/api/recommendations", json={})
    assert response.status_code == 400

def test_recommendations_no_genres(client):
    with patch("beatsforrunning.app.get_spotify_conn") as mock_conn_func:
        mock_conn = MagicMock()
        # Mock search_tracks to return empty then populated test case or valid data
        mock_conn.search_tracks.return_value = {"tracks": [{"id": "1", "name": "track", "artists": [{"name": "A"}], "duration_ms": 1000, "uri": "spotify:track:1"}], "total_matches": 1}
        mock_conn_func.return_value = mock_conn

        response = client.post("/api/recommendations", json={"pace": "5:00"})
        response = client.post("/api/recommendations", json={"pace": "5:00"})
        assert json.loads(response.data)
        assert response.status_code == 200

def test_recommendations_no_tracks_artist_error(client):
    with patch("beatsforrunning.app.get_spotify_conn") as mock_conn_func:
        mock_conn = MagicMock()
        # First call has no tracks for exact tempo matching
        # Second diagnostic call has also no tracks (artist might not exist)
        mock_conn.search_tracks.side_effect = [{"tracks": [], "total_matches": 0}, {"tracks": []}]
        mock_conn_func.return_value = mock_conn
        
        response = client.post("/api/recommendations", json={"pace": "5:00", "artists": ["FakeArtist"]})
        assert response.status_code == 404
        assert "We couldn't find any results for" in json.loads(response.data)["error"]

def test_recommendations_no_tracks_tempo_error(client):
    with patch("beatsforrunning.app.get_spotify_conn") as mock_conn_func:
        mock_conn = MagicMock()
        # Diagnostic call has tracks, indicating tempo is the issue
        mock_conn.search_tracks.side_effect = [{"tracks": [], "total_matches": 0}, {"tracks": [{"id": "1"}]}]
        mock_conn_func.return_value = mock_conn
        
        response = client.post("/api/recommendations", json={"pace": "5:00", "artists": ["RealArtist"]})
        assert response.status_code == 404
        assert "but none of their songs match your target tempo" in json.loads(response.data)["error"]

def test_recommendations_exception(client):
    with patch("beatsforrunning.app.get_spotify_conn") as mock_conn_func:
        mock_conn_func.side_effect = Exception("System error")
        response = client.post("/api/recommendations", json={"pace": "5:00"})
        assert response.status_code == 500

def test_save_playlist_no_token(client):
    response = client.post("/api/playlist/save", json={})
    assert response.status_code == 401

def test_save_playlist_no_tracks(client):
    with client.session_transaction() as sess:
        sess["spotify_token"] = "fake"
    response = client.post("/api/playlist/save", json={})
    assert response.status_code == 400

def test_save_playlist_success(client):
    with client.session_transaction() as sess:
        sess["spotify_token"] = "fake"
        
    with patch("beatsforrunning.app.get_spotify_conn") as mock_conn_func:
        mock_conn = MagicMock()
        mock_conn.get_user_profile.return_value = {"id": "user123"}
        mock_conn.create_playlist.return_value = {"id": "pl1", "external_urls": {"spotify": "url"}}
        mock_conn_func.return_value = mock_conn
        
        response = client.post("/api/playlist/save", json={"uris": ["uri1"]})
        assert response.status_code == 200
        assert json.loads(response.data)["success"]

def test_save_playlist_error(client):
    with client.session_transaction() as sess:
        sess["spotify_token"] = "fake"
        
    with patch("beatsforrunning.app.get_spotify_conn") as mock_conn_func:
        mock_conn = MagicMock()
        mock_conn.get_user_profile.side_effect = Exception("Playlist Creation Failed")
        mock_conn_func.return_value = mock_conn
        
        response = client.post("/api/playlist/save", json={"uris": ["uri1"]})
        assert response.status_code == 500
