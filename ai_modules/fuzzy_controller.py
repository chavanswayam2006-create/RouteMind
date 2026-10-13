"""Experiment 6: Fuzzy Logic Controller for RouteMind AI.

Classifies road traffic conditions and computes estimated road-delay score:
- Inputs:
  * Congestion: 0 to 100% (Low, Medium, High)
  * Road Condition: 1 to 10 scale (Poor, Fair, Good)
- Output:
  * Delay Score: 0 to 100 (Minimal, Moderate, Severe)
- Uses scikit-fuzzy if available, with a pure-Python Mamdani centroid defuzzifier fallback.
"""
from typing import Dict, Any, Tuple
import warnings
import numpy as np

# Filter benign numpy 2.x deprecation warnings inside skfuzzy
warnings.filterwarnings("ignore", category=DeprecationWarning, module="skfuzzy")

# Try importing scikit-fuzzy
try:
    import skfuzzy as fuzz
    from skfuzzy import control as ctrl
    SKFUZZY_AVAILABLE = True
except Exception:
    SKFUZZY_AVAILABLE = False

def trimf(x: float, abc: Tuple[float, float, float]) -> float:
    """Pure-Python triangular membership function."""
    a, b, c = abc
    if x <= a or x >= c:
        return 0.0
    if a < x <= b:
        return (x - a) / (b - a) if b != a else 1.0
    if b < x < c:
        return (c - x) / (c - b) if c != b else 1.0
    return 0.0

def trapmf(x: float, abcd: Tuple[float, float, float, float]) -> float:
    """Pure-Python trapezoidal membership function."""
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

def run_pure_python_fuzzy(congestion: float, road_condition: float) -> Dict[str, Any]:
    """Pure-Python Mamdani Fuzzy Controller simulation with Centroid Defuzzification."""
    # Fuzzification
    # Congestion: Low [0, 0, 45], Med [30, 50, 70], High [55, 100, 100]
    mu_cong_low = trapmf(congestion, (0, 0, 20, 45))
    mu_cong_med = trimf(congestion, (30, 50, 70))
    mu_cong_high = trapmf(congestion, (55, 80, 100, 100))

    # Road Condition: Poor [1, 1, 4], Fair [3, 5.5, 8], Good [7, 10, 10]
    mu_road_poor = trapmf(road_condition, (1, 1, 2.5, 4.5))
    mu_road_fair = trimf(road_condition, (3.5, 5.5, 7.5))
    mu_road_good = trapmf(road_condition, (6.5, 8.5, 10, 10))

    # Linguistic Rules (Mamdani Min operator for AND)
    # R1: IF Congestion is High OR Road Condition is Poor -> Delay Severe
    r1 = max(mu_cong_high, mu_road_poor)
    # R2: IF Congestion is Med AND Road Condition is Fair -> Delay Moderate
    r2 = min(mu_cong_med, mu_road_fair)
    # R3: IF Congestion is Low AND Road Condition is Good -> Delay Minimal
    r3 = min(mu_cong_low, mu_road_good)
    # R4: IF Congestion is Low AND Road Condition is Fair -> Delay Minimal
    r4 = min(mu_cong_low, mu_road_fair)
    # R5: IF Congestion is Med AND Road Condition is Good -> Delay Moderate
    r5 = min(mu_cong_med, mu_road_good)
    # R6: IF Congestion is High AND Road Condition is Good -> Delay Moderate
    r6 = min(mu_cong_high, mu_road_good)

    # Aggregated Consequent Strengths (Max for OR)
    strength_minimal = max(r3, r4)
    strength_moderate = max(r2, r5, r6)
    strength_severe = r1

    # Centroid Defuzzification over 0 to 100 universe
    x_universe = np.linspace(0, 100, 201)
    aggregated_mf = np.zeros_like(x_universe)

    for i, x in enumerate(x_universe):
        # Consequent MFs: Minimal [0, 0, 35], Moderate [25, 50, 75], Severe [65, 100, 100]
        mf_min = trapmf(x, (0, 0, 15, 35))
        mf_mod = trimf(x, (25, 50, 75))
        mf_sev = trapmf(x, (65, 85, 100, 100))
        
        # Clip by rule strengths
        val = max(
            min(strength_minimal, mf_min),
            min(strength_moderate, mf_mod),
            min(strength_severe, mf_sev)
        )
        aggregated_mf[i] = val

    sum_mf = np.sum(aggregated_mf)
    if sum_mf > 0:
        delay_score = float(np.sum(x_universe * aggregated_mf) / sum_mf)
    else:
        delay_score = 50.0

    delay_score = round(delay_score, 2)

    # Categorize output
    if delay_score < 35:
        category = "Minimal Delay"
        category_color = "success"
    elif delay_score <= 68:
        category = "Moderate Delay"
        category_color = "warning"
    else:
        category = "Severe Delay"
        category_color = "danger"

    return {
        "engine": "Pure-Python Mamdani Logic Engine (Centroid Defuzzification)",
        "inputs": {
            "congestion_pct": congestion,
            "road_condition": road_condition
        },
        "memberships": {
            "congestion": {
                "Low": round(float(mu_cong_low), 3),
                "Medium": round(float(mu_cong_med), 3),
                "High": round(float(mu_cong_high), 3)
            },
            "road_condition": {
                "Poor": round(float(mu_road_poor), 3),
                "Fair": round(float(mu_road_fair), 3),
                "Good": round(float(mu_road_good), 3)
            }
        },
        "rule_strengths": {
            "Minimal": round(float(strength_minimal), 3),
            "Moderate": round(float(strength_moderate), 3),
            "Severe": round(float(strength_severe), 3)
        },
        "delay_score": delay_score,
        "output_category": category,
        "category_color": category_color
    }

