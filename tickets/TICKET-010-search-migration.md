# TICKET-010: Migrate from Recommendations to Search API

## Description

The Spotify `v1/recommendations` endpoint has been deprecated or restricted for many new Web API applications (returning 404). To ensure reliable playlist generation, the application must migrate to using the `v1/search` endpoint combined with query-based filtering.

## Acceptance Criteria

- [ ] `SpotifyConnector` updated with a robust `search_tracks` method.
- [ ] Search query construction includes `genre:` filters and BPM keywords (e.g., "160 bpm").
- [ ] `app.py` updated to call the new search-based retrieval logic.
- [ ] Removal or deprecation of the `get_recommendations` method.
- [ ] Verification: Generated playlists contain tracks that roughly match the target genre and tempo based on search relevance.

## Technical Details

- Use the `q` parameter in `v1/search`: `genre:"rock" 160 bpm`.
- Limit search results to `track` type.
- Handle multiple genres by constructing a complex query string.
