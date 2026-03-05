import pytest
from beatsforrunning.core.playlist import PlaylistGenerator

def test_playlist_invalid_pace():
    with pytest.raises(ValueError, match="Invalid pace format"):
        PlaylistGenerator(5.0, "invalid_pace", "km")
