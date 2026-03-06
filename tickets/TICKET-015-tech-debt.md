# TICKET-015: Tech Debt — Security, Logging, and Code Quality

## Description

Address accumulated tech debt identified in codebase review. Covers a weak secret key default, a playlist search loop bug, missing structured logging, a hardcoded port, a stale Dockerfile reference, and minor code quality issues.

## Acceptance Criteria

- [ ] `app.py`: Raise `ValueError` at startup if `SECRET_KEY` env var is not set — remove weak hardcoded fallback.
- [ ] `spotify.py`: Move the `p_resp = requests.get(...)` call inside the `for tempo in search_tempos` loop so all tempos are searched, not just the last one.
- [ ] `app.py`: Replace all `print()` debug statements with `logging` calls at appropriate levels (`logging.info`, `logging.warning`, `logging.error`).
- [ ] `app.py`: Read port from `$PORT` env var — `port = int(os.getenv("PORT", 5000))`.
- [ ] `spotify.py`: Move `import random` to module level (top of file).
- [ ] `Dockerfile`: Remove references to `social.html` and `strava.html` (files don't exist).
- [ ] `.github/workflows/ci.yml`: Replace `requirements.txt` install with `pip install -e ".[dev]"` to match Makefile.
- [ ] All changes pass `make check` (format, lint, typecheck, tests) with no regressions.

## Technical Details

### Secret Key (app.py:17)
```python
# Before
app.secret_key = os.getenv("SECRET_KEY", "super-secret-running-key")

# After
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    raise ValueError("SECRET_KEY environment variable must be set")
app.secret_key = secret_key
```

### Playlist Loop Bug (spotify.py:174–177)
The `p_resp = requests.get(...)` line is currently outside the `for tempo in search_tempos` loop due to indentation — only the last iteration's params are used. Indent it inside the loop and accumulate results.

### Logging (app.py)
Add `import logging` and `logging.basicConfig(level=logging.INFO)` at module level. Replace all `print(...)` calls with appropriate `logging.*()` calls. Remove user-identifiable data (e.g. user IDs) from logs or log at `DEBUG` level.

### Port (app.py:227)
```python
# Before
app.run(debug=False, host="0.0.0.0", port=5000)

# After
port = int(os.getenv("PORT", 5000))
app.run(debug=False, host="0.0.0.0", port=port)
```

### CI Workflow (.github/workflows/ci.yml)
```yaml
# Before
- run: pip install -r requirements.txt

# After
- run: pip install -e ".[dev]"
```

## Out of Scope

- Rate limiting (separate ticket)
- Removing unused dependencies (`flask-sqlalchemy`, `flask-bcrypt`)
- Frontend JS error handling improvements
- Accessibility improvements
