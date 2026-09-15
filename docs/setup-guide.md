# Setup Guide

> **This file is read by the automated evaluation pipeline. Be precise and complete.**

## Prerequisites

Before you begin, ensure you have the following installed:

- [x] Python 3.9+ (tested on 3.9 – 3.13)
- [x] Node.js 18+ and npm
- [x] Git
- [x] Modern web browser (Chrome, Edge, Firefox, or Safari)

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable | Description | Required | Default |
|---|---|---|---|
| `APP_ENV` | Application runtime environment (`development` / `production`) | No | `development` |
| `API_PORT` | Port for the FastAPI backend service | No | `8000` |
| `FRONTEND_PORT` | Port for the React 19 Vite dev server | No | `5173` |

*(Note: No external API keys or cloud credentials are required; GridGuard AI runs completely self-contained and offline for evaluation).*

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/smitgoyani123/bob-ai-hackathon-team-photon.git
cd bob-ai-hackathon-team-photon

# 2. Set up Python virtual environment
python -m venv .venv

# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# 3. Install backend dependencies
pip install -r src/requirements.txt

# 4. Install frontend dependencies
cd frontend
npm install
cd ..
```

## Running the Application

GridGuard AI operates with a FastAPI backend service and a React 19 frontend:

```bash
# Terminal 1 — Start the backend FastAPI server (from project root):
python src/api.py
```
*The backend API will initialize at: `http://localhost:8000` (Interactive API docs at `http://localhost:8000/docs`).*

```bash
# Terminal 2 — Start the React 19 frontend (in a separate terminal):
cd frontend
npm run dev
```
*The application command center will be available at: `http://localhost:5173`.*

## Running Tests

Run the pre-flight acceptance and diagnostic suites:

```bash
# Run the diagnostic test suite
python ui_diagnostic.py

# Run the end-to-end ML pipeline directly (CLI mode)
python src/pipeline.py
```

## Quick Demo (Optional)

To verify the platform end-to-end immediately:

```bash
# 1. Start the backend: python src/api.py
# 2. Start the frontend: cd frontend && npm run dev
# 3. Open http://localhost:5173 in your browser
# 4. Click "Run AI Pipeline" in the top-right navbar to trigger a live re-computation
# 5. Navigate to "Live Grid Map" to see real-world Leaflet GIS, weather radar, and crew pre-positioning lines
```

## Troubleshooting

| Issue | Solution |
|---|---|
| `Port 8000 already in use` | Another process is occupying port 8000. Run `netstat -ano \| findstr :8000` and terminate the PID, or restart your terminal. |
| `Frontend displays 'Backend Offline'` | Ensure Terminal 1 is actively running `python src/api.py`. Verify `http://localhost:8000/api/health` returns `{"status":"healthy"}`. |
| `ModuleNotFoundError: No module named 'fastapi'` | Activate your virtual environment (`.\.venv\Scripts\Activate.ps1` or `source .venv/bin/activate`) and run `pip install -r src/requirements.txt`. |
| `Leaflet map tiles not displaying` | Ensure active internet access for downloading OpenStreetMap / Esri satellite tiles. |
