# Recorded project demonstrations

These are outputs from actual local project runs captured on 2026-09-09 UTC.
They are recorded demonstrations, not live remote engine execution.

- `chess.json`: 24 legal self-play moves from FunChessEngine with a 180 ms per-move
  search budget. The capture checked each UCI move against python-chess legality
  before applying it. The exact source commit and telemetry are in the file.
- `piano-chroma.csv`: actual detected chroma from PianoMirRustPublic's Rust CLI.
  The input is the first 12 seconds of the repository's tracked Minuet MIDI,
  converted by its own MIDI importer and synthesized with a sine fundamental plus
  two harmonics. This is a controlled synthetic example, not a human performance.
- `piano.json`: source commit, input description and actual verification results.
- `piano-notes.json`: the source MIDI notes used for the synthetic audio.
- `piano-report.md`: unedited analysis text except local input/output paths changed
  to portable names. It retains the algorithm's interpretation and limitations.
- `frog.svg` and `frog-light.svg`: copies of the existing photographic ASCII frog
  used as embedded animation sprites. The user's selected photograph is unchanged.

The profile generator draws deterministic SVG replays. Refreshing profile activity
never reruns or fabricates these project demonstrations. To replace a recording,
run the source project again and replace its captured data and provenance together.

The companion source is maintained in the sibling `EthanChenPond` Sites project.
It reads the public profile snapshot on load, with a bundled fallback and explicit
date/status when the network is unavailable. Visitors need no GitHub token.
