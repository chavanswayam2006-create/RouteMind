/**
 * RouteMind AI - Dashboard Operations & Controller Module
 */

const RouteMindApp = (function() {
  let activeStart = "A";
  let activeGoal = "G";
  let activeAlgorithm = "astar";

  function init() {
    // Initialize Cytoscape
    RouteMindNetwork.init('cy-network', window.INITIAL_NETWORK_DATA);
    updateRoadCounts();

    // Auto-calculate initial optimal route on load
    setTimeout(() => {
      findBestRoute();
    }, 400);
  }

  function updateRoadCounts() {
    fetch('/api/network')
      .then(r => r.json())
      .then(data => {
        if (data.success && data.network) {
          const roads = data.network.roads || [];
          const blocked = roads.filter(r => r.is_blocked).length;
          const open = roads.length - blocked;
          
          const activeEl = document.getElementById('active-roads-count');
          const blockedEl = document.getElementById('blocked-roads-count');
          if (activeEl) activeEl.innerText = `${open} Open Corridors`;
          if (blockedEl) blockedEl.innerText = `${blocked} Blocked`;
        }
      })
      .catch(console.error);
  }

  function findBestRoute() {
    const startSelect = document.getElementById('select-start-node');
    const goalSelect = document.getElementById('select-goal-node');
    const algoSelect = document.getElementById('select-algorithm');

    activeStart = startSelect ? startSelect.value : "A";
    activeGoal = goalSelect ? goalSelect.value : "G";
    activeAlgorithm = algoSelect ? algoSelect.value : "astar";

    // Set UI to calculating state
    const btn = document.getElementById('btn-find-best-route');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Calculating...';
    }

    if (activeAlgorithm === 'compare_all') {
      runBenchmark();
      // Still run A* for main display
      fetch('/api/route/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start: activeStart, destination: activeGoal, algorithm: 'astar' })
      })
      .then(r => r.json())
      .then(handleRouteResult)
      .finally(resetButtonState);
    } else {
      fetch('/api/route/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start: activeStart, destination: activeGoal, algorithm: activeAlgorithm })
      })
      .then(r => r.json())
      .then(handleRouteResult)
      .finally(resetButtonState);
    }
  }

  function resetButtonState() {
    const btn = document.getElementById('btn-find-best-route');
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-compass"></i> Find Best Route';
    }
  }

  function handleRouteResult(data) {
    if (!data.success) {
      alert("Error: " + (data.error || "Route calculation failed."));
      return;
    }

    const res = data.result || {};
    const found = res.found || false;
    const path = res.path || [];

    // 1. Highlight on graph
    RouteMindNetwork.highlightPath(path);

    // 2. Update telemetry numbers
    const timeEl = document.getElementById('res-time');
    const distEl = document.getElementById('res-dist');
    const costEl = document.getElementById('res-cost');
    const exploredEl = document.getElementById('res-explored');
    const statusPill = document.getElementById('route-status-pill');
    const dispatchState = document.getElementById('dispatch-state-text');

    if (found) {
      if (timeEl) timeEl.innerText = `${res.travel_time_min} min`;
      if (distEl) distEl.innerText = `${res.distance_km} km`;
      if (costEl) costEl.innerText = `${res.route_cost}`;
      if (exploredEl) exploredEl.innerText = `${res.nodes_explored_count} hubs`;
      
      if (statusPill) {
        statusPill.className = "badge-rm optimal";
        statusPill.innerText = "RECOMMENDED ROUTE";
      }
      if (dispatchState) {
        dispatchState.style.color = "#34d399";
        dispatchState.innerText = "Optimal Path Locked";
      }

      // Update recommendation banner
      updateBanner(
        "Optimal Route Identified",
        `Autonomous dispatcher selected corridor <strong>${path.join(' &rarr; ')}</strong> (${res.travel_time_min} min, ${res.distance_km} km). All road segments confirmed unblocked.`,
        "optimal"
      );

      // Update Waypoint Stepper
      renderStepper(path);
    } else {
      if (timeEl) timeEl.innerText = `-- min`;
      if (distEl) distEl.innerText = `-- km`;
      if (costEl) costEl.innerText = `--`;
      if (exploredEl) exploredEl.innerText = `${res.nodes_explored_count || 0} hubs`;

      if (statusPill) {
        statusPill.className = "badge-rm danger";
        statusPill.innerText = "NO VALID ROUTE";
      }
      if (dispatchState) {
        dispatchState.style.color = "#ef4444";
        dispatchState.innerText = "Dispatch Blocked";
      }

      updateBanner(
        "No Traversable Route Available",
        `Critical corridor obstruction: all valid paths from <strong>Hub ${activeStart}</strong> to <strong>Hub ${activeGoal}</strong> are blocked by road closures. Unblock at least one segment to resume transit.`,
        "danger"
      );

      renderStepper([]);
    }

    refreshActivityFeed();
  }

  function updateBanner(title, body, type) {
    const banner = document.getElementById('recommendation-banner-box');
    const titleEl = document.getElementById('recommendation-banner-title');
    const bodyEl = document.getElementById('recommendation-banner-body');

    if (titleEl) titleEl.innerHTML = title;
    if (bodyEl) bodyEl.innerHTML = body;

    if (banner) {
      if (type === 'danger') {
        banner.style.borderLeftColor = '#ef4444';
        banner.style.background = 'rgba(239, 68, 68, 0.08)';
      } else {
        banner.style.borderLeftColor = 'var(--rm-teal)';
        banner.style.background = 'linear-gradient(135deg, rgba(13, 148, 136, 0.08) 0%, rgba(11, 19, 43, 0.04) 100%)';
      }
    }
  }

  function renderStepper(path) {
    const container = document.getElementById('route-stepper-container');
    if (!container) return;

    if (!path || path.length === 0) {
      container.innerHTML = '<span style="color: #ef4444; font-size: 13px;"><i class="bi bi-x-circle"></i> No reachable path under current road closures.</span>';
      return;
    }

    let html = '';
    path.forEach((hub, idx) => {
      const isStart = idx === 0;
      const isGoal = idx === path.length - 1;
      let badgeStyle = "background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1;";
      if (isStart) badgeStyle = "background: #064e3b; color: #34d399; border: 1px solid #10b981;";
      if (isGoal) badgeStyle = "background: #083344; color: #38bdf8; border: 1px solid #06b6d4;";

      html += `<span class="badge-rm" style="${badgeStyle}; padding: 4px 10px;">${hub}</span>`;
      if (idx < path.length - 1) {
        html += `<i class="bi bi-arrow-right" style="color: var(--rm-teal); font-size: 12px;"></i>`;
      }
    });

    container.innerHTML = html;
  }

  function toggleRoadBlock(roadId) {
    fetch('/api/network/road/toggle-block', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ road_id: roadId })
    })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        // Update network in cytoscape
        RouteMindNetwork.updateNetwork(data.network);
        updateRoadCounts();

        // Update button badge on quick list
        const btn = document.getElementById(`toggle-road-${roadId}`);
        if (btn) {
          btn.className = `badge-rm ${data.is_blocked ? 'danger' : 'success'}`;
          btn.innerText = data.is_blocked ? 'BLOCKED' : 'OPEN';
        }

        // Re-calculate route dynamically to test autonomous re-routing
        findBestRoute();
      }
    })
    .catch(console.error);
  }

  function unblockAllRoads() {
    fetch('/api/network')
      .then(r => r.json())
      .then(data => {
        if (data.success && data.network) {
          const promises = data.network.roads
            .filter(r => r.is_blocked)
            .map(r => 
              fetch('/api/network/road/toggle-block', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ road_id: r.id })
              })
            );

          Promise.all(promises).then(() => {
            fetch('/api/network')
              .then(r => r.json())
              .then(d => {
                RouteMindNetwork.updateNetwork(d.network);
                updateRoadCounts();
                // Reset all road buttons
                (d.network.roads || []).forEach(r => {
                  const b = document.getElementById(`toggle-road-${r.id}`);
                  if (b) {
                    b.className = 'badge-rm success';
                    b.innerText = 'OPEN';
                  }
                });
                findBestRoute();
              });
          });
        }
      });
  }

  function resetNetwork() {
    fetch('/api/network/reset', { method: 'POST' })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          RouteMindNetwork.updateNetwork(data.network);
          updateRoadCounts();
          location.reload();
        }
      })
      .catch(console.error);
  }

  function runBenchmark() {
    const startSelect = document.getElementById('select-start-node');
    const goalSelect = document.getElementById('select-goal-node');
    const start = startSelect ? startSelect.value : "A";
    const goal = goalSelect ? goalSelect.value : "G";

    fetch('/api/route/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ start: start, destination: goal })
    })
    .then(r => r.json())
    .then(data => {
      if (data.success && data.benchmark) {
        const tableBody = document.getElementById('benchmark-table-body');
        const rows = data.benchmark.comparison_table || [];

        let html = '';
        rows.forEach(row => {
          const badgeClass = row.status === 'Optimal Route' ? 'optimal' : (row.status === 'Found Path' ? 'info' : 'danger');
          html += `
            <tr>
              <td><strong>${row.algorithm}</strong></td>
              <td><span style="font-size: 11px; color: var(--rm-text-muted);">${row.type}</span></td>
              <td class="mono-data" style="color: var(--rm-teal);">${row.path}</td>
              <td class="mono-data">${row.edges}</td>
              <td class="mono-data">${row.distance_km} km</td>
              <td class="mono-data"><strong>${row.time_min} min</strong></td>
              <td class="mono-data">${row.cost}</td>
              <td class="mono-data">${row.nodes_explored}</td>
            </tr>
          `;
        });
        if (tableBody) tableBody.innerHTML = html;

        // Render Chart.js
        RouteMindCharts.renderBenchmarkChart('benchmark-chart', rows);
      }
    })
    .catch(console.error);
  }

  function refreshActivityFeed() {
    // Activity feed updates automatically through simulation events
  }

  // Initialize when DOM ready
  document.addEventListener('DOMContentLoaded', init);

  return {
    init: init,
    findBestRoute: findBestRoute,
    toggleRoadBlock: toggleRoadBlock,
    unblockAllRoads: unblockAllRoads,
    resetNetwork: resetNetwork,
    runBenchmark: runBenchmark
  };
})();
