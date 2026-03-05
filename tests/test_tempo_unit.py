import pytest
from beatsforrunning.core.tempo import calculate_target_bpm

def test_tempo_invalid_str():
    with pytest.raises(ValueError, match="Invalid pace format"):
        calculate_target_bpm("invalid_pace")

def test_tempo_float():
    result = calculate_target_bpm(5.5)
    assert "optimal" in result

def test_tempo_negative():
    with pytest.raises(ValueError, match="Pace must be > 0."):
        calculate_target_bpm(-5.0)

def test_tempo_invalid_unit():
    with pytest.raises(ValueError, match="Unknown unit"):
        calculate_target_bpm("5:00", unit="invalid")

def test_tempo_preference_low():
    result_normal = calculate_target_bpm("5:00", preference="normal")
    result_low = calculate_target_bpm("5:00", preference="low")
    assert result_low["optimal"] < result_normal["optimal"]
