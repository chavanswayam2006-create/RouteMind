"""RouteMind AI - Intelligent Package Routing & Dispatch System.
Flask Application Server.
"""
import os
import json
import copy
from typing import Dict, Any
from flask import Flask, render_template, request, jsonify

# Import AI modules
from ai_modules.problem_formulation import formulate_problem, get_peas_description
from ai_modules.prolog_rules import execute_rule_query, check_swi_prolog_installed
from ai_modules.search_algorithms import breadth_first_search, depth_first_search
from ai_modules.astar_router import astar_search, compare_search_algorithms
from ai_modules.minimax import solve_minimax, run_custom_minimax, default_minimax_tree
from ai_modules.fuzzy_controller import evaluate_fuzzy_controller, SKFUZZY_AVAILABLE
from ai_modules.fuzzy_inference import compute_mamdani_and_sugeno
from ai_modules.neuro_fuzzy import evaluate_neuro_fuzzy_pipeline
from ai_modules.neural_learning import run_supervised_perceptron_experiment, run_unsupervised_clustering_experiment
from ai_modules.language_models import run_language_experiment

app = Flask(__name__)
app.config["SECRET_KEY"] = "routemind-ai-secure-lab-secret"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
NETWORK_FILE = os.path.join(DATA_DIR, "city_network.json")

# Default network definition in memory for instant resets
DEFAULT_NETWORK: Dict[str, Any] = {}

def load_initial_network():
    global DEFAULT_NETWORK
    if os.path.exists(NETWORK_FILE):
        try:
            with open(NETWORK_FILE, "r", encoding="utf-8") as f:
                DEFAULT_NETWORK = json.load(f)
        except Exception:
            DEFAULT_NETWORK = {}
    return copy.deepcopy(DEFAULT_NETWORK)

CURRENT_NETWORK: Dict[str, Any] = load_initial_network()

# Recent simulation activities log
RECENT_ACTIVITIES = [
    {
        "timestamp": "Just now",
        "action": "System Initialized",
        "detail": "Loaded default 7-node distribution topology (Hubs A through G).",
        "badge": "INFO"
    },
    {
        "timestamp": "Just now",
        "action": "Autonomous Dispatch",
        "detail": "Parcel PKG-901 flagged for High Priority dispatch from Warehouse A to Hub G.",
        "badge": "PRIORITY"
    }
]

def log_activity(action: str, detail: str, badge: str = "SIMULATION"):
    RECENT_ACTIVITIES.insert(0, {
        "timestamp": "Just now",
        "action": action,
        "detail": detail,
        "badge": badge
    })
    # Keep only the latest 15 activities
    if len(RECENT_ACTIVITIES) > 15:
        RECENT_ACTIVITIES.pop()

# -------------------------------------------------------------
# PAGE ROUTES
# -------------------------------------------------------------

@app.route("/")
def dashboard():
    return render_template(
        "index.html",
        page="dashboard",
        network=CURRENT_NETWORK,
        activities=RECENT_ACTIVITIES
    )

@app.route("/experiments")
def experiments():
    return render_template(
        "experiments.html",
        page="experiments",
        network=CURRENT_NETWORK,
        skfuzzy_available=SKFUZZY_AVAILABLE,
        swipl_available=check_swi_prolog_installed()
    )

@app.route("/network")
def network_editor():
    return render_template(
        "network.html",
        page="network",
        network=CURRENT_NETWORK
    )

@app.route("/about")
def about():
    return render_template(
        "about.html",
        page="about",
        peas=get_peas_description()
    )

# -------------------------------------------------------------
# NETWORK API ENDPOINTS
# -------------------------------------------------------------

@app.route("/api/network", methods=["GET"])
def get_network():
    return jsonify({"success": True, "network": CURRENT_NETWORK})

