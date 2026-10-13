"""Experiment 7: Mamdani vs Sugeno Fuzzy Inference for RouteMind AI.

Direct comparison of the two foundational fuzzy inference paradigms on a shared route-delay scenario:
- Inputs:
  * Route Distance (km): 5 to 50 km (Short, Medium, Long)
  * Traffic Congestion (%): 0 to 100% (Low, Medium, High)
- Mamdani Method:
  * Consequent is a continuous fuzzy set (Minimal, Moderate, High).
  * Uses min implication, max aggregation, and continuous Centroid defuzzification.
- Sugeno Method (Takagi-Sugeno-Kang):
  * Consequent is a crisp mathematical function of inputs: z_i = a_i * dist + b_i * cong + c_i.
  * Uses Weighted Average defuzzification: sum(w_i * z_i) / sum(w_i).
"""
from typing import Dict, Any, Tuple
import numpy as np

def trimf(x: float, abc: Tuple[float, float, float]) -> float:
    a, b, c = abc
    if x <= a or x >= c:
        return 0.0
    if a < x <= b:
        return (x - a) / (b - a) if b != a else 1.0
    if b < x < c:
        return (c - x) / (c - b) if c != b else 1.0
    return 0.0

def trapmf(x: float, abcd: Tuple[float, float, float, float]) -> float:
    a, b, c, d = abcd
    if x <= a or x >= d:
        return 0.0
    if a < x < b:
        return (x - a) / (b - a) if b != a else 1.0
    if b <= x <= c:
        return 1.0
    if c < x < d:
        return (d - x) / (d - c) if d != c else 1.0
    return 0.0

