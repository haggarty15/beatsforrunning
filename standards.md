# BeatsForRunning - Development Standards

This document outlines the coding standards and operational rules for the BeatsForRunning project. **These rules must be reviewed and followed before executing changes.**

## Operational Rules

1. **Terminal Command Execution (PowerShell)**:
   - Always run terminal commands sequentially, one at a time.
   - **NEVER** use Unix-style command chaining (`&&`) as this project operates within a Windows PowerShell environment where this syntax will cause parser errors.

## Code Quality

1. **Pre-Commit Checks**:
   - Run `make check` prior to committing ANY code. This runs formatting (ruff), linting (ruff), type checking (mypy), and the full test suite (pytest).
   - The test pipeline enforces strict >80% coverage requirements.
   - Never push failing code to the repository.

2. **Error Handling**:
   - Always include explicit `try...except` blocks when handling external APIs (e.g., Spotify).
   - Avoid generic exceptions where possible. Return specific, user-friendly error messages down to the UI layers.
