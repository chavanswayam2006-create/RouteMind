"""Experiment 4: Informed Search: A* Router for RouteMind AI.

Implements A* Search Algorithm:
f(n) = g(n) + h(n)
- g(n): Accumulated travel time / path cost from start to node n.
- h(n): Admissible heuristic (scaled Euclidean straight-line distance to goal hub).
- Guarantees optimal path when heuristic is admissible and consistent.
- Avoids blocked road segments.
"""
import math
import heapq
from typing import Dict, Any, List, Set, Tuple

def calculate_heuristic(node_id: str, goal_id: str, nodes_dict: Dict[str, Dict[str, Any]]) -> float:
    """Calculates admissible straight-line distance heuristic scaled to travel time.
    h(n) <= true remaining transit time (admissible).
    """
    if node_id == goal_id:
        return 0.0
    u = nodes_dict.get(node_id)
    v = nodes_dict.get(goal_id)
    if not u or not v or "x" not in u or "x" not in v:
        return 0.0
    # Euclidean distance in coordinate space (scaled by 0.05 to ensure strict admissibility)
    dx = float(u["x"] - v["x"])
    dy = float(u["y"] - v["y"])
    euclidean = math.sqrt(dx * dx + dy * dy)
    # Average speed factor to keep heuristic strictly less than or equal to true transit time
    h_val = euclidean * 0.035
    return round(h_val, 2)

def astar_search(network_data: Dict[str, Any], start: str, goal: str, cost_criterion: str = "time") -> Dict[str, Any]:
    """Runs A* search on the network.
    cost_criterion: 'time' (travel time in minutes) or 'weighted_cost' (time * congestion factor).
    """
    nodes_dict = {n["id"]: n for n in network_data.get("nodes", [])}
    if start not in nodes_dict or goal not in nodes_dict:
        return {
            "algorithm": "A* Informed Search",
            "found": False,
            "error": f"Invalid start node '{start}' or goal node '{goal}'.",
            "path": [],
            "explored_nodes": []
        }

    if start == goal:
        return {
            "algorithm": "A* Informed Search",
            "found": True,
            "path": [start],
            "edge_count": 0,
            "distance_km": 0.0,
            "travel_time_min": 0.0,
            "route_cost": 0.0,
            "explored_nodes": [start],
            "node_heuristics": {start: 0.0},
            "evaluations": [],
            "explanation": "Start and goal nodes are identical. Zero transit required."
        }

    # Build adjacency excluding blocked edges
    adj: Dict[str, List[Dict[str, Any]]] = {n_id: [] for n_id in nodes_dict}
    roads_map = {}
    for r in network_data.get("roads", []):
        if not r.get("is_blocked", False):
            u, v = r["from"], r["to"]
            dist, time_m = float(r["distance_km"]), float(r["time_min"])
            cong = int(r.get("congestion_pct", 0))
            step_cost = time_m if cost_criterion == "time" else time_m * (1.0 + cong / 100.0)
            
            roads_map[(u, v)] = r
            adj[u].append({"to": v, "cost": step_cost, "dist": dist, "time": time_m, "cong": cong})
            if r.get("bidirectional", True):
                roads_map[(v, u)] = r
                adj[v].append({"to": u, "cost": step_cost, "dist": dist, "time": time_m, "cong": cong})

    # Pre-calculate heuristics for all nodes
    heuristics = {nid: calculate_heuristic(nid, goal, nodes_dict) for nid in nodes_dict}

    # Priority queue: (f_score, g_score, current_node, path)
    h_start = heuristics[start]
    open_heap = []
    # tie-breaker counter
    counter = 0
    heapq.heappush(open_heap, (h_start, 0.0, counter, start, [start]))
    
    # Track lowest g_score seen for each node
    g_scores = {nid: float("inf") for nid in nodes_dict}
    g_scores[start] = 0.0
    
    closed_set: Set[str] = set()
    explored_nodes: List[str] = []
    evaluations: List[Dict[str, Any]] = []
    step_num = 0

    while open_heap:
        f_val, g_val, _, current, path = heapq.heappop(open_heap)

        if current in closed_set:
            continue
        closed_set.add(current)
        explored_nodes.append(current)
        step_num += 1

        evaluations.append({
            "step": step_num,
            "node": current,
            "node_name": nodes_dict[current]["name"],
            "g_cost": round(g_val, 2),
            "h_cost": round(heuristics[current], 2),
            "f_cost": round(f_val, 2),
            "path_so_far": list(path),
            "open_set_size": len(open_heap)
        })

        if current == goal:
            # Reconstruct exact path distance and time
            total_dist = 0.0
            total_time = 0.0
            total_cost = 0.0
            for i in range(len(path) - 1):
                u_n, v_n = path[i], path[i+1]
                edge = roads_map.get((u_n, v_n))
                if edge:
                    total_dist += float(edge["distance_km"])
                    total_time += float(edge["time_min"])
                    cong = int(edge.get("congestion_pct", 0))
                    total_cost += float(edge["time_min"]) * (1.0 + cong / 100.0)

            return {
                "algorithm": "A* Informed Search",
                "found": True,
                "path": path,
                "edge_count": len(path) - 1,
                "distance_km": round(total_dist, 2),
                "travel_time_min": round(total_time, 2),
                "route_cost": round(total_cost, 2),
                "explored_nodes": explored_nodes,
                "nodes_explored_count": len(explored_nodes),
                "node_heuristics": heuristics,
                "evaluations": evaluations,
                "properties": {
                    "formula": "f(n) = g(n) + h(n)",
                    "heuristic_type": "Admissible Euclidean straight-line distance scaled to transit minutes",
                    "admissibility": "h(n) <= h*(n) (guarantees optimal shortest-cost path)",
                    "optimality": "Optimal and Complete"
                },
                "explanation": f"A* identified the mathematically optimal path {(' -> ').join(path)} (estimated travel time: {round(total_time, 2)} min, total distance: {round(total_dist, 2)} km) after evaluating {len(explored_nodes)} nodes."
            }

        for edge in adj.get(current, []):
            nxt = edge["to"]
            step_cost = edge["cost"]
            tentative_g = g_val + step_cost

            if tentative_g < g_scores[nxt]:
                g_scores[nxt] = tentative_g
                h_nxt = heuristics[nxt]
                f_nxt = tentative_g + h_nxt
                counter += 1
                heapq.heappush(open_heap, (f_nxt, tentative_g, counter, nxt, path + [nxt]))

    return {
        "algorithm": "A* Informed Search",
        "found": False,
        "path": [],
        "edge_count": 0,
        "distance_km": 0.0,
        "travel_time_min": 0.0,
        "route_cost": 0.0,
        "explored_nodes": explored_nodes,
        "nodes_explored_count": len(explored_nodes),
        "node_heuristics": heuristics,
        "evaluations": evaluations,
        "explanation": f"A* explored all accessible reachable nodes from '{start}', but no unblocked path reaches '{goal}'."
    }

