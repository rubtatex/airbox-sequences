#!/usr/bin/env python3
"""Validates every sequences/*.airbox.json and regenerates index.json.

Applies the same bounds as the Airbox app, so a file accepted here imports in the app.
    python3 scripts/build_index.py          rewrite index.json
    python3 scripts/build_index.py --check  fail if index.json is out of date
    python3 scripts/build_index.py --files-only  validate the files, ignore index.json (pull requests)
The workflow "Update index" rewrites index.json after every merge, so contributors only add their file.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEQ_DIR = ROOT / "sequences"
SUFFIX = ".airbox.json"

MAX_FILE_BYTES = 1_000_000
MAX_STEPS = 500
MAX_DEPTH = 4
MAX_REPEAT = 100
MAX_WAIT = 3600
MAX_ACTIONS = 5000
MAX_VISITS = 50_000
ENERGIZE = {
    ("air", "close"): True, ("air", "open"): False,
    ("rebreath", "open"): True, ("rebreath", "close"): False,
    ("aroma", "start"): True, ("aroma", "stop"): False,
}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class Invalid(Exception):
    pass


def check_wait(value):
    if isinstance(value, int) and not isinstance(value, bool):
        lo = hi = value
    elif isinstance(value, dict) and set(value) == {"min", "max"} and all(isinstance(v, int) for v in value.values()):
        lo, hi = value["min"], value["max"]
    else:
        raise Invalid("a wait is a number of seconds or {min, max}")
    if not (1 <= lo <= MAX_WAIT and 1 <= hi <= MAX_WAIT and lo <= hi):
        raise Invalid(f"a wait must be between 1 and {MAX_WAIT} seconds, with min <= max")
    return lo, hi


def validate_steps(steps, depth, budget):
    """Returns the parsed steps; raises Invalid."""
    if not isinstance(steps, list):
        raise Invalid("steps must be a list")
    parsed = []
    for step in steps:
        budget[0] -= 1
        if budget[0] < 0:
            raise Invalid("too many steps")
        if not isinstance(step, dict):
            raise Invalid("a step must be an object")
        shapes = [
            "relay" in step or "do" in step,
            "wait" in step,
            "together" in step,
            "repeat" in step or "steps" in step,
        ]
        if sum(shapes) != 1:
            raise Invalid("each step must be a command, a wait, a 'together' group or a 'repeat' group")
        if shapes[0]:
            key = (step.get("relay"), step.get("do"))
            if key not in ENERGIZE:
                raise Invalid(f"invalid command {key}")
            parsed.append(("relay", key[0], ENERGIZE[key]))
        elif shapes[1]:
            parsed.append(("wait",) + check_wait(step["wait"]))
        else:
            if depth >= MAX_DEPTH:
                raise Invalid("groups are nested too deeply")
            if shapes[2]:
                parsed.append(("together", validate_steps(step["together"], depth + 1, budget)))
            else:
                count = step.get("repeat")
                if not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= MAX_REPEAT:
                    raise Invalid(f"a repeat needs a count between 1 and {MAX_REPEAT}")
                parsed.append(("repeat", count, validate_steps(step.get("steps"), depth + 1, budget)))
    return parsed


def simulate(parsed):
    """Longest duration in seconds and the relays used; raises Invalid when too large."""
    visits = [0]
    actions = [0]
    relays = set()

    def walk(steps, t):
        for step in steps:
            visits[0] += 1
            if visits[0] > MAX_VISITS or actions[0] > MAX_ACTIONS:
                raise Invalid("this sequence is too large to run")
            kind = step[0]
            if kind == "relay":
                actions[0] += 1
                relays.add(step[1])
            elif kind == "wait":
                t += step[2]
            elif kind == "together":
                t = max([walk([child], t) for child in step[1]] or [t])
            else:
                for _ in range(step[1]):
                    t = walk(step[2], t)
        return t

    return walk(parsed, 0), relays


def load_file(path):
    if path.stat().st_size > MAX_FILE_BYTES:
        raise Invalid("file too large")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise Invalid(f"not valid JSON: {e}")
    if data.get("format") != "airbox-sequence" or data.get("version") != 1:
        raise Invalid('"format" must be "airbox-sequence" and "version" 1')
    if "sequences" in data:
        raise Invalid("catalog files hold a single sequence, not a bundle")
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise Invalid('"name" is required')
    for field in ("author", "description"):
        if field in data and not isinstance(data[field], str):
            raise Invalid(f'"{field}" must be text')
    parsed = validate_steps(data.get("steps"), 0, [MAX_STEPS])
    if not parsed:
        raise Invalid("a sequence needs at least one step")
    duration, relays = simulate(parsed)
    return data, duration, relays


def build():
    entries, errors = [], []
    for path in sorted(SEQ_DIR.glob("*" + SUFFIX)):
        entry_id = path.name[: -len(SUFFIX)]
        try:
            if not NAME_RE.match(entry_id):
                raise Invalid("file name must be lowercase letters, digits and dashes")
            data, duration, relays = load_file(path)
        except Invalid as e:
            errors.append(f"{path.relative_to(ROOT)}: {e}")
            continue
        entry = {"id": entry_id, "name": data["name"].strip()}
        if data.get("author"):
            entry["author"] = data["author"].strip()
        if data.get("description"):
            entry["description"] = data["description"].strip()
        entry["path"] = f"sequences/{path.name}"
        entry["durationSeconds"] = duration
        entry["relays"] = [r for r in ("air", "rebreath", "aroma") if r in relays]
        entries.append(entry)
    for stray in sorted(SEQ_DIR.iterdir()):
        if not stray.name.endswith(SUFFIX):
            errors.append(f"{stray.relative_to(ROOT)}: only *{SUFFIX} files belong in sequences/")
    index = {
        "format": "airbox-index",
        "version": 1,
        "name": "Airbox community sequences",
        "sequences": entries,
    }
    return json.dumps(index, indent=2, ensure_ascii=False) + "\n", errors


def main():
    text, errors = build()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    target = ROOT / "index.json"
    if "--files-only" in sys.argv:
        print("sequence files are valid")
        return 0
    if "--check" in sys.argv:
        if not target.exists() or target.read_text(encoding="utf-8") != text:
            print("index.json is out of date: run python3 scripts/build_index.py", file=sys.stderr)
            return 1
        print("index.json is up to date")
        return 0
    target.write_text(text, encoding="utf-8")
    print(f"index.json written ({len(json.loads(text)['sequences'])} sequences)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
