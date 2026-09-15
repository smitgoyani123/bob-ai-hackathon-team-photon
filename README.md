# ⚡ GridGuard AI — Autonomous Power Grid Failure Prediction & Operational Command Center

**Team:** Photon | **Track:** AI & Smart Infrastructure | **Hackathon:** IBM Bob Hackathon 2025

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React 19](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Leaflet GIS](https://img.shields.io/badge/Leaflet-GIS_Map-199900.svg)](https://leafletjs.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Predict. Assess. Prioritize. Assign. Keep the Power On.**  
> Transforming raw grid SCADA telemetry, ambient weather spikes, and historical incident logs into explainable operational field crew pre-positioning in real-time.

---

## 👥 Team Photon

| Role | Name | Email |
|---|---|---|
| **AI / ML Engineer** | Smit Goyani | goyanismit04@gmail.com |
| **Risk Engine Specialist** | Parikshit Matieda | parikshit.matieda2005@gmail.com |
| **Frontend & Command Center** | Parth Mavani | parthmavani2706@gmail.com |
| **Integration & QA Engineer** | Divy Rajput | 24it047@charusat.edu.in |

---

## ⚡ The Problem

Power grid equipment (transformers, automated switches, high-voltage transmission lines) fails unpredictably under intense thermal stress, overload, physical aging, and severe monsoon or storm conditions. Today, grid dispatchers and utilities face significant bottlenecks:

1. **Reactive Disaster Response**: Crews are dispatched only *after* a transformer explodes or a feeder trips, prolonging power restoration by hours.
2. **Suboptimal Crew Dispatch**: Field technicians are dispatched from distant depots or lack the certified skill set required for the specific equipment type.
3. **Black-Box Confusion**: Operators have no explainability signal explaining *why* an asset is prioritized.
4. **Disjointed Weather & Grid Telemetry**: Weather radar and SCADA systems operate in silos, blinding engineers to localized storm impacts.

---

## 💡 The GridGuard AI Solution

GridGuard AI closes the loop from **raw sensor signal to proactive field dispatch**. It ingests equipment telemetry, assigns nearest weather station data via spatial Haversine mathematics, runs a 21-feature Random Forest ML failure model, computes multidimensional grid impact and weather risk, provides deterministic explainability, and automatically pre-positions certified field crews before an outage cascades.

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│ Raw SCADA Data  │ ──> │  Preprocessing   │ ──> │ ML Failure Model     │
│ Equipment/Crews │     │  & Imputation    │     │ (RandomForest 7-Day) │
└─────────────────┘     └──────────────────┘     └──────────────────────┘
                                                            │
                                                            ▼
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│  Leaflet GIS    │ <── │ Crew Proximity   │ <── │ Priority Engine      │
│  Command Center │     │ (Haversine Disp) │     │ (0 - 100 Multi-Risk) │
└─────────────────┘     └──────────────────┘     └──────────────────────┘
```

---

## 🌟 Key Capabilities & Features

### 1. 🤖 Multi-Signal Machine Learning & Risk Engines
- **Failure Prediction (Random Forest Classifier)**: 21 engineered features (`temp_stress`, `incident_rate`, `network_importance`, `load_risk_flag`, etc.) with `class_weight="balanced"`.
- **Weather Risk Engine (0–100)**:
  $$\text{Weather Risk} = 0.40 \times \text{Rainfall} + 0.30 \times \text{Wind} + 0.20 \times \text{Temp Stress} + 0.10 \times \text{Storm}$$
- **Grid Consequence Impact Engine (0–100)**:
  $$\text{Grid Impact} = 0.40 \times \text{Customers} + 0.20 \times \text{Critical Facility} + 0.20 \times \text{Load} + 0.20 \times \text{Importance}$$
- **Composite Priority Score (0–100)**:
  $$\text{Priority} = 0.50 \times (\text{Failure Prob} \times 100) + 0.20 \times \text{Weather Risk} + 0.30 \times \text{Grid Impact}$$
  Categorized into `CRITICAL` (80–100), `HIGH` (60–80), `MEDIUM` (30–60), and `LOW` (0–30).

### 2. 🔍 Zero-Hallucination Deterministic Explainability
- Evaluates 16 data-grounded threshold rules per asset (e.g. `Aging equipment (>20 yrs)`, `Operating Temp > 70°C`, `Load > 75%`, `Critical Facility Dependency`).
- Generates transparent, verifiable operational reasons without black-box hallucination.

### 3. 🗺️ Real-World Interactive GIS Mapping
- **Multiple Cartographic Views**:
  - 🗺️ **OpenStreetMap Real**: Street-level topology, landmarks, substations, and roads.
  - 🛰️ **Esri World Satellite Imagery**: Real aerial photographic view of electrical physical infrastructure.
  - 🏙️ **City Navigation (Voyager)**: Clean urban GIS presentation.
  - 🌙 **Tactical Dark Ops**: Command-center dark mode.
- **Live Weather Radar Overlay**: Real-time Doppler precipitation radar powered by the RainViewer API.
- **Pre-positioning Dispatch Lines**: Animated flight paths connecting field crew depots directly to high-risk assets with Haversine distance badges.
- **Camera Fly-to Navigation**: Smooth animated glide to any selected equipment node.

### 4. 📂 Custom CSV & Real-Time Data Ingestion
- **One-Click Import CSV**: Directly upload custom or real-time utility equipment `.csv` files from the top navigation bar.
- **Instant Pipeline Recalculation**: Ingests the data, runs the full end-to-end ML and risk pipeline, and dynamically updates the entire dashboard, GIS map, and crew rosters in under 2 seconds.
- **Template Download**: Provides `equipment_template.csv` with the exact schema for instant operational onboarding.

### 5. 🎛️ Interactive What-If Scenario Simulator
- Parametric sliders for **Wind Speed**, **Rainfall**, **Operating Temp**, **Grid Load %**, **Severe Storm Flag**, and **Flood Risk**.
- Real-time reactive recalculation comparing baseline telemetry against simulated escalations.

---

## 🖥️ React Command Center Suite (7 Operational Views)

| View | Description |
|---|---|
| **1. Command Center** | Executive KPIs (Health Score 55.3%, Asset Count, Crew Fleet Readiness, Critical Facilities at Risk), Emergency Alert Ticker, Multi-Signal Risk Matrix, and Action Queue. |
| **2. Risk Command** | Multidimensional filtering (Type, Risk, Critical Facilities), asset-class breakdown bar charts, 2D risk dispersion plot, and prioritized ranking table. |
| **3. Live Grid Map** | Fullscreen GIS Leaflet map with real-world satellite, street, and dark layers, live Doppler rain radar, and crew-to-asset dispatch lines. |
| **4. Equipment Intelligence** | Single-asset deep dive, physical specs, 6-vector radar signature, AI explainability factors, and one-click crew dispatch orders. |
| **5. Crew Operations** | Fleet readiness, certified skill mapping (Electrical, Mechanical, Civil), vehicle capacities, and mapped target assets. |
| **6. AI Insights & Sim** | Random Forest model architecture, global feature importance chart, and interactive parametric stress-testing simulator. |
| **7. Alert Center** | Filterable operational alerts with acknowledgement checkboxes and one-click export to **CSV** and **JSON**. |

---

## 🛠️ Tech Stack & Architecture

- **Backend & Pipeline**: Python 3.9+, FastAPI, Uvicorn, pandas, NumPy, scikit-learn, joblib.
- **Frontend Command Center**: React 19, TypeScript, Vite, Recharts, Leaflet, React-Leaflet, Lucide Icons, Vanilla CSS Design System.
- **Geospatial Engine**: Haversine Geodesic Distance algorithms, OpenStreetMap, Esri World Imagery, RainViewer Doppler API.
- **SDLC & AI Partner**: IBM Bob.

---

## 🚀 Quick Start & Installation

### 1. Clone & Setup Environment

```bash
# Clone the repository
git clone https://github.com/TODO-your-org/bob-ai-hackathon-photon.git
cd bob-ai-hackathon-photon

# Create and activate Python virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install Python backend dependencies
pip install -r src/requirements.txt
```

### 2. Start Backend FastAPI Server

```bash
# From project root:
python src/api.py
```
*The FastAPI backend starts at **http://localhost:8000** (Swagger documentation available at **http://localhost:8000/docs**).*

### 3. Start React 19 Frontend

```bash
# In a new terminal, navigate to frontend:
cd frontend
npm install
npm run dev
```
*The command center opens at **http://localhost:5173**.*

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status and asset availability flag |
| `GET` | `/api/summary` | Executive telemetry summary, health index, risk counts |
| `GET` | `/api/predictions` | Complete predictions dataset with explainability reasons |
| `GET` | `/api/equipment/{id}` | Single equipment technical specs and AI decision summary |
| `GET` | `/api/crews` | Crew fleet roster, skills, and active pre-positioned targets |
| `GET` | `/api/feature-importance`| Model weights from the trained Random Forest classifier |
| `POST` | `/api/simulate` | Interactive what-if scenario priority calculator |
| `POST` | `/api/pipeline/run` | Trigger full end-to-end pipeline execution |
| `POST` | `/api/upload/equipment`| Upload custom equipment CSV and dynamically refresh grid |
| `GET` | `/api/template/equipment`| Download standard equipment CSV template |

---

## 📁 Repository Structure

```
bob-ai-hackathon-photon/
├── src/
│   ├── config/settings.py          # Centralized path configuration
│   ├── data/
│   │   ├── raw/                    # equipment.csv, weather.csv, incidents.csv, crews.csv
│   │   └── processed/              # model_input.csv (feature-engineered)
│   ├── models/failure_model.pkl    # Trained Random Forest classifier
│   ├── results/predictions.csv     # Full prediction & dispatch results
│   ├── api.py                      # FastAPI REST service & upload engine
│   ├── pipeline.py                 # End-to-end orchestration pipeline
│   ├── preprocessing.py            # Missing-value imputation & feature engineering
│   ├── failure_prediction.py       # Random Forest training & inference
│   ├── weather_risk.py             # Weather risk formulation engine
│   ├── grid_impact.py              # Grid consequence scoring engine
│   ├── priority.py                 # Multi-signal priority scoring
│   ├── explainability.py           # Deterministic threshold explainability
│   └── crew_assignment.py          # Haversine distance & skill-matched dispatch
├── frontend/
│   ├── src/
│   │   ├── components/             # Navbar.tsx, Sidebar.tsx
│   │   ├── pages/                  # Overview, Risk, Map, Equipment, Crews, Sim, Alerts
│   │   ├── types/grid.ts           # Strict TypeScript interfaces
│   │   ├── index.css               # Obsidian & cyber dark command-center design system
│   │   └── App.tsx                 # Application root & reactive state hub
│   ├── package.json
│   └── vite.config.ts
├── docs/                           # Problem statement, solution, architecture, setup guides
├── demo/                           # Video links, live URLs, and screenshots
├── ui_diagnostic.py                # Pre-launch diagnostic test suite
├── validate.py                     # Acceptance validation script
└── README.md                       # Comprehensive documentation
```

---

## 🤝 IBM Bob Integration

IBM Bob served as the AI Software Engineering partner across the complete SDLC:
- **System Architecture**: Defining modular boundaries between data loading, ML modeling, and geospatial dispatch.
- **Code Generation & Optimization**: Authoring robust scikit-learn models, vector-safe normalization formulas, and reactive React components.
- **Testing & Diagnostics**: Automated smoke tests, NaN-sanitization in JSON pipelines, and end-to-end validation.

> **Integrity Note**: IBM Bob was utilized during the development lifecycle. All real-time predictions, explainability evaluations, and crew dispatches are generated locally by scikit-learn and deterministic mathematical engines.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
