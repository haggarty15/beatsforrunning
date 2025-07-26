# RunBeats

RunBeats is a simple demo web app that generates running playlists based on your favourite artists, genres and running pace. The interface is written in plain HTML/JavaScript and the backend exposes a few Spotify helper endpoints using Flask.

## Features

- Lightweight single‑page UI with modern styling and navigation.
- Form to collect favourite artists, genres, pace and distance.
- Playlist generator that pulls tracks from Spotify matching your pace.
- Placeholder sections for future social and Strava integration.

## Getting Started

1. Install dependencies:
   ```bash
   pip install Flask python-dotenv requests
   ```
2. Create a `.env` file with your Spotify API credentials:
   ```
   CLIENT_ID=your_spotify_client_id
   CLIENT_SECRET=your_spotify_client_secret
   ```
3. Run the Flask server:
   ```bash
   python spotify/client.py
   ```
4. Open `index.html` in your browser and start generating playlists.
   The page will request song suggestions from the Flask server which queries
   the Spotify API using your credentials.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
