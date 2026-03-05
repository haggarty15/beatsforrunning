from __future__ import annotations
import re

class PlaylistGenerator:
    def __init__(self, distance: float, pace: str, unit: str = "km") -> None:
        """
        distance: float (e.g. 5.0)
        pace: str (e.g. "5:30")
        unit: str ("km" or "mi")
        """
        self.distance = distance
        self.pace_str = pace
        self.unit = unit
        self.total_seconds = self._calculate_total_duration()

    def _calculate_total_duration(self) -> int:
        match = re.match(r'^(\d+):(\d+)$', self.pace_str.strip())
        if not match:
            raise ValueError(f"Invalid pace format: {self.pace_str}")
        
        m, s = int(match.group(1)), int(match.group(2))
        pace_seconds_per_unit = (m * 60) + s
        
        return int(self.distance * pace_seconds_per_unit)

    def assemble_playlist(self, available_tracks: list[dict]) -> dict:
        """
        Filters and selects tracks to match the total duration.
        """
        selected_tracks = []
        current_duration_ms = 0
        target_duration_ms = self.total_seconds * 1000

        for track in available_tracks:
            selected_tracks.append(track)
            current_duration_ms += track["duration_ms"]
            
            if current_duration_ms >= target_duration_ms:
                break
        
        return {
            "total_duration_ms": current_duration_ms,
            "target_duration_ms": target_duration_ms,
            "tracks": selected_tracks,
            "count": len(selected_tracks)
        }
