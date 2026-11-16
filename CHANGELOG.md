# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html), as described in the
README's Versioning section.

## [Unreleased]

## [0.1.0] - 2026-11-15

First versioned release, covering the work done since March 2026.

### Added
- `CHANGELOG.md`, `CLAUDE.md` and a Versioning section in the README.
- Web UI (`index.html`) for building routines visually: exercise search with
  muscle group and equipment filters, rep-based and timed sets, set types,
  supersets, reordering, JSON save and load, and a draft kept in `localStorage`.
- `serve` command: serves the web UI locally and proxies `POST /proxy/routines`
  to the Hevy API with the API key added server-side.
- `build-ui` command: bakes the exercise cache into the web UI for offline use.
- `create-routine --verify`: fetches the created routine back and checks every
  exercise, set, rep, duration and weight against the workout JSON.
- Example workouts in `examples/`; personal workouts in `workouts/`.
- `refresh-cache`, `list-exercises` and `create-routine` (with `--dry-run`), with
  fuzzy exercise name matching and lb-to-kg conversion.

### Fixed
- Request logging in `serve` no longer crashes on Python 3.14.
- `serve` and `build-ui` are wired into the command line.
- Routine creation reads the Hevy API's response correctly.
- Exercise names in the workouts match Hevy's catalog.

[Unreleased]: https://github.com/thebruge/hevy-workout-creator/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/thebruge/hevy-workout-creator/releases/tag/v0.1.0
