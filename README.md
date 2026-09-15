# GridGuard AI

**Team:** Photon | **Track:** AI | **Hackathon:** IBM Bob Hackathon 2025

> Predict. Assess. Prioritize. Assign. Keep the Power On.

---

## Team

| Role | Name | Email |
|---|---|---|
| Lead | TODO: Lead Name | TODO: lead@example.com |
| AI/ML Engineer | TODO: Member 1 | TODO: member1@example.com |
| Risk & Dashboard | TODO: Member 2 | TODO: member2@example.com |
| Integration & QA | TODO: Member 3 | TODO: member3@example.com |

---

## Problem Statement

Power grid operators have no predictive signal for equipment failure. Transformers, switches, and transmission lines fail unpredictably due to combinations of age, load, temperature, weather exposure, and prior incident history. When failure occurs, crews are dispatched reactively from suboptimal locations with no risk prioritisation and no network impact scoring — causing prolonged outages, critical facility disruption, and wasted field capacity.

---

## Solution

GridGuard AI is an end-to-end AI-powered grid failure prediction, risk assessment, and crew pre-positioning platform. It converts raw equipment, weather, and incident data into fully explainable operational field assignments in under one second — predicting failure probability per asset, scoring weather exposure and grid impact, computing a composite priority score, explaining exactly why each asset is at risk, recommending the correct maintenance action, and assigning the nearest available skill-matched crew via Haversine distance.

---

## Key Features

- **RandomForest failure prediction** — 21 engineered features, `class_weight=balanced`, `random_state=42`
- **Weather Risk Engine** — `0.40×rainfall + 0.30×wind + 0.20×temp_stress + 0.10×storm` (0–100)
- **Grid Impact Engine** — `0.40×customers + 0.20×critical_facility + 0.20×load + 0.20×network_importance` (0–100)
- **Priority Score** — `0.50×failure_probability + 0.20×weather_risk + 0.30×grid_impact` with CRITICAL/HIGH/MEDIUM/LOW levels
- **Deterministic explainability** — 16 threshold-based data-grounded risk factors per asset
- **Crew pre-positioning** — Haversine distance + skill match + availability filter
- **What-if Scenario Simulator** — adjust wind, rain, temperature, load to explore risk escalation interactively
- **7-page enterprise dashboard** — Grid Map, Risk Matrix, AI Decision Card, Crew Operations, Alert Center

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| Data Processing | pandas, NumPy |
| Machine Learning | scikit-learn (RandomForestClassifier), joblib |
| Dashboard | Streamlit |
| Charts | Plotly |
| Map | Folium + streamlit-folium |
| Geospatial | Haversine (Python stdlib math) |
| AI SDLC Partner | IBM Bob |

---

## IBM Bob Integration

IBM Bob was used as the AI software engineering and SDLC partner throughout the entire project:

| Phase | Bob Mode | Usage |
|---|---|---|
| Architecture design | Ask + Plan | System design, module boundaries, data flow |
| Implementation | Agent | All Python source code generated and refined |
| Testing | Shell | Smoke-tests run after every module |
| Code review | Agent | NaN bugs, encoding issues, edge cases fixed |
| Documentation | Agent | All docs, README, architecture diagram generated |

> IBM Bob is a **development tool**, not a runtime component. All AI decisions in GridGuard AI run on scikit-learn and deterministic Python formulas — not on a language model at runtime.

---

## How to Run

**Prerequisites:** Python 3.9+, pip, git

```bash
# 1. Clone the repository
git clone https://github.com/TODO-your-org/bob-ai-hackathon-photon.git
cd bob-ai-hackathon-photon

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\Activate.ps1       # Windows PowerShell

# 3. Install dependencies
pip install -r src/requirements.txt

# 4. Run the prediction pipeline
python src/main.py

# 5. Launch the dashboard
streamlit run src/dashboard/app.py
```

Dashboard opens at **http://localhost:8501**

See [`docs/setup-guide.md`](docs/setup-guide.md) for full instructions and troubleshooting.

---

## Repository Structure

```
bob-ai-hackathon-photon/
├── src/
│   ├── config/settings.py          # Centralised path config
│   ├── data/raw/                   # equipment, weather, incidents, crews CSVs
│   ├── data/processed/             # model_input.csv (generated)
│   ├── models/                     # failure_model.pkl (generated)
│   ├── results/                    # predictions.csv (generated)
│   ├── dashboard/
│   │   ├── app.py                  # Streamlit entry point
│   │   ├── pages/                  # 7 dashboard pages
│   │   └── styles/theme.css        # Dark enterprise CSS theme
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── failure_prediction.py
│   ├── weather_risk.py
│   ├── grid_impact.py
│   ├── priority.py
│   ├── explainability.py
│   ├── crew_assignment.py
│   ├── pipeline.py
│   └── main.py
├── docs/
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
├── demo/
│   ├── demo-video-link.txt
│   ├── live-demo-url.txt
│   └── screenshots/
├── presentation/
│   └── gridguard-presentation.md
├── submission.yaml
└── README.md
```

---

## End-to-End Workflow

```
RAW DATA  -->  PREPROCESSING  -->  ML PREDICTION  -->  WEATHER RISK
          -->  GRID IMPACT  -->  PRIORITY SCORE  -->  EXPLAINABILITY
          -->  MAINTENANCE ACTION  -->  CREW ASSIGNMENT  -->  DASHBOARD
```

---

## Demo

- **Video:** [demo/demo-video-link.txt](demo/demo-video-link.txt) — TODO: record and add URL
- **Live Demo:** [demo/live-demo-url.txt](demo/live-demo-url.txt) — NOT DEPLOYED
- **Screenshots:** [demo/screenshots/](demo/screenshots/) — TODO: add after recording

---

## Known Limitations

- Dataset is **synthetic demo data** (`random_state=42`) — not real utility telemetry
- Risk formulas are simplified composites, not calibrated against real outage history
- `network_importance` is derived from available features, not a real network topology graph
- Crew assignment uses nearest Haversine distance only — no traffic, shift, or multi-crew optimisation
- ML model trained on 30 rows — metrics reflect the demo dataset, not production scale
- No real-time data feed — pipeline must be re-run manually to refresh predictions

---

## What We Are Most Proud Of

The core innovation of GridGuard AI is the **prediction-to-decision pipeline**.

Most ML projects stop at a probability score. GridGuard AI answers the operational question: *What does that score mean? What should we do? Who should go? How far are they?*

Every value shown in the dashboard is calculated from actual data. Every risk explanation is grounded in a real feature threshold. No numbers are hard-coded. No metrics are fabricated.

That is what makes GridGuard AI a genuine operational tool, not a demo.
