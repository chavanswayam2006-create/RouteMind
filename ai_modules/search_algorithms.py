"""Experiment 3: Uninformed Search Algorithms (BFS & DFS) for RouteMind AI.

Genuine implementation of Breadth-First Search (FIFO queue) and Depth-First Search (LIFO stack).
- Explores city network distribution graph avoiding blocked roads.
- Tracks step-by-step frontier, visited nodes, path, edge counts, and execution metrics.
- Highlights that BFS guarantees minimum hops (edges), while DFS dives deep and backtracks.
"""
from collections import deque
from typing import Dict, Any, List, Set, Tuple

def build_adjacency(network_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Constructs adjacency list ignoring blocked roads."""
    adj: Dict[str, List[Dict[str, Any]]] = {}
    for node in network_data.get("nodes", []):
        adj[node["id"]] = []
        
    for road in network_data.get("roads", []):
        if not road.get("is_blocked", False):
            u, v = road["from"], road["to"]
            dist, time_m = float(road["distance_km"]), float(road["time_min"])
            cong = int(road.get("congestion_pct", 0))
            
            if u in adj:
                adj[u].append({"to": v, "dist": dist, "time": time_m, "cong": cong, "road_id": road.get("id", f"{u}-{v}")})
            if road.get("bidirectional", True) and v in adj:
                adj[v].append({"to": u, "dist": dist, "time": time_m, "cong": cong, "road_id": road.get("id", f"{v}-{u}")})
                
    # Sort neighbors alphabetically for deterministic, reproducible traversal order
    for u in adj:
        adj[u].sort(key=lambda x: x["to"])
    return adj

def get_path_metrics(path: List[str], network_data: Dict[str, Any]) -> Tuple[float, float, float]:
    """Calculates total distance (km), travel time (min), and congestion-adjusted cost for a path."""
    if len(path) <= 1:
        return 0.0, 0.0, 0.0
    roads_map = {}
    for r in network_data.get("roads", []):
        u, v = r["from"], r["to"]
        roads_map[(u, v)] = r
        if r.get("bidirectional", True):
            roads_map[(v, u)] = r
            
    total_dist = 0.0
    total_time = 0.0
    total_cost = 0.0
    
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        r = roads_map.get((u, v))
        if r:
            dist = float(r["distance_km"])
            time_m = float(r["time_min"])
            cong = int(r.get("congestion_pct", 0))
            cost = time_m * (1.0 + cong / 100.0)
            total_dist += dist
            total_time += time_m
            total_cost += cost
            
    return round(total_dist, 2), round(total_time, 2), round(total_cost, 2)

def breadth_first_search(network_data: Dict[str, Any], start: str, goal: str) -> Dict[str, Any]:
    """Genuine Breadth-First Search using a FIFO queue.
    Guarantees finding the path with the fewest edges in unweighted graph.
    """
    valid_nodes = {n["id"] for n in network_data.get("nodes", [])}
    if start not in valid_nodes or goal not in valid_nodes:
        return {
            "algorithm": "Breadth-First Search (BFS)",
            "found": False,
            "error": f"Invalid start node '{start}' or goal node '{goal}'.",
            "path": [],
            "explored_nodes": []
        }
        
    if start == goal:
        return {
            "algorithm": "Breadth-First Search (BFS)",
            "found": True,
            "path": [start],
            "edge_count": 0,
            "distance_km": 0.0,
            "travel_time_min": 0.0,
            "route_cost": 0.0,
            "explored_nodes": [start],
            "steps": [{"step": 1, "action": "Start equals Goal", "node": start, "queue": []}],
            "explanation": "Start and goal nodes are identical. Zero transit required."
        }
        
    adj = build_adjacency(network_data)
    
    # FIFO queue of paths: deque([[start]])
    queue = deque([[start]])
    visited: Set[str] = {start}
    explored_order: List[str] = []
    step_log: List[Dict[str, Any]] = []
    step_num = 0

    while queue:
        current_path = queue.popleft()
        current_node = current_path[-1]
        explored_order.append(current_node)
        step_num += 1

        step_log.append({
            "step": step_num,
            "current_node": current_node,
            "current_path": list(current_path),
            "queue_state": [p[-1] for p in queue],
            "action": f"Expanded node {current_node}"
        })

        if current_node == goal:
            dist, time_m, cost = get_path_metrics(current_path, network_data)
            return {
                "algorithm": "Breadth-First Search (BFS)",
                "found": True,
                "path": current_path,
                "edge_count": len(current_path) - 1,
                "distance_km": dist,
                "travel_time_min": time_m,
                "route_cost": cost,
                "explored_nodes": explored_order,
                "nodes_explored_count": len(explored_order),
                "steps": step_log,
                "properties": {
                    "strategy": "FIFO Queue (Layer by Layer)",
                    "completeness": "Complete (always finds a solution if one exists)",
                    "optimality": "Optimal in terms of number of road segments (hops/edges), not necessarily travel time",
                    "time_complexity": "O(b^d)",
                    "space_complexity": "O(b^d)"
                },
                "explanation": f"BFS found path {(' -> ').join(current_path)} in {len(current_path) - 1} hops after exploring {len(explored_order)} nodes."
            }

        for neighbor in adj.get(current_node, []):
            nxt = neighbor["to"]
            if nxt not in visited:
                visited.add(nxt)
                new_path = list(current_path) + [nxt]
                queue.append(new_path)

    return {
        "algorithm": "Breadth-First Search (BFS)",
        "found": False,
        "path": [],
        "edge_count": 0,
        "distance_km": 0.0,
        "travel_time_min": 0.0,
        "route_cost": 0.0,
        "explored_nodes": explored_order,
        "nodes_explored_count": len(explored_order),
        "steps": step_log,
        "explanation": f"No unblocked route exists between '{start}' and '{goal}'. All potential paths are obstructed."
    }

def depth_first_search(network_data: Dict[str, Any], start: str, goal: str) -> Dict[str, Any]:
    """Genuine Depth-First Search using a LIFO stack.
    Explores deepest branch before backtracking. Does NOT guarantee shortest path.
    """
    valid_nodes = {n["id"] for n in network_data.get("nodes", [])}
    if start not in valid_nodes or goal not in valid_nodes:
        return {
            "algorithm": "Depth-First Search (DFS)",
            "found": False,
            "error": f"Invalid start node '{start}' or goal node '{goal}'.",
            "path": [],
            "explored_nodes": []
        }
        
    if start == goal:
        return {
            "algorithm": "Depth-First Search (DFS)",
            "found": True,
            "path": [start],
            "edge_count": 0,
            "distance_km": 0.0,
            "travel_time_min": 0.0,
            "route_cost": 0.0,
            "explored_nodes": [start],
            "steps": [{"step": 1, "action": "Start equals Goal", "node": start, "stack": []}],
            "explanation": "Start and goal nodes are identical. Zero transit required."
        }
        
    adj = build_adjacency(network_data)
    
    # LIFO stack of paths: list([[start]])
    stack = [[start]]
    visited: Set[str] = set()
    explored_order: List[str] = []
    step_log: List[Dict[str, Any]] = []
    step_num = 0

    while stack:
        current_path = stack.pop()
        current_node = current_path[-1]
        
        if current_node in visited:
            continue
        visited.add(current_node)
        explored_order.append(current_node)
        step_num += 1

        step_log.append({
            "step": step_num,
            "current_node": current_node,
            "current_path": list(current_path),
            "stack_state": [p[-1] for p in stack],
            "action": f"Popped node {current_node} from stack"
        })

        if current_node == goal:
            dist, time_m, cost = get_path_metrics(current_path, network_data)
            return {
                "algorithm": "Depth-First Search (DFS)",
                "found": True,
                "path": current_path,
                "edge_count": len(current_path) - 1,
                "distance_km": dist,
                "travel_time_min": time_m,
                "route_cost": cost,
                "explored_nodes": explored_order,
                "nodes_explored_count": len(explored_order),
                "steps": step_log,
                "properties": {
                    "strategy": "LIFO Stack (Deep Branch First)",
                    "completeness": "Complete in finite acyclic graphs",
                    "optimality": "Non-Optimal (does NOT guarantee fewest edges or shortest time)",
                    "time_complexity": "O(b^m)",
                    "space_complexity": "O(b*m) - highly memory efficient"
                },
                "explanation": f"DFS found path {(' -> ').join(current_path)} in {len(current_path) - 1} hops after exploring {len(explored_order)} nodes (deepest branch first)."
            }

        # Push neighbors in reverse order so the first neighbor is explored first
        neighbors = adj.get(current_node, [])
        for neighbor in reversed(neighbors):
            nxt = neighbor["to"]
            if nxt not in visited:
                new_path = list(current_path) + [nxt]
                stack.append(new_path)

    return {
        "algorithm": "Depth-First Search (DFS)",
        "found": False,
        "path": [],
        "edge_count": 0,
        "distance_km": 0.0,
        "travel_time_min": 0.0,
        "route_cost": 0.0,
        "explored_nodes": explored_order,
        "nodes_explored_count": len(explored_order),
        "steps": step_log,
        "explanation": f"No unblocked route exists between '{start}' and '{goal}'. Graph search terminated with exhausted stack."
    }
