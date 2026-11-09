# Airbox community sequences

Sequences shared by Airbox users, for the [Airbox iOS app](https://github.com/rubtatex/Airbox-APP-ios).

In the app: **Sequences tab → ⋯ → Browse the community**, tick the sequences you want, then **Import**. You get a preview with the steps and any safety warning before anything is added.

## Use a sequence without the catalog

Open the file on GitHub, copy its address, and in the app choose **⋯ → Import from a link**. A single file can also be downloaded and opened with Airbox from Files or AirDrop.

## Contribute

1. Fork this repository and add `sequences/your-title.airbox.json` (lowercase letters, digits and dashes).
2. Fill in `name`, `author` and a one-line `description`. The format is documented in [SEQUENCES.md](https://github.com/rubtatex/Airbox-APP-ios/blob/main/SEQUENCES.md), and [`schema.json`](schema.json) describes it for editors.
3. Run `python3 scripts/build_index.py`. It validates your file with the same limits as the app and updates `index.json`. Commit both.
4. Open a pull request. A workflow checks the files and the index.

The easiest way to write a sequence is to build it in the app, then use **Share** and add your file here.

### Rules

- A sequence only drives the three relays (air, Re-Breath, Aroma). Keep it compatible with the safety caps of the firmware.
- One sequence per file. The file name is its stable identifier: don't rename it once published.
- Limits (the script enforces them): 500 steps, 4 nesting levels, repeats up to 100, waits from 1 s to 1 h.

## Add this repository to another source

Any GitHub repository with this layout works in the app: **Community → slider button → Add a repository**, then `owner/repo` or `owner/repo@branch`.
