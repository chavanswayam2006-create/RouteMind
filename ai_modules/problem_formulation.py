"""Experiment 1: PEAS and Problem Formulation for RouteMind AI.

Formalizes the AI agent problem for the package routing and dispatch system:
- Performance measure
- Environment
- Actuators
- Sensors
- Initial State, Goal State, State Space, Actions, Transition Model, Goal Test, Path Cost.
"""
from typing import Dict, Any, List

def get_peas_description() -> Dict[str, Any]:
    return {
        "title": "PEAS Framework for Autonomous Package Routing Agent",
        "agent_type": "Goal-Based Autonomous Routing Agent",
        "performance_measure": [
            "Minimize total travel time (minutes) from dispatch warehouse to final delivery hub.",
            "Minimize cumulative route cost (distance + congestion penalties).",
            "Zero tolerance for traversing blocked road segments (safety & SLA constraint).",
            "Maximize on-time delivery rate for high-priority packages."
        ],
        "environment": [
            "Interconnected city distribution network with 7 primary distribution hubs (A through G).",
            "Dynamic road segment conditions: distance (km), estimated time, and congestion (0-100%).",
            "Static and dynamic road blockages (construction, emergency closures).",
            "Deterministic transitions between connected, unblocked hubs."
        ],
        "actuators": [
            "Dispatch instruction generator (authorizes courier departure).",
            "Route selector (recommends optimal sequence of hubs: e.g. A -> D -> E -> G).",
            "Dynamic re-routing trigger (updates path if intermediate road segment is blocked).",
            "Courier telemetry notifications (ETA, milestone alerts sent to destination hub)."
        ],
        "sensors": [
            "Road blockage status sensors (binary: unblocked/blocked).",
            "Traffic congestion sensors (percentage: 0-100%).",
            "Transit time and distance telemetric estimators.",
            "Hub arrival confirmation sensors (GPS geofencing)."
        ],
        "environment_properties": {
            "observability": "Fully Observable (the agent has access to complete network topology & live road states)",
            "deterministic_vs_stochastic": "Deterministic (moving from node X along road X-Y reliably lands at node Y)",
            "episodic_vs_sequential": "Sequential (current dispatch choice affects available subsequent branches)",
            "static_vs_dynamic": "Static during route calculation, Semi-Dynamic when road blockages occur",
            "discrete_vs_continuous": "Discrete (finite hubs, discrete road connections)",
            "single_vs_multiagent": "Single-Agent (dispatch optimization from the warehouse's perspective)"
        }
    }

def formulate_problem(network_data: Dict[str, Any], start_node: str = "A", goal_node: str = "G") -> Dict[str, Any]:
    """Generates the formal state-space problem formulation based on current network state."""
    nodes = {n["id"]: n for n in network_data.get("nodes", [])}
    roads = network_data.get("roads", [])
    
    # State space
    state_space = list(nodes.keys())
    
    # Build adjacency with actions
    actions_map: Dict[str, List[Dict[str, Any]]] = {n_id: [] for n_id in state_space}
    for road in roads:
        if not road.get("is_blocked", False):
            u, v = road["from"], road["to"]
            dist, time_m = road["distance_km"], road["time_min"]
            cong = road.get("congestion_pct", 0)
            cost = round(time_m * (1.0 + cong / 100.0), 2)
            
            if u in actions_map:
                actions_map[u].append({
                    "action": f"Transit({u} -> {v})",
                    "target_state": v,
                    "distance_km": dist,
                    "time_min": time_m,
                    "congestion_pct": cong,
                    "step_cost": cost
                })
            if road.get("bidirectional", True) and v in actions_map:
                actions_map[v].append({
                    "action": f"Transit({v} -> {u})",
                    "target_state": u,
                    "distance_km": dist,
                    "time_min": time_m,
                    "congestion_pct": cong,
                    "step_cost": cost
                })
                
    # Validate start and goal
    valid_start = start_node in nodes
    valid_goal = goal_node in nodes
    
    # Simulate a step-by-step state space traversal demo to demonstrate goal test
    simulation_trace = []
    current = start_node
    visited = set()
    total_cost = 0.0
    total_time = 0.0
    goal_reached = False
    
    # Simple greedy search simulation for step-by-step goal test demonstration
    while current and current not in visited:
        visited.add(current)
        is_goal = (current == goal_node)
        simulation_trace.append({
            "step": len(simulation_trace) + 1,
            "current_state": current,
            "state_name": nodes[current]["name"] if current in nodes else current,
            "goal_test": f"GoalTest({current} == {goal_node}) -> {'SUCCESS (GOAL REACHED)' if is_goal else 'FALSE (CONTINUE SEARCH)'}",
            "is_goal": is_goal,
            "cumulative_time_min": round(total_time, 2),
            "cumulative_cost": round(total_cost, 2)
        })
        if is_goal:
            goal_reached = True
            break
            
        # Choose best available action towards goal
        candidates = [a for a in actions_map.get(current, []) if a["target_state"] not in visited]
        if not candidates:
            break
        # Pick action with lowest step_cost
        best_action = min(candidates, key=lambda a: a["step_cost"])
        total_cost += best_action["step_cost"]
        total_time += best_action["time_min"]
        current = best_action["target_state"]
        
    return {
        "peas": get_peas_description(),
        "formulation": {
            "initial_state": {
                "id": start_node,
                "label": nodes.get(start_node, {}).get("name", "Unknown Start"),
                "valid": valid_start
            },
            "goal_state": {
                "id": goal_node,
                "label": nodes.get(goal_node, {}).get("name", "Unknown Goal"),
                "valid": valid_goal
            },
            "state_space_size": len(state_space),
            "state_space": state_space,
            "actions_definition": "Actions(s) = { Transit(s -> s') | Road(s, s') exists and is_blocked == False }",
            "transition_model": "Result(s, Transit(s -> s')) = s'",
            "goal_test_definition": "GoalTest(s) = True if s == GoalState else False",
            "path_cost_definition": "Cost(path) = sum( travel_time * (1 + congestion_pct / 100) ) over each traversed segment"
        },
        "available_actions_by_state": actions_map,
        "demonstration_trace": simulation_trace,
        "goal_reached": goal_reached
    }
