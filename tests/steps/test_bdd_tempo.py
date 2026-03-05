from pytest_bdd import scenario, given, when, then, parsers
import pytest
from beatsforrunning.core.tempo import calculate_target_bpm


@scenario(
    "../features/TICKET-002-tempo.feature", "Calculate BPM for 5:30 min/km pace with normal cadence"
)
def test_tempo_1():
    pass


@scenario(
    "../features/TICKET-002-tempo.feature", "Calculate BPM for 8:00 min/mi pace with high cadence"
)
def test_tempo_2():
    pass


@scenario("../features/TICKET-002-tempo.feature", "Calculate BPM bounded by realistic ranges")
def test_tempo_3():
    pass


@scenario("../features/TICKET-002-tempo.feature", "Calculate BPM for slow walking pace")
def test_tempo_4():
    pass


@pytest.fixture
def context():
    return {}


@given(parsers.parse('a pace of "{pace}" "{unit}"'))
def pace_step(context, pace, unit):
    context["pace"] = pace
    context["unit"] = unit


@given('a cadence preference of "normal"')
def cadence_normal(context):
    context["preference"] = "normal"


@given('a cadence preference of "high"')
def cadence_high(context):
    context["preference"] = "high"


@when("I calculate the target BPM")
def calculate_bpm(context):
    preference = context.get("preference", "normal")
    context["result"] = calculate_target_bpm(context["pace"], context["unit"], preference)


@then(parsers.parse("the optimal BPM should be roughly {expected:d}"))
def optimal_bpm_roughly(context, expected):
    optimal = context["result"]["optimal"]
    assert abs(optimal - expected) <= 2, f"Expected ~{expected}, got {optimal}"


@then("the lower bound should be 5 less than optimal")
def lower_bound(context):
    res = context["result"]
    assert res["lower"] == res["optimal"] - 5


@then("the upper bound should be 5 more than optimal")
def upper_bound(context):
    res = context["result"]
    assert res["upper"] == res["optimal"] + 5


@then(parsers.parse("the optimal BPM should not exceed {max_bpm:d}"))
def max_bound(context, max_bpm):
    assert context["result"]["optimal"] <= max_bpm


@then(parsers.parse("the optimal BPM should not be less than {min_bpm:d}"))
def min_bound(context, min_bpm):
    assert context["result"]["optimal"] >= min_bpm
