document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('playlistForm');
    const tracksList = document.getElementById('tracks-list');
    const bpmVal = document.getElementById('bpm-val');
    const visualizer = document.getElementById('visualizer');
    const paceInput = document.getElementById('pace');
    const widgetContainer = document.getElementById('spotify-widget-container');
    const embedContainer = document.getElementById('spotify-embed');

    // Initialize visualizer bars
    for (let i = 0; i < 30; i++) {
        const bar = document.createElement('div');
        bar.className = 'bar';
        visualizer.appendChild(bar);
    }

    function updateVisualizer(active = false) {
        const bars = visualizer.querySelectorAll('.bar');
        bars.forEach(bar => {
            if (active) {
                const height = 10 + Math.random() * 40;
                bar.style.height = `${height}px`;
                bar.style.opacity = '1';
                bar.style.background = 'var(--accent-orange)';
            } else {
                bar.style.height = '10px';
                bar.style.opacity = '0.5';
                bar.style.background = 'var(--accent-pink)';
            }
        });
    }

    paceInput.addEventListener('input', (e) => {
        const val = e.target.value;
        if (/^\d+:\d{2}$/.test(val)) {
            const [m, s] = val.split(':').map(Number);
            const decPace = m + (s / 60);
            const speedKmh = 60 / decPace;
            const bpm = Math.round(130 + (speedKmh * 3));
            bpmVal.innerText = bpm;
            updateVisualizer(true);
        } else {
            bpmVal.innerText = '--';
            updateVisualizer(false);
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const pace = paceInput.value;
        const genre = document.getElementById('genre').value || 'rock';
        const distance = document.getElementById('distance').value;

        widgetContainer.style.display = 'none';
        tracksList.innerHTML = `
            <div style="text-align: center; margin-top: 4rem;">
                <div class="visualizer-container">
                    <div class="bar" style="animation: pulse 1s infinite"></div>
                </div>
                <p>Building your rhythm...</p>
            </div>
        `;

        try {
            const response = await fetch('/api/recommendations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    pace: pace,
                    genres: genre.split(',').map(s => s.trim().toLowerCase().replace(/\s+/g, '-')),
                    distance: parseFloat(distance),
                    unit: 'min/km'
                })
            });

            const data = await response.json();

            if (data.error) {
                tracksList.innerHTML = `<p style="color: var(--accent-pink); padding: 2rem;">Error: ${data.error}</p>`;
                return;
            }

            renderPlaylist(data);
        } catch (err) {
            tracksList.innerHTML = `<p style="color: var(--accent-pink); padding: 2rem;">Error: ${err.message}</p>`;
        }
    });

    function renderPlaylist(data) {
        const { bpm_range, playlist } = data;

        bpmVal.innerText = bpm_range.optimal;

        // Update Spotify Widget
        const ids = playlist.tracks.map(t => t.id).join(',');
        if (ids) {
            const embedUrl = `https://open.spotify.com/embed/trackset/MyRun/${ids}`;
            embedContainer.innerHTML = `
                <iframe src="${embedUrl}" width="100%" height="450" frameborder="0" allowtransparency="true" allow="encrypted-media" style="border-radius: 12px; border: none; box-shadow: 0 10px 30px rgba(0,0,0,0.5);"></iframe>
            `;
            widgetContainer.style.display = 'block';
        } else {
            widgetContainer.style.display = 'none';
        }

        let html = `
            <div style="margin-bottom: 2rem;">
                <h2 style="font-size: 1.8rem; margin-bottom: 0.5rem;">Your Running Journey</h2>
                <p style="color: var(--text-dim)">${playlist.count} tracks curated for a ${playlist.target_duration_ms / 60000} minute run.</p>
            </div>
        `;

        playlist.tracks.forEach(track => {
            html += `
                <div class="track-card">
                    <div class="track-art">🎵</div>
                    <div class="track-info">
                        <div class="track-name">${track.name}</div>
                        <div class="track-artist">${track.artists.join(', ')}</div>
                    </div>
                    <a href="${track.uri}" class="track-uri">Open in Spotify</a>
                </div>
            `;
        });

        tracksList.innerHTML = html;
        updateVisualizer(true);
    }
});