@app.route("/api/network/reset", methods=["POST"])
def reset_network():
    global CURRENT_NETWORK
    CURRENT_NETWORK = copy.deepcopy(DEFAULT_NETWORK)
    log_activity("Network Reset", "Restored network to default baseline topology.", "RESET")
    return jsonify({"success": True, "message": "Network restored to default state.", "network": CURRENT_NETWORK})

@app.route("/api/network/road/toggle-block", methods=["POST"])
def toggle_road_block():
    try:
        data = request.get_json() or {}
        road_id = data.get("road_id")
        found = False
        new_state = False

        for r in CURRENT_NETWORK.get("roads", []):
            if r.get("id") == road_id:
                r["is_blocked"] = not r.get("is_blocked", False)
                new_state = r["is_blocked"]
                found = True
                break

        if not found:
            return jsonify({"success": False, "error": f"Road ID '{road_id}' not found."}), 404

        status_text = "Blocked (Closure)" if new_state else "Unblocked (Open)"
        log_activity("Road Status Changed", f"Segment {road_id} is now {status_text}.", "WARNING" if new_state else "SUCCESS")
        return jsonify({"success": True, "road_id": road_id, "is_blocked": new_state, "network": CURRENT_NETWORK})
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to toggle road status: {str(e)}"}), 500

