"""RouteMind AI - Automated Verification & Test Suite.
Validates the 10 core requirements and scenarios from Section 11.
"""
import copy
import json
import unittest

from ai_modules.problem_formulation import formulate_problem
from ai_modules.prolog_rules import execute_rule_query
from ai_modules.search_algorithms import breadth_first_search, depth_first_search
from ai_modules.astar_router import astar_search, compare_search_algorithms
from ai_modules.minimax import solve_minimax, default_minimax_tree
from ai_modules.fuzzy_controller import evaluate_fuzzy_controller
from ai_modules.fuzzy_inference import compute_mamdani_and_sugeno
from ai_modules.neuro_fuzzy import evaluate_neuro_fuzzy_pipeline
from ai_modules.neural_learning import run_supervised_perceptron_experiment, run_unsupervised_clustering_experiment
from ai_modules.language_models import run_language_experiment

class TestRouteMindAI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open("data/city_network.json", "r", encoding="utf-8") as f:
            cls.baseline_network = json.load(f)

    def test_scenario_01_valid_route_exists_A_to_G(self):
        """Scenario 1: A valid route exists from A to G."""
        res = astar_search(self.baseline_network, "A", "G")
        self.assertTrue(res["found"])
        self.assertEqual(res["path"][0], "A")
        self.assertEqual(res["path"][-1], "G")
        self.assertGreater(res["travel_time_min"], 0)
        self.assertGreater(res["distance_km"], 0)
        print("  [PASS] Scenario 1: Valid route A -> G found:", res["path"], f"({res['travel_time_min']} min)")

    def test_scenario_02_and_03_blocked_shortest_and_alternative_route(self):
        """Scenario 2 & 3: The shortest route is blocked, and an alternative valid route exists."""
        net = copy.deepcopy(self.baseline_network)
        # Identify road D-E and block it
        for r in net["roads"]:
            if r["id"] in ["D-E", "B-E"]:
                r["is_blocked"] = True

        res = astar_search(net, "A", "G")
        self.assertTrue(res["found"])
        self.assertNotIn("D-E", res["path"])
        # Alternative path should traverse through B-C-G or D-F-G
        self.assertTrue("C" in res["path"] or "F" in res["path"])
        print("  [PASS] Scenarios 2 & 3: Rerouted successfully avoiding blocked D-E/B-E:", res["path"])

    def test_scenario_04_all_routes_to_G_blocked(self):
        """Scenario 4: All roads leading to G are blocked."""
        net = copy.deepcopy(self.baseline_network)
        # Block all roads terminating at G (C-G, E-G, F-G)
        for r in net["roads"]:
            if r["from"] == "G" or r["to"] == "G":
                r["is_blocked"] = True

        res = astar_search(net, "A", "G")
        self.assertFalse(res["found"])
        self.assertEqual(res["path"], [])
        print("  [PASS] Scenario 4: Gracefully detected disconnected destination G without crashing.")

    def test_scenario_05_start_and_goal_same_node(self):
        """Scenario 5: Start and goal are the same node."""
        res_astar = astar_search(self.baseline_network, "B", "B")
        res_bfs = breadth_first_search(self.baseline_network, "B", "B")
        self.assertTrue(res_astar["found"])
        self.assertEqual(res_astar["path"], ["B"])
        self.assertEqual(res_astar["travel_time_min"], 0.0)
        self.assertTrue(res_bfs["found"])
        self.assertEqual(res_bfs["path"], ["B"])
        print("  [PASS] Scenario 5: Same node (B -> B) returns zero transit.")

    def test_scenario_06_invalid_node_entered(self):
        """Scenario 6: An invalid node is entered."""
        res = astar_search(self.baseline_network, "A", "Z")
        self.assertFalse(res["found"])
        self.assertIn("Invalid", res.get("error", ""))
        print("  [PASS] Scenario 6: Invalid node 'Z' handled safely with descriptive error message.")

    def test_scenario_07_network_edited_and_recalculated(self):
        """Scenario 7: Network is edited (add new shortcut road) and route recalculated."""
        net = copy.deepcopy(self.baseline_network)
        # Add high-speed express bypass directly from A to G
        net["roads"].append({
            "id": "A-G-EXPRESS",
            "from": "A",
            "to": "G",
            "distance_km": 20.0,
            "time_min": 10.0,
            "congestion_pct": 5,
            "is_blocked": False,
            "bidirectional": True
        })
        res = astar_search(net, "A", "G")
        self.assertTrue(res["found"])
        self.assertEqual(res["path"], ["A", "G"])
        self.assertEqual(res["travel_time_min"], 10.0)
        print("  [PASS] Scenario 7: Network edit (express bypass) immediately chosen as optimal path.")

    def test_scenario_08_fuzzy_controller_traffic_levels(self):
        """Scenario 8: Fuzzy controller handles low, medium, and high congestion."""
        # Low congestion, pristine road
        low_res = evaluate_fuzzy_controller(congestion=15.0, road_condition=9.0)
        self.assertEqual(low_res["output_category"], "Minimal Delay")
        self.assertLess(low_res["delay_score"], 40.0)

        # Medium congestion, fair road
        med_res = evaluate_fuzzy_controller(congestion=50.0, road_condition=5.5)
        self.assertEqual(med_res["output_category"], "Moderate Delay")

        # High congestion, severe road potholes
        high_res = evaluate_fuzzy_controller(congestion=95.0, road_condition=1.5)
        self.assertEqual(high_res["output_category"], "Severe Delay")
        self.assertGreater(high_res["delay_score"], 65.0)

        print("  [PASS] Scenario 8: Fuzzy controller correctly classifies Low, Med, High traffic conditions.")

    def test_scenario_09_neural_modules_produce_valid_predictions(self):
        """Scenario 9: Neural-network modules produce valid predictions."""
        # Supervised Perceptron
        sup_res = run_supervised_perceptron_experiment(test_dist=20.0, test_cong=75.0, test_cond=3.0)
        self.assertIn(sup_res["prediction"]["class_code"], [0, 1])
        self.assertGreater(sup_res["epochs_trained"], 0)

        # Unsupervised Clustering
        unsup_res = run_unsupervised_clustering_experiment()
        self.assertEqual(len(unsup_res["cluster_profiles"]), 3)
        self.assertEqual(len(unsup_res["clustered_points"]), 24)

        # Hybrid Neuro-Fuzzy
        nf_res = evaluate_neuro_fuzzy_pipeline(25.0, 60.0, "moderate")
        self.assertGreater(nf_res["hybrid_final_delay_min"], 0)
        self.assertGreater(nf_res["neural_network"]["raw_neural_prediction_min"], 0)

        print("  [PASS] Scenario 9: Perceptron, Competitive Learning, and Neuro-Fuzzy models generate valid predictions.")

    def test_scenario_10_language_models_known_and_unknown_contexts(self):
        """Scenario 10: Both language models handle known and unknown contexts gracefully."""
        # Known context
        res_known = run_language_experiment("high priority", "both")
        self.assertTrue(res_known["bigram_micro_model"]["context_known"])
        self.assertGreater(len(res_known["bigram_micro_model"]["predictions"]), 0)

        # Unknown out-of-vocabulary context
        res_unknown = run_language_experiment("interstellar quantum warp", "both")
        self.assertFalse(res_unknown["bigram_micro_model"]["context_known"])
        self.assertGreater(len(res_unknown["bigram_micro_model"]["predictions"]), 0)
        self.assertIsNotNone(res_unknown["trigram_completion"]["generated_sentence"])

        print("  [PASS] Scenario 10: Micro and Small language models gracefully handled known and unknown contexts.")

if __name__ == "__main__":
    unittest.main()
