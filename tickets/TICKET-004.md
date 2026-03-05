# TICKET-004: Playlist Assembly Logic

## Description

Calculate the required playlist length based on target distance and pace. Assemble tracks from Spotify into a coherent object that can be converted into a Spotify playlist.

## Acceptance Criteria

- [x] `core/playlist.py` implemented
- [x] Logic for calculating total duration needed (distance * pace) implemented
- [x] Logic for selecting enough tracks to fill that duration implemented
- [x] BDD tests passing
