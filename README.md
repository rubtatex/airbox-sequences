# Airbox community sequences

Sequences shared by Airbox users, for the Airbox app.

**Online editor and catalog: https://rubtatex.github.io/airbox-sequences/**

In the app: **Sequences tab → ⋯ → Browse the community**, tick the sequences you want, then **Import**. You get a preview with the steps and any safety warning before anything is added.

## Use a sequence without the catalog

Open the file on GitHub, copy its address, and in the app choose **⋯ → Import from a link**. A single file can also be downloaded and opened with Airbox from Files or AirDrop.

## Contribute

The easiest way: build your sequence in the [online editor](https://rubtatex.github.io/airbox-sequences/) and click **Propose to the community**. GitHub opens with your file already filled in; click *Propose new file*, then *Create pull request*.

By hand:

1. Fork this repository and add `sequences/your-title.airbox.json` (lowercase letters, digits and dashes).
2. Fill in `name`, `author` and a one-line `description`. The format is in [FORMAT.md](FORMAT.md), and [`schema.json`](schema.json) describes it for editors.
3. Open a pull request. A workflow checks your file with the same limits as the app. After the merge, `index.json` is rebuilt automatically.

You can also run `python3 scripts/build_index.py` to check a file on your computer.

### Rules

- A sequence only drives the three relays (air, Re-Breath, Aroma). Keep it compatible with the safety caps of the firmware.
- One sequence per file. The file name is its stable identifier: don't rename it once published.
- Limits (the script enforces them): 500 steps, 4 nesting levels, repeats up to 100, waits from 1 s to 1 h.

## Add this repository to another source

Any GitHub repository with this layout works in the app: **Community → slider button → Add a repository**, then `owner/repo` or `owner/repo@branch`.
