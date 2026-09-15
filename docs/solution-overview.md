# Solution Overview

## What GridGuard AI Does

GridGuard AI converts raw grid data into fully explainable operational decisions, following a deterministic pipeline from raw CSV data through to crew field assignments.

---

## Core Workflow

```
RAW DATA (Equipment + Weather + Incidents + Crews)
        |
        v
   PREPROCESSING
   - Clean & validate all four datasets
   - Median imputation for missing numerics
   - Nearest-zone weather assignment (Haversine)
   - Feature engineering (temp_stress, incident_rate, network_importance)
        |
        v
   FAILURE PREDICTION (Random Forest Classifier)
   - 21 engineered features
   - Predicts failure_next_7_days (binary)
   - Outputs failure_probability per asset (0.0 – 1.0)
        |
        v
   WEATHER RISK ENGINE
   - Formula: 0.40 × rainfall + 0.30 × wind + 0.20 × temp_stress + 0.10 × storm
   - Output: 0 – 100
        |
        v
   GRID IMPACT ENGINE
   - Formula: 0.40 × customers + 0.20 × critical_facility + 0.20 × load + 0.20 × network_importance
   - network_importance derived transparently from voltage + customers + criticality
   - Output: 0 – 100
        |
        v
   PRIORITY ENGINE
   - Formula: 0.50 × failure_probability + 0.20 × weather_risk + 0.30 × grid_impact
   - Output: 0 – 100
   - Risk levels: LOW (0-30) / MEDIUM (30-60) / HIGH (60-80) / CRITICAL (80-100)
        |
        v
   EXPLAINABILITY ENGINE
   - 16 deterministic threshold-based risk factors
   - Only breached factors shown per asset
   - No generated text — fully data-grounded
        |
        v
   MAINTENANCE DECISION
   - CRITICAL  -> Immediate Inspection
   - HIGH      -> Preventive Maintenance
   - MEDIUM    -> Monitor
   - LOW       -> Normal Maintenance
        |
        v
   CREW PRE-POSITIONING (Haversine + Skill Match)
   - Filter: available, skill-compatible, positive capacity
   - Rank by Haversine distance
   - Select nearest suitable crew
        |
        v
   RESULTS (predictions.csv + Dashboard)
```

---

## Failure Prediction

**Algorithm:** RandomForestClassifier (scikit-learn)  
**Target:** `failure_next_7_days` (binary)  
**Features (21):** age, temperature, load, health, voltage, customers_served, critical_facility, previous_incidents, severity_encoded, days_since_last_failure, weather_rainfall, weather_wind, weather_temperature, weather_storm, weather_flood_risk, age_risk_flag, health_risk_flag, load_risk_flag, temp_stress, incident_rate, network_importance  
**Class balancing:** `class_weight="balanced"` to handle imbalanced targets  
**Reproducibility:** `random_state=42`  

---

## Weather Risk

The weather risk formula weights four sub-signals:

| Component | Weight | Derivation |
|---|---|---|
| Rainfall risk | 40% | Min-max normalised rainfall |
| Wind risk | 30% | Min-max normalised wind speed |
| Temperature stress | 20% | Degrees above 35°C safe threshold |
| Storm risk | 10% | Binary storm flag (60%) + flood_risk (40%) |

All normalisation uses epsilon-guard division to prevent zero-division errors.

---

## Grid Impact

The grid impact formula reflects operational consequence of failure:

| Component | Weight | Derivation |
|---|---|---|
| Customer impact | 40% | Min-max normalised customers_served |
| Critical facility | 20% | Binary flag × 100 |
| Load impact | 20% | Min-max normalised load |
| Network importance | 20% | Derived: 40% voltage + 40% customers + 20% criticality |

---

## Priority Score

```
priority_score = 0.50 × (failure_probability × 100)
               + 0.20 × weather_risk
               + 0.30 × grid_impact
```

---

## Explainability

Each asset receives a data-driven explanation listing only the risk factors that are actually breached:

- "Aging equipment (>20 years)"
- "High operating temperature (>70°C)"
- "High load (>75%)"
- "Low equipment health (<40)"
- "High historical incident count (>4)"
- "Severe weather exposure (risk >55)"
- "Active storm conditions"
- "High customer dependency (>4000 customers)"
- "Critical facility dependency"
- ... and 7 more threshold conditions

No text is generated or hallucinated. Every factor is directly tied to a feature value threshold.

---

## Crew Pre-Positioning

Assignment only triggers for HIGH and CRITICAL risk assets. For each eligible asset:

1. Filter crews to `status == available`
2. Match crew skill to equipment type (electrical → Transformer/Switch, mechanical → Switch/Line, civil → Line/Transformer)
3. Filter by `capacity > 0`
4. Compute Haversine distance to all eligible crews
5. Assign nearest crew

---

## Dashboard

Seven pages in a dark-navy enterprise command-centre UI:

| Page | Purpose |
|---|---|
| Overview | Grid health gauge, KPIs, critical attention cards |
| Risk Command Center | Risk matrix, priority charts, full risk table |
| Live Grid Map | Folium map with risk-coded markers and popups |
| Equipment Intelligence | AI Decision Card with explainability per asset |
| Crew Operations | Crew roster, skill distribution, assignments |
| AI Insights | Model metrics, feature importance, scenario simulator |
| Alert Center | Filtered alert list with download |

---

## IBM Bob Development Workflow

IBM Bob was used throughout the entire SDLC as an AI software engineering partner:

- **Architecture design** — system design, pipeline flow, module boundaries
- **Code generation** — all Python modules written with Bob in Agent Mode
- **Code review** — iterative review and bug fixing
- **Testing** — smoke-test validation after each module
- **Documentation** — this document and all other docs generated with Bob

IBM Bob is **not** used as a runtime API or backend service within the application. The AI decisions in GridGuard AI are produced by the RandomForestClassifier and the deterministic rule engine, not by a language model.
