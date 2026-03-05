import pytest
import responses
from beatsforrunning.connectors.spotify import SpotifyConnector

@pytest.fixture
def spotify_conn():
    conn = SpotifyConnector(client_id="mock_id", client_secret="mock_secret", redirect_uri="mock_uri")
    conn.token = "mock_token"
    return conn

def test_get_auth_url(spotify_conn):
    url = spotify_conn.get_auth_url(state="test_state")
    assert "https://accounts.spotify.com/authorize" in url
    assert "client_id=mock_id" in url
    assert "state=test_state" in url

@responses.activate
def test_get_token_from_code(spotify_conn):
    responses.add(
        responses.POST,
        "https://accounts.spotify.com/api/token",
        json={"access_token": "new_mock_token"},
        status=200
    )
    token = spotify_conn.get_token_from_code("some_code")
    assert token == "new_mock_token"
    assert spotify_conn.token == "new_mock_token"

@responses.activate
def test_get_user_profile(spotify_conn):
    responses.add(
        responses.GET,
        "https://api.spotify.com/v1/me",
        json={"id": "user123"},
        status=200
    )
    user = spotify_conn.get_user_profile()
    assert user["id"] == "user123"

@responses.activate
def test_get_user_profile_no_token(spotify_conn):
    spotify_conn.token = ""
    responses.add(
        responses.GET,
        "https://api.spotify.com/v1/me",
        json={"error": "unauthorized"},
        status=401
    )
    with pytest.raises(Exception):
        spotify_conn.get_user_profile()

@responses.activate
def test_create_playlist(spotify_conn):
    responses.add(
        responses.POST,
        "https://api.spotify.com/v1/users/user123/playlists",
        json={"id": "pl1", "external_urls": {"spotify": "url"}},
        status=201
    )
    responses.add(
        responses.POST,
        "https://api.spotify.com/v1/playlists/pl1/tracks",
        json={"snapshot_id": "snap1"},
        status=201
    )
    result = spotify_conn.create_playlist("user123", "Run", ["uri1", "uri2"])
    assert result["id"] == "pl1"

@responses.activate
def test_create_playlist_no_token(spotify_conn):
    spotify_conn.token = ""
    responses.add(
        responses.POST,
        "https://api.spotify.com/v1/users/user123/playlists",
        json={"error": "unauthorized"},
        status=401
    )
    with pytest.raises(Exception):
        spotify_conn.create_playlist("user123", "Run", [])

def test_check_health_exception(spotify_conn):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://api.spotify.com/v1/browse/new-releases?limit=1",
            body=Exception("Network error")
        )
        assert spotify_conn.check_health() is False

@responses.activate
def test_search_tracks_auth_fallback(spotify_conn):
    # Test token fetching if empty
    spotify_conn.token = ""
    responses.add(
        responses.POST,
        "https://accounts.spotify.com/api/token",
        json={"access_token": "client_token"},
        status=200
    )
    responses.add(
        responses.GET,
        "https://api.spotify.com/v1/search",
        json={"tracks": {"items": []}},
        status=200
    )
    res = spotify_conn.search_tracks(seed_genres=["rock"])
    assert res["tracks"] == []
    assert spotify_conn.token == "client_token"
