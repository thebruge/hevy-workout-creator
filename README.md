# hevy-tool

Automate routine creation in the Hevy app via the v1 API.

## Setup

```bash
pip install requests
export HEVY_API_KEY="your_key_here"   # from https://hevy.com/settings?developer
```

## Workflow

### 1. Build the local exercise cache (do once, re-run if exercises seem missing)

```bash
python hevy.py refresh-cache
```

Downloads all exercise templates from Hevy's catalog into `exercise_cache.json`.
Required before any other commands.

### 2. Find correct exercise names

Your workout JSON must use names that match Hevy's catalog. Search the cache:

```bash
python hevy.py list-exercises --search "kettlebell"
python hevy.py list-exercises --search "plank"
python hevy.py list-exercises --search "deadlift"
```

The tool does fuzzy matching, so close-but-not-exact names will still resolve
with a warning. But it's better to use exact names in your JSON.

### 3. Dry-run to verify resolution

```bash
python hevy.py create-routine --file full_body_strength.json --dry-run
```

Prints the exercise → template_id resolution table and the full JSON payload
without sending anything to the API. Use this to confirm everything resolves
correctly before committing.

### 4. Create the routine

```bash
python hevy.py create-routine --file full_body_strength.json
```

## Workout JSON Format

```json
{
  "title": "My Workout",
  "notes": "Optional workout-level notes",
  "exercises": [
    {
      "name": "Exact Exercise Name From Hevy Catalog",
      "rest_seconds": 90,
      "notes": "Optional per-exercise notes",
      "sets": [
        { "duration_seconds": 60, "weight_lb": 25 },
        { "duration_seconds": 45, "weight_lb": 25 },
        { "reps": 12, "weight_lb": 135 }
      ]
    }
  ]
}
```

### Set fields

| Field              | Type    | Notes                                         |
|--------------------|---------|-----------------------------------------------|
| `duration_seconds` | int     | Use for timed sets; mutually exclusive w/ reps |
| `reps`             | int     | Use for rep-based sets                         |
| `weight_lb`        | float   | Converted to kg automatically                  |
| `weight_kg`        | float   | Used directly if present (overrides weight_lb) |
| `type`             | string  | `"normal"` (default) / `"warmup"` / `"dropset"` |

Bodyweight exercises: omit both weight fields (or set to 0).

## Notes on the Hevy API

- Requires **Hevy Pro** subscription for API access
- Weights are stored and sent in **kg** — this tool converts from lb automatically
- `POST /v1/routines` creates a reusable routine template (what you want for
  pre-programmed workouts)
- `POST /v1/workouts` logs a completed session with timestamps (use for
  after-the-fact logging)
- Exercise names in Hevy may differ from common usage — always verify with
  `list-exercises --search` before building a new workout file
