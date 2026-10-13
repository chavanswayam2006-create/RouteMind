/**
 * RouteMind AI - Cytoscape.js Network Visualization Module
 */

const RouteMindNetwork = (function() {
  let cy = null;
  let currentNetwork = null;
  let highlightedPath = [];

  function init(containerId, networkData) {
    currentNetwork = networkData || window.INITIAL_NETWORK_DATA || { nodes: [], roads: [] };
    const container = document.getElementById(containerId);
    if (!container) return;

    const elements = buildElements(currentNetwork);

    cy = cytoscape({
      container: container,
      elements: elements,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(id)',
            'color': '#ffffff',
            'font-family': 'Plus Jakarta Sans, sans-serif',
            'font-size': '14px',
            'font-weight': 'bold',
            'text-valign': 'center',
            'text-halign': 'center',
            'background-color': '#0b132b',
            'border-width': 3,
            'border-color': '#475569',
            'width': 44,
            'height': 44,
            'transition-property': 'background-color, border-color, width, height',
            'transition-duration': '0.2s'
          }
        },
        {
          selector: 'node[id = "A"]',
          style: {
            'border-color': '#10b981',
            'border-width': 4,
            'background-color': '#064e3b'
          }
        },
        {
          selector: 'node[id = "G"]',
          style: {
            'border-color': '#06b6d4',
            'border-width': 4,
            'background-color': '#083344'
          }
        },
        {
          selector: 'node.highlighted',
          style: {
            'background-color': '#0d9488',
            'border-color': '#38bdf8',
            'border-width': 5,
            'width': 50,
            'height': 50
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 3,
            'line-color': '#94a3b8',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '10px',
            'font-family': 'JetBrains Mono, monospace',
            'color': '#334155',
            'text-background-color': '#ffffff',
            'text-background-opacity': 0.85,
            'text-background-padding': '3px',
            'text-background-shape': 'roundrectangle',
            'text-border-color': '#e2e8f0',
            'text-border-width': 1,
            'text-border-opacity': 1,
            'transition-property': 'line-color, width, opacity',
            'transition-duration': '0.25s'
          }
        },
        {
          selector: 'edge.blocked',
          style: {
            'line-style': 'dashed',
            'line-dash-pattern': [6, 4],
            'line-color': '#ef4444',
            'width': 4,
            'opacity': 0.85,
            'color': '#b91c1c'
          }
        },
        {
          selector: 'edge.path-highlighted',
          style: {
            'line-color': '#0d9488',
            'width': 6,
            'z-index': 99,
            'color': '#0f766e',
            'line-style': 'solid'
          }
        }
      ],
      layout: {
        name: 'preset',
        fit: true,
        padding: 40
      },
      userZoomingEnabled: true,
      userPanningEnabled: true,
      boxSelectionEnabled: false
    });

    // Click on edge to toggle blocked status
    cy.on('tap', 'edge', function(evt) {
      const edge = evt.target;
      const roadId = edge.data('road_id');
      if (roadId && window.RouteMindApp && window.RouteMindApp.toggleRoadBlock) {
        window.RouteMindApp.toggleRoadBlock(roadId);
      }
    });

    // Hover effect
    cy.on('mouseover', 'node', function(e) {
      document.body.style.cursor = 'pointer';
    });
    cy.on('mouseout', 'node', function(e) {
      document.body.style.cursor = 'default';
    });
  }

  function buildElements(networkData) {
    const elements = [];
    (networkData.nodes || []).forEach(n => {
      elements.push({
        group: 'nodes',
        data: {
          id: n.id,
          name: n.name,
          role: n.role
        },
        position: {
          x: n.x || 100,
          y: n.y || 100
        }
      });
    });

    (networkData.roads || []).forEach(r => {
      const isBlocked = r.is_blocked || false;
      const label = `${r.distance_km}km | ${r.time_min}m`;
      elements.push({
        group: 'edges',
        data: {
          id: r.id || `${r.from}-${r.to}`,
          source: r.from,
          target: r.to,
          road_id: r.id,
          distance_km: r.distance_km,
          time_min: r.time_min,
          congestion_pct: r.congestion_pct,
          label: isBlocked ? `⛔ BLOCKED` : label
        },
        classes: isBlocked ? 'blocked' : ''
      });
    });
    return elements;
  }

  function updateNetwork(newNetworkData) {
    currentNetwork = newNetworkData;
    if (!cy) return;
    cy.elements().remove();
    cy.add(buildElements(currentNetwork));
    cy.layout({ name: 'preset', fit: true, padding: 40 }).run();
    if (highlightedPath.length > 0) {
      highlightPath(highlightedPath);
    }
  }

  function highlightPath(pathArray) {
    highlightedPath = pathArray || [];
    if (!cy) return;

    // Reset styles
    cy.nodes().removeClass('highlighted');
    cy.edges().removeClass('path-highlighted');

    if (!pathArray || pathArray.length === 0) return;

    // Highlight nodes
    pathArray.forEach(nodeId => {
      const node = cy.getElementById(nodeId);
      if (node) node.addClass('highlighted');
    });

    // Highlight edges along path
    for (let i = 0; i < pathArray.length - 1; i++) {
      const u = pathArray[i];
      const v = pathArray[i+1];
      cy.edges().forEach(edge => {
        const src = edge.source().id();
        const tgt = edge.target().id();
        if ((src === u && tgt === v) || (src === v && tgt === u)) {
          edge.addClass('path-highlighted');
        }
      });
    }
  }

  function zoomIn() { if (cy) cy.zoom(cy.zoom() * 1.2); }
  function zoomOut() { if (cy) cy.zoom(cy.zoom() * 0.8); }
  function fitView() { if (cy) cy.fit(null, 40); }
  function resetLayout() {
    if (cy) {
      cy.layout({ name: 'preset', fit: true, padding: 40 }).run();
    }
  }

  return {
    init: init,
    updateNetwork: updateNetwork,
    highlightPath: highlightPath,
    zoomIn: zoomIn,
    zoomOut: zoomOut,
    fitView: fitView,
    resetLayout: resetLayout
  };
})();
