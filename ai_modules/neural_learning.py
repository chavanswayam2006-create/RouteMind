"""Experiment 9: Supervised and Unsupervised Neural Networks for RouteMind AI.

1. Supervised Learning:
   - Rosenblatt Perceptron Learning Rule (implemented from first principles).
   - Binary Classification: Normal Route (Class 0) vs High-Delay Corridor (Class 1).
   - Features: [Distance (km), Congestion (%), Road Condition (1-10)].
   - Step-by-step weight updates: w <- w + eta * (y - y_hat) * x.
   - Shows epoch loss/error count and prediction for new user input.

2. Unsupervised Learning:
   - Competitive Learning / Winner-Take-All Vector Quantization.
   - Groups unlabeled road observations into K=3 distinct clusters:
     * Cluster 0: Fast Expressway Corridor
     * Cluster 1: Balanced Arterial Transit
     * Cluster 2: Severe Congestion Chokepoint
   - Updates winning centroid: w_winner <- w_winner + eta * (x - w_winner).
   - Provides 2D projection for Chart.js scatter plot.
"""
from typing import Dict, Any, List, Tuple
import numpy as np

# Reproducible synthetic dataset for Experiment 9
def get_road_observation_dataset(random_seed: int = 42) -> List[Dict[str, Any]]:
    np.random.seed(random_seed)
    # 24 simulated road segments
    data = []
    # Fast roads
    for i in range(8):
        dist = round(float(np.random.uniform(5.0, 18.0)), 1)
        cong = round(float(np.random.uniform(10.0, 35.0)), 1)
        cond = round(float(np.random.uniform(7.5, 9.8)), 1)
        data.append({"id": f"RD-{i+1:02d}", "dist": dist, "cong": cong, "cond": cond, "label": 0, "label_name": "Normal"})

    # Moderate roads
    for i in range(8, 16):
        dist = round(float(np.random.uniform(18.0, 32.0)), 1)
        cong = round(float(np.random.uniform(35.0, 65.0)), 1)
        cond = round(float(np.random.uniform(4.5, 7.5)), 1)
        # Label 1 if congestion is high or condition poor
        lbl = 1 if (cong > 50 or cond < 5.5) else 0
        data.append({"id": f"RD-{i+1:02d}", "dist": dist, "cong": cong, "cond": cond, "label": lbl, "label_name": "High Delay" if lbl == 1 else "Normal"})

    # Severe chokepoints
    for i in range(16, 24):
        dist = round(float(np.random.uniform(25.0, 45.0)), 1)
        cong = round(float(np.random.uniform(65.0, 95.0)), 1)
        cond = round(float(np.random.uniform(2.0, 5.0)), 1)
        data.append({"id": f"RD-{i+1:02d}", "dist": dist, "cong": cong, "cond": cond, "label": 1, "label_name": "High Delay"})

    return data

class PerceptronClassifier:
    """Supervised Perceptron learning rule from scratch."""
    def __init__(self, learning_rate: float = 0.05, max_epochs: int = 50):
        self.lr = learning_rate
        self.max_epochs = max_epochs
        self.weights = np.zeros(3)
        self.bias = 0.0
        self.training_history = []

    def fit(self, X: np.ndarray, y: np.ndarray):
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0.0
        self.training_history = []

        for epoch in range(1, self.max_epochs + 1):
            errors = 0
            for i in range(n_samples):
                linear_output = np.dot(X[i], self.weights) + self.bias
                y_pred = 1 if linear_output >= 0.0 else 0
                update = self.lr * (y[i] - y_pred)
                if update != 0.0:
                    self.weights += update * X[i]
                    self.bias += update
                    errors += 1
            self.training_history.append({
                "epoch": epoch,
                "misclassifications": errors,
                "weights": [round(float(w), 4) for w in self.weights],
                "bias": round(float(self.bias), 4)
            })
            if errors == 0:
                break

    def predict(self, x: np.ndarray) -> int:
        linear_output = np.dot(x, self.weights) + self.bias
        return 1 if linear_output >= 0.0 else 0

class CompetitiveLearningClustering:
    """Unsupervised Winner-Take-All Competitive Learning Network."""
    def __init__(self, n_clusters: int = 3, learning_rate: float = 0.1, epochs: int = 40, random_seed: int = 42):
        self.k = n_clusters
        self.lr = learning_rate
        self.epochs = epochs
        self.random_seed = random_seed
        self.centroids = None

    def fit(self, X: np.ndarray):
        np.random.seed(self.random_seed)
        n_samples, n_features = X.shape
        # Initialize centroids randomly from data points
        indices = np.random.choice(n_samples, self.k, replace=False)
        self.centroids = X[indices].copy()

        for epoch in range(self.epochs):
            eta = self.lr * (1.0 - epoch / self.epochs) # decaying learning rate
            for i in range(n_samples):
                xi = X[i]
                # Compute Euclidean distances to all centroids
                distances = np.linalg.norm(self.centroids - xi, axis=1)
                # Winner is closest centroid
                winner_idx = np.argmin(distances)
                # Update winner weights towards input
                self.centroids[winner_idx] += eta * (xi - self.centroids[winner_idx])

    def predict(self, X: np.ndarray) -> np.ndarray:
        assignments = []
        for xi in X:
            distances = np.linalg.norm(self.centroids - xi, axis=1)
            assignments.append(np.argmin(distances))
        return np.array(assignments)

