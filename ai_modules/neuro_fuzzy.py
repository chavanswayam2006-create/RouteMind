"""Experiment 8: Hybrid Neuro-Fuzzy System for RouteMind AI.

Couples an Artificial Neural Network (learning baseline transit delay from empirical data)
with a Fuzzy Post-Processing Expert Layer (incorporating contextual operational rules):
1. Neural Network Layer:
   - Multi-Layer Perceptron (MLPRegressor or pure-Python feedforward net)
   - Trained on reproducible synthetic city dispatch observations: (distance_km, congestion_pct) -> base_delay_min.
2. Fuzzy Expert Supervisory Layer:
   - Takes the raw neural prediction + secondary contextual factor (weather_severity or peak_hour_factor)
   - Applies linguistic IF-THEN rules (e.g. IF Neural Delay is High AND Severe Rain THEN adjust delay by +25%)
   - Prevents unphysical neural outputs and provides transparent domain explainability.
3. Outputs:
   - Neural-only prediction
   - Fuzzy adjustment delta
   - Combined Hybrid prediction
   - Side-by-side comparison table.
"""
from typing import Dict, Any, List, Tuple
import numpy as np

# Reproducible synthetic dataset generator
def generate_synthetic_dataset(num_samples: int = 40, random_seed: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    np.random.seed(random_seed)
    # distance between 5 and 45 km
    distances = np.random.uniform(5.0, 45.0, num_samples)
    # congestion between 0 and 95%
    congestions = np.random.uniform(0.0, 95.0, num_samples)
    # Base physics formula with realistic stochastic variance:
    # delay = (distance / 45) * 60 + (congestion / 100) * 25 + noise
    delays = (distances / 40.0) * 60.0 + (congestions / 100.0) * 22.0 + np.random.normal(0, 2.0, num_samples)
    delays = np.maximum(5.0, delays)
    
    X = np.column_stack((distances, congestions))
    y = delays
    return X, y

class SimpleNeuralRegressor:
    """Lightweight 2-layer Feedforward Neural Network with backpropagation (NumPy-based).
    Guarantees instant zero-dependency execution and reproducible weights.
    """
    def __init__(self, hidden_dim: int = 6, random_seed: int = 42):
        np.random.seed(random_seed)
        # Weights: input (2) -> hidden (6) -> output (1)
        self.W1 = np.random.randn(2, hidden_dim) * 0.2
        self.b1 = np.zeros((1, hidden_dim))
        self.W2 = np.random.randn(hidden_dim, 1) * 0.2
        self.b2 = np.zeros((1, 1))
        # Feature normalization scales
        self.X_mean = np.array([25.0, 50.0])
        self.X_std = np.array([12.0, 28.0])
        self.y_mean = 45.0
        self.y_std = 20.0
        self.loss_history = []

    def _relu(self, z):
        return np.maximum(0, z)

    def _relu_deriv(self, z):
        return (z > 0).astype(float)

    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 350, lr: float = 0.04):
        # Normalize
        self.X_mean = np.mean(X, axis=0)
        self.X_std = np.std(X, axis=0) + 1e-6
        self.y_mean = np.mean(y)
        self.y_std = np.std(y) + 1e-6

        X_norm = (X - self.X_mean) / self.X_std
        y_norm = ((y - self.y_mean) / self.y_std).reshape(-1, 1)

        self.loss_history = []
        m = X.shape[0]

        for epoch in range(epochs):
            # Forward pass
            z1 = np.dot(X_norm, self.W1) + self.b1
            a1 = self._relu(z1)
            z2 = np.dot(a1, self.W2) + self.b2
            y_pred = z2

            loss = np.mean((y_pred - y_norm) ** 2)
            if epoch % 35 == 0:
                self.loss_history.append(round(float(loss), 4))

            # Backpropagation
            d_out = (y_pred - y_norm) / m
            dW2 = np.dot(a1.T, d_out)
            db2 = np.sum(d_out, axis=0, keepdims=True)

            d_hidden = np.dot(d_out, self.W2.T) * self._relu_deriv(z1)
            dW1 = np.dot(X_norm.T, d_hidden)
            db1 = np.sum(d_hidden, axis=0, keepdims=True)

            self.W1 -= lr * dW1
            self.b1 -= lr * db1
            self.W2 -= lr * dW2
            self.b2 -= lr * db2

    def predict(self, distance: float, congestion: float) -> float:
        X_in = np.array([[distance, congestion]])
        X_norm = (X_in - self.X_mean) / self.X_std
        z1 = np.dot(X_norm, self.W1) + self.b1
        a1 = self._relu(z1)
        z2 = np.dot(a1, self.W2) + self.b2
        pred_norm = z2[0, 0]
        pred_unnorm = pred_norm * self.y_std + self.y_mean
        return max(5.0, float(pred_unnorm))

# Singleton trained instance
_MODEL_INSTANCE = None

