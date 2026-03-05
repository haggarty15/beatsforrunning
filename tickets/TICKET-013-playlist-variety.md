# TICKET-013: Playlist Variety & Quality Weighting

## Description

Generated playlists currently return the same top search results every time for the same inputs. This ticket aims to introduce randomness (shuffling) and a weighting factor—high-energy/popularity—to ensure a fresh, high-quality running experience every time.

## Acceptance Criteria

- [ ] `SpotifyConnector.search_tracks` updated to increase the `limit` (e.g., to 50) to provide a larger pool of tracks.
- [ ] `PlaylistGenerator.assemble_playlist` updated to shuffle the pool of available tracks before selection.
- [ ] Incorporate Spotify's popularity or energy metrics (if available via Search API or a secondary lookup) to weight track selection.
- [ ] Verification: Generating a "Linkin Park" playlist twice for the same pace should result in different track sequences/selections.

## Technical Details

- Increase `search_tracks` limit to 50.
- Use `random.shuffle()` on the available pool.
- Consider adding a "Surprise Me" factor by mixing in 10-20% related but non-strict-match tracks to ensure the playlist is full.
