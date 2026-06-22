(function () {
  const BAR_COLOR = "#173f5f";
  const BAR_BORDER = "#173f5f";

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

  function createValueLabelPlugin() {
    return {
      id: "valueLabels",
      afterDatasetsDraw(chart) {
        const {
          ctx,
          data,
          chartArea: { right },
        } = chart;

        ctx.save();
        ctx.fillStyle = BAR_COLOR;
        ctx.font = "600 12px Inter, system-ui, sans-serif";
        ctx.textBaseline = "middle";

        chart.getDatasetMeta(0).data.forEach((bar, index) => {
          const value = data.datasets[0].data[index];
          const label = formatDistance(value);
          const labelWidth = ctx.measureText(label).width;
          const x = Math.min(bar.x + 10, right - labelWidth - 4);
          const y = bar.y;
          ctx.fillText(label, x, y);
        });

        ctx.restore();
      },
    };
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
            borderRadius: 10,
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
            borderColor: "#173f5f",
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
      plugins: [createValueLabelPlugin()],
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
