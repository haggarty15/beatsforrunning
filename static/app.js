document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('playlistForm');
    const resultsDiv = document.getElementById('playlistResults');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const pace = document.getElementById('pace').value;
        const artist = document.getElementById('artist').value;
        const genre = document.getElementById('genre').value || 'rock';

        resultsDiv.innerHTML = '<p>Generating your perfect run...</p>';

        try {
            const response = await fetch('/api/recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    pace: pace,
                    genres: [genre],
                    distance: 5.0, // Default for now
                    unit: 'km'
                })
            });

            const data = await response.json();

            if (data.error) {
                resultsDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
                return;
            }

            renderPlaylist(data);
        } catch (err) {
            resultsDiv.innerHTML = `<p style="color: red;">Error: ${err.message}</p>`;
        }
    });

    function renderPlaylist(data) {
        const { bpm_range, playlist } = data;

        let html = `
            <div class="playlist">
                <h3>Your Run (${bpm_range.optimal} BPM)</h3>
                <p>Target Pace: ${playlist.target_duration_ms / 60000} mins for 5km</p>
                <ul>
        `;

        playlist.tracks.forEach(track => {
            html += `
                <li class="song">
                    <strong>${track.name}</strong> by ${track.artists.join(', ')}
                </li>
            `;
        });

        html += '</ul></div>';
        resultsDiv.innerHTML = html;
    }
});
