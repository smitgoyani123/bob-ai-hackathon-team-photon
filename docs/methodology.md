# 📐 GridGuard AI — Engineering & Mathematical Methodology

This document details the mathematical formulations, feature engineering pipelines, machine learning algorithms, and dispatch optimization logic implemented in GridGuard AI.

---

## 1. Feature Engineering & Preprocessing

The preprocessing module (`src/preprocessing.py`) ingests 4 distinct utility datasets and creates 21 engineered signals:

### 1.1 Data Ingestion & Imputation
- **Equipment Telemetry**: Age (years), Operating Temperature (°C), Grid Load (%), Health Index (0–100), Operating Voltage (kV), Connected Customers, Critical Facility Flag (0/1), Latitude/Longitude.
- **Missing Value Handling**: Median imputation for numerical attributes to preserve distribution robustness against extreme outliers.
- **Geospatial Nearest-Zone Weather Join**: Each equipment asset is mapped to the closest weather monitoring station using spherical Haversine distance:
  $$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
  where $R = 6371\text{ km}$.

### 1.2 Core Engineered Features
1. **`temp_stress`**: Compound thermal stress ratio:
   $$\text{temp\_stress} = \frac{\text{operating\_temp}}{\text{max}(1.0, \text{ambient\_temp})} \times \left(\frac{\text{load\_pct}}{100}\right)$$
2. **`incident_rate`**: Historical failure frequency adjusted for asset operating lifespan:
   $$\text{incident\_rate} = \frac{\text{previous\_incidents} + 1}{\text{age} + 1}$$
3. **`network_importance`**: Multi-factor topological criticality index (0–100):
   $$\text{network\_importance} = 0.40 \times \left(\frac{\text{customers}}{5000} \times 100\right) + 0.30 \times (\text{critical\_facility} \times 100) + 0.30 \times \left(\frac{\text{voltage\_kv}}{132} \times 100\right)$$
4. **`load_risk_flag`**: Binary indicator triggered when grid load exceeds 85% capacity.
5. **`age_risk_flag`**: Binary indicator triggered when equipment age exceeds 20 years.

---

## 2. Machine Learning Failure Prediction

The predictive engine (`src/failure_prediction.py`) employs a **Random Forest Classifier**:
- **Target Variable**: `failure_next_7_days` (binary 0/1).
- **Hyperparameters**:
  - `n_estimators`: 100 decision trees
  - `criterion`: Gini impurity
  - `max_depth`: None (full tree expansion with leaf regularization)
  - `class_weight`: `"balanced"` (mitigating positive class imbalance)
  - `random_state`: 42 (ensuring deterministic reproducibility)
- **Output**: Calibrated class probability $P(\text{failure}) \in [0.0, 1.0]$ via `predict_proba`.

---

## 3. Multi-Signal Operational Engines

### 3.1 Weather Risk Engine (0–100)
Combines ambient and severe meteorological metrics into a normalized scale:
$$\text{Weather Risk} = 0.40 \times \text{rainfall\_norm} + 0.30 \times \text{wind\_norm} + 0.20 \times \text{temp\_stress\_norm} + 0.10 \times (\text{storm\_alert} \times 100)$$

### 3.2 Grid Consequence Impact Engine (0–100)
Evaluates downstream humanitarian, network, and economic ramifications:
$$\text{Grid Impact} = 0.40 \times \text{customer\_impact} + 0.20 \times (\text{critical\_facility} \times 100) + 0.20 \times \text{load\_pct} + 0.20 \times \text{network\_importance}$$

### 3.3 Composite Priority Score (0–100)
Synthesizes the three distinct threat dimensions into a single operational dispatch score:
$$\text{Priority Score} = 0.50 \times (P(\text{failure}) \times 100) + 0.20 \times \text{Weather Risk} + 0.30 \times \text{Grid Impact}$$

#### Risk Categorization Thresholds:
- **CRITICAL** ($80 \le \text{Score} \le 100$): Mandatory immediate field inspection.
- **HIGH** ($60 \le \text{Score} < 80$): Scheduled preventive maintenance within 24 hours.
- **MEDIUM** ($30 \le \text{Score} < 60$): Continuous telemetry monitoring.
- **LOW** ($0 \le \text{Score} < 30$): Standard routine maintenance.

---

## 4. Field Crew Pre-Positioning Optimization

The dispatch algorithm (`src/crew_assignment.py`) executes spatial and operational matching:
1. **Candidate Eligibility Filtering**:
   - `status == "Available"`
   - `capacity > 0`
   - `skill_set` compatible with equipment category (e.g. Electrical crew for Transformers, Mechanical crew for Automated Switches, Civil crew for Transmission Lines).
2. **Geodesic Distance Ranking**:
   - Calculates Haversine distance between candidate crew depot coordinates and equipment GPS coordinates.
3. **Dispatch Allocation**:
   - Selects nearest qualified crew $\arg\min_{c \in \text{Eligible}} \text{dist}(c, e)$.
   - Decrements crew capacity and records assignment distance in `predictions.csv`.
