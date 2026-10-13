"""RouteMind AI - Flask Application Integration Tests.
Verifies all web pages and REST API endpoints.
"""
import unittest
import json
from app import app

class TestFlaskEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_pages_load_200(self):
        pages = ["/", "/experiments", "/network", "/about"]
        for p in pages:
            res = self.client.get(p)
            self.assertEqual(res.status_code, 200, f"Page {p} failed to load.")
        print("  [PASS] All 4 UI pages load successfully with HTTP 200.")

    def test_get_network_api(self):
        res = self.client.get("/api/network")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("roads", data["network"])
        self.assertIn("nodes", data["network"])
        print("  [PASS] GET /api/network returned network structure.")

    def test_plan_route_api(self):
        res = self.client.post("/api/route/plan", json={"start": "A", "destination": "G", "algorithm": "astar"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["result"]["found"])
        print("  [PASS] POST /api/route/plan successfully found route.")

    def test_compare_routes_api(self):
        res = self.client.post("/api/route/compare", json={"start": "A", "destination": "G"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["benchmark"]["comparison_table"]), 3)
        print("  [PASS] POST /api/route/compare returned BFS, DFS, and A* benchmark table.")

    def test_experiments_api_endpoints(self):
        # Exp 1
        r1 = self.client.post("/api/experiments/exp1/formulation", json={"start": "A", "goal": "G"})
        self.assertEqual(r1.status_code, 200)
        # Exp 2
        r2 = self.client.post("/api/experiments/exp2/prolog", json={"query_type": "available_roads", "params": {"node": "A"}})
        self.assertEqual(r2.status_code, 200)
        # Exp 3
        r3 = self.client.post("/api/experiments/exp3/uninformed", json={"algorithm": "bfs", "start": "A", "goal": "G"})
        self.assertEqual(r3.status_code, 200)
        # Exp 4
        r4 = self.client.post("/api/experiments/exp4/astar", json={"start": "A", "goal": "G", "criterion": "time"})
        self.assertEqual(r4.status_code, 200)
        # Exp 5
        r5 = self.client.post("/api/experiments/exp5/minimax", json={"custom_leafs": {}})
        self.assertEqual(r5.status_code, 200)
        # Exp 6
        r6 = self.client.post("/api/experiments/exp6/fuzzy", json={"congestion": 50, "road_condition": 6})
        self.assertEqual(r6.status_code, 200)
        # Exp 7
        r7 = self.client.post("/api/experiments/exp7/fuzzy_compare", json={"distance": 25, "congestion": 40})
        self.assertEqual(r7.status_code, 200)
        # Exp 8
        r8 = self.client.post("/api/experiments/exp8/neuro_fuzzy", json={"distance": 20, "congestion": 50, "weather": "moderate"})
        self.assertEqual(r8.status_code, 200)
        # Exp 9 supervised & unsupervised
        r9s = self.client.post("/api/experiments/exp9/supervised", json={"distance": 20, "congestion": 50, "condition": 5})
        self.assertEqual(r9s.status_code, 200)
        r9u = self.client.post("/api/experiments/exp9/unsupervised")
        self.assertEqual(r9u.status_code, 200)
        # Exp 10
        r10 = self.client.post("/api/experiments/exp10/language", json={"prompt": "high priority"})
        self.assertEqual(r10.status_code, 200)

        print("  [PASS] All 10 experiment API endpoints returned HTTP 200 and valid JSON data.")

if __name__ == "__main__":
    unittest.main()
