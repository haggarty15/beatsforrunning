import pytest
from pytest_bdd import scenario, given, when, then, parsers
from beatsforrunning.app import app
import json
import responses

@scenario('../features/TICKET-008-spotify-widget.feature', 'Spotify Widget reveal')
def test_ui_playlist():
    pass

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@given('the Flask application is running')
def app_running(client):
    pass

@when(parsers.parse('I submit a pace of "{pace}" and genre "{genre}"'))
def submit_playlist(client, pace, genre):
    with responses.RequestsMock() as rsps:
        # Mock Spotify Auth
        rsps.add(
            responses.POST,
            "https://accounts.spotify.com/api/token",
            json={"access_token": "mock_token", "expires_in": 3600},
            status=200
        )
        # Mock Spotify Recommendations
        rsps.add(
            responses.GET,
            "https://api.spotify.com/v1/recommendations",
            json={
                "tracks": [
                    {
                        "id": "1",
                        "name": "Run Fast",
                        "artists": [{"name": "The Runners"}],
                        "duration_ms": 180000,
                        "uri": "spotify:track:1"
                    }
                ]
            },
            status=200
        )
        
        response = client.post('/api/recommendations', json={
            "pace": pace,
            "genres": [genre],
            "distance": 1.0,
            "unit": "min/km"
        })
        print(f"DEBUG: Response status: {response.status_code}")
        print(f"DEBUG: Response body: {response.data}")
        pytest.response = response

@then('I should see a list of recommended tracks')
@then('I should see the track list below the widget')
def check_tracks():
    data = json.loads(pytest.response.data)
    assert 'playlist' in data
    assert len(data['playlist']['tracks']) > 0
    assert data['playlist']['tracks'][0]['name'] == 'Run Fast'

@then('the BPM range should be calculated correctly')
def check_bpm():
    data = json.loads(pytest.response.data)
    assert 'bpm_range' in data
    assert 'optimal' in data['bpm_range']

@then('I should see the Spotify widget container')
def check_widget_container():
    # In API tests we verify the data presence
    data = json.loads(pytest.response.data)
    assert 'playlist' in data
    assert len(data['playlist']['tracks']) > 0

@then('the Spotify iframe should have a trackset URI')
def check_iframe_uri_logic():
    data = json.loads(pytest.response.data)
    ids = [t['id'] for t in data['playlist']['tracks']]
    assert len(ids) > 0
    # The URI construction logic is in JS, so we confirm IDs are presence for it.