def run_skfuzzy_controller(congestion: float, road_condition: float) -> Dict[str, Any]:
    """Runs scikit-fuzzy control system."""
    try:
        # Antecedents
        cong = ctrl.Antecedent(np.arange(0, 101, 1), 'congestion')
        road = ctrl.Antecedent(np.arange(1, 11, 0.1), 'road_condition')
        # Consequent
        delay = ctrl.Consequent(np.arange(0, 101, 1), 'delay_score')

        # Membership functions
        cong['Low'] = fuzz.trapmf(cong.universe, [0, 0, 20, 45])
        cong['Medium'] = fuzz.trimf(cong.universe, [30, 50, 70])
        cong['High'] = fuzz.trapmf(cong.universe, [55, 80, 100, 100])

        road['Poor'] = fuzz.trapmf(road.universe, [1, 1, 2.5, 4.5])
        road['Fair'] = fuzz.trimf(road.universe, [3.5, 5.5, 7.5])
        road['Good'] = fuzz.trapmf(road.universe, [6.5, 8.5, 10, 10])

        delay['Minimal'] = fuzz.trapmf(delay.universe, [0, 0, 15, 35])
        delay['Moderate'] = fuzz.trimf(delay.universe, [25, 50, 75])
        delay['Severe'] = fuzz.trapmf(delay.universe, [65, 85, 100, 100])

        # Rules
        r1 = ctrl.Rule(cong['High'] | road['Poor'], delay['Severe'])
        r2 = ctrl.Rule(cong['Medium'] & road['Fair'], delay['Moderate'])
        r3 = ctrl.Rule(cong['Low'] & road['Good'], delay['Minimal'])
        r4 = ctrl.Rule(cong['Low'] & road['Fair'], delay['Minimal'])
        r5 = ctrl.Rule(cong['Medium'] & road['Good'], delay['Moderate'])
        r6 = ctrl.Rule(cong['High'] & road['Good'], delay['Moderate'])

        delay_ctrl = ctrl.ControlSystem([r1, r2, r3, r4, r5, r6])
        sim = ctrl.ControlSystemSimulation(delay_ctrl)

        sim.input['congestion'] = max(0.0, min(100.0, congestion))
        sim.input['road_condition'] = max(1.0, min(10.0, road_condition))
        sim.compute()

        delay_score = round(float(sim.output['delay_score']), 2)

        if delay_score < 35:
            cat = "Minimal Delay"
            cat_color = "success"
        elif delay_score <= 68:
            cat = "Moderate Delay"
            cat_color = "warning"
        else:
            cat = "Severe Delay"
            cat_color = "danger"

        # Also get memberships for visual clarity
        c_low = fuzz.interp_membership(cong.universe, cong['Low'].mf, congestion)
        c_med = fuzz.interp_membership(cong.universe, cong['Medium'].mf, congestion)
        c_high = fuzz.interp_membership(cong.universe, cong['High'].mf, congestion)

        r_poor = fuzz.interp_membership(road.universe, road['Poor'].mf, road_condition)
        r_fair = fuzz.interp_membership(road.universe, road['Fair'].mf, road_condition)
        r_good = fuzz.interp_membership(road.universe, road['Good'].mf, road_condition)

        return {
            "engine": "scikit-fuzzy Control System (Centroid Defuzzification)",
            "inputs": {
                "congestion_pct": congestion,
                "road_condition": road_condition
            },
            "memberships": {
                "congestion": {"Low": round(float(c_low), 3), "Medium": round(float(c_med), 3), "High": round(float(c_high), 3)},
                "road_condition": {"Poor": round(float(r_poor), 3), "Fair": round(float(r_fair), 3), "Good": round(float(r_good), 3)}
            },
            "rule_strengths": {
                "Minimal": round(float(max(min(c_low, r_good), min(c_low, r_fair))), 3),
                "Moderate": round(float(max(min(c_med, r_fair), min(c_med, r_good), min(c_high, r_good))), 3),
                "Severe": round(float(max(c_high, r_poor)), 3)
            },
            "delay_score": delay_score,
            "output_category": cat,
            "category_color": cat_color
        }
    except Exception:
        # Fall back gracefully to pure Python implementation if skfuzzy internal error occurs
        return run_pure_python_fuzzy(congestion, road_condition)

def evaluate_fuzzy_controller(congestion: float, road_condition: float, use_engine: str = "auto") -> Dict[str, Any]:
    """Public interface for evaluating fuzzy controller."""
    if use_engine == "pure_python" or not SKFUZZY_AVAILABLE:
        return run_pure_python_fuzzy(congestion, road_condition)
    return run_skfuzzy_controller(congestion, road_condition)
