import re

MIN_BPM = 120
MAX_BPM = 190


def calculate_target_bpm(
    pace: str | float, unit: str = "min/km", preference: str = "normal"
) -> dict[str, int]:
    """
    Calculate a target BPM range perfectly fitted to standard running strides (usually 150-180 SPM)
    based on the provided pace, unit ("min/km" or "min/mi"), and cadence preference.
    """
    # 1. Parse pace into min/km decimal
    if isinstance(pace, str):
        match = re.match(r"^(\d+):(\d+)$", pace.strip())
        if not match:
            raise ValueError(f"Invalid pace format. Expected 'MM:SS', got {pace}")
        m, s = int(match.group(1)), int(match.group(2))
        decimal_pace = m + (s / 60.0)
    else:
        decimal_pace = float(pace)

    if decimal_pace <= 0:
        raise ValueError("Pace must be > 0.")

    # 2. Convert to speed in km/h
    # if unit is min/mi, decimal_pace is in min/mi.
    # To get min/km, divide by 1.60934
    if unit == "min/mi":
        decimal_pace = decimal_pace / 1.60934
    elif unit != "min/km":
        raise ValueError(f"Unknown unit: {unit}. Use 'min/km' or 'min/mi'")

    speed_kmh = 60.0 / decimal_pace

    # 3. Base Formula: SPM = 130 + speed_kmh * 3.0
    base_bpm = 130 + (speed_kmh * 3.0)

    # 4. Apply preference bias
    bias = 0
    if preference == "high":
        bias = 5
    elif preference == "low":
        bias = -5

    optimal_bpm = int(round(base_bpm + bias))

    # 5. Cap limits
    optimal_bpm = max(MIN_BPM, min(MAX_BPM, optimal_bpm))

    # 6. +/- 5 bounds
    lower = optimal_bpm - 5
    upper = optimal_bpm + 5

    return {"lower": lower, "optimal": optimal_bpm, "upper": upper}
