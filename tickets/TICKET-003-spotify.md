# TICKET-003: Spotify Integration

## Description

Create a connector to search and retrieve songs from Spotify that match a given genre/artist and fall within a specific BPM range natively.

## Acceptance Criteria

- [x] `connectors/spotify.py` implements a search function
- [x] Connects to Spotify using standard Client Credentials or provides a mockable interface for testing.
- [x] Incorporates `min_tempo` and `max_tempo` in the track search.
- [x] BDD tests passing
