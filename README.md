# RouteMind AI — Intelligent Package Routing & Dispatch System

> **Artificial Intelligence Laboratory Capstone Project**  
> A desktop-first, modular AI dispatch and routing application for urban distribution networks.  
> Designed with **Google Stitch AI**, built with **Python 3.x, Flask, Cytoscape.js, and Chart.js**.

---

## 1. Overview & Problem Statement

**RouteMind AI** tackles autonomous package routing and dispatch across an interconnected 7-hub city network (Hubs **A** through **G**). The central warehouse (**Hub A**) dispatches high-priority parcels to the final delivery hub (**Hub G**) while dynamically circumventing blocked road segments, minimizing estimated transit delay, and benchmarking alternative routing policies.

The system serves as a hands-on AI laboratory platform showcasing:
1. **Problem Formulation & PEAS Framework**
2. **Prolog Rule-Based Logic** (with automatic SWI-Prolog detection & pure-Python logic engine fallback)
3. **Uninformed Search** (Breadth-First Search & Depth-First Search)
4. **Informed Search** (A* Search with admissible straight-line Euclidean heuristics)
5. **Game-Theoretic Decision Trees** (Minimax with adversarial traffic modeling)
6. **Fuzzy Logic Control** (Centroid defuzzification for traffic and road conditions)
7. **Fuzzy Inference Comparison** (Mamdani continuous fuzzy output vs. Sugeno linear functions)
8. **Hybrid Neuro-Fuzzy Systems** (ANN baseline learning + Fuzzy supervisory safety layer)
9. **Supervised & Unsupervised Neural Networks** (Perceptron learning rule from scratch + Winner-Take-All competitive clustering)
10. **Statistical Language Models** (Micro Bigram & Small Trigram models on domain logistics corpora)

---

## 2. System Architecture

```
RouteMind AI/
├── app.py                      # Flask backend application & REST API server
├── requirements.txt            # Python dependencies
├── test_routemind.py           # Comprehensive 10-scenario verification test suite
├── test_flask_app.py           # Integration tests for all web routes & API endpoints
├── README.md                   # Complete documentation & lab demonstration guide
├── data/
│   ├── city_network.json       # 7-node, 12-road topology with distances, times & congestion
│   ├── language_corpus.txt     # Domain text corpus for N-gram language models
│   └── routemind_rules.pl      # ISO Prolog knowledge base export
├── ai_modules/
│   ├── __init__.py
│   ├── problem_formulation.py  # Exp 1: PEAS & state-space problem formulation
│   ├── prolog_rules.py         # Exp 2: Prolog knowledge base & Horn-clause logic engine
│   ├── search_algorithms.py    # Exp 3: Genuine BFS & DFS implementations
│   ├── astar_router.py         # Exp 4: A* Search with admissible Euclidean heuristic
│   ├── minimax.py              # Exp 5: Minimax decision tree for dispatch vs adverse traffic
│   ├── fuzzy_controller.py     # Exp 6: Fuzzy controller with scikit-fuzzy & pure-Python fallback
│   ├── fuzzy_inference.py      # Exp 7: Direct Mamdani vs Sugeno comparative inference
│   ├── neuro_fuzzy.py          # Exp 8: Hybrid MLP Regressor + Fuzzy expert supervisor
│   ├── neural_learning.py      # Exp 9: Supervised Perceptron & Unsupervised Clustering
│   └── language_models.py      # Exp 10: Micro Bigram & Small Trigram statistical NLP
├── templates/
│   ├── base.html               # Shared layout, Google Fonts, Cytoscape & Chart.js imports
│   ├── index.html              # Main Dispatch Dashboard with live Cytoscape graph
│   ├── experiments.html        # Interactive 10-module AI Experiment Center
│   ├── network.html            # Distribution Network Topology Editor
│   └── about.html              # System architecture, Stitch workflow & Viva guide
└── static/
    ├── css/
    │   └── style.css           # Stitch Design System tokens (Plus Jakarta Sans, Inter, JetBrains Mono)
    └── js/
        ├── network.js          # Cytoscape.js interactive topology visualization
        ├── charts.js           # Chart.js multi-algorithm benchmark bar charts
        ├── dashboard.js        # Main dashboard controller & live re-routing engine
        ├── experiments.js      # Controller for all 10 AI laboratory experiments
        └── editor.js           # Network editor controller for road CRUD & status toggles
```

---

## 3. Google Stitch AI Design System

