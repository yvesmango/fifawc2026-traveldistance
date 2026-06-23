(function () {
  const BAR_COLOR = "#7fa8d6";
  const BAR_BORDER = "#5f88b8";

  function formatKilometers(value) {
    return new Intl.NumberFormat("en-US", {
      maximumFractionDigits: 0,
    }).format(value);
  }

  function formatMiles(value) {
    return new Intl.NumberFormat("en-US", {
      maximumFractionDigits: 0,
    }).format(Math.round(value * 0.621371));
  }

  function formatDistance(value) {
    return `${formatKilometers(value)} km (${formatMiles(value)} mi)`;
  }

  function buildChartConfig(dataset) {
    return {
      type: "bar",
      data: {
        labels: dataset.map((item) => item.team),
        datasets: [
          {
            label: "Total distance (km)",
            data: dataset.map((item) => item.total_distance_km),
            backgroundColor: BAR_COLOR,
            borderColor: BAR_BORDER,
            borderWidth: 1,
            borderRadius: 0,
            barThickness: 18,
            maxBarThickness: 22,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: "y",
        layout: {
          padding: {
            right: 72,
          },
        },
        animation: {
          duration: 800,
          easing: "easeOutQuart",
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            backgroundColor: "#0f172a",
            titleColor: "#ffffff",
            bodyColor: "#ffffff",
            borderColor: BAR_BORDER,
            borderWidth: 1,
            padding: 12,
            callbacks: {
              label(context) {
                const value = context.parsed.x ?? context.raw;
                return `${context.label}: ${formatDistance(value)}`;
              },
            },
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            grid: {
              color: "rgba(15, 23, 42, 0.08)",
            },
            ticks: {
              callback(value) {
                return `${formatKilometers(value)} km`;
              },
            },
          },
          y: {
            grid: {
              display: false,
            },
            ticks: {
              color: "#0f172a",
              font: {
                size: 12,
                weight: "600",
              },
            },
          },
        },
      },
    };
  }

  function renderTravelChart(canvas, dataset) {
    return new Chart(canvas, buildChartConfig(dataset));
  }

  window.TravelDistanceChart = {
    renderTravelChart,
    formatKilometers,
    formatMiles,
    formatDistance,
  };
})();
