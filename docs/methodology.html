---
layout: default
title: Methodology | FIFA World Cup 2026 Travel Distance Dashboard
description: Methodology notes for the training-site geocoding and airport-distance workflow.
---
<link rel="stylesheet" href="{{ '/css/style.css' | relative_url }}" />
<div class="page-shell content-page">
  <section class="hero">
    <div class="eyebrow">Methodology</div>
    <h1>How the travel distances were estimated</h1>
    <p class="lede">
      The analysis uses each team&apos;s training site as the origin point, then maps that site and every match
      venue to nearby commercial airports before calculating the airport-to-airport distance.
    </p>
  </section>

  <section class="content-grid content-grid-2">
    <article class="panel">
      <h2>1. Training-site origin</h2>
      <p>
        Each team starts from its <strong>Training_Site</strong>, not the city field. That makes the origin
        point much more precise and avoids understating travel for teams based outside the listed city center.
      </p>
    </article>

    <article class="panel">
      <h2>2. Geocode and proximity scan</h2>
      <p>
        Training sites are geocoded with <strong>geopy</strong> and Nominatim. The resulting coordinates are
        then passed through an airport proximity scan that looks for the nearest valid commercial airport.
      </p>
    </article>

    <article class="panel">
      <h2>3. Airport filtering</h2>
      <p>
        Only medium and large airports with scheduled service are considered. If a precise venue lookup is not
        available, the script falls back to city-level airport matching.
      </p>
    </article>

    <article class="panel">
      <h2>4. Distance calculation</h2>
      <p>
        Distances are calculated in kilometers using airport-to-airport great-circle distance and rounded to
        the nearest whole kilometer for display.
      </p>
    </article>
  </section>

  <section class="panel">
    <h2>Assumptions and guardrails</h2>
    <ul class="check-list">
      <li>Team names are normalized so variants such as Cabo Verde and Cape Verde map to a single label.</li>
      <li>The script logs warnings when geocoding or airport lookup misses occur, then continues so the run can finish.</li>
      <li>A static fallback dataset exists only to keep the frontend usable if the generated JSON cannot load.</li>
      <li>The published dashboard consumes a precomputed JSON file and does not require any backend service.</li>
    </ul>
  </section>

  <section class="panel callout-panel">
    <div class="panel-header">
      <div>
        <h2>What to look for on the chart</h2>
        <p>
          The longest bars surface the teams with the heaviest estimated travel burden. Hover to see exact
          kilometer totals and use the table to scan the same ranking in text form.
        </p>
      </div>
    </div>
    <div class="cta-row">
      <a class="button-primary" href="{{ '/dashboard.html' | relative_url }}">Open dashboard</a>
      <a class="button-secondary" href="{{ '/process.html' | relative_url }}">See the pipeline</a>
    </div>
  </section>
</div>