def get_trained_neural_model() -> SimpleNeuralRegressor:
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        X_train, y_train = generate_synthetic_dataset(num_samples=48, random_seed=42)
        model = SimpleNeuralRegressor(hidden_dim=8, random_seed=42)
        model.train(X_train, y_train, epochs=400, lr=0.035)
        _MODEL_INSTANCE = model
    return _MODEL_INSTANCE

def evaluate_neuro_fuzzy_pipeline(distance_km: float, congestion_pct: float, weather_risk: str = "moderate") -> Dict[str, Any]:
    """Evaluates the hybrid Neuro-Fuzzy pipeline."""
    dist = max(3.0, min(50.0, float(distance_km)))
    cong = max(0.0, min(100.0, float(congestion_pct)))
    weather_risk = weather_risk.lower()
    if weather_risk not in ["low", "moderate", "severe"]:
        weather_risk = "moderate"

    # Step 1: Neural Network prediction
    model = get_trained_neural_model()
    raw_nn_pred = model.predict(dist, cong)
    raw_nn_pred = round(raw_nn_pred, 2)

    # Step 2: Fuzzy Supervisory Layer
    # Linguistic classification of neural prediction:
    # Short (< 25 min), Medium (20 to 50 min), Long (> 45 min)
    mu_nn_short = max(0.0, min(1.0, (30.0 - raw_nn_pred) / 15.0)) if raw_nn_pred <= 30 else 0.0
    mu_nn_med = max(0.0, min(1.0, 1.0 - abs(raw_nn_pred - 40.0) / 20.0))
    mu_nn_high = max(0.0, min(1.0, (raw_nn_pred - 35.0) / 25.0)) if raw_nn_pred >= 35 else 0.0

    # Weather multipliers from fuzzy rules
    fuzzy_rule_explanations = []
    fuzzy_multiplier = 1.0

    if weather_risk == "low":
        fuzzy_multiplier = 0.96  # slightly faster flow under clear weather
        fuzzy_rule_explanations.append("Rule NF-1: IF Weather is Clear/Low THEN apply -4% favorable traffic bonus.")
    elif weather_risk == "moderate":
        if raw_nn_pred > 45.0:
            fuzzy_multiplier = 1.08
            fuzzy_rule_explanations.append("Rule NF-2: IF Neural Delay is High AND Weather is Moderate THEN apply +8% safety margin.")
        else:
            fuzzy_multiplier = 1.03
            fuzzy_rule_explanations.append("Rule NF-3: IF Neural Delay is Nominal AND Weather is Moderate THEN apply +3% minor margin.")
    elif weather_risk == "severe":
        if cong > 60:
            fuzzy_multiplier = 1.28
            fuzzy_rule_explanations.append("Rule NF-4: IF Congestion > 60% AND Weather is Severe (Storm) THEN apply +28% acute chokepoint penalty.")
        else:
            fuzzy_multiplier = 1.18
            fuzzy_rule_explanations.append("Rule NF-5: IF Weather is Severe THEN apply +18% precautionary speed reduction.")

    # Calculate final hybrid delay
    hybrid_pred = round(raw_nn_pred * fuzzy_multiplier, 2)
    adjustment_delta = round(hybrid_pred - raw_nn_pred, 2)

    return {
        "inputs": {
            "distance_km": dist,
            "congestion_pct": cong,
            "weather_condition": weather_risk
        },
        "neural_network": {
            "architecture": "MLP (Input: 2 -> Hidden: 8 ReLU -> Output: 1 Linear)",
            "training_dataset": "48 Synthetic city dispatch observation samples (synthetic demonstration data)",
            "random_seed": 42,
            "training_loss_history": model.loss_history,
            "raw_neural_prediction_min": raw_nn_pred
        },
        "fuzzy_supervisory_layer": {
            "neural_linguistic_activation": {
                "Short Delay (< 25 min)": round(mu_nn_short, 3),
                "Medium Delay (25-45 min)": round(mu_nn_med, 3),
                "Long Delay (> 45 min)": round(mu_nn_high, 3)
            },
            "rules_activated": fuzzy_rule_explanations,
            "fuzzy_multiplier": fuzzy_multiplier,
            "fuzzy_adjustment_delta_min": adjustment_delta
        },
        "hybrid_final_delay_min": hybrid_pred,
        "comparison": {
            "neural_only": f"{raw_nn_pred} min",
            "fuzzy_adjustment": f"{'+' if adjustment_delta >= 0 else ''}{adjustment_delta} min ({round((fuzzy_multiplier - 1.0) * 100, 1)}%)",
            "hybrid_result": f"{hybrid_pred} min",
            "interpretation": f"Neural net estimated baseline {raw_nn_pred} min from physics features; Fuzzy layer applied {weather_risk} weather adjustments yielding {hybrid_pred} min."
        },
        "disclaimer": "Synthetic training data used strictly for academic illustration. Not live GPS telemetry."
    }
