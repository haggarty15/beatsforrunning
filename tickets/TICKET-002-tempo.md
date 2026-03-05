# TICKET-002: Pace to BPM Algorithm

## Description

Convert a running pace (e.g. 5:30 min/km or min/mi) into a target BPM range perfectly fitted to standard running strides (usually 150-180 SPM or steps per minute). Provide configurations to bias towards higher/lower cadences.

## Acceptance Criteria

- [x] function `calculate_target_bpm(pace, unit)` implemented
- [x] Provides valid boundaries (+/- 5 BPM buffer) for Spotify API querying
- [x] BDD tests passing
