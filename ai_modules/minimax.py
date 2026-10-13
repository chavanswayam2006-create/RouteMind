"""Experiment 5: Minimax Game-Theoretic Decision Tree for RouteMind AI.

Educational decision-making simulation modeling competing dispatch scenarios:
- MAX Player: Central Dispatch Planner (aims to maximize dispatch efficiency / delivery utility).
- MIN Player: Adversarial / Unfavorable Traffic Environment (e.g., peak-hour surge, road constriction, adverse weather delays).
- Demonstrates tree evaluation, leaf utilities, backward induction (minimax backup values), and optimal branch choice.
- Clearly notes this is an educational adversarial decision model, not the primary graph-search router.
"""
from typing import Dict, Any, List

def default_minimax_tree() -> Dict[str, Any]:
    """Default 2-ply (3-level) logistics decision tree:
    Root (MAX: Dispatch Route Selection)
      -> Branch 1: North Expressway (MIN: Traffic Condition)
           -> Leaf A1: Clear Weather, Light Traffic (Utility = 85)
           -> Leaf A2: Rainstorm / Slowdown (Utility = 40)
      -> Branch 2: Central Arterial (MIN: Traffic Condition)
           -> Leaf B1: Standard Flow (Utility = 70)
           -> Leaf B2: Downtown Chokepoint Surge (Utility = 65)
      -> Branch 3: Industrial By-pass (MIN: Traffic Condition)
           -> Leaf C1: Open Freight Corridor (Utility = 90)
           -> Leaf C2: Rail Crossing Closure (Utility = 30)
    """
    return {
        "id": "root",
        "name": "Route Selection (MAX: Dispatcher)",
        "player": "MAX",
        "children": [
            {
                "id": "north_expressway",
                "name": "Decision 1: North Expressway",
                "player": "MIN",
                "children": [
                    {"id": "north_light", "name": "Light Traffic Scenario", "utility": 85, "player": "LEAF"},
                    {"id": "north_rain", "name": "Rain & Bottleneck", "utility": 40, "player": "LEAF"}
                ]
            },
            {
                "id": "central_arterial",
                "name": "Decision 2: Central Arterial",
                "player": "MIN",
                "children": [
                    {"id": "central_normal", "name": "Standard Flow", "utility": 70, "player": "LEAF"},
                    {"id": "central_surge", "name": "Downtown Peak Surge", "utility": 65, "player": "LEAF"}
                ]
            },
            {
                "id": "industrial_bypass",
                "name": "Decision 3: Industrial Bypass",
                "player": "MIN",
                "children": [
                    {"id": "bypass_open", "name": "Open Freight Corridor", "utility": 90, "player": "LEAF"},
                    {"id": "bypass_rail", "name": "Rail Crossing Halt", "utility": 30, "player": "LEAF"}
                ]
            }
        ]
    }

def solve_minimax(tree_data: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluates the decision tree using Minimax backward induction."""
    evaluation_log = []

    def evaluate_node(node: Dict[str, Any], depth: int = 0) -> int:
        if "utility" in node or not node.get("children"):
            val = int(node.get("utility", 0))
            node["minimax_val"] = val
            evaluation_log.append({
                "depth": depth,
                "node_id": node["id"],
                "node_name": node["name"],
                "type": "LEAF",
                "value": val,
                "action": f"Static Leaf Utility evaluated = {val}"
            })
            return val

        player = node.get("player", "MAX")
        if player == "MAX":
            best_val = -float("inf")
            best_child = None
            for child in node["children"]:
                val = evaluate_node(child, depth + 1)
                if val > best_val:
                    best_val = val
                    best_child = child
            node["minimax_val"] = int(best_val)
            node["best_child_id"] = best_child["id"] if best_child else None
            node["best_child_name"] = best_child["name"] if best_child else ""
            evaluation_log.append({
                "depth": depth,
                "node_id": node["id"],
                "node_name": node["name"],
                "type": "MAX",
                "value": int(best_val),
                "action": f"MAX selected max({[c['minimax_val'] for c in node['children']]}) = {int(best_val)} via {node['best_child_name']}"
            })
            return int(best_val)
        else: # MIN player
            best_val = float("inf")
            best_child = None
            for child in node["children"]:
                val = evaluate_node(child, depth + 1)
                if val < best_val:
                    best_val = val
                    best_child = child
            node["minimax_val"] = int(best_val)
            node["best_child_id"] = best_child["id"] if best_child else None
            node["best_child_name"] = best_child["name"] if best_child else ""
            evaluation_log.append({
                "depth": depth,
                "node_id": node["id"],
                "node_name": node["name"],
                "type": "MIN",
                "value": int(best_val),
                "action": f"MIN selected min({[c['minimax_val'] for c in node['children']]}) = {int(best_val)} via {node['best_child_name']}"
            })
            return int(best_val)

    root_utility = evaluate_node(tree_data, 0)
    best_decision = tree_data.get("best_child_name", "Unknown Decision")
    
    return {
        "root_utility": root_utility,
        "best_decision": best_decision,
        "evaluated_tree": tree_data,
        "evaluation_steps": evaluation_log,
        "educational_context": {
            "purpose": "Simulates robust decision making under adversarial traffic uncertainty.",
            "why_minimax": "Guarantees the best worst-case outcome (MaxiMin principle). Even if traffic conditions turn worst-case, the chosen strategy provides the highest guaranteed utility.",
            "notice": "This is an independent pedagogical module demonstrating game-theoretic AI. Graph routing is handled by graph search (BFS/DFS/A*)."
        }
    }

def run_custom_minimax(custom_leaf_utilities: Dict[str, int]) -> Dict[str, Any]:
    """Allows user to customize the 6 leaf values and observe minimax recomputation."""
    tree = default_minimax_tree()
    # Apply custom utilities if provided
    for branch in tree["children"]:
        for leaf in branch["children"]:
            leaf_id = leaf["id"]
            if leaf_id in custom_leaf_utilities:
                leaf["utility"] = int(custom_leaf_utilities[leaf_id])
    return solve_minimax(tree)
