---
layout: default
title: Python Script | FIFA World Cup 2026 Travel Distance Dashboard
description: Compact summary of the Python processing script used to generate the dashboard JSON.
---

# Python Script

The processing script is the single source of truth for the dataset.

## What it does

- Loads `data/raw/fifaworldcup2026-groupstage.csv`
- Loads `data/raw/fifaworldcup2026-basecamps.csv`
- Standardizes team names
- Geocodes training sites
- Finds nearby commercial airports
- Calculates total travel distance per team
- Writes `data/processed/travel_distances.json`
- Copies the same payload to `docs/data/travel_distances.json`

## Run it

```bash
uv run python scripts/process_data.py
```

## Output

The JSON includes:

- team name
- total distance in kilometers
- matches counted
- generation timestamp
- short methodology note
