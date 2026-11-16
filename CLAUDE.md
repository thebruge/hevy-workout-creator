# hevy-workout-creator

Creates routines in the [Hevy](https://hevyapp.com) workout app through its v1
API, from workout JSON files (`hevy.py`) or a visual builder (`index.html`).
`README.md` covers setup, every command and the workout JSON format; read it
before changing behaviour.

## Layout

- `hevy.py`: the whole CLI (`refresh-cache`, `list-exercises`, `create-routine`,
  `serve`, `build-ui`), using `requests` and `python-dotenv`.
- `index.html`: the web UI, a single file with its own CSS and JavaScript.
- `examples/`: example workouts that the README refers to. `workouts/`: my own
  workouts.
- `.env` (from `env.example`) holds `HEVY_API_KEY`, and `exercise_cache.json`
  is Hevy's exercise catalog. Both are gitignored; never commit them or print
  the key.

## Things to know

- Hevy stores weights in kg. Workout JSON may use `weight_lb`, which `hevy.py`
  converts; keep that conversion in one place.
- `serve` keeps the API key on the server and adds it when proxying to Hevy. Don't
  move the key into the page.
- `index.html` is a template: `build-ui` replaces its
  `/* __EXERCISE_CACHE_PLACEHOLDER__ */` line with the exercise cache and writes
  the result to `hevy_ui.html` (gitignored) or `--output`. It refuses to write
  over `index.html`. Keep the placeholder line, and never commit a baked
  `index.html` (one was committed by mistake on 2026-03-25 and broke `build-ui`).
- The README's setup line mentions `requirements.txt`, which doesn't exist yet;
  the dependencies are `requests` and `python-dotenv`.
- `create-routine` without `--dry-run` creates a real routine in my Hevy account.
  Use `--dry-run` to check changes, and ask before creating anything.
- In the sandbox, `pip install` needs `--use-deprecated=legacy-certs --cert
  /etc/ssl/cert.pem`, the Hevy API host must be allowed, and `serve` can't bind a
  port (ask me to run it with `!`).

## Changes, versions and releases

- Commits use Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`).
- Add each user-visible change under `## [Unreleased]` in `CHANGELOG.md` in the
  same commit.
- To release, follow the README's Versioning section: move the Unreleased
  entries under a new dated version, update the compare links at the bottom,
  commit as `chore(release): vX.Y.Z`, and tag `vX.Y.Z`.
- Keep the README in step when commands, flags or the JSON format change.