def run_supervised_perceptron_experiment(test_dist: float = 22.0, test_cong: float = 55.0, test_cond: float = 6.0) -> Dict[str, Any]:
    dataset = get_road_observation_dataset()
    X_raw = np.array([[d["dist"], d["cong"], d["cond"]] for d in dataset])
    y = np.array([d["label"] for d in dataset])

    # Normalize features for stable perceptron convergence
    means = np.mean(X_raw, axis=0)
    stds = np.std(X_raw, axis=0) + 1e-6
    X_norm = (X_raw - means) / stds

    clf = PerceptronClassifier(learning_rate=0.08, max_epochs=35)
    clf.fit(X_norm, y)

    # Test point
    x_test = np.array([test_dist, test_cong, test_cond])
    x_test_norm = (x_test - means) / stds
    pred = clf.predict(x_test_norm)
    pred_label = "High Delay Corridor" if pred == 1 else "Normal Route"

    return {
        "paradigm": "Supervised Learning",
        "algorithm": "Rosenblatt Perceptron Learning Rule",
        "task": "Binary Classification (Normal=0 vs High Delay=1)",
        "features": ["Distance (km)", "Congestion (%)", "Road Condition (1-10)"],
        "dataset_size": len(dataset),
        "epochs_trained": len(clf.training_history),
        "final_weights": clf.training_history[-1]["weights"] if clf.training_history else [],
        "final_bias": clf.training_history[-1]["bias"] if clf.training_history else 0.0,
        "history": clf.training_history,
        "user_test_input": {
            "distance_km": test_dist,
            "congestion_pct": test_cong,
            "road_condition": test_cond
        },
        "prediction": {
            "class_code": int(pred),
            "class_name": pred_label,
            "interpretation": f"Perceptron classified input ({test_dist}km, {test_cong}% cong, cond {test_cond}) as '{pred_label}' based on linear decision boundary."
        }
    }

def run_unsupervised_clustering_experiment() -> Dict[str, Any]:
    dataset = get_road_observation_dataset()
    X_raw = np.array([[d["dist"], d["cong"], d["cond"]] for d in dataset])

    # Normalize
    means = np.mean(X_raw, axis=0)
    stds = np.std(X_raw, axis=0) + 1e-6
    X_norm = (X_raw - means) / stds

    comp = CompetitiveLearningClustering(n_clusters=3, learning_rate=0.15, epochs=30, random_seed=42)
    comp.fit(X_norm)
    assignments = comp.predict(X_norm)

    # Convert centroids back to original scale
    centroids_orig = comp.centroids * stds + means

    # Name clusters based on centroid congestion
    cluster_profiles = []
    cluster_indices = sorted(range(3), key=lambda k: centroids_orig[k][1])
    profile_names = ["Low-Congestion Expressways", "Moderate Arterial Corridors", "Severe Chokepoints"]
    
    mapping = {}
    for rank, orig_idx in enumerate(cluster_indices):
        mapping[orig_idx] = profile_names[rank]

    points = []
    for i, d in enumerate(dataset):
        c_id = int(assignments[i])
        points.append({
            "road_id": d["id"],
            "distance_km": d["dist"],
            "congestion_pct": d["cong"],
            "road_condition": d["cond"],
            "cluster_id": c_id,
            "cluster_label": mapping.get(c_id, f"Cluster {c_id}")
        })

    for k in range(3):
        cluster_profiles.append({
            "cluster_id": k,
            "profile_label": mapping.get(k, f"Cluster {k}"),
            "centroid": {
                "distance_km": round(float(centroids_orig[k][0]), 1),
                "congestion_pct": round(float(centroids_orig[k][1]), 1),
                "road_condition": round(float(centroids_orig[k][2]), 1)
            },
            "member_count": int(np.sum(assignments == k))
        })

    return {
        "paradigm": "Unsupervised Learning",
        "algorithm": "Competitive Learning (Winner-Take-All / Vector Quantization)",
        "task": "Clustering road observations without any human class labels",
        "n_clusters": 3,
        "cluster_profiles": cluster_profiles,
        "clustered_points": points,
        "educational_contrast": {
            "supervised_vs_unsupervised": [
                "Supervised Learning trains on input-output pairs (X, y) with an explicit teacher/target. Weights update using ground-truth error signal.",
                "Unsupervised Learning receives only inputs X without labels. Neurons compete to represent clusters based on intrinsic data geometry and feature similarities."
            ]
        }
    }
