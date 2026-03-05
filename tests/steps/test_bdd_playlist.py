import pytest
from pytest_bdd import scenario, given, when, then, parsers
from beatsforrunning.core.playlist import PlaylistGenerator

@scenario('../features/TICKET-004-assembly.feature', 'Calculate total duration for a 5km run at 6:00 pace')
def test_calc_duration():
    pass

@scenario('../features/TICKET-004-assembly.feature', 'Assemble tracks to fill a 10 minute requirement')
def test_assemble_playlist():
    pass

@pytest.fixture
def context():
    return {}

@given(parsers.parse('a distance of {dist:f} "{unit}"'))
def distance_step(context, dist, unit):
    context['distance'] = dist
    context['unit'] = unit

@given(parsers.parse('a pace of "{pace}"'))
def pace_step(context, pace):
    context['pace'] = pace

@when('I calculate the duration')
def calc_dur_step(context):
    context['gen'] = PlaylistGenerator(context['distance'], context['pace'], context['unit'])

@then(parsers.parse('the raw duration should be {expected:d} seconds'))
def check_duration(context, expected):
    assert context['gen'].total_seconds == expected

@given(parsers.parse('a target duration of {seconds:d} seconds'))
def target_dur(context, seconds):
    context['target_seconds'] = seconds

@given(parsers.parse('a pool of tracks each {sec:d} seconds long'))
def pool_tracks(context, sec):
    # Create enough tracks to potentially fill more than needed
    context['pool'] = [
        {"id": str(i), "name": f"Track {i}", "duration_ms": sec * 1000}
        for i in range(10)
    ]

@when('I assemble the playlist')
def assemble_step(context):
    # Note: playlist generator normally calculates duration from distance/pace
    # For this test, we can mock the duration or just use a dummy distance/pace that results in the target
    # 600 seconds = 1km at 10:00 pace
    gen = PlaylistGenerator(1.0, f"{context['target_seconds']//60}:00", "km")
    context['result'] = gen.assemble_playlist(context['pool'])

@then(parsers.parse('I should have {count:d} tracks in the playlist'))
def check_count(context, count):
    assert context['result']['count'] == count

@then(parsers.parse('the playlist duration should be {expected:d} seconds'))
def check_result_duration(context, expected):
    assert context['result']['total_duration_ms'] == expected * 1000
