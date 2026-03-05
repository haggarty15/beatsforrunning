# TICKET-014: Graceful Handling of Invalid Music Inputs

## Description

If a user inputs a non-existent genre or artist, the app currently might return a generic "No tracks found" message. This ticket introduces a "Search Diagnostic" step to distinguish between "No matches for this BPM" and "This genre/artist doesn't exist on Spotify," providing more helpful feedback.

## Acceptance Criteria

- [ ] `SpotifyConnector.search_tracks` updated to return detailed metadata about the search attempt.
- [ ] Backend logic updated to perform a "Diagnostic Search" (ignoring BPM) if the primary search returns zero results.
- [ ] UI updated to show specific error messages:
  - *"We found [Artist], but none of their songs match your target tempo of [BPM]."*
  - *"We couldn't find any record of '[Genre]' on Spotify. Please check the spelling or try another style."*
- [ ] Validation: Entering "keyboard-noises" as a genre should inform the user it wasn't found, while "Linkin Park" at a very slow pace should inform them the BPM was the issue.

## Technical Details

- If `tracks` is empty, run a second search without `target_bpm`.
- If the second search is still empty, the seed terms (Genre/Artist) are invalid.
- If the second search has tracks, the tempo filter was the problem.
