document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('playlistForm');
    const tracksList = document.getElementById('tracks-list');
    const bpmVal = document.getElementById('bpm-val');
    const visualizer = document.getElementById('visualizer');
    const paceInput = document.getElementById('pace');
    const widgetContainer = document.getElementById('spotify-widget-container');
    const embedContainer = document.getElementById('spotify-embed');
    const userStatus = document.getElementById('user-status');
    const heroSection = document.getElementById('hero-section');

    let currentPlaylistUris = [];

    async function checkAuth() {
        try {
            const resp = await fetch('/api/user');
            const user = await resp.json();
            if (user.authenticated) {
                userStatus.innerHTML = `
                    <span style="color: var(--text-dim); margin-right: 1rem;">Logged in as <strong>${user.display_name}</strong></span>
                    <a href="/logout" style="color: var(--accent-pink); font-size: 0.8rem;">Logout</a>
                `;
            }
        } catch (err) {
            console.error('Auth check failed', err);
        }
    }

    checkAuth();

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
        const genre = document.getElementById('genre').value;
        const artists = document.getElementById('artists').value;
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
            const genresArr = genre ? genre.split(',').map(s => s.trim().toLowerCase().replace(/\s+/g, '-')) : [];
            const artistsArr = artists ? artists.split(',').map(s => s.trim()) : [];

            const response = await fetch('/api/recommendations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    pace: pace,
                    genres: genresArr,
                    artists: artistsArr,
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
        const { bpm_range, playlist, warning, total_matches } = data;

        if (heroSection) heroSection.style.display = 'none';

        bpmVal.innerText = bpm_range.optimal;
        currentPlaylistUris = playlist.tracks.map(t => t.uri);

        // Update Spotify Widget
        const tracks = playlist.tracks;
        if (tracks && tracks.length > 0) {
            // Use the first track as a preview since 'trackset' is deprecated/404
            const firstTrackId = tracks[0].id;
            const embedUrl = `https://open.spotify.com/embed/track/${firstTrackId}`;
            embedContainer.innerHTML = `
                <div style="margin-bottom: 0.8rem; text-align: center; background: rgba(29, 185, 84, 0.1); padding: 0.5rem; border-radius: 8px; border: 1px solid rgba(29, 185, 84, 0.3);">
                    <p style="color: var(--spotify-green); font-size: 0.85rem; font-weight: 600; margin: 0;">🔥 Found ${total_matches} tracks matching your taste and pace!</p>
                </div>
                <div style="margin-bottom: 0.5rem; text-align: center;">
                    <span style="color: var(--text-dim); font-size: 0.75rem;">Previewing first track</span>
                </div>
                <iframe src="${embedUrl}" width="100%" height="200" frameborder="0" allowtransparency="true" allow="encrypted-media" style="border-radius: 12px; border: none; box-shadow: 0 4px 15px rgba(0,0,0,0.3);"></iframe>
                <div style="display: flex; gap: 1rem; margin-top: 1rem;">
                    <button type="button" id="btn-save-playlist" class="btn-generate" style="flex: 1; background: var(--spotify-green); color: black;">Save To Spotify</button>
                    <button type="button" id="btn-regenerate" class="btn-generate" style="flex: 1; background: transparent; border: 1px solid var(--accent-orange); color: var(--accent-orange);">Regenerate</button>
                </div>
            `;
            widgetContainer.style.display = 'block';

            document.getElementById('btn-save-playlist').addEventListener('click', savePlaylist);
            document.getElementById('btn-regenerate').addEventListener('click', (e) => {
                e.preventDefault();
                form.dispatchEvent(new Event('submit'));
            });
        } else {
            widgetContainer.style.display = 'none';
        }

        const warningHtml = warning ? `
            <div style="background: rgba(255, 107, 107, 0.1); border-left: 4px solid var(--accent-pink); padding: 1rem; margin-bottom: 2rem; border-radius: 4px;">
                <p style="color: var(--accent-pink); margin: 0; font-size: 0.9rem;"><strong>Note:</strong> ${warning}</p>
            </div>
        ` : '';

        let html = `
            ${warningHtml}
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

    async function savePlaylist(e) {
        if (e) e.preventDefault();
        const btn = document.getElementById('btn-save-playlist');
        const originalText = btn.innerText;
        btn.innerText = 'Saving...';
        btn.disabled = true;

        try {
            const pace = document.getElementById('pace').value;
            const resp = await fetch('/api/playlist/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    uris: currentPlaylistUris,
                    name: `Run @ ${pace} min/km`
                })
            });

            const data = await resp.json();
            if (data.success) {
                btn.innerText = 'Playlist Saved!';
                btn.style.background = '#333';
                btn.style.color = 'white';

                // Extract playlist ID from URL (e.g., https://open.spotify.com/playlist/7Abc123...)
                const playlistUrl = data.playlist_url;
                const playlistId = playlistUrl.split('/').pop();

                // Update embed to show the FULL newly created playlist
                const fullEmbedUrl = `https://open.spotify.com/embed/playlist/${playlistId}`;
                embedContainer.innerHTML = `
                    <p style="color: var(--spotify-green); font-size: 0.9rem; margin-bottom: 0.5rem; text-align: center; font-weight: bold;">✓ Live in your Spotify!</p>
                    <iframe src="${fullEmbedUrl}" width="100%" height="450" frameborder="0" allowtransparency="true" allow="encrypted-media" style="border-radius: 12px; border: none; box-shadow: 0 10px 30px rgba(0,0,0,0.5);"></iframe>
                    <a href="${playlistUrl}" target="_blank" class="btn-generate" style="display: block; text-align: center; margin-top: 1rem; background: #191414; color: white; text-decoration: none;">Open in App</a>
                `;
            } else {
                if (resp.status === 401) {
                    window.location.href = '/login';
                } else {
                    alert('Error: ' + data.error);
                    btn.innerText = originalText;
                    btn.disabled = false;
                }
            }
        } catch (err) {
            alert('Failed to save: ' + err.message);
            btn.innerText = originalText;
            btn.disabled = false;
        }
    }
});
