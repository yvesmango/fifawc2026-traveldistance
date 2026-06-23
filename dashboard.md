---
layout: default
title: Dashboard | FIFA World Cup 2026 Travel Distance Dashboard
description: Interactive chart of estimated group-stage air travel distance by national team.
---

<link rel="stylesheet" href="./docs/css/style.css" />
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<script>
  window.TRAVEL_DISTANCE_DATA_URL = "./docs/data/travel_distances.json";
</script>
<script src="./docs/js/chart.js" defer></script>
<script src="./docs/js/main.js" defer></script>

# Team travel distance by group stage

The chart ranks all 48 teams by total estimated group-stage air travel distance. Each bar is the sum of the three match journeys calculated from a team&apos;s training site and the nearest venue airport.

<div class="page-shell dashboard-page">
  <section class="hero">
    <div class="meta-row" aria-live="polite">
      <div class="meta-card">
        <span class="meta-label">Teams</span>
        <strong id="team-count">Loading</strong>
      </div>
      <div class="meta-card">
        <span class="meta-label">Dataset</span>
        <strong id="dataset-status">Fetching JSON</strong>
      </div>
      <div class="meta-card">
        <span class="meta-label">Updated</span>
        <strong id="generated-at">Pending</strong>
      </div>
    </div>
  </section>

  <section class="panel chart-panel" aria-labelledby="chart-title">
    <div class="panel-header">
      <div>
        <h2 id="chart-title">Total estimated travel distance</h2>
        <p>
          Bars are sorted descending. Distances are rounded to the nearest kilometer and reflect the three
          group-stage matches for each team. Miles are shown in parentheses for quick reference.
        </p>
      </div>
      <div class="source-note">
        Source: prepared Google Sheets exports, processed locally with Python
      </div>
    </div>

    <div id="loading-state" class="loading-state" role="status" aria-live="polite">
      <div class="spinner" aria-hidden="true"></div>
      <span>Loading travel distance data…</span>
    </div>

    <div id="error-state" class="error-state hidden" role="alert">
      <strong>Could not load the generated JSON.</strong>
      <p id="error-message">
        A fallback demo dataset will be shown so the dashboard remains usable.
      </p>
    </div>

    <div class="chart-wrap">
      <canvas id="travel-chart" aria-label="Horizontal bar chart of team travel distance" role="img"></canvas>
    </div>

    <div class="table-wrap">
      <table class="summary-table" aria-label="Travel distance summary table">
        <thead>
          <tr>
            <th>Team</th>
            <th>Training Site</th>
            <th>Distance</th>
            <th>Matches</th>
          </tr>
        </thead>
        <tbody id="summary-body"></tbody>
      </table>
    </div>
  </section>

  <footer class="footer">
    <p>
      Methodology: each team starts from its training site, which is mapped to the nearest commercial
      airport before distances are calculated against the nearest airport to each venue. Values are shown in
      kilometers with miles in parentheses. The summary table includes the original training site used for
      each team.
    </p>
  </footer>
</div>
