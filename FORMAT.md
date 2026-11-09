# Airbox sequence format

A sequence is an automation of the three relays of the Airbox (Air, Re-Breath, Aroma). It is a plain JSON file named `something.airbox.json`, made of data only: relays, waits and groups. It can never contain code.

Before a sequence starts, the Airbox app unrolls it: loops are expanded and every random wait is drawn. The result is a flat timeline of relay changes that the Airbox plays, through the same safety gate as a manual command (armed only, Re-Breath and Air caps, emergency stop, always ends with every relay off).

The online editor at the root of this site's documentation builds and checks these files for you. [`schema.json`](schema.json) describes the format for other editors.

## Building blocks

| Step | What it does |
|---|---|
| Command | Sets one relay: Air close/open, Re-Breath open/close, Aroma start/stop. One step = one relay. |
| Wait | Pauses for a fixed time (1 s to 1 h), or for a random time drawn between a minimum and a maximum. |
| Together | Its steps all start at the same moment. The group ends when its longest step ends. |
| Repeat | Plays its steps N times (1 to 100). Repeats can contain other repeats. |

A **random wait** draws a new duration every time the step runs, including on each round of a loop. The app shows the total duration as a range (shortest to longest), and checks the safety limits (Re-Breath cap, Air cap) against the **longest** possible run.

Safety is never bypassed by a sequence: the firmware still enforces the Re-Breath and Air caps, and a sequence that would exceed them is shown with a warning, in the app and before importing it.

## The `.airbox.json` format

Plain UTF-8 JSON. The file name ends with `.airbox.json`. A file holds **one sequence** or a **bundle** of sequences.

### One sequence

```json
{
  "format": "airbox-sequence",
  "version": 1,
  "name": "Square breathing",
  "author": "lea-m",
  "description": "Open and close Re-Breath in four equal phases, six times.",
  "steps": [
    { "repeat": 6, "steps": [
      { "relay": "rebreath", "do": "open" },
      { "wait": 4 },
      { "relay": "rebreath", "do": "close" },
      { "wait": { "min": 3, "max": 6 } }
    ] }
  ]
}
```

### A bundle

```json
{
  "format": "airbox-sequence",
  "version": 1,
  "sequences": [
    { "name": "First", "steps": [ ... ] },
    { "name": "Second", "author": "someone", "steps": [ ... ] }
  ]
}
```

### Fields

| Field | Where | Meaning |
|---|---|---|
| `format` | file | Always `"airbox-sequence"`. |
| `version` | file | Format version, currently `1`. A file with a higher version is refused by older apps. |
| `name` | sequence | Required, shown in the app (80 characters kept). |
| `author`, `description` | sequence | Optional credits and short description (500 characters kept). |
| `steps` | sequence | Ordered list of steps. |

### Steps

Each step is an object with **exactly one** of the following shapes.

| Shape | Meaning |
|---|---|
| `{ "relay": "air", "do": "close" }` | Command. |
| `{ "wait": 20 }` | Fixed wait, in seconds (1 to 3600). |
| `{ "wait": { "min": 10, "max": 20 } }` | Random wait, in seconds (1 to 3600, `min` ≤ `max`). |
| `{ "together": [ step, step, ... ] }` | Steps that start together. |
| `{ "repeat": 3, "steps": [ step, ... ] }` | Repeat (1 to 100). |

The relay words are physical-wiring independent, and only these pairs are valid:

| `relay` | `do` values | Effect |
|---|---|---|
| `air` | `close`, `open` | `close` energizes the relay (air blocked), `open` releases it (normal air, safe state). |
| `rebreath` | `open`, `close` | `open` energizes the relay (re-breathing, capped by the firmware), `close` releases it. |
| `aroma` | `start`, `stop` | `start` runs the pump. |

### Limits

The app refuses files outside these bounds (community files are untrusted input):

| Limit | Value |
|---|---|
| File size | 1 MB |
| Sequences per file | 100 |
| Steps per sequence (all levels counted) | 500 |
| Nesting depth of `together` / `repeat` | 4 levels |
| Repeat count | 1 to 100 |
| One wait | 1 s to 3600 s |
| Unrolled size | at most 5000 commands, otherwise the sequence is "too large to run" |

A file contains data only: relays, waits and groups. It can never contain code or a command other than the three relays.

### Compatibility

`version` increases only when an older app could misread a file. New optional fields are ignored by older apps. Files exported by the app always use the current version.
