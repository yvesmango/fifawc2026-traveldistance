---
layout: default
title: Python Pipeline | FIFA World Cup 2026 Travel Distance Dashboard
description: Readable overview of the Python processing pipeline that generates the dashboard JSON.
---
<link rel="stylesheet" href="{{ '/css/style.css' | relative_url }}" />
<div class="page-shell content-page">
  <section class="hero">
    <div class="eyebrow">Python pipeline</div>
    <h1>Data preparation, end to end</h1>
    <p class="lede">
      The processing script is the single source of truth for the dataset. It loads the CSV exports, resolves
      airports, calculates distances, and writes the JSON that powers the GitHub Pages dashboard.
    </p>
  </section>

  <section class="panel">
    <h2>Workflow</h2>
    <ol class="step-list">
      <li>Load the raw Google Sheets exports from <code>data/raw/</code> with pandas.</li>
      <li>Normalize team names and reconcile aliases such as Cabo Verde and Cape Verde.</li>
      <li>Geocode each unique training site with Nominatim through geopy.</li>
      <li>Find the nearest valid commercial airport using the airports dataset.</li>
      <li>Resolve each venue to an airport, with a city-level fallback if needed.</li>
      <li>Compute airport-to-airport distances for each team&apos;s three group matches.</li>
      <li>Aggregate the totals, sort them descending, and write the final JSON payload.</li>
    </ol>
  </section>

  <section class="content-grid content-grid-2">
    <article class="panel">
      <h2>Run it locally</h2>
      <p>After the CSV exports are in place, regenerate the payload with:</p>
      <pre class="code-block"><code>uv run python scripts/process_data.py</code></pre>
      <p>
        The script writes both <code>data/processed/travel_distances.json</code> and
        <code>docs/data/travel_distances.json</code>.
      </p>
    </article>

    <article class="panel">
      <h2>Outputs</h2>
      <ul class="check-list">
        <li>Sorted team totals in kilometers.</li>
        <li>Metadata with timestamp, unit, and methodology summary.</li>
        <li>Warnings for any geocoding or airport-resolution gaps.</li>
      </ul>
    </article>
  </section>

  <section class="panel callout-panel">
    <div class="panel-header">
      <div>
        <h2>Source code</h2>
        <p>
          The processor lives in the repository under <code>scripts/process_data.py</code> and is designed to
          stay modular so it can be swapped for an API-backed workflow later.
        </p>
      </div>
    </div>
    <div class="cta-row">
      <a class="button-primary" href="https://github.com/yvesmango/worldcup2026-traveldistance" target="_blank" rel="noreferrer">Open repository</a>
      <a class="button-secondary" href="{{ '/methodology.html' | relative_url }}">Read methodology</a>
    </div>
  </section>
</div>
