---
layout: default
title: Dashboard | FIFA World Cup 2026 Travel Distance
---

<link rel="stylesheet" href="{{ '/docs/css/style.css' | relative_url }}" />
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<script>
  window.TRAVEL_DISTANCE_DATA_URL = "{{ '/docs/data/travel_distances.json' | relative_url }}";
</script>
<script src="{{ '/docs/js/chart.js' | relative_url }}" defer></script>
<script src="{{ '/docs/js/main.js' | relative_url }}" defer></script>

<div class="dashboard-page">
  <section class="hero">
    <div class="meta-row" aria-live="polite">
      <div class="meta-card">
        <span class="meta-label">Teams</span>
        <strong id="team-count">Loading</strong>
      </div>
      <div class="meta-card meta-card-dataset">
        <span class="meta-label">Datasets</span>
        <span class="meta-source">
          <a
            href="https://www.roadtrips.com/world-cup/2026-world-cup-packages/schedule/"
            target="_blank"
            rel="noreferrer"
          >
            World Cup match schedule
          </a>
          and
          <a
            href="https://inside.fifa.com/organisation/media-releases/world-cup-2026-team-base-camps-tbc-48-nations-usa-mexico-canada"
            target="_blank"
            rel="noreferrer"
          >
            FIFA base camps
          </a>
        </span>
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
        <h2 id="chart-title">Total estimated air travel distance</h2>
      </div>
    </div>

    <div id="loading-state" class="loading-state" role="status" aria-live="polite">
      <div class="spinner" aria-hidden="true"></div>
      <span>Loading air travel distance data…</span>
    </div>

    <div id="error-state" class="error-state hidden" role="alert">
      <strong>Could not load the generated JSON.</strong>
      <p id="error-message">
        A fallback demo dataset will be shown so the dashboard remains usable.
      </p>
    </div>

    <div class="chart-wrap">
      <canvas id="travel-chart" aria-label="Horizontal bar chart of team air travel distance" role="img"></canvas>
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
      airport before flight distances are calculated against the nearest airport to each venue. Values are shown
      in kilometers with miles in parentheses. The summary table includes the original training site used for
      each team.
    </p>
  </footer>
</div>
