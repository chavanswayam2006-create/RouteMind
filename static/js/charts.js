/**
 * RouteMind AI - Chart.js Visualizations Module
 */

const RouteMindCharts = (function() {
  let benchmarkChart = null;

  function renderBenchmarkChart(canvasId, comparisonData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = (comparisonData || []).map(item => item.algorithm);
    const transitTimes = (comparisonData || []).map(item => item.time_min || 0);
    const nodesExplored = (comparisonData || []).map(item => item.nodes_explored || 0);

    if (benchmarkChart) {
      benchmarkChart.destroy();
    }

    benchmarkChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Transit Time (min)',
            data: transitTimes,
            backgroundColor: '#0d9488',
            borderRadius: 6,
            barPercentage: 0.6
          },
          {
            label: 'Nodes Explored',
            data: nodesExplored,
            backgroundColor: '#06b6d4',
            borderRadius: 6,
            barPercentage: 0.6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              boxWidth: 12,
              font: { family: 'Inter', size: 11 }
            }
          },
          tooltip: {
            padding: 10,
            cornerRadius: 8
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { font: { family: 'Inter', size: 10 } }
          },
          y: {
            beginAtZero: true,
            grid: { color: '#f1f5f9' },
            ticks: { font: { family: 'JetBrains Mono', size: 10 } }
          }
        }
      }
    });
  }

  return {
    renderBenchmarkChart: renderBenchmarkChart
  };
})();
