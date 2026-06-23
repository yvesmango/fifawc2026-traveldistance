**[Home](https://yvesmango.github.io/) >> [Projects](https://yvesmango.github.io/projects) >> FIFA World Cup 2026 Travel Distance Dashboard**

**Goal**: Estimate the total one-way group-stage air travel burden for each national team in the 2026 World Cup.

## Introduction

This project combines training-site geocoding with airport proximity mapping to estimate how far each team is likely to travel by air during the group stage. The main metric is a one-way distance total from each team&apos;s training site to each match venue. The result is a static, GitHub Pages-friendly portfolio site with a precomputed JSON dataset and an interactive chart.

## Data Sources

- Group stage schedule exported from Google Sheets
- Team origin data with training-site locations exported from Google Sheets
- Airport reference data used for nearest-airport matching

## Methodology

1. Load the CSV exports with Python and pandas.
2. Geocode each unique training site with geopy and Nominatim.
3. Find the nearest valid commercial airport with airports-py.
4. Resolve each venue to a destination airport with a city-level fallback.
5. Calculate airport-to-airport distance in kilometers and sum the three one-way group-stage flights for each team.

## Outputs

- [Dashboard](./dashboard.html)
- [Executive Summary](./executive-summary.html)
- [Python script](./scripts/process_data.py)

## Metric Note

Kilometers are the canonical unit in the analysis. The dashboard also shows a flight time equivalent based on the same one-way distance total, using 900 km/h as the cruise-speed assumption. That time is a convenience for readers, not a separate routing model. IR Iran is the lone exception: its total is doubled to approximate same-day out-and-back travel.

## Packages Used

`pandas`, `geopy`, `airports-py`, `Chart.js`,
