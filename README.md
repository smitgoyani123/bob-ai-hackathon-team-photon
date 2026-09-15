# 🚀 GridGuard AI — Autonomous Power Grid Failure Prediction & Operational Command Center

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | Team Photon |
| **Track** | AI |
| **Team Lead** | Parikshit Matieda — [24it049@charusat.edu.in](mailto:24it049@charusat.edu.in) |
| **Members** | Parth Mavani — [24it050@charusat.edu.in](mailto:24it050@charusat.edu.in)<br>Smit Goyani — [24it026@charusat.edu.in](mailto:24it026@charusat.edu.in)<br>Divy Mangukiya — [24it047@charusat.edu.in](mailto:24it047@charusat.edu.in) |

---

## 🎯 Problem Statement

Power grid operators and transmission engineers have no predictive signal for equipment failure, forcing them to rely on fixed schedules or reactive disaster recovery after assets trip. When power equipment fails unpredictably during high thermal loads or severe storm conditions, emergency crews are dispatched reactively from distant depots with no network impact prioritization. This leads to prolonged cascading blackouts, critical facility disruptions (such as hospitals and water plants), wasted field capacity, and severe regulatory penalties.

---

## 💡 Solution

GridGuard AI is an autonomous, end-to-end power grid failure prediction, consequence risk assessment, and field crew pre-positioning platform. It ingests SCADA telemetry, geospatial coordinates, and ambient weather radar to train a 21-feature Random Forest machine learning classifier that predicts 7-day failure probabilities. It combines these predictions with multi-component weather risk and grid consequence scores, generates zero-hallucination deterministic explanations, and dynamically pre-positions certified repair crews via geodesic Haversine distance before blackouts cascade.

---

## ✨ Key Features

- **Multi-Signal ML & Risk Engines**: 21-feature Random Forest failure classifier coupled with a 4-component weather risk engine (rainfall, wind, thermal stress, storm) and a consequence impact scoring formula.
- **Zero-Hallucination Deterministic Explainability**: 16 data-grounded engineering threshold rules evaluated per asset to provide transparent, verifiable operational reasons without black-box drift.
- **Interactive Leaflet GIS Command Center**: Fullscreen mapping with street, satellite, and dark tactical layers, live Doppler precipitation radar overlay (RainViewer API), and animated pre-positioning dispatch flight paths.
- **Parametric What-If Scenario Simulator**: Interactive environmental stress sliders (wind speed, precipitation, temperature, grid load, storm alerts) enabling operators to simulate extreme storm fronts and inspect risk escalations in real-time.
- **Automated Skill-Matched Crew Pre-positioning**: Real-time geodesic matching connecting the nearest available certified field crews (Electrical, Mechanical, Civil) to high-consequence assets prior to failure.

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python 3.9+, TypeScript, SQL, Modern CSS3 |
| **Frameworks** | React 19, Vite, FastAPI, Uvicorn, Leaflet / React-Leaflet, Recharts |
| **IBM Technologies** | IBM Bob (AI Software Engineering Partner for architecture design, vector optimization, and test automation) |
| **Machine Learning & Data** | scikit-learn (RandomForestClassifier), pandas, NumPy, joblib, geopy |
| **Geospatial & APIs** | OpenStreetMap, Esri World Satellite Imagery, RainViewer Doppler Radar API, Haversine Geodesic Math |
| **Tooling & DevOps** | Git, GitHub Actions, Microsoft Edge Headless Testing, npm |

---

## 📁 Repository Structure

