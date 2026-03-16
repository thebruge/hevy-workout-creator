# hevy-workout-creator

Automate routine creation in the [Hevy](https://hevyapp.com) workout app via the v1 API. Define your workouts in JSON and push them directly to Hevy as reusable routines — or use the local web UI to build routines visually.

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

## Web UI

A visual routine builder is available at `index.html`. It lets you search exercises, configure sets, reorder exercises, and push directly to Hevy — without editing JSON files.

### Served mode (recommended)

```bash
python hevy.py serve            # default port 8000
python hevy.py serve --port 9000
```

Opens a local server that:
- Serves `index.html` at `http://localhost:8000`
- Proxies `POST /proxy/routines` to the Hevy API with your API key injected server-side (key never touches the browser)

Open `http://localhost:8000` in your browser, build your routine, click **Push to Hevy**.

### Standalone mode (offline)

Bake the exercise cache directly into `index.html` so it works without a server:

```bash
python hevy.py build-ui                      # overwrites index.html
python hevy.py build-ui --output my_ui.html  # write to a different file
```

Open the output file with `file://` in your browser. Switch to **Direct** mode in Settings, enter your API key, and push.

### UI features

- Live exercise search with muscle group and equipment filters
- Rep-based and timed (duration) sets per exercise
- Warmup / Normal / Drop set types
- Superset grouping (color-coded borders)
- ▲/▼ reorder exercises
- **Save as JSON** — downloads a file compatible with `create-routine --file`
- **Load JSON** — load an existing workout JSON file into the builder
- Draft auto-saved to `localStorage` — survives page reloads

---

## Notes on the Hevy API

- Weights are stored in **kg** — this tool converts from lb automatically
- `POST /v1/routines` creates a reusable routine template
- `POST /v1/workouts` logs a completed session (use for after-the-fact logging)
- Exercise names in Hevy may differ from common usage — always verify with `list-exercises --search`
- Fuzzy matching will warn you when an exact name isn't found and show alternate candidates
