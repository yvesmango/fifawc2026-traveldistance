---
layout: default
title: FIFA World Cup 2026 Travel Distance Dashboard
description: Project overview and links to the dashboard, methodology, and Python pipeline.
---

# FIFA World Cup 2026 Travel Distance Dashboard

**Goal**: Estimate total group-stage air travel distance for each 2026 World Cup national team.

This project combines training-site geocoding, airport proximity, and match venue geography to produce a precomputed dataset for a static GitHub Pages dashboard.

## Introduction

The analysis uses each team&apos;s training site as the origin point, then maps that site and each venue to nearby commercial airports. The result is a simple ranking of which teams are expected to travel the most during the group stage.

## Data Sources

- Group stage schedule exported from Google Sheets
- Team origin data with training-site locations exported from Google Sheets
- Airport lookup data used for nearest-airport matching

## Methodology

1. Load the two CSV exports with Python and pandas.
2. Normalize team names, including Cape Verde and Cabo Verde.
3. Geocode each unique training site with geopy and Nominatim.
4. Find the nearest valid commercial airport with airports-py.
5. Resolve venues to destination airports, using a city-level fallback when needed.
6. Calculate airport-to-airport distances in kilometers and aggregate the totals by team.

## Outputs

- [Dashboard](./dashboard.html)
- [Methodology](./methodology.html)
- [Python script](./process.html)
- Generated JSON used by the chart: `docs/data/travel_distances.json`

## Technologies Used

`Python`, `pandas`, `geopy`, `airports-py`, `Chart.js`, `Jekyll`