def compare_search_algorithms(network_data: Dict[str, Any], start: str = "A", goal: str = "G") -> Dict[str, Any]:
    """Runs BFS, DFS, and A* on the same network and produces a side-by-side benchmark comparison."""
    from ai_modules.search_algorithms import breadth_first_search, depth_first_search
    
    bfs_res = breadth_first_search(network_data, start, goal)
    dfs_res = depth_first_search(network_data, start, goal)
    astar_res = astar_search(network_data, start, goal, cost_criterion="time")
    
    comparison_table = [
        {
            "algorithm": "Breadth-First Search (BFS)",
            "type": "Uninformed (Blind)",
            "strategy": "FIFO Queue (Level-by-level)",
            "path": (" -> ").join(bfs_res.get("path", [])) if bfs_res.get("found") else "No Route",
            "edges": bfs_res.get("edge_count", 0),
            "distance_km": bfs_res.get("distance_km", 0.0),
            "time_min": bfs_res.get("travel_time_min", 0.0),
            "cost": bfs_res.get("route_cost", 0.0),
            "nodes_explored": bfs_res.get("nodes_explored_count", 0),
            "optimal_edges": True,
            "optimal_time": False,
            "status": "Found Path" if bfs_res.get("found") else "Failed"
        },
        {
            "algorithm": "Depth-First Search (DFS)",
            "type": "Uninformed (Blind)",
            "strategy": "LIFO Stack (Deep branch first)",
            "path": (" -> ").join(dfs_res.get("path", [])) if dfs_res.get("found") else "No Route",
            "edges": dfs_res.get("edge_count", 0),
            "distance_km": dfs_res.get("distance_km", 0.0),
            "time_min": dfs_res.get("travel_time_min", 0.0),
            "cost": dfs_res.get("route_cost", 0.0),
            "nodes_explored": dfs_res.get("nodes_explored_count", 0),
            "optimal_edges": False,
            "optimal_time": False,
            "status": "Found Path" if dfs_res.get("found") else "Failed"
        },
        {
            "algorithm": "A* Search",
            "type": "Informed (Heuristic)",
            "strategy": "Priority Queue (f = g + h)",
            "path": (" -> ").join(astar_res.get("path", [])) if astar_res.get("found") else "No Route",
            "edges": astar_res.get("edge_count", 0),
            "distance_km": astar_res.get("distance_km", 0.0),
            "time_min": astar_res.get("travel_time_min", 0.0),
            "cost": astar_res.get("route_cost", 0.0),
            "nodes_explored": astar_res.get("nodes_explored_count", 0),
            "optimal_edges": False,
            "optimal_time": True,
            "status": "Optimal Route" if astar_res.get("found") else "Failed"
        }
    ]
    
    return {
        "start_node": start,
        "goal_node": goal,
        "bfs": bfs_res,
        "dfs": dfs_res,
        "astar": astar_res,
        "comparison_table": comparison_table
    }
