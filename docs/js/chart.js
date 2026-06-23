(function () {
  const BAR_COLOR = "#8fb4dc";
  const BAR_BORDER = "#6f93bc";

  const FLAG_BY_TEAM = {
    Algeria: "🇩🇿",
    Argentina: "🇦🇷",
    Australia: "🇦🇺",
    Austria: "🇦🇹",
    Belgium: "🇧🇪",
    Bosnia_and_Herzegovina: "🇧🇦",
    Brazil: "🇧🇷",
    Canada: "🇨🇦",
    Cape_Verde: "🇨🇻",
    Colombia: "🇨🇴",
    Congo_DR: "🇨🇩",
    Croatia: "🇭🇷",
    Curaçao: "🇨🇼",
    Czech_Republic: "🇨🇿",
    Ecuador: "🇪🇨",
    Egypt: "🇪🇬",
    England: "🇬🇧",
    France: "🇫🇷",
    Germany: "🇩🇪",
    Ghana: "🇬🇭",
    Haiti: "🇭🇹",
    IR_Iran: "🇮🇷",
    Iraq: "🇮🇶",
    Ivory_Coast: "🇨🇮",
    Japan: "🇯🇵",
    Jordan: "🇯🇴",
    Mexico: "🇲🇽",
    Morocco: "🇲🇦",
    Netherlands: "🇳🇱",
    New_Zealand: "🇳🇿",
    Norway: "🇳🇴",
    Panama: "🇵🇦",
    Paraguay: "🇵🇾",
    Portugal: "🇵🇹",
    Qatar: "🇶🇦",
    Saudi_Arabia: "🇸🇦",
    Scotland: "🏴",
    Senegal: "🇸🇳",
    South_Africa: "🇿🇦",
    South_Korea: "🇰🇷",
    Spain: "🇪🇸",
    Sweden: "🇸🇪",
    Switzerland: "🇨🇭",
    Tunisia: "🇹🇳",
    Türkiye: "🇹🇷",
    United_States: "🇺🇸",
    Uruguay: "🇺🇾",
    Uzbekistan: "🇺🇿",
  };

  function teamKey(team) {
    return String(team).replace(/[\s-]+/g, "_");
  }

  function formatTeamLabel(team) {
    const flag = FLAG_BY_TEAM[teamKey(team)] || "⚽";
    return `${flag} ${team}`;
  }

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
        labels: dataset.map((item) => formatTeamLabel(item.team)),
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
              autoSkip: false,
              padding: 6,
              color: "#0f172a",
              font: {
                size: 11,
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