```
bob-ai-hackathon-team-photon/
├── src/                            # Backend source code & ML pipeline
│   ├── config/settings.py          # Centralized path configuration
│   ├── data/
│   │   ├── raw/                    # equipment.csv, weather.csv, incidents.csv, crews.csv
│   │   └── processed/              # model_input.csv (feature-engineered dataset)
│   ├── models/failure_model.pkl    # Serialized trained Random Forest classifier
│   ├── results/predictions.csv     # Scored predictions, priority levels & crew assignments
│   ├── api.py                      # FastAPI REST service & live pipeline endpoints
│   ├── pipeline.py                 # End-to-end ML & risk scoring orchestrator
│   ├── preprocessing.py            # Missing-value imputation & 21-feature engineering
│   ├── failure_prediction.py       # Random Forest training, evaluation & inference
│   ├── weather_risk.py             # 4-factor weather risk formulation engine
│   ├── grid_impact.py              # Grid consequence impact scoring engine
│   ├── priority.py                 # Multi-signal priority scoring (0-100) & risk levels
│   ├── explainability.py           # Deterministic 16-factor explainability engine
│   ├── crew_assignment.py          # Haversine distance & skill-matched dispatch
│   └── requirements.txt            # Python dependencies
├── frontend/                       # React 19 + TypeScript Command Center
│   ├── src/
│   │   ├── components/             # Navbar, Sidebar, KPI cards
│   │   ├── pages/                  # Overview, Risk, Map, Equipment, Crews, Sim, Alerts
│   │   ├── types/grid.ts           # Strict TypeScript interfaces
│   │   ├── index.css               # Obsidian & Cyber Dark Enterprise Design System
│   │   └── App.tsx                 # Root application state & API synchronization
│   ├── package.json
│   └── vite.config.ts
├── docs/                           # Comprehensive technical documentation
│   ├── problem-statement.md        # Problem background & user persona
│   ├── solution-overview.md        # Architecture & methodology deep-dive
│   ├── architecture.md             # System diagrams & component tables
│   ├── setup-guide.md              # Step-by-step local execution instructions
│   ├── demo-script.md              # 3-5 minute live demo narration guide
│   ├── methodology.md              # Mathematical formulas & ML design decisions
│   └── explainable-ai.md           # Deterministic explainability rules breakdown
├── demo/                           # Demo artifacts
│   ├── screenshots/                # Real 1080p HD screenshots of all 7 operational views
│   ├── demo-video-link.txt         # Link to 3-5 minute demonstration video
│   └── live-demo-url.txt           # Deployment status / local URL instructions
├── presentation/                   # Presentation materials
│   ├── slides.pdf                  # Exported pitch deck (PDF)
│   ├── slides-link.txt             # Google Slides deck URL
│   └── gridguard-presentation.md   # Presentation script & slide outline
├── submission.yaml                 # Hackathon submission metadata
├── requirements.txt                # Python dependencies (root copy)
└── README.md                       # Main project documentation
```

---

## ⚡ How to Run

Copy these exact steps from your [docs/setup-guide.md](docs/setup-guide.md):

```bash
# 1. Clone the repo
git clone https://github.com/smitgoyani123/bob-ai-hackathon-team-photon.git
cd bob-ai-hackathon-team-photon

# 2. Install dependencies & activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r src/requirements.txt

# 3. Configure environment
cp .env.example .env

# 4. Run the project
# Terminal 1 — Start FastAPI Backend:
python src/api.py

# Terminal 2 — Start React 19 Frontend Command Center:
cd frontend
npm install
npm run dev
```

*The backend initializes at **http://localhost:8000** and the frontend opens at **http://localhost:5173**.*

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 📹 **Demo Video** | [Watch Demo Video on Google Drive](https://drive.google.com/file/d/1cLAg9iycwF9eLyQStQmlIF8E8s5egSnu/view?usp=sharing) · *([demo/demo-video-link.txt](demo/demo-video-link.txt))* |
| 🌐 **Live Demo** | Local Deployment: `http://localhost:5173` · *([demo/live-demo-url.txt](demo/live-demo-url.txt): `NO`)* |
| 🖼️ **Screenshots** | [View All App Screenshots](demo/screenshots/) |
| 📊 **Presentation** | [Open Pitch Deck on Google Slides](https://docs.google.com/presentation/d/1qgCz25Mz0dNmMWO3YwvGoF_p7epX_F18/edit?usp=sharing&ouid=100753298897245147197&rtpof=true&sd=true) · *([Download presentation/slides.pdf](presentation/slides.pdf))* |

---

## ⚠️ Known Limitations

1. **Synthetic Telemetry Baseline**: The system is trained on a 30-equipment, 10-weather zone telemetry benchmark calibrated to realistic utility operating parameters; full production deployment requires streaming connection to enterprise SCADA/Historian databases.
2. **Local Deployment**: The frontend and backend run locally on ports 5173 and 8000 rather than public cloud endpoints to maintain security and avoid third-party cloud hosting latency during evaluation.
3. **Geodesic Dispatch Routing**: Dispatch distances are calculated via spherical Haversine distance; integration with real-time road topology routing APIs (e.g. OpenRouteService) is planned for future enterprise scale.

---

## 🏅 What We're Most Proud Of

1. **End-to-End Operational Pipeline in Sub-2-Seconds**: Taking raw telemetry, imputing missing data, running 21-feature Random Forest inference, computing weather risk and grid impact, generating deterministic audit reasons, and pre-positioning crews in under 2 seconds.
2. **Zero-Hallucination Explainability**: In high-voltage utility management, operators cannot trust probabilistic text hallucinations. Our 16-factor deterministic threshold engine ensures every decision is grounded in verifiable engineering telemetry.
3. **Mission-Critical GIS Command Center**: The 7-page React 19 interface features interactive GIS mapping, live Doppler rain radar overlays, dynamic what-if simulation sliders, and instant CSV/JSON report exports, delivering a control-room grade experience.
