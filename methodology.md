---
layout: default
title: Methodology | FIFA World Cup 2026 Travel Distance Dashboard
description: Notes on the geocoding, airport mapping, and air travel distance workflow.
---

# Methodology

This project starts with each team&apos;s **Training_Site** rather than its city field. That choice makes the origin point more precise and better reflects the travel a squad actually faces.

## Workflow

1. Geocode each unique training site with Nominatim through geopy.
2. Scan for the nearest valid commercial airport with airports-py.
3. Resolve each venue to a destination airport, falling back to the venue city if needed.
4. Calculate airport-to-airport great-circle air distance in kilometers.
5. Sum the three group-stage matches for each team.

## Assumptions

- Team names are normalized so variants such as Cabo Verde and Cape Verde resolve to one label.
- The script logs warnings when geocoding or airport lookup fails.
- The published dashboard reads only the generated JSON file.

## Notes

Miles are shown alongside kilometers in the dashboard for readers who want a secondary unit reference, but kilometers remain the canonical unit for the analysis.
