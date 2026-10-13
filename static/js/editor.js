/**
 * RouteMind AI - Network Topology Editor Module
 */

const RouteMindEditor = (function() {

  function toggleBlock(roadId) {
    fetch('/api/network/road/toggle-block', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ road_id: roadId })
    })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        const btn = document.getElementById(`editor-btn-block-${roadId}`);
        if (btn) {
          btn.className = `badge-rm ${data.is_blocked ? 'danger' : 'success'}`;
          btn.innerText = data.is_blocked ? 'BLOCKED' : 'OPEN';
        }
      } else {
        alert(data.error || 'Failed to toggle status.');
      }
    })
    .catch(console.error);
  }

  function saveRoad(roadId) {
    const dist = parseFloat(document.getElementById(`edit-dist-${roadId}`).value);
    const time_m = parseFloat(document.getElementById(`edit-time-${roadId}`).value);
    const cong = parseInt(document.getElementById(`edit-cong-${roadId}`).value);

    fetch('/api/network/road/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        road_id: roadId,
        distance_km: dist,
        time_min: time_m,
        congestion_pct: cong
      })
    })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        alert(`Road ${roadId} metrics saved successfully!`);
      } else {
        alert('Update failed: ' + data.error);
      }
    })
    .catch(console.error);
  }

  function deleteRoad(roadId) {
    if (!confirm(`Are you sure you want to delete road segment ${roadId}?`)) return;

    fetch('/api/network/road/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ road_id: roadId })
    })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        const row = document.getElementById(`row-road-${roadId}`);
        if (row) row.remove();
      } else {
        alert('Delete failed: ' + data.error);
      }
    })
    .catch(console.error);
  }

  function addRoad() {
    const fromNode = document.getElementById('new-road-from').value;
    const toNode = document.getElementById('new-road-to').value;
    const dist = parseFloat(document.getElementById('new-road-dist').value);
    const time_m = parseFloat(document.getElementById('new-road-time').value);
    const cong = parseInt(document.getElementById('new-road-cong').value);
    const blocked = document.getElementById('new-road-blocked').checked;

    fetch('/api/network/road/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: fromNode,
        to: toNode,
        distance_km: dist,
        time_min: time_m,
        congestion_pct: cong,
        is_blocked: blocked
      })
    })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        alert(`Road ${fromNode}-${toNode} added successfully!`);
        location.reload();
      } else {
        alert('Failed to add road: ' + data.error);
      }
    })
    .catch(console.error);
  }

  function resetNetwork() {
    if (!confirm("Reset city network topology to default configuration?")) return;
    fetch('/api/network/reset', { method: 'POST' })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          location.reload();
        }
      })
      .catch(console.error);
  }

  return {
    toggleBlock: toggleBlock,
    saveRoad: saveRoad,
    deleteRoad: deleteRoad,
    addRoad: addRoad,
    resetNetwork: resetNetwork
  };
})();
