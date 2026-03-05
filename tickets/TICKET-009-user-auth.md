# TICKET-009: Spotify User Authentication (OAuth2)

## Description

Migrate the application from "Client Credentials Flow" to "Authorization Code Flow" to restore access to restricted Spotify API endpoints (Recommendations, Audio Features) and enable user-specific features like creating playlists directly in their accounts.

## Acceptance Criteria

- [ ] Implementation of `/login` route to redirect users to Spotify Accounts service
- [ ] Implementation of `/callback` route to handle the OAuth2 dance and store `access_token` in session
- [ ] UI updated with a "Connect Spotify" button or user profile indicator
- [ ] Backend logic updated to use the User Access Token for API calls
- [ ] Ability to "Save to Spotify" for the generated running playlist
- [ ] Secure session management for tokens

## Technical Details

- Use Flask Session for token storage.
- Scopes required: `user-read-private`, `playlist-modify-public`, `playlist-modify-private`.
- Update `SpotifyConnector` to support authorization codes.
