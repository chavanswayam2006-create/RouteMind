/**
 * RouteMind AI - AI Experiments Controller Module (Experiments 1 to 10)
 */

const RouteMindExps = (function() {

  // -------------------------------------------------------------
  // EXPERIMENT 1: PEAS & FORMULATION
  // -------------------------------------------------------------
  function runExp1() {
    fetch('/api/experiments/exp1/formulation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ start: 'A', goal: 'G' })
    })
    .then(r => r.json())
    .then(data => {
      if (data.success && data.data) {
        const trace = data.data.demonstration_trace || [];
        const container = document.getElementById('exp1-output-container');
        const wrapper = document.getElementById('exp1-trace-table-wrapper');

        let html = `
          <table class="table-rm">
            <thead>
              <tr>
                <th>Step</th>
                <th>Current State (Hub)</th>
                <th>Goal Test Result</th>
                <th>Cumulative Time</th>
                <th>Cumulative Cost</th>
              </tr>
            </thead>
            <tbody>
        `;

        trace.forEach(step => {
          const badgeClass = step.is_goal ? 'badge-rm optimal' : 'badge-rm info';
          html += `
            <tr>
              <td class="mono-data">#${step.step}</td>
              <td><strong>Hub ${step.current_state}</strong> (${step.state_name})</td>
              <td><span class="${badgeClass}">${step.goal_test}</span></td>
              <td class="mono-data">${step.cumulative_time_min} min</td>
              <td class="mono-data">${step.cumulative_cost}</td>
            </tr>
          `;
        });

        html += '</tbody></table>';
        if (wrapper) wrapper.innerHTML = html;
        if (container) container.style.display = 'block';
      }
    })
    .catch(console.error);
  }

  // -------------------------------------------------------------
  // EXPERIMENT 2: PROLOG RULES
  // -------------------------------------------------------------
  function onExp2QueryChange() {
    const qtype = document.getElementById('exp2-query-type').value;
    const box = document.getElementById('exp2-params-box');
    if (!box) return;

    if (qtype === 'available_roads') {
      box.innerHTML = `
        <div class="form-group">
          <label class="form-label">Origin Hub:</label>
          <select class="form-select" id="exp2-origin-node">
            <option value="A" selected>Hub A</option>
            <option value="B">Hub B</option>
            <option value="C">Hub C</option>
            <option value="D">Hub D</option>
            <option value="E">Hub E</option>
            <option value="F">Hub F</option>
          </select>
        </div>
      `;
    } else if (qtype === 'can_dispatch') {
      box.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px;">
          <div>
            <label class="form-label" style="font-size: 11px;">From Hub:</label>
            <select class="form-select" id="exp2-dispatch-from"><option value="A" selected>A</option><option value="B">B</option><option value="D">D</option></select>
          </div>
          <div>
            <label class="form-label" style="font-size: 11px;">To Hub:</label>
            <select class="form-select" id="exp2-dispatch-to"><option value="B" selected>B</option><option value="D">D</option><option value="E">E</option></select>
          </div>
          <div>
            <label class="form-label" style="font-size: 11px;">Parcel Priority:</label>
            <select class="form-select" id="exp2-dispatch-prio"><option value="high" selected>High</option><option value="standard">Standard</option></select>
          </div>
        </div>
      `;
    } else if (qtype === 'find_paths') {
      box.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
          <div>
            <label class="form-label" style="font-size: 11px;">Start Hub:</label>
            <select class="form-select" id="exp2-path-start"><option value="A" selected>A</option><option value="B">B</option></select>
          </div>
          <div>
            <label class="form-label" style="font-size: 11px;">Goal Hub:</label>
            <select class="form-select" id="exp2-path-goal"><option value="G" selected>G</option><option value="E">E</option></select>
          </div>
        </div>
      `;
    } else {
      box.innerHTML = '<p style="font-size: 12px; color: var(--rm-text-muted);">No additional parameters needed.</p>';
    }
  }

  function runExp2() {
    const qtype = document.getElementById('exp2-query-type').value;
    const params = {};

    if (qtype === 'available_roads') {
      const nodeEl = document.getElementById('exp2-origin-node');
      params.node = nodeEl ? nodeEl.value : 'A';
    } else if (qtype === 'can_dispatch') {
      params.from = document.getElementById('exp2-dispatch-from').value;
      params.to = document.getElementById('exp2-dispatch-to').value;
      params.priority = document.getElementById('exp2-dispatch-prio').value;
    } else if (qtype === 'find_paths') {
      params.start = document.getElementById('exp2-path-start').value;
      params.goal = document.getElementById('exp2-path-goal').value;
    }

    fetch('/api/experiments/exp2/prolog', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query_type: qtype, params: params })
    })
    .then(r => r.json())
    .then(data => {
      const out = document.getElementById('exp2-results-box');
      if (out && data.success && data.data) {
        const d = data.data;
        let text = `% Engine: ${d.engine_used}\n`;
        text += `% Prolog Knowledge Base Export: ${d.prolog_kb_file}\n\n`;
        text += `Query: ${d.query_display}\n\n`;
        text += `Result Summary: ${d.explanation}\n\n`;
        text += `Unification Deductions:\n`;
        text += JSON.stringify(d.query_results, null, 2);
        out.innerText = text;
      }
    })
    .catch(console.error);
  }

  // -------------------------------------------------------------
  // EXPERIMENT 3: BFS & DFS SEARCH
  // -------------------------------------------------------------
  function runExp3() {
    const algo = document.getElementById('exp3-algo').value;
    const start = document.getElementById('exp3-start').value;
    const goal = document.getElementById('exp3-goal').value;

    fetch('/api/experiments/exp3/uninformed', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ algorithm: algo, start: start, goal: goal })
    })
    .then(r => r.json())
    .then(data => {
      if (data.success && data.data) {
        const d = data.data;
        document.getElementById('exp3-res-edges').innerText = d.edge_count || 0;
        document.getElementById('exp3-res-dist').innerText = `${d.distance_km || 0} km`;
        document.getElementById('exp3-res-time').innerText = `${d.travel_time_min || 0} min`;
        document.getElementById('exp3-res-explored').innerText = d.nodes_explored_count || 0;

        const traceBox = document.getElementById('exp3-trace-box');
        let text = `Algorithm: ${d.algorithm}\n`;
        text += `Path Found: ${(d.path || []).join(' -> ')}\n`;
        text += `Explanation: ${d.explanation}\n\n`;
        text += `Step-by-step Frontier Operations:\n`;
        (d.steps || []).forEach(s => {
          text += `Step ${s.step}: ${s.action} | Path: ${(s.current_path || []).join(' -> ')}\n`;
        });
        if (traceBox) traceBox.innerText = text;
      }
    })
    .catch(console.error);
  }

  // -------------------------------------------------------------
  // EXPERIMENT 4: A* SEARCH
  // -------------------------------------------------------------
  function runExp4() {
    const start = document.getElementById('exp4-start').value;
    const goal = document.getElementById('exp4-goal').value;
    const crit = document.getElementById('exp4-criterion').value;

    fetch('/api/experiments/exp4/astar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ start: start, goal: goal, criterion: crit })
    })
    .then(r => r.json())
    .then(data => {
      if (data.success && data.data) {
        const d = data.data;
        const tbody = document.getElementById('exp4-eval-table-body');
        let html = '';
        (d.evaluations || []).forEach(ev => {
          html += `
            <tr>
              <td class="mono-data">#${ev.step}</td>
              <td><strong>Hub ${ev.node}</strong> (${ev.node_name})</td>
              <td class="mono-data">${ev.g_cost} min</td>
              <td class="mono-data">${ev.h_cost} min</td>
              <td class="mono-data" style="color: var(--rm-teal); font-weight: 700;">${ev.f_cost}</td>
              <td class="mono-data">${ev.open_set_size}</td>
            </tr>
          `;
        });
        if (tbody) tbody.innerHTML = html;
      }
    })
    .catch(console.error);
  }

  // -------------------------------------------------------------
  // EXPERIMENT 5: MINIMAX DECISION TREE
  // -------------------------------------------------------------
  function runExp5() {
    const customLeafs = {
      north_light: parseInt(document.getElementById('minimax-leaf-1').value) || 85,
      north_rain: parseInt(document.getElementById('minimax-leaf-2').value) || 40,
      central_normal: parseInt(document.getElementById('minimax-leaf-3').value) || 70,
      central_surge: parseInt(document.getElementById('minimax-leaf-4').value) || 65,
      bypass_open: parseInt(document.getElementById('minimax-leaf-5').value) || 90,
      bypass_rail: parseInt(document.getElementById('minimax-leaf-6').value) || 30
    };

    fetch('/api/experiments/exp5/minimax', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ custom_leafs: customLeafs })
    })
    .then(r => r.json())
    .then(data => {
      if (data.success && data.data) {
        const d = data.data;
        document.getElementById('minimax-root-utility').innerText = d.root_utility;
        document.getElementById('minimax-best-decision').innerText = `Optimal Decision: ${d.best_decision}`;

        const logBox = document.getElementById('minimax-log-box');
        let text = `Backward Induction Trace:\n`;
        (d.evaluation_steps || []).forEach(st => {
          text += `[Depth ${st.depth}] ${st.type} Node '${st.node_name}': ${st.action}\n`;
        });
        if (logBox) logBox.innerText = text;
      }
    })
    .catch(console.error);
  }

  // -------------------------------------------------------------
  // EXPERIMENT 6: FUZZY CONTROLLER
  // -------------------------------------------------------------
  function runExp6() {
    const cong = parseFloat(document.getElementById('exp6-cong-slider').value) || 65;
    const cond = parseFloat(document.getElementById('exp6-cond-slider').value) || 4.5;
    const engine = document.getElementById('exp6-engine').value;

    fetch('/api/experiments/exp6/fuzzy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ congestion: cong, road_condition: cond, engine: engine })
    })
    .then(r => r.json())
    .then(data => {
      if (data.success && data.data) {
        const d = data.data;
        const scoreEl = document.getElementById('exp6-score-display');
        const badgeEl = document.getElementById('exp6-cat-badge');

        if (scoreEl) {
          scoreEl.innerText = `${d.delay_score} / 100`;
          scoreEl.style.color = d.category_color === 'danger' ? '#ef4444' : (d.category_color === 'warning' ? '#f59e0b' : '#10b981');
        }
        if (badgeEl) {
          badgeEl.className = `badge-rm ${d.category_color}`;
          badgeEl.innerText = d.output_category;
        }

        const detailsBox = document.getElementById('exp6-details-box');
        let text = `Fuzzy Engine: ${d.engine}\n\n`;
        text += `Membership Degrees:\n`;
        text += `Congestion: Low=${d.memberships.congestion.Low}, Med=${d.memberships.congestion.Medium}, High=${d.memberships.congestion.High}\n`;
        text += `Road Condition: Poor=${d.memberships.road_condition.Poor}, Fair=${d.memberships.road_condition.Fair}, Good=${d.memberships.road_condition.Good}\n\n`;
        text += `Rule Consequent Strengths:\n`;
        text += `Minimal=${d.rule_strengths.Minimal}, Moderate=${d.rule_strengths.Moderate}, Severe=${d.rule_strengths.Severe}\n`;
        if (detailsBox) detailsBox.innerText = text;
      }
    })
    .catch(console.error);
  }

  // -------------------------------------------------------------
  // EXPERIMENT 7: MAMDANI VS SUGENO
  // -------------------------------------------------------------
  function runExp7() {
    const dist = parseFloat(document.getElementById('exp7-dist-slider').value) || 28;
    const cong = parseFloat(document.getElementById('exp7-cong-slider').value) || 60;

    fetch('/api/experiments/exp7/fuzzy_compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ distance: dist, congestion: cong })
    })
    .then(r => r.json())
    .then(data => {
      if (data.success && data.data) {
        const d = data.data;
        document.getElementById('exp7-mamdani-out').innerText = `${d.mamdani_output_min} min`;
        document.getElementById('exp7-sugeno-out').innerText = `${d.sugeno_output_min} min`;

        const box = document.getElementById('exp7-comparison-box');
        let text = `Absolute Difference: ${d.difference_min} min (${d.percentage_difference}%)\n\n`;
        text += `Sugeno Linear Consequents:\n`;
        text += `z_minimal = ${d.sugeno_functions.z_minimal}\n`;
        text += `z_moderate = ${d.sugeno_functions.z_moderate}\n`;
        text += `z_high = ${d.sugeno_functions.z_high}\n\n`;
        text += `Fired Rules:\n`;
        (d.rules_fired || []).filter(r => r.firing_strength > 0).forEach(r => {
          text += `${r.rule} [w = ${r.firing_strength}]\n`;
        });
        if (box) box.innerText = text;
      }
    })
    .catch(console.error);
  }

  // -------------------------------------------------------------
  // EXPERIMENT 8: NEURO-FUZZY
  // -------------------------------------------------------------
  function runExp8() {
    const dist = parseFloat(document.getElementById('exp8-dist').value) || 25;
    const cong = parseFloat(document.getElementById('exp8-cong').value) || 65;
    const weather = document.getElementById('exp8-weather').value;

    fetch('/api/experiments/exp8/neuro_fuzzy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ distance: dist, congestion: cong, weather: weather })
    })
    .then(r => r.json())
    .then(data => {
      if (data.success && data.data) {
        const d = data.data;
        document.getElementById('exp8-nn-pred').innerText = `${d.neural_network.raw_neural_prediction_min} min`;
        document.getElementById('exp8-fuzzy-adj').innerText = `${d.fuzzy_supervisory_layer.fuzzy_adjustment_delta_min} min`;
        document.getElementById('exp8-hybrid-pred').innerText = `${d.hybrid_final_delay_min} min`;

        const box = document.getElementById('exp8-details-box');
        let text = `Neural Architecture: ${d.neural_network.architecture}\n`;
        text += `Training Dataset: ${d.neural_network.training_dataset}\n\n`;
        text += `Fuzzy Expert Supervisory Rules Activated:\n`;
        (d.fuzzy_supervisory_layer.rules_activated || []).forEach(r => text += `${r}\n`);
        text += `\nComparison: ${d.comparison.interpretation}\n`;
        if (box) box.innerText = text;
      }
    })
    .catch(console.error);
  }

  // -------------------------------------------------------------
  // EXPERIMENT 9: NEURAL LEARNING
  // -------------------------------------------------------------
  function runExp9Supervised() {
    const dist = parseFloat(document.getElementById('exp9-dist').value) || 22;
    const cong = parseFloat(document.getElementById('exp9-cong').value) || 65;
    const cond = parseFloat(document.getElementById('exp9-cond').value) || 4.0;

    fetch('/api/experiments/exp9/supervised', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ distance: dist, congestion: cong, condition: cond })
    })
    .then(r => r.json())
    .then(data => {
      if (data.success && data.data) {
        const d = data.data;
        const box = document.getElementById('exp9-sup-box');
        let text = `Perceptron Trained: ${d.epochs_trained} epochs\n`;
        text += `Final Weights: [${(d.final_weights || []).join(', ')}], Bias: ${d.final_bias}\n\n`;
        text += `Prediction for [Dist: ${dist}km, Cong: ${cong}%, Cond: ${cond}]:\n`;
        text += `Class: ${d.prediction.class_code} (${d.prediction.class_name})\n`;
        text += `Details: ${d.prediction.interpretation}\n`;
        if (box) box.innerText = text;
      }
    })
    .catch(console.error);
  }

  function runExp9Unsupervised() {
    fetch('/api/experiments/exp9/unsupervised', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      if (data.success && data.data) {
        const d = data.data;
        const box = document.getElementById('exp9-unsup-box');
        let text = `Competitive Learning (Winner-Take-All VQ):\n\n`;
        (d.cluster_profiles || []).forEach(p => {
          text += `Cluster ${p.cluster_id}: ${p.profile_label} (${p.member_count} roads)\n`;
          text += `  Centroid -> Dist: ${p.centroid.distance_km}km, Cong: ${p.centroid.congestion_pct}%, Cond: ${p.centroid.road_condition}\n\n`;
        });
        if (box) box.innerText = text;
      }
    })
    .catch(console.error);
  }

  // -------------------------------------------------------------
  // EXPERIMENT 10: LANGUAGE MODELS
  // -------------------------------------------------------------
  function runExp10() {
    const prompt = document.getElementById('exp10-prompt').value || 'high priority';

    fetch('/api/experiments/exp10/language', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: prompt })
    })
    .then(r => r.json())
    .then(data => {
      if (data.success && data.data) {
        const d = data.data;
        const box = document.getElementById('exp10-results-box');
        let text = `Corpus Vocabulary: ${d.vocabulary_size} words | Unigrams: ${d.corpus_stats.unigram_tokens} | Bigrams: ${d.corpus_stats.distinct_bigrams} | Trigrams: ${d.corpus_stats.distinct_trigrams}\n\n`;
        
        text += `1. MICRO MODEL (BIGRAM: N=2) on "${(d.bigram_micro_model.context || []).join(' ')}":\n`;
        (d.bigram_micro_model.predictions || []).slice(0, 3).forEach(p => {
          text += `   -> "${p.word}" (P = ${p.probability})\n`;
        });
        text += `   Generated: "${d.bigram_completion.generated_sentence}"\n\n`;

        text += `2. SMALL MODEL (TRIGRAM: N=3) on "${(d.trigram_small_model.context || []).join(' ')}":\n`;
        (d.trigram_small_model.predictions || []).slice(0, 3).forEach(p => {
          text += `   -> "${p.word}" (P = ${p.probability})\n`;
        });
        text += `   Generated: "${d.trigram_completion.generated_sentence}"\n\n`;

        text += `Note: ${d.educational_note}\n`;
        if (box) box.innerText = text;
      }
    })
    .catch(console.error);
  }

  return {
    runExp1: runExp1,
    onExp2QueryChange: onExp2QueryChange,
    runExp2: runExp2,
    runExp3: runExp3,
    runExp4: runExp4,
    runExp5: runExp5,
    runExp6: runExp6,
    runExp7: runExp7,
    runExp8: runExp8,
    runExp9Supervised: runExp9Supervised,
    runExp9Unsupervised: runExp9Unsupervised,
    runExp10: runExp10
  };
})();