@app.route("/api/network/road/update", methods=["POST"])
def update_road():
    try:
        data = request.get_json() or {}
        road_id = data.get("road_id")
        if not road_id:
            return jsonify({"success": False, "error": "Road ID is required."}), 400

        for r in CURRENT_NETWORK.get("roads", []):
            if r.get("id") == road_id:
                if "distance_km" in data:
                    r["distance_km"] = max(0.5, float(data["distance_km"]))
                if "time_min" in data:
                    r["time_min"] = max(1.0, float(data["time_min"]))
                if "congestion_pct" in data:
                    r["congestion_pct"] = max(0, min(100, int(data["congestion_pct"])))
                if "is_blocked" in data:
                    r["is_blocked"] = bool(data["is_blocked"])

                log_activity("Road Updated", f"Modified metrics for segment {road_id}.", "UPDATE")
                return jsonify({"success": True, "road": r, "network": CURRENT_NETWORK})

        return jsonify({"success": False, "error": f"Road ID '{road_id}' not found."}), 404
    except ValueError:
        return jsonify({"success": False, "error": "Invalid numeric values provided."}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/network/road/add", methods=["POST"])
def add_road():
    try:
        data = request.get_json() or {}
        u = str(data.get("from", "")).strip().upper()
        v = str(data.get("to", "")).strip().upper()
        
        valid_nodes = {n["id"] for n in CURRENT_NETWORK.get("nodes", [])}
        if u not in valid_nodes or v not in valid_nodes:
            return jsonify({"success": False, "error": f"Nodes must be valid existing hubs: {list(valid_nodes)}"}), 400
        if u == v:
            return jsonify({"success": False, "error": "Self-loops are disallowed in this distribution network."}), 400

        # Check existing
        for r in CURRENT_NETWORK.get("roads", []):
            if (r["from"] == u and r["to"] == v) or (r["from"] == v and r["to"] == u):
                return jsonify({"success": False, "error": f"Road segment between {u} and {v} already exists."}), 400

        dist = max(0.5, float(data.get("distance_km", 15.0)))
        time_m = max(1.0, float(data.get("time_min", 20.0)))
        cong = max(0, min(100, int(data.get("congestion_pct", 20))))
        is_blocked = bool(data.get("is_blocked", False))

        new_road = {
            "id": f"{u}-{v}",
            "from": u,
            "to": v,
            "distance_km": dist,
            "time_min": time_m,
            "congestion_pct": cong,
            "is_blocked": is_blocked,
            "bidirectional": True
        }
        CURRENT_NETWORK["roads"].append(new_road)
        log_activity("Road Created", f"Added new road segment {u}-{v} ({dist}km).", "NETWORK")
        return jsonify({"success": True, "road": new_road, "network": CURRENT_NETWORK})
    except ValueError:
        return jsonify({"success": False, "error": "Invalid numeric parameters."}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/network/road/delete", methods=["POST"])
def delete_road():
    try:
        data = request.get_json() or {}
        road_id = data.get("road_id")
        orig_len = len(CURRENT_NETWORK.get("roads", []))
        CURRENT_NETWORK["roads"] = [r for r in CURRENT_NETWORK.get("roads", []) if r.get("id") != road_id]

        if len(CURRENT_NETWORK["roads"]) == orig_len:
            return jsonify({"success": False, "error": f"Road ID '{road_id}' not found."}), 404

        log_activity("Road Removed", f"Deleted road segment {road_id}.", "DELETE")
        return jsonify({"success": True, "road_id": road_id, "network": CURRENT_NETWORK})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -------------------------------------------------------------
# ROUTE PLANNING & ALGORITHM BENCHMARK APIS
# -------------------------------------------------------------

@app.route("/api/route/plan", methods=["POST"])
def plan_route():
    try:
        data = request.get_json() or {}
        start = str(data.get("start", "A")).strip().upper()
        destination = str(data.get("destination", "G")).strip().upper()
        algorithm = str(data.get("algorithm", "astar")).strip().lower()

        valid_nodes = {n["id"] for n in CURRENT_NETWORK.get("nodes", [])}
        if start not in valid_nodes or destination not in valid_nodes:
            return jsonify({
                "success": False,
                "error": f"Invalid start node '{start}' or destination '{destination}'. Available nodes: {sorted(list(valid_nodes))}"
            }), 400

        if algorithm == "bfs":
            result = breadth_first_search(CURRENT_NETWORK, start, destination)
        elif algorithm == "dfs":
            result = depth_first_search(CURRENT_NETWORK, start, destination)
        elif algorithm in ["astar", "a*"]:
            result = astar_search(CURRENT_NETWORK, start, destination, cost_criterion="time")
        elif algorithm == "compare_all":
            result = compare_search_algorithms(CURRENT_NETWORK, start, destination)
        else:
            return jsonify({"success": False, "error": f"Unknown algorithm '{algorithm}'. Choose 'bfs', 'dfs', or 'astar'."}), 400

        status_label = "Optimal Route" if result.get("found") else "No Valid Route"
        path_str = (" -> ").join(result.get("path", [])) if result.get("found") else "None"
        log_activity(
            f"Route Calculated ({algorithm.upper()})",
            f"Path: {path_str} | Status: {status_label}",
            "SUCCESS" if result.get("found") else "ALERT"
        )

        return jsonify({
            "success": True,
            "algorithm": algorithm,
            "start": start,
            "destination": destination,
            "result": result
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Route calculation failed: {str(e)}"}), 500

@app.route("/api/route/compare", methods=["POST"])
def compare_routes():
    try:
        data = request.get_json() or {}
        start = str(data.get("start", "A")).strip().upper()
        destination = str(data.get("destination", "G")).strip().upper()

        valid_nodes = {n["id"] for n in CURRENT_NETWORK.get("nodes", [])}
        if start not in valid_nodes or destination not in valid_nodes:
            return jsonify({
                "success": False,
                "error": f"Invalid start '{start}' or destination '{destination}'."
            }), 400

        benchmark = compare_search_algorithms(CURRENT_NETWORK, start, destination)
        log_activity("Search Benchmark Run", f"Compared BFS, DFS, and A* from {start} to {destination}.", "BENCHMARK")
        return jsonify({"success": True, "benchmark": benchmark})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -------------------------------------------------------------
# EXPERIMENT APIS (EXPERIMENTS 1 THROUGH 10)
# -------------------------------------------------------------

@app.route("/api/experiments/exp1/formulation", methods=["POST"])
def run_exp1_formulation():
    data = request.get_json() or {}
    start = str(data.get("start", "A")).strip().upper()
    goal = str(data.get("goal", "G")).strip().upper()
    res = formulate_problem(CURRENT_NETWORK, start, goal)
    return jsonify({"success": True, "data": res})

@app.route("/api/experiments/exp2/prolog", methods=["POST"])
def run_exp2_prolog():
    try:
        data = request.get_json() or {}
        qtype = data.get("query_type", "available_roads")
        params = data.get("params", {})
        res = execute_rule_query(CURRENT_NETWORK, qtype, params)
        return jsonify({"success": True, "data": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/experiments/exp3/uninformed", methods=["POST"])
def run_exp3_uninformed():
    try:
        data = request.get_json() or {}
        algo = data.get("algorithm", "bfs").lower()
        start = str(data.get("start", "A")).strip().upper()
        goal = str(data.get("goal", "G")).strip().upper()

        if algo == "dfs":
            res = depth_first_search(CURRENT_NETWORK, start, goal)
        else:
            res = breadth_first_search(CURRENT_NETWORK, start, goal)
        return jsonify({"success": True, "data": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/experiments/exp4/astar", methods=["POST"])
def run_exp4_astar():
    try:
        data = request.get_json() or {}
        start = str(data.get("start", "A")).strip().upper()
        goal = str(data.get("goal", "G")).strip().upper()
        criterion = data.get("criterion", "time")
        res = astar_search(CURRENT_NETWORK, start, goal, cost_criterion=criterion)
        return jsonify({"success": True, "data": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/experiments/exp5/minimax", methods=["POST"])
def run_exp5_minimax():
    try:
        data = request.get_json() or {}
        custom_leafs = data.get("custom_leafs", {})
        res = run_custom_minimax(custom_leafs)
        return jsonify({"success": True, "data": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/experiments/exp6/fuzzy", methods=["POST"])
def run_exp6_fuzzy():
    try:
        data = request.get_json() or {}
        congestion = float(data.get("congestion", 50.0))
        road_condition = float(data.get("road_condition", 5.0))
        engine_mode = data.get("engine", "auto")
        res = evaluate_fuzzy_controller(congestion, road_condition, use_engine=engine_mode)
        return jsonify({"success": True, "data": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/experiments/exp7/fuzzy_compare", methods=["POST"])
def run_exp7_fuzzy_compare():
    try:
        data = request.get_json() or {}
        dist = float(data.get("distance", 25.0))
        cong = float(data.get("congestion", 50.0))
        res = compute_mamdani_and_sugeno(dist, cong)
        return jsonify({"success": True, "data": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/experiments/exp8/neuro_fuzzy", methods=["POST"])
def run_exp8_neuro_fuzzy():
    try:
        data = request.get_json() or {}
        dist = float(data.get("distance", 22.0))
        cong = float(data.get("congestion", 45.0))
        weather = str(data.get("weather", "moderate"))
        res = evaluate_neuro_fuzzy_pipeline(dist, cong, weather)
        return jsonify({"success": True, "data": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/experiments/exp9/supervised", methods=["POST"])
def run_exp9_supervised():
    try:
        data = request.get_json() or {}
        dist = float(data.get("distance", 24.0))
        cong = float(data.get("congestion", 55.0))
        cond = float(data.get("condition", 5.5))
        res = run_supervised_perceptron_experiment(dist, cong, cond)
        return jsonify({"success": True, "data": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/experiments/exp9/unsupervised", methods=["POST"])
def run_exp9_unsupervised():
    try:
        res = run_unsupervised_clustering_experiment()
        return jsonify({"success": True, "data": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/experiments/exp10/language", methods=["POST"])
def run_exp10_language():
    try:
        data = request.get_json() or {}
        prompt = str(data.get("prompt", "high priority"))
        model = str(data.get("model", "both"))
        res = run_language_experiment(prompt, model)
        return jsonify({"success": True, "data": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Global Error Handlers (ensure no stack traces exposed)
@app.errorhandler(404)
def handle_404(e):
    return render_template("base.html", page="error", error_message="Page not found (404)"), 404

@app.errorhandler(500)
def handle_500(e):
    return jsonify({"success": False, "error": "Internal server processing error."}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
