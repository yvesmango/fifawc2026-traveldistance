(function () {
  const DATA_URL = window.TRAVEL_DISTANCE_DATA_URL || "./docs/data/travel_distances.json";
  const DEMO_DATA = {
    metadata: {
      generated_at: "Demo fallback",
      methodology: "This is a fallback dataset shown when JSON loading fails.",
      teams_processed: 5,
      units: "km",
    },
    teams: [
      {
        team: "Argentina",
        training_site: "Sporting KC Training Centre",
        total_distance_km: 5340,
        matches_count: 3,
      },
      {
        team: "Brazil",
        training_site: "Columbia Park Training Facility",
        total_distance_km: 4980,
        matches_count: 3,
      },
      {
        team: "France",
        training_site: "Bentley University",
        total_distance_km: 4720,
        matches_count: 3,
      },
      {
        team: "United States",
        training_site: "Great Park Sports Complex",
        total_distance_km: 4550,
        matches_count: 3,
      },
      {
        team: "Japan",
        training_site: "Nashville SC",
        total_distance_km: 4210,
        matches_count: 3,
      },
    ],
  };

  const loadingState = document.getElementById("loading-state");
  const errorState = document.getElementById("error-state");
  const errorMessage = document.getElementById("error-message");
  const teamCount = document.getElementById("team-count");
  const datasetStatus = document.getElementById("dataset-status");
  const generatedAt = document.getElementById("generated-at");
  const summaryBody = document.getElementById("summary-body");
  const canvas = document.getElementById("travel-chart");
  let chartInstance = null;

  if (!loadingState || !errorState || !summaryBody || !canvas) {
    return;
  }

  function formatKilometers(value) {
    return window.TravelDistanceChart.formatKilometers(value);
  }

  function formatDistance(value) {
    return window.TravelDistanceChart.formatDistance(value);
  }

  function updateMeta(metadata, datasetLabel) {
    teamCount.textContent = String(metadata.teams_processed ?? 0);
    datasetStatus.textContent = datasetLabel;
    generatedAt.textContent = metadata.generated_at ?? "Unknown";
  }

  function renderSummaryRows(dataset) {
    summaryBody.innerHTML = "";
    dataset.forEach((row) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${row.team}</td>
        <td>${row.training_site ?? "Unknown"}</td>
        <td>${formatDistance(row.total_distance_km)}</td>
        <td>${row.matches_count ?? 3}</td>
      `;
      summaryBody.appendChild(tr);
    });
  }

  function destroyChart() {
    if (chartInstance) {
      chartInstance.destroy();
      chartInstance = null;
    }
  }

  function renderChart(dataset) {
    destroyChart();
    chartInstance = window.TravelDistanceChart.renderTravelChart(canvas, dataset);
  }

  function showError(message) {
    errorMessage.textContent = message;
    errorState.classList.remove("hidden");
  }

  function hideLoading() {
    loadingState.classList.add("hidden");
  }

  function sortDataset(dataset) {
    return [...dataset].sort((left, right) => right.total_distance_km - left.total_distance_km);
  }

  async function loadData() {
    try {
      const response = await fetch(DATA_URL, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const payload = await response.json();
      if (!Array.isArray(payload.teams) || payload.teams.length === 0) {
        throw new Error("JSON payload missing team records");
      }
      const dataset = sortDataset(payload.teams);
      const metadata = payload.metadata ?? {};
      const label = metadata.dataset_type === "demo" ? "Demo fallback JSON" : "Live JSON";
      updateMeta(metadata, label);
      renderSummaryRows(dataset);
      renderChart(dataset);
      if (metadata.dataset_type === "demo") {
        showError(
          "The generated JSON is a demo fallback because the raw CSV inputs are not present in this workspace."
        );
      }
    } catch (error) {
      console.warn("Falling back to demo data:", error);
      showError("The generated JSON could not be loaded, so a demo dataset is shown instead.");
      updateMeta(DEMO_DATA.metadata, "Demo fallback");
      renderSummaryRows(DEMO_DATA.teams);
      renderChart(DEMO_DATA.teams);
    } finally {
      hideLoading();
    }
  }

  document.addEventListener("DOMContentLoaded", loadData, { once: true });
})();
