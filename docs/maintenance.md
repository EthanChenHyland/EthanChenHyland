# Maintaining the profile

Edit the short introduction in `README.md` directly. Scripts own only the marked
hero, repository-links, and accessible activity-text blocks. All imagery stays
in this repository; GitHub serves the SVGs, not a third-party stats service.

## Generate

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
# Supply an existing GitHub token in the environment; never commit it.
python scripts/generate_profile.py
# Replay the committed public snapshot with no network or token:
python scripts/generate_profile.py --snapshot generated/activity.json
python -m unittest discover -s tests -v
python scripts/validate.py
```

The live generator uses `GITHUB_TOKEN` / `GH_TOKEN` and `GH_LOGIN` /
`GITHUB_REPOSITORY_OWNER`. It needs only Python's standard library. Pillow is
used exclusively for the image conversion and its tests.

## Hero source

`assets/source/hero.png` is a lossless, EXIF-oriented copy of Ethan's supplied
frog photograph. The original pixels are preserved in that source file.
`assets/source/hero.json` stores its crop, character density, tone curve,
accessible description, and a hand-traced, softly feathered silhouette matte.
The matte removes the background and floor shadow; it does not synthesize pixels.

```sh
python scripts/make_ascii.py assets/source/hero.png
```

This inserts the hero into its README marker and creates both SVG themes. The
pipeline adjusts tonal contrast, sharpens at character resolution, and corrects
for monospace aspect ratio. Edit the JSON for art direction; the generator,
workflow, and reproducibility check all read the same settings. For a different
source, replace the PNG and update/remove the image-specific matte and crop.

The SVG reveal runs once over 1.6 seconds using native SMIL, with no JavaScript.
Its underlying clip is fully open, so unsupported animation shows the finished
artwork. Reduced-motion CSS disables the clip. All other panels stay still.

## Definitions and scope

- Activity: 365 consecutive UTC dates, including the current, unfinished day.
  Data is GitHub's contribution calendar, not the incomplete recent Events API.
  Counts follow what GitHub exposes to the token; private contribution visibility
  follows the account's settings. No private repository metadata is requested.
- Active days: dates with at least one contribution.
- Best week: largest Sunday–Saturday calendar-week total in the window; boundary
  weeks can be partial. The sparkline uses those same buckets.
- Current streak: consecutive active days ending today or yesterday. An empty
  current day does not end the streak before that day finishes.
- Longest streak: longest run **within this window**, not an all-time claim.
- Languages: GitHub's approximate language bytes in public, owned, non-fork,
  nonempty repositories, including archives and excluding this profile repo.
  Repository counts include every repo containing a language, not just those
  where it is the primary language. The chart shows the largest six; other
  languages remain in the denominator and in the accessible text/snapshot.
  These are code-size measurements, not a proficiency ranking.
- Recent work: the four most recently pushed public, non-fork, nonempty,
  unarchived repositories, excluding the profile. GitHub descriptions are used
  verbatim with visual truncation. `profile.json` supplies a sourced editorial
  fallback for FunChessEngine, whose API description is empty. Other missing
  descriptions are stated explicitly.
- Pagination covers both repositories and languages. API failures stop the run
  before replacing graphics. Public snapshots allow offline reproduction.

## Automation

`.github/workflows/profile.yml` runs daily at 08:23 UTC, on manual dispatch, and
on relevant source pushes to `main`. It uses the built-in `GITHUB_TOKEN` with
`contents: write`, tests, generates, validates, and commits only `generated/`
and managed README changes. Bot-only output does not match the push path filter;
GitHub also suppresses recursive push runs from the built-in token.

Dates are whole UTC days. Sorting, coordinates, font bytes, and JSON are stable.
The displayed observation date/window is meaningful and advances daily; there
are no wall-clock timestamps or random values. Replaying the same snapshot must
produce byte-identical files. A push conflict fails safely rather than force
pushing. Inspect the run before retrying against the latest branch.

## Visual system

620px width; IBM Plex Mono embedded as a small WOFF2 subset; transparent
backgrounds; grayscale ink; 1px rules; consistent type and numbered sections.
Separate `-dark.svg` variants selected by GitHub-supported `<picture>` elements
avoid depending only on a viewer's operating-system theme inside an SVG.
Each SVG has a title and description; README images have alt text and the
activity has a native text equivalent. Repository links stay in Markdown,
since SVG links are not interactive when the graphic is loaded as an image.

`python scripts/preview.py` builds local light, dark, and narrow previews in
`.preview/`. Serve the repository with `python -m http.server 8765` and visit
`http://localhost:8765/.preview/index.html`. It is a review harness, not a hosted
website and not part of the GitHub profile.

## Design references

The [reference profile](https://github.com/andriidrok1/andriidrok1) informed the
repo-owned SVG approach and restraint. Layout, implementation, and wording were
written for Ethan. The companion [article](https://agreeable-credit-859.notion.site/A-GitHub-profile-that-generates-itself-3abedfe9a65a81e4afc9daed90cb4e7e)
was also reviewed for GitHub sanitization, font embedding, and animation constraints.

The font comes from [IBM Plex](https://github.com/IBM/plex), under the included
SIL Open Font License. `assets/fonts/README.md` documents the subset.