The application's interface was designed using **Google Stitch AI** via the Model Context Protocol (`StitchMCP`, Project `5399150869426497947`). Stitch synthesized the **"RouteMind Precision Logistics"** design system:

- **Command Deck & Dark Elevation:** Deep navy slate (`#0B132B`, `#1C2541`) for focused navigation.
- **Data Workspaces:** Crisp neutral surfaces (`#F8FAFC`, `#FFFFFF`) with 1px borders (`#E2E8F0`).
- **Machine Intelligence Accents:** Electric Cyan (`#06B6D4`) and Algorithmic Teal (`#0D9488`).
- **Status Signals:** Emerald (`#10B981`, optimal), Amber (`#F59E0B`, warning), Crimson (`#EF4444`, blocked).
- **Typography:**
  - *Plus Jakarta Sans*: Bold, modern headings and metric cards.
  - *Inter*: Clean, high-legibility body copy and form controls.
  - *JetBrains Mono*: Telemetric readouts, coordinates, timestamps, and transit durations.

### Ready-to-Paste Stitch Prompt
```text
Design a polished, modern AI logistics dashboard called RouteMind AI. It is a desktop-first package routing and dispatch application for a city distribution network. Use a clean enterprise logistics aesthetic with a deep navy sidebar, light neutral workspace, cyan and teal accents, rounded cards, subtle shadows, clear typography, and accessible contrast.

Create a collapsible sidebar containing Dashboard, Route Planner, AI Experiments, Network Editor, and About Project.

The dashboard must include:
- A high-priority parcel status card.
- Start warehouse A and destination hub G.
- A large interactive-looking city network visualization with connected nodes, blocked roads, alternative paths, and a highlighted recommended route.
- Route distance, estimated transit time, path cost, and blocked-route count.
- A route-planning form with editable start, destination, and algorithm.
- A prominent Find Best Route button.
- A route comparison table for BFS, DFS, and A*.
- An AI experiments panel with clearly labeled practical modules.
- A recent simulation activity panel.

Create responsive layouts for desktop, tablet, and mobile. Prioritize usability and clarity over excessive animation. All cards, buttons, forms, menus, and tabs must have obvious interactive states. Use realistic but clearly illustrative sample data. Do not present simulated data as live GPS or real-time traffic.
```

---

## 4. Installation & Windows Execution Guide

### Prerequisites
- Python 3.8 to 3.14 (standard Windows installer).
- Standard web browser (Chrome, Edge, Firefox).
- *Optional:* SWI-Prolog (`swipl`) installed and added to PATH (if absent, RouteMind AI automatically switches to its built-in Python Rule-Based Logic Engine fallback).

### Step 1: Open PowerShell or Command Prompt
Navigate to the project root directory:
```powershell
cd "c:\Users\Swayam\OneDrive\Desktop\RouteMind AI"
```

### Step 2: Install Required Dependencies
```powershell
pip install -r requirements.txt
```
*(Dependencies: `flask`, `numpy`, `scikit-learn`, `scikit-fuzzy`, `scipy`)*

### Step 3: Run Automated Test Suites
Run the 10-scenario core verification test suite:
```powershell
python test_routemind.py
```
Run the web server and REST API integration tests:
```powershell
python test_flask_app.py
```

