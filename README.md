# hevy-workout-creator

Automate routine creation in the [Hevy](https://hevyapp.com) workout app via the v1 API. Define your workouts in JSON and push them directly to Hevy as reusable routines.

## Setup

```bash
pip install -r requirements.txt   # or: pip install requests python-dotenv
cp env.example .env
# Edit .env and add your HEVY_API_KEY (from https://hevy.com/settings?developer)
```

> Requires a **Hevy Pro** subscription for API access.

## Workflow

### 1. Build the local exercise cache

```bash
python hevy.py refresh-cache
```

Downloads all exercise templates from Hevy's catalog into `exercise_cache.json`. Run once, and re-run if exercises seem to be missing.

### 2. Find correct exercise names

Your workout JSON must use names that match Hevy's catalog exactly (or close enough for fuzzy matching):

```bash
python hevy.py list-exercises --search "squat"
python hevy.py list-exercises --search "plank"
python hevy.py list-exercises --search "curl"
```

### 3. Dry-run to verify resolution

```bash
python hevy.py create-routine --file examples/upper_body_example.json --dry-run
```

Prints the exercise → template_id resolution table and the full JSON payload without sending anything to the API.

### 4. Create the routine

```bash
python hevy.py create-routine --file examples/upper_body_example.json
```

### 5. Verify it was created correctly

```bash
python hevy.py create-routine --file examples/upper_body_example.json --verify
```

The `--verify` flag fetches the created routine back from the API and checks every exercise name, set count, reps, duration, and weight against your JSON.

## Workout JSON Format

See `examples/` for ready-to-use templates. The general structure:

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
        { "reps": 10, "weight_lb": 95, "type": "warmup" },
        { "reps": 8,  "weight_lb": 135 },
        { "duration_seconds": 60 }
      ]
    }
  ]
}
```

### Set fields

| Field              | Type   | Notes                                            |
|--------------------|--------|--------------------------------------------------|
| `reps`             | int    | Rep-based sets                                   |
| `duration_seconds` | int    | Timed sets — mutually exclusive with `reps`      |
| `weight_lb`        | float  | Converted to kg automatically                    |
| `weight_kg`        | float  | Used directly if present (overrides `weight_lb`) |
| `type`             | string | `"normal"` (default) / `"warmup"` / `"dropset"`  |

Bodyweight exercises: omit both weight fields.

### Supersets

Assign the same `superset_id` (any integer) to exercises that should be grouped together:

```json
{ "name": "Triceps Rope Pushdown", "superset_id": 1, "sets": [...] },
{ "name": "Seated Incline Curl (Dumbbell)", "superset_id": 1, "sets": [...] }
```

## Examples

| File | Description |
|------|-------------|
| `examples/upper_body_example.json` | Push/pull upper body with superset finisher |
| `examples/lower_body_example.json` | Compound-focused lower body strength session |

## Notes on the Hevy API

- Weights are stored in **kg** — this tool converts from lb automatically
- `POST /v1/routines` creates a reusable routine template
- `POST /v1/workouts` logs a completed session (use for after-the-fact logging)
- Exercise names in Hevy may differ from common usage — always verify with `list-exercises --search`
- Fuzzy matching will warn you when an exact name isn't found and show alternate candidates
