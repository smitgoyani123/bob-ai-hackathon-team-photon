# Setup Guide

## Prerequisites

- Python 3.9 or higher
- pip
- Git

---

## 1. Clone the Repository

```bash
git clone <repository-url>
cd bob-ai-hackathon-photon
```

---

## 2. Create a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r src/requirements.txt
```

Dependencies installed:
- `pandas` — data loading and processing
- `numpy` — numerical operations
- `scikit-learn` — RandomForestClassifier
- `joblib` — model serialisation
- `streamlit` — dashboard framework
- `plotly` — interactive charts
- `folium` — geographic map
- `streamlit-folium` — Folium integration for Streamlit
- `geopy` — geospatial utilities

---

## 4. Dataset Placement

The synthetic demo datasets are already included:

```
src/data/raw/
    equipment.csv    # 30 equipment assets
    weather.csv      # 10 weather zones
    incidents.csv    # 30 incident records
    crews.csv        # 8 field crews
```

To use real data, replace these files with your own CSVs maintaining the same column schema. See `docs/solution-overview.md` for column requirements.

---

## 5. Run the Pipeline

From the project root:

```bash
python src/main.py
```

This will:
1. Load all 4 raw CSVs
2. Preprocess and feature-engineer the data
3. Train (or load cached) the RandomForest model
4. Calculate weather risk, grid impact, priority scores
5. Assign crews to HIGH/CRITICAL assets
6. Save results to `src/results/predictions.csv`

To force model retraining:

```bash
python src/main.py --retrain
```

---

## 6. Launch the Dashboard

```bash
streamlit run src/dashboard/app.py
```

The dashboard will open at `http://localhost:8501` in your browser.

> **Note:** Run the pipeline at least once before launching the dashboard so that `predictions.csv` exists. Alternatively, use the **Run Pipeline** button in the dashboard sidebar.

---

## 7. Running Individual Modules (Optional)

Each module has a built-in smoke-test. Run from `src/`:

```bash
python src/data_loader.py
python src/preprocessing.py
python src/failure_prediction.py
python src/weather_risk.py
python src/grid_impact.py
python src/priority.py
python src/crew_assignment.py
python src/explainability.py
python src/pipeline.py
```

---

## 8. Environment Variables

No environment variables are required for the demo setup.

If integrating with external services in future, copy `.env.example` to `.env` and populate:

```bash
cp src/.env.example .env
```

`.env` is listed in `.gitignore` and will never be committed.

---

## 9. Troubleshooting

| Error | Resolution |
|---|---|
| `ModuleNotFoundError` | Ensure venv is activated and `pip install -r src/requirements.txt` was run |
| `FileNotFoundError: predictions.csv` | Run `python src/main.py` first |
| `No data rows in CSV` | Check that `src/data/raw/*.csv` files contain data (not just headers) |
| `Streamlit: missing ScriptRunContext` | This warning is safe to ignore when running Python scripts directly |
| Pipeline error on model load | Run `python src/main.py --retrain` to force fresh training |
| Map not rendering | Ensure `streamlit-folium` is installed: `pip install streamlit-folium` |

---

## 10. Project Structure

```
bob-ai-hackathon-photon/
├── .venv/                       # virtual environment (not committed)
├── src/
│   ├── config/settings.py       # centralised path config
│   ├── data/
│   │   ├── raw/                 # input CSVs
│   │   └── processed/           # model_input.csv
│   ├── models/                  # failure_model.pkl
│   ├── results/                 # predictions.csv
│   ├── dashboard/
│   │   ├── app.py               # Streamlit entry point
│   │   ├── pages/               # 7 dashboard pages
│   │   └── styles/theme.css     # dark enterprise CSS
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
├── docs/                        # documentation
├── demo/                        # demo artifacts
├── presentation/                # slide content
├── submission.yaml
├── README.md
└── requirements.txt
```
