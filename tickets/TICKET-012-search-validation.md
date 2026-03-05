# TICKET-012: Playlist Validation & Search Accuracy

## Description

Improve the accuracy of generated playlists by ensuring that the results strictly (or more closely) match the user's specified artists and genres. Also, provide clear validation and feedback if Spotify cannot find enough tracks to fill the requested run duration.

## Acceptance Criteria

- [ ] `SpotifyConnector.search_tracks` updated to try strict filtering for artists first.
- [ ] Post-search validation in the backend to check if the returned tracks actually match the requested artist names.
- [ ] Logic to handle "partial matches" or "no matches" and inform the user via the UI.
- [ ] `PlaylistGenerator` updated to report if it couldn't reach the target duration and why.
- [ ] Frontend updated to show a helpful message (e.g., "We found some tracks for Linkin Park, but not enough to fill a 5km run at your pace. Here is a partial list.") instead of just a broken 1-song playlist.

## Technical Details

- If `artists` are provided, verify the `artist` field in the response items.
- If results are < 5, try a broader search (e.g., just genres) but flag it to the user.
- Ensure the search query `artist:"Name"` is used correctly for strictness.
