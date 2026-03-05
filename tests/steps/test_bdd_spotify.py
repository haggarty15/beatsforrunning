import pytest
from pytest_bdd import scenario, given, when, then
import responses
from beatsforrunning.connectors.spotify import SpotifyConnector

@scenario('../features/TICKET-003-spotify.feature', 'Token retrieval on missing credentials')
def test_spotify_no_creds():
    pass

@scenario('../features/TICKET-003-spotify.feature', 'Health check returns true on success')
def test_spotify_health():
    pass

@scenario('../features/TICKET-003-spotify.feature', 'Fetch recommendations successfully')
def test_spotify_recommendations():
    pass

@pytest.fixture
def context():
    return {}

@given('missing Spotify credentials')
def missing_creds(context):
    context['conn'] = SpotifyConnector(client_id="", client_secret="")

@when('I retrieve the token')
def retrieve_token(context):
    try:
        context['conn'].get_token()
    except Exception as e:
        context['exception'] = e

@then('it raises a ValueError')
def raises_value_error(context):
    assert isinstance(context.get('exception'), ValueError)

@given('a mock Spotify API with a valid token')
def mock_spotify_api(context):
    context['conn'] = SpotifyConnector(client_id="dummy", client_secret="dummy")
    context['conn'].token = "valid_token"

@when('I perform a health check')
def perform_health_check(context):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://api.spotify.com/v1/browse/new-releases?limit=1",
            json={"albums": {"items": []}},
            status=200
        )
        context['health_result'] = context['conn'].check_health()

@then('the result should be true')
def check_true(context):
    assert context['health_result'] is True

@given('a genre "rock" with limits 150 to 160 BPM')
def genre_limits(context):
    context['genres'] = ["rock"]
    context['min_tempo'] = 150
    context['max_tempo'] = 160
from responses import matchers

@when('I get recommendations')
def get_recommendations(context):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://api.spotify.com/v1/recommendations?seed_genres=rock&min_tempo=150&max_tempo=160&limit=10",
            json={
                "tracks": [
                    {
                        "id": "1",
                        "name": "Song 1",
                        "artists": [{"name": "Artist 1"}],
                        "duration_ms": 200000,
                        "uri": "spotify:track:1"
                    },
                    {
                        "id": "2",
                        "name": "Song 2",
                        "artists": [{"name": "Artist 2"}],
                        "duration_ms": 210000,
                        "uri": "spotify:track:2"
                    }
                ]
            },
            status=200
        )
        context['result'] = context['conn'].get_recommendations(
            context['genres'], 
            context['min_tempo'], 
            context['max_tempo']
        )

@then('I get a list of 2 tracks matching my criteria')
def list_tracks(context):
    tracks = context.get('result', [])
    assert len(tracks) == 2
    assert tracks[0]['name'] == 'Song 1'
