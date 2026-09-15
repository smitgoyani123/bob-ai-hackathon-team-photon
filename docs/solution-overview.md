# Solution Overview

## What We Built

GridGuard AI is an autonomous, end-to-end power grid failure prediction, risk assessment, and field crew pre-positioning platform. It transforms raw utility telemetry, geospatial coordinates, and ambient weather radar feeds into explainable operational dispatch decisions in real-time, enabling grid operators to inspect high-consequence electrical assets and pre-position certified repair crews before cascading power failures occur.

## How It Works

The platform processes telemetry through a unified 7-step deterministic pipeline:

1. **Telemetry & Weather Ingestion**: Ingests equipment specs (age, operating temperature, load %, voltage, customer count, critical facility status), incident logs, and regional weather radar data (rainfall, wind speed, ambient temperature, storm alerts).
2. **Preprocessing & Geospatial Joins**: Performs median imputation for missing values and maps each equipment asset to the nearest weather station using geodesic Haversine mathematics.
3. **Machine Learning Failure Prediction**: A 21-feature Random Forest Classifier models asset degradation and estimates 7-day failure probabilities ($0.0 \le P(\text{failure}) \le 1.0$) with class balancing.
4. **Multi-Signal Risk Formulation**:
   - **Weather Risk (0–100)**: $0.40 \times \text{rainfall} + 0.30 \times \text{wind} + 0.20 \times \text{temp\_stress} + 0.10 \times \text{storm}$.
   - **Grid Impact (0–100)**: $0.40 \times \text{customers} + 0.20 \times \text{critical\_facility} + 0.20 \times \text{load} + 0.20 \times \text{network\_importance}$.
   - **Composite Priority Score (0–100)**: $0.50 \times (P(\text{failure}) \times 100) + 0.20 \times \text{Weather Risk} + 0.30 \times \text{Grid Impact}$.
5. **Zero-Hallucination Explainability**: Evaluates 16 data-grounded engineering threshold rules per asset to generate an auditable AI Decision Card.
6. **Automated Crew Pre-positioning**: Filters certified available field crews (Electrical, Mechanical, Civil), calculates Haversine distances to high-risk assets, and assigns the closest qualified crew.
7. **Interactive Command Center Delivery**: Renders real-time telemetry, live RainViewer Doppler radar overlays, satellite GIS layers, what-if stress simulation, and alert dispatch workflows across a 7-page React 19 interface.

## Architecture Diagram

> See [`architecture.md`](architecture.md) for the detailed system architecture diagram.

```
[SCADA Telemetry & Weather Feeds]
              ↓
  [FastAPI Backend Pipeline]
  ├── Preprocessing & Haversine Joins
  ├── Random Forest Failure Predictor
  ├── Weather Risk & Grid Impact Engines
  └── Crew Pre-positioning Optimizer
              ↓
  [REST API: http://localhost:8000]
              ↓
  [React 19 GIS Command Center: http://localhost:5173]
  ├── Overview Telemetry & Risk Matrix
  ├── Fullscreen Leaflet GIS & Doppler Radar
  ├── Equipment Intelligence & AI Decision Card
  ├── Crew Operations & Route Dispatch
  ├── Parametric What-If Scenario Simulator
  └── Audit Alert Center (CSV / JSON Export)
```

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **Random Forest for Failure Prediction** | Robust to tabular non-linear interactions between age, thermal stress, and weather without requiring deep neural architectures; provides fast deterministic inference and verifiable feature importances. |
| **Deterministic Threshold Rules over Generative LLM Text** | High-voltage utility dispatch requires strict auditable accountability; deterministic rules eliminate LLM hallucinations and ensure compliance with utility safety standards. |
| **Composite Multi-Signal Priority Formula** | Prevents dispatch blindness by balancing failure likelihood ($50\%$), severe weather exposure ($20\%$), and humanitarian/grid criticality ($30\%$). |
| **Haversine Geodesic Matching with Skill Compatibility** | Guarantees that dispatched crews have the exact trade certification (e.g. Electrical for Transformers, Mechanical for Switches) while minimizing travel transit time. |
| **Decoupled FastAPI + React 19 Architecture** | Enables sub-second pipeline execution via high-speed Python numerical libraries while delivering a fluid, control-room grade dark cyber GIS dashboard. |

## IBM Technologies Used

- **IBM Bob**: Utilized as the primary AI Software Engineering Partner throughout the development lifecycle:
  - **System Architecture & Modular Boundaries**: Formulating clean abstractions between data ingestion, machine learning inference, risk engines, and geospatial dispatch.
  - **Algorithm & Vector Optimization**: Authoring vectorized numpy calculations, scikit-learn training pipelines, and Haversine distance functions.
  - **Code Generation & Review**: Implementing reactive TypeScript interfaces, Leaflet GIS mapping components, and NaN-sanitized REST responses.
  - **Testing & Diagnostics**: Structuring acceptance verification scripts, smoke test suites, and pre-flight validation routines.