### Step 4: Launch the Application
```powershell
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 5. Walkthrough of the 10 AI Experiments

| # | Module | AI Paradigm | Key Concept Demonstrated |
|---|--------|-------------|--------------------------|
| **1** | **PEAS & Problem Formulation** | Agent Architecture | Formalizes Performance, Environment, Actuators, Sensors, Initial State, Goal State, and step-by-step goal testing. |
| **2** | **Prolog Rule-Based Logic** | Knowledge Representation | Evaluates Horn clauses for road connectivity, high-priority parcel rules, and blocked avoidance. Auto-exports `.pl` file. |
| **3** | **Uninformed Search (BFS & DFS)** | Classical Search | Compares queue-based BFS (fewest edges) with stack-based DFS (deep exploration, non-optimal). |
| **4** | **Informed Search (A\*)** | Heuristic Search | Computes $f(n) = g(n) + h(n)$ using admissible Euclidean straight-line distance heuristic scaled to travel time. |
| **5** | **Minimax Decision Tree** | Game Theory | Models dispatcher (MAX) vs adverse traffic conditions (MIN) using backward induction to guarantee optimal utility. |
| **6** | **Fuzzy Logic Controller** | Soft Computing | Evaluates continuous inputs (Congestion 0–100%, Road Condition 1–10) with Mamdani Centroid Defuzzification (0–100 delay score). |
| **7** | **Mamdani vs Sugeno Fuzzy** | Fuzzy Systems | Side-by-side comparison of continuous fuzzy output sets (Mamdani) vs crisp linear polynomial functions (Sugeno). |
| **8** | **Hybrid Neuro-Fuzzy System** | Hybrid AI | Couples an Artificial Neural Network (learning baseline transit delay from empirical data) with a Fuzzy Supervisory safety layer. |
| **9** | **Supervised & Unsupervised ANN** | Machine Learning | Supervised Rosenblatt Perceptron (classification from scratch) vs Unsupervised Competitive Learning (Winner-Take-All clustering). |
| **10**| **Small & Micro Language Models** | Natural Language Processing | Micro Bigram ($N=2$) and Small Trigram ($N=3$) statistical models computing token transition probabilities on a logistics corpus. |

---

## 6. Faculty Demonstration Guide & Viva Prep

### Key Demonstrations to Perform:
1. **Optimal Pathfinding:**
   - On the Dashboard, click **Find Best Route** using **A\***.
   - Observe the highlighted green-to-cyan corridor: **A &rarr; D &rarr; E &rarr; G** (Total time: **52.0 min**, Distance: **43.0 km**).
2. **Autonomous Detour (Blocked Corridor Avoidance):**
   - Click the road toggle button on corridor **D-E** to mark it **BLOCKED**.
   - Notice the dashed crimson line on Cytoscape. Click **Find Best Route**.
   - A* dynamically reroutes via **A &rarr; B &rarr; E &rarr; G** (Total time: **56.0 min**).
   - If all paths are blocked, RouteMind AI displays a friendly **No Valid Route** banner without crashing.
3. **Multi-Algorithm Benchmark:**
   - Click **Run Comprehensive Benchmark**.
   - Point out that **BFS** discovers a path with 3 hops (**A &rarr; B &rarr; C &rarr; G**, 57.0 min), while **A\*** finds the true minimum travel time path (**A &rarr; D &rarr; E &rarr; G**, 52.0 min).

### Common Viva Questions & Answers:
- **Q: Why is A\* guaranteed to find the optimal path?**  
  *A:* Because the Euclidean straight-line distance heuristic is **admissible** ($h(n) \le h^*(n)$); it never overestimates the true remaining transit time to Goal G.
- **Q: What is the computational difference between Mamdani and Sugeno fuzzy inference?**  
  *A:* Mamdani uses continuous fuzzy output sets requiring numerical integration during centroid defuzzification. Sugeno uses crisp mathematical functions and fast weighted-average defuzzification, making it computationally faster.
- **Q: How does the hybrid neuro-fuzzy model operate?**  
  *A:* The neural network learns empirical physics from simulated road data, while the fuzzy supervisory layer enforces human-interpretable domain rules and weather adjustments.

---

## 7. Verification & Test Results

The project includes automated test coverage validating all 10 evaluation scenarios:

```
[PASS] Scenario 1: Valid route A -> G found: ['A', 'D', 'E', 'G'] (52.0 min)
[PASS] Scenarios 2 & 3: Rerouted successfully avoiding blocked D-E/B-E: ['A', 'B', 'C', 'G']
[PASS] Scenario 4: Gracefully detected disconnected destination G without crashing.
[PASS] Scenario 5: Same node (B -> B) returns zero transit.
[PASS] Scenario 6: Invalid node 'Z' handled safely with descriptive error message.
[PASS] Scenario 7: Network edit (express bypass) immediately chosen as optimal path.
[PASS] Scenario 8: Fuzzy controller correctly classifies Low, Med, High traffic conditions.
[PASS] Scenario 9: Perceptron, Competitive Learning, and Neuro-Fuzzy models generate valid predictions.
[PASS] Scenario 10: Micro and Small language models gracefully handled known and unknown contexts.
```

---

## 8. Limitations & Disclaimers

1. **Synthetic Demonstration Data:** All network metrics, traffic congestion percentages, and neural training sets are generated synthetically for educational purposes. Simulated data is never presented as live GPS feeds or real-time municipality telemetry.
2. **Zero Paid APIs:** The entire software stack runs 100% locally on a Windows laptop without requiring OpenAI, Google Cloud, or external API keys.
3. **Prolog Compatibility:** If SWI-Prolog (`swipl`) is not detected on the Windows PATH, the system transparently utilizes its built-in Python Rule-Based Logic Engine fallback while clearly informing the user.
