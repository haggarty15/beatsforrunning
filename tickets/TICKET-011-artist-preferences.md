# TICKET-011: Expand Music Preferences (Artists & Genres)

## Description

Enhance the Music Preferences section to allow users to specify a list of artists in addition to (or instead of) genres. This will provide more personalized running playlists.

## Acceptance Criteria

- [ ] UI updated in `index.html` to include an "Artists" input field (comma-separated).
- [ ] Frontend logic in `app.js` updated to capture and send the `artists` list to the backend.
- [ ] Backend logic in `app.py` updated to handle the `artists` parameter.
- [ ] `SpotifyConnector.search_tracks` updated to incorporate artist names into the search query for better results.
- [ ] Verification: Generated playlists contain tracks from the specified artists or related styles.

## Technical Details

- Use the `artist:` filter in Spotify Search API: `artist:"Artist Name" genre:"rock" 160 bpm`.
- Handle cases where only genres, only artists, or both are provided.
- Update the visual layout to accommodate the new input field while maintaining premium aesthetics.
