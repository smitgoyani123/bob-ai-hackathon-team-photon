# 🛠️ GridGuard AI — Setup & Execution Guide

This guide provides step-by-step instructions to install dependencies, run the backend ML pipeline & REST API, and launch the React 19 GIS Command Center.

---

## Prerequisites

- **Python 3.9+** (tested on Python 3.9 – 3.13)
- **Node.js 18+** & **npm**
- **Git**

---

## 1. Clone the Repository

```bash
git clone https://github.com/smitgoyani123/bob-ai-hackathon-team-photon.git
cd bob-ai-hackathon-team-photon
```

---

## 2. Python Virtual Environment Setup

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Python Dependencies

```bash
pip install -r src/requirements.txt
```

Installed packages:
- `fastapi`, `uvicorn`, `pydantic` — High-performance REST service
- `scikit-learn`, `joblib` — Random Forest classifier & model serialization
- `pandas`, `numpy` — Data handling, missing-value imputation & feature engineering
- `geopy` — Spatial Haversine distance computations

---

## 4. Environment Configuration

Copy the example environment template:

```bash
cp .env.example .env
```

*(No external API keys are strictly required for offline local demonstration).*

---

## 5. Launch Application Services

GridGuard AI consists of two coordinated services:

### Terminal 1: Start FastAPI REST Service & ML Pipeline

From the project root directory:

```bash
python src/api.py
```
- API initializes at: `http://localhost:8000`
- Interactive OpenAPI / Swagger UI: `http://localhost:8000/docs`

### Terminal 2: Start React 19 Frontend Command Center

In a new terminal window:

```bash
cd frontend
npm install
npm run dev
```
- Open your browser at: `http://localhost:5173`

---

## 6. Running the Standalone ML Pipeline (CLI)

If you wish to execute the ML training and scoring pipeline directly via command line:

```bash
python src/pipeline.py
```

Or with forced model retraining:
```bash
python src/failure_prediction.py
```
Outputs are written to:
- `src/models/failure_model.pkl`
- `src/results/predictions.csv`
- `src/data/processed/model_input.csv`

---

## 7. Troubleshooting

| Issue | Resolution |
|---|---|
| `Port 8000 already in use` | Check if an existing uvicorn instance is running with `netstat -ano \| findstr :8000` and terminate the process. |
| `Frontend fails to load grid data` | Verify that the backend is active by opening `http://localhost:8000/api/health` in your browser. |
| `Node modules error` | Run `cd frontend && npm clean-install` or `npm install`. |
