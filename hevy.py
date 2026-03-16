#!/usr/bin/env python3
"""
hevy.py — Automate routine creation in Hevy via the v1 API.

Usage:
    python hevy.py list-exercises [--search TERM]
    python hevy.py create-routine --file workout.json [--dry-run]
    python hevy.py refresh-cache

Environment:
    HEVY_API_KEY   — required, get from https://hevy.com/settings?developer
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from difflib import get_close_matches
from dotenv import load_dotenv

load_dotenv()  # loads .env from cwd or any parent directory

# ── Config ────────────────────────────────────────────────────────────────────

BASE_URL = "https://api.hevyapp.com/v1"
CACHE_FILE = Path(__file__).parent / "exercise_cache.json"
PAGE_SIZE = 100


def get_headers() -> dict:
    key = os.environ.get("HEVY_API_KEY")
    if not key:
        print("ERROR: HEVY_API_KEY environment variable not set.")
        print("Get your key at: https://hevy.com/settings?developer")
        sys.exit(1)
    return {"api-key": key, "Content-Type": "application/json"}


# ── API helpers ───────────────────────────────────────────────────────────────

def fetch_all_exercise_templates() -> list[dict]:
    """Paginate through all exercise templates and return full list."""
    headers = get_headers()
    templates = []
    page = 1
    while True:
        resp = requests.get(
            f"{BASE_URL}/exercise_templates",
            params={"page": page, "pageSize": PAGE_SIZE},
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("exercise_templates", [])
        templates.extend(batch)
        page_count = data.get("page_count", 1)
        print(f"  Fetched page {page}/{page_count} ({len(batch)} exercises)", flush=True)
        if page >= page_count:
            break
        page += 1
    return templates


def load_cache() -> dict:
    """Load exercise cache as {normalized_name: template_id, ...}."""
    if not CACHE_FILE.exists():
        print("No exercise cache found. Run: python hevy.py refresh-cache")
        sys.exit(1)
    with open(CACHE_FILE) as f:
        return json.load(f)


def save_cache(templates: list[dict]) -> None:
    """Save {title: id} and {normalized_title: id} mappings to cache."""
    cache = {
        "by_title": {t["title"]: t["id"] for t in templates},
        "by_title_lower": {t["title"].lower(): t["id"] for t in templates},
        "all": templates,
    }
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)
    print(f"Cached {len(templates)} exercise templates → {CACHE_FILE}")


def resolve_exercise(name: str, cache: dict) -> tuple[str, str]:
    """
    Resolve exercise name to (template_id, matched_name).
    Strategy: exact → case-insensitive exact → fuzzy close match.
    Raises ValueError if no reasonable match found.
    """
    by_title = cache["by_title"]
    by_lower = cache["by_title_lower"]

    # Exact match
    if name in by_title:
        return by_title[name], name

    # Case-insensitive exact
    name_lower = name.lower()
    if name_lower in by_lower:
        matched = next(t for t in cache["all"] if t["title"].lower() == name_lower)
        return by_lower[name_lower], matched["title"]

    # Fuzzy match against all titles
    all_titles = list(by_title.keys())
    close = get_close_matches(name, all_titles, n=3, cutoff=0.5)
    if close:
        best = close[0]
        print(f"  ⚠  '{name}' → fuzzy matched to '{best}'")
        if len(close) > 1:
            print(f"     Other candidates: {close[1:]}")
        return by_title[best], best

    raise ValueError(
        f"Could not resolve exercise: '{name}'\n"
        f"Run: python hevy.py list-exercises --search \"{name}\" to find the correct name."
    )


# ── Unit conversion ───────────────────────────────────────────────────────────

def lb_to_kg(lb: float | None) -> float | None:
    if lb is None:
        return None
    return round(lb * 0.453592, 3)


# ── Payload builder ───────────────────────────────────────────────────────────

def build_set(set_def: dict) -> dict:
    """
    Build a single set object from workout definition.

    set_def keys:
        duration_seconds  — for timed sets
        reps              — for rep-based sets
        weight_lb         — load in pounds (converted to kg)
        weight_kg         — load in kg (used directly if present)
        type              — "normal" | "warmup" | "dropset" (default: "normal")
    """
    s = {}
    s["type"] = set_def.get("type", "normal")

    # Weight: prefer explicit kg, fall back to lb conversion
    if "weight_kg" in set_def:
        s["weight_kg"] = set_def["weight_kg"]
    elif "weight_lb" in set_def:
        s["weight_kg"] = lb_to_kg(set_def["weight_lb"])
    else:
        s["weight_kg"] = None

    # Duration vs reps
    if "duration_seconds" in set_def:
        s["duration_seconds"] = set_def["duration_seconds"]
        s["reps"] = None
    else:
        s["reps"] = set_def.get("reps")
        s["duration_seconds"] = None

    return s


def build_routine_payload(workout_def: dict, cache: dict) -> dict:
    """
    Build the full POST /v1/routines request body.
    Resolves exercise names → template IDs, converts units.
    """
    exercises = []
    resolution_log = []

    for ex in workout_def["exercises"]:
        template_id, matched_name = resolve_exercise(ex["name"], cache)
        resolution_log.append((ex["name"], matched_name, template_id))

        sets = [build_set(s) for s in ex["sets"]]

        exercises.append({
            "exercise_template_id": template_id,
            "superset_id": ex.get("superset_id", None),
            "rest_seconds": ex.get("rest_seconds", 90),
            "notes": ex.get("notes", ""),
            "sets": sets,
        })

    return {
        "routine": {
            "title": workout_def["title"],
            "folder_id": workout_def.get("folder_id", None),
            "notes": workout_def.get("notes", ""),
            "exercises": exercises,
        }
    }, resolution_log


def post_routine(payload: dict) -> dict:
    resp = requests.post(
        f"{BASE_URL}/routines",
        headers=get_headers(),
        json=payload,
    )
    resp.raise_for_status()
    return resp.json()


# ── CLI commands ──────────────────────────────────────────────────────────────

def cmd_refresh_cache(_args):
    print("Fetching all exercise templates from Hevy API...")
    templates = fetch_all_exercise_templates()
    save_cache(templates)
    print(f"Done. {len(templates)} exercises available.")


def cmd_list_exercises(args):
    cache = load_cache()
    all_exercises = cache["all"]

    if args.search:
        term = args.search.lower()
        results = [t for t in all_exercises if term in t["title"].lower()]
        print(f"\nExercises matching '{args.search}':")
    else:
        results = all_exercises
        print(f"\nAll {len(results)} exercises:")

    for t in sorted(results, key=lambda x: x["title"]):
        muscle = t.get("muscle_group") or "—"
        print(f"  {t['title']:<45} {muscle:<20} {t['id']}")


def cmd_create_routine(args):
    # Load workout definition
    workout_file = Path(args.file)
    if not workout_file.exists():
        print(f"ERROR: File not found: {args.file}")
        sys.exit(1)

    with open(workout_file) as f:
        workout_def = json.load(f)

    print(f"\nBuilding routine: '{workout_def['title']}'")
    print(f"  {len(workout_def['exercises'])} exercises\n")

    cache = load_cache()

    try:
        payload, resolution_log = build_routine_payload(workout_def, cache)
    except ValueError as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

    # Print resolution table
    print("Exercise resolution:")
    for original, matched, tid in resolution_log:
        status = "✓" if original == matched else "~"
        print(f"  {status} '{original}' → '{matched}' ({tid[:8]}...)")

    # Print full payload in dry-run mode
    if args.dry_run:
        print("\n── DRY RUN: payload that would be sent ──")
        print(json.dumps(payload, indent=2))
        return

    print("\nPosting to Hevy API...")
    try:
        result = post_routine(payload)
        raw = result.get("routine") or result.get("routines") or []
        routine = raw[0] if isinstance(raw, list) else raw
        routine_id = routine.get("id", "unknown")
        print(f"\n✓ Routine created successfully!")
        print(f"  ID: {routine_id}")
        print(f"  Title: {routine.get('title')}")
    except requests.HTTPError as e:
        print(f"\nERROR: API request failed: {e}")
        print(f"Response: {e.response.text}")
        sys.exit(1)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Hevy workout automation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # refresh-cache
    sub.add_parser("refresh-cache", help="Download and cache all exercise templates")

    # list-exercises
    p_list = sub.add_parser("list-exercises", help="List exercises from cache")
    p_list.add_argument("--search", "-s", help="Filter by name substring")

    # create-routine
    p_create = sub.add_parser("create-routine", help="Create a routine from a JSON file")
    p_create.add_argument("--file", "-f", required=True, help="Path to workout JSON file")
    p_create.add_argument("--dry-run", action="store_true",
                          help="Print payload without sending to API")

    args = parser.parse_args()
    {
        "refresh-cache": cmd_refresh_cache,
        "list-exercises": cmd_list_exercises,
        "create-routine": cmd_create_routine,
    }[args.command](args)


if __name__ == "__main__":
    main()
