# EPIC: Beats For Running - Pace-Based Running Playlists

> **Project:** BeatsForRunning
> **Status:** 🚧 In Development
> **Last Updated:** 2026-03-05
> **Tickets:** 0/5 total

---

## Vision

BeatsForRunning generates running playlists tailored to an athlete's physical exertion and personal music taste. By combining music preferences (artist, genre) with running pace, the app algorithmically builds an audio journey. The user's pace is mapped to a target BPM (Beats Per Minute) range, ensuring the tempo of the music matches their stride and performance goals.

---

## Problem Statement

Runners often struggle to find music that consistently matches their stride and running pace. Manual curation is tedious, and generic running playlists do not cater to personal music preferences. There is no simple tool that allows a runner to say "I am running at a 5:30/km pace and want to listen to Indie Rock", and instantly receive a curated playlist perfectly matched with their target BPM.

---

## Goals

| # | Goal |
| :--- | :--- |
| G1 | User can input their target running pace (e.g. min/km or min/mi). |
| G2 | User can specify music preferences (favorite artists or genres). |
| G3 | The system calculates a target BPM range based on the inputted running pace. |
| G4 | The system queries external music APIs (e.g. Spotify) to find songs matching the genre/artist and BPM range. |
| G5 | The system constructs a continuous playlist and provides it/saves it to the user's account. |

## Non-Goals (MVP)

- Complex workout intervals (e.g. varying pace throughout the run). (To be done in v2)
- Heart rate monitor integration.

---

## Architecture Decisions (ADRs)

| ADR | Decision | Rationale |
| :--- | :--- | :--- |
| ADR-1 | Python backend, direct API connection | Flask application provides the easiest way to bridge the Spotify API and simple UI. |
| ADR-2 | `requests` for API calls | Straightforward HTTP interaction. |
| ADR-3 | `pytest` + `ruff` + `mypy` | Ensures high code quality, typing confidence, and fast testing. |

---

## Ticket Index

<a name="ticket-001"></a>
<a name="ticket-002"></a>
<a name="ticket-003"></a>
<a name="ticket-004"></a>
<a name="ticket-005"></a>
<a name="ticket-006"></a>

| ID | Title | Priority | Status | Source/Notes | BDD Feature |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [TICKET-001](#ticket-001) | Backend Scaffold & Setup | P0-Critical | ✅ Done | `Makefile`, `pyproject` | - |
| [TICKET-002](#ticket-002) | Pace to BPM Algorithm | P0-Critical | ✅ Done | `core/tempo.py` | `TICKET-002-tempo.feature` |
| [TICKET-003](#ticket-003) | Spotify Integration | P0-Critical | ✅ Done | `connectors/spotify.py` | `TICKET-003-spotify.feature` |
| [TICKET-004](#ticket-004) | Playlist Assembly Logic | P0-Critical | ✅ Done | `core/playlist.py` | `TICKET-004-assembly.feature` |
| [TICKET-005](#ticket-005) | Web Interface (Flask UI) | P1-High | ✅ Done | `app.py`, `static/` | `TICKET-005-ui.feature` |
| [TICKET-006](#ticket-006) | UI Redesign & Premium Aesthetics | P1-High | ✅ Done | `index.html`, `static/` | `TICKET-006-ui-v2.feature` |

---

## Repository Structure

```text
beatsforrunning/
├── EPIC.md                          ← this file
├── Makefile
├── pyproject.toml
├── requirements.txt
├── .github/
│   └── workflows/
├── client.py
├── main.py
├── tickets/
└── tests/
```
