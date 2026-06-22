# FIFA World Cup 2026 Travel Distance Dashboard

A GitHub Pages-ready portfolio project that estimates total group-stage air travel distance for each 2026 World Cup national team. The site now uses a Jekyll shell in `docs/` with Markdown pages for the overview, dashboard, methodology, and pipeline write-up.

## What it does

- Reads two prepared CSV exports from Google Sheets:
  - `data/raw/group_stage.csv`
  - `data/raw/team_origins.csv`
- Geocodes each team training site with `geopy` and Nominatim.
- Maps each training site and venue to the nearest commercial airport with `airports-py`.
- Calculates match-by-match travel distance in kilometers.
- Aggregates total travel distance per team.
- Writes a precomputed JSON file for the static frontend in `docs/`.

## Repo layout

```text
worldcup2026-traveldistance/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   ├── _config.yml
│   ├── css/
│   ├── data/
│   ├── dashboard.md
│   ├── index.md
│   ├── methodology.md
│   ├── process.md
│   └── js/
├── scripts/
├── pyproject.toml
└── README.md
```

## Setup

1. Install Python 3.11 or newer.
2. Add the prepared CSV exports into `data/raw/`.
3. Install dependencies and create the lockfile with `uv`.

```bash
uv sync
```

## Generate the data

Run the processing script end to end:

```bash
uv run python scripts/process_data.py
```

This writes:

- `data/processed/travel_distances.json`
- `docs/data/travel_distances.json`

If the raw CSV exports are not present yet, the script writes a small demo payload so the frontend still has something to render.
That demo payload is marked in the JSON metadata with `"dataset_type": "demo"`.

## Expected CSV columns

The processor auto-detects common column variants, but the cleanest input shape is:

- `data/raw/team_origins.csv`
  - `Team`
  - `Training_Site`
- `data/raw/group_stage.csv`
  - `Team_1`
  - `Team_2`
  - `Venue`
  - optional venue city columns such as `City` or `Venue_City`

## View the site locally

Open `docs/` with a local static server. For example:

```bash
python -m http.server 8000 -d docs
```

Then visit `http://localhost:8000`.

The overview lives at `http://localhost:8000/`, the dashboard at `http://localhost:8000/dashboard.html`, and the supporting write-up pages at `methodology.html` and `process.html`.

## Methodology

- The origin for each team is its `Training_Site`, not its city field.
- Training sites are geocoded once and cached.
- Each site is mapped to the nearest valid commercial airport with scheduled service, preferring medium and large airports.
- Each match venue is also mapped to the nearest valid commercial airport, with a city-level fallback if needed.
- If Nominatim geocoding is rate-limited, the script falls back to a local airport text-matching resolver so the dataset can still be generated end to end.
- Travel distance is computed as great-circle airport-to-airport distance in kilometers.
- Team totals are the sum of their three group-stage matches.

## Data notes

- Team naming is normalized so common variants like `Cabo Verde` and `Cape Verde` resolve to one canonical label.
- The processing script logs warnings when geocoding or airport resolution fails and continues so the dataset can be manually reviewed.
- The frontend includes a fallback demo dataset so the page still renders if the JSON file is missing or fails to load.

## Deployment

GitHub Pages should publish from the `docs/` folder.

1. Generate the JSON.
2. Commit the source files and generated JSON.
3. Enable GitHub Pages for the repository and point it at the `docs/` folder.
4. GitHub Pages will render the Jekyll theme from `docs/_config.yml` and the Markdown content pages in `docs/`.

## Reproduction checklist

- `uv sync`
- `uv run python scripts/process_data.py`
- Serve `docs/` locally
- Verify the overview, dashboard, methodology, and pipeline pages all load
- Confirm the chart renders in descending order
- Confirm the mobile layout works and tooltips show exact kilometer values