def compute_mamdani_and_sugeno(distance_km: float, congestion_pct: float) -> Dict[str, Any]:
    """Computes Mamdani and Sugeno inference on identical inputs and rules."""
    dist = max(5.0, min(50.0, float(distance_km)))
    cong = max(0.0, min(100.0, float(congestion_pct)))

    # 1. Fuzzify Distance: Short [5, 5, 12, 22], Medium [16, 26, 36], Long [30, 42, 50, 50]
    mu_dist_short = trapmf(dist, (5, 5, 12, 22))
    mu_dist_med = trimf(dist, (16, 26, 36))
    mu_dist_long = trapmf(dist, (30, 42, 50, 50))

    # 2. Fuzzify Congestion: Low [0, 0, 20, 40], Medium [30, 50, 70], High [60, 80, 100, 100]
    mu_cong_low = trapmf(cong, (0, 0, 20, 40))
    mu_cong_med = trimf(cong, (30, 50, 70))
    mu_cong_high = trapmf(cong, (60, 80, 100, 100))

    # Shared Rule Set (9 rules in grid)
    # Rule 1: Short & Low -> Minimal Delay
    w1 = min(mu_dist_short, mu_cong_low)
    # Rule 2: Short & Med -> Minimal Delay
    w2 = min(mu_dist_short, mu_cong_med)
    # Rule 3: Short & High -> Moderate Delay
    w3 = min(mu_dist_short, mu_cong_high)
    # Rule 4: Medium & Low -> Minimal Delay
    w4 = min(mu_dist_med, mu_cong_low)
    # Rule 5: Medium & Med -> Moderate Delay
    w5 = min(mu_dist_med, mu_cong_med)
    # Rule 6: Medium & High -> High Delay
    w6 = min(mu_dist_med, mu_cong_high)
    # Rule 7: Long & Low -> Moderate Delay
    w7 = min(mu_dist_long, mu_cong_low)
    # Rule 8: Long & Med -> High Delay
    w8 = min(mu_dist_long, mu_cong_med)
    # Rule 9: Long & High -> High Delay
    w9 = min(mu_dist_long, mu_cong_high)

    rules_fired = [
        {"rule": "R1: IF Dist Short AND Cong Low THEN Minimal", "firing_strength": round(w1, 3)},
        {"rule": "R2: IF Dist Short AND Cong Med THEN Minimal", "firing_strength": round(w2, 3)},
        {"rule": "R3: IF Dist Short AND Cong High THEN Moderate", "firing_strength": round(w3, 3)},
        {"rule": "R4: IF Dist Med AND Cong Low THEN Minimal", "firing_strength": round(w4, 3)},
        {"rule": "R5: IF Dist Med AND Cong Med THEN Moderate", "firing_strength": round(w5, 3)},
        {"rule": "R6: IF Dist Med AND Cong High THEN High", "firing_strength": round(w6, 3)},
        {"rule": "R7: IF Dist Long AND Cong Low THEN Moderate", "firing_strength": round(w7, 3)},
        {"rule": "R8: IF Dist Long AND Cong Med THEN High", "firing_strength": round(w8, 3)},
        {"rule": "R9: IF Dist Long AND Cong High THEN High", "firing_strength": round(w9, 3)},
    ]

    # Aggregated Consequent Weights
    weight_minimal = max(w1, w2, w4)
    weight_moderate = max(w3, w5, w7)
    weight_high = max(w6, w8, w9)

    # -------------------------------------------------------------
    # A. MAMDANI INFERENCE: Centroid Defuzzification over Delay (min)
    # Universe: 0 to 90 minutes
    # -------------------------------------------------------------
    delay_universe = np.linspace(0, 90, 181)
    mamdani_aggregated = np.zeros_like(delay_universe)

    for i, y in enumerate(delay_universe):
        # Consequent MFs
        mf_min = trapmf(y, (0, 0, 10, 25))
        mf_mod = trimf(y, (18, 35, 55))
        mf_high = trapmf(y, (45, 65, 90, 90))
        
        # Max of clipped fuzzy sets
        val = max(
            min(weight_minimal, mf_min),
            min(weight_moderate, mf_mod),
            min(weight_high, mf_high)
        )
        mamdani_aggregated[i] = val

    sum_mamdani = np.sum(mamdani_aggregated)
    if sum_mamdani > 0:
        mamdani_output = float(np.sum(delay_universe * mamdani_aggregated) / sum_mamdani)
    else:
        mamdani_output = 35.0
    mamdani_output = round(mamdani_output, 2)

    # -------------------------------------------------------------
    # B. SUGENO INFERENCE: Crisp Consequents & Weighted Average
    # Sugeno Consequent Functions z_i = f(distance, congestion)
    # Minimal: z = 0.5 * dist + 5
    # Moderate: z = 0.85 * dist + 0.22 * cong + 6
    # High: z = 1.25 * dist + 0.40 * cong + 10
    # -------------------------------------------------------------
    z_minimal = 0.50 * dist + 5.0
    z_moderate = 0.85 * dist + (0.22 * cong) + 6.0
    z_high = 1.25 * dist + (0.40 * cong) + 10.0

    all_rule_weights = [w1, w2, w3, w4, w5, w6, w7, w8, w9]
    all_rule_consequents = [
        z_minimal,   # R1
        z_minimal,   # R2
        z_moderate,  # R3
        z_minimal,   # R4
        z_moderate,  # R5
        z_high,      # R6
        z_moderate,  # R7
        z_high,      # R8
        z_high       # R9
    ]

    numerator = sum(w * z for w, z in zip(all_rule_weights, all_rule_consequents))
    denominator = sum(all_rule_weights)

    if denominator > 0:
        sugeno_output = round(float(numerator / denominator), 2)
    else:
        sugeno_output = round(z_moderate, 2)

    # Comparison summary
    difference = round(abs(mamdani_output - sugeno_output), 2)
    pct_diff = round((difference / ((mamdani_output + sugeno_output) / 2)) * 100, 2) if (mamdani_output + sugeno_output) > 0 else 0

    return {
        "inputs": {
            "distance_km": dist,
            "congestion_pct": cong
        },
        "memberships": {
            "distance": {
                "Short": round(mu_dist_short, 3),
                "Medium": round(mu_dist_med, 3),
                "Long": round(mu_dist_long, 3)
            },
            "congestion": {
                "Low": round(mu_cong_low, 3),
                "Medium": round(mu_cong_med, 3),
                "High": round(mu_cong_high, 3)
            }
        },
        "rules_fired": rules_fired,
        "consequent_category_strengths": {
            "Minimal": round(weight_minimal, 3),
            "Moderate": round(weight_moderate, 3),
            "High": round(weight_high, 3)
        },
        "sugeno_functions": {
            "z_minimal": f"0.50 * {dist} + 5.0 = {round(z_minimal, 2)} min",
            "z_moderate": f"0.85 * {dist} + 0.22 * {cong} + 6.0 = {round(z_moderate, 2)} min",
            "z_high": f"1.25 * {dist} + 0.40 * {cong} + 10.0 = {round(z_high, 2)} min"
        },
        "mamdani_output_min": mamdani_output,
        "sugeno_output_min": sugeno_output,
        "difference_min": difference,
        "percentage_difference": pct_diff,
        "defuzzification_comparison": {
            "mamdani": {
                "consequent_nature": "Fuzzy Sets (Linguistic)",
                "defuzzification": "Centroid (Center of Gravity) Integration over continuous area",
                "computational_cost": "Higher (numerical integration required over output universe)",
                "interpretability": "Very intuitive for human domain experts"
            },
            "sugeno": {
                "consequent_nature": "Mathematical Functions (Linear / Polynomial of Inputs)",
                "defuzzification": "Weighted Average (sum(w_i * z_i) / sum(w_i))",
                "computational_cost": "Extremely fast, highly efficient for real-time controllers & optimization",
                "interpretability": "Mathematical equations; well-suited for adaptive neuro-fuzzy (ANFIS) tuning"
            }
        }
    }
