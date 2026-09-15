import sys
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

# Ensure src/ directory is in python path
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from explainability import explain_equipment, build_ai_decision_summary
from data_loader import load_all_data

app = FastAPI(title="GridGuard AI API", version="1.0")

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RESULTS_PATH = SRC_DIR / "results" / "predictions.csv"
CREWS_PATH = SRC_DIR / "data" / "raw" / "crews.csv"

def get_predictions_df() -> pd.DataFrame:
    if not RESULTS_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(RESULTS_PATH)

def get_crews_df() -> pd.DataFrame:
    if not CREWS_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(CREWS_PATH)

@app.get("/api/health")
def get_health():
    df = get_predictions_df()
    return {
        "status": "healthy",
        "engine": "GridGuard AI",
        "version": "1.0",
        "total_assets": len(df),
        "results_ready": not df.empty,
    }

@app.get("/api/summary")
def get_summary():
    df = get_predictions_df()
    crews_df = get_crews_df()
    if df.empty:
        return {"error": "Predictions not found"}
    
    total = len(df)
    risk_counts = df['risk_level'].value_counts().to_dict()
    
    # Ensure all risk levels exist
    for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if level not in risk_counts:
            risk_counts[level] = 0
            
    avg_priority = float(df['priority_score'].mean()) if 'priority_score' in df.columns else 0.0
    health_score = round(max(0.0, min(100.0, 100.0 - avg_priority)), 1)
    avg_failure_prob = round(float(df['failure_probability'].mean()) * 100, 1) if 'failure_probability' in df.columns else 0.0
    avg_weather_risk = round(float(df['weather_risk'].mean()), 1) if 'weather_risk' in df.columns else 0.0
    avg_grid_impact = round(float(df['grid_impact'].mean()), 1) if 'grid_impact' in df.columns else 0.0
    
    critical_facilities = int((df['critical_facility'] == 1).sum()) if 'critical_facility' in df.columns else 0
    
    available_crews = 0
    total_crews = 0
    if not crews_df.empty and 'status' in crews_df.columns:
        total_crews = len(crews_df)
        available_crews = int((crews_df['status'].astype(str).str.strip().str.lower() == 'available').sum())
        
    # Active alerts = High + Critical assets
    active_alerts = risk_counts.get("CRITICAL", 0) + risk_counts.get("HIGH", 0)
    
    return {
        "total_equipment": total,
        "risk_counts": risk_counts,
        "system_health_score": health_score,
        "avg_failure_probability": avg_failure_prob,
        "avg_weather_risk": avg_weather_risk,
        "avg_grid_impact": avg_grid_impact,
        "critical_facilities": critical_facilities,
        "total_crews": total_crews,
        "available_crews": available_crews,
        "active_alerts": active_alerts
    }

@app.get("/api/predictions")
def get_predictions():
    df = get_predictions_df()
    if df.empty:
        return []
    
    # Enrich with deterministic explainability risk reasons
    reasons_list = []
    for _, row in df.iterrows():
        try:
            reasons = explain_equipment(row)
        except Exception:
            reasons = ["Operational monitoring active"]
        reasons_list.append(reasons)
    
    df["risk_reasons"] = reasons_list
    
    records = df.to_dict(orient="records")
    for row in records:
        for k, v in row.items():
            if isinstance(v, (list, dict, tuple)):
                continue
            if pd.isna(v):
                row[k] = None
    return records

@app.get("/api/equipment/{equipment_id}")
def get_equipment_detail(equipment_id: str):
    df = get_predictions_df()
    if df.empty:
        raise HTTPException(status_code=404, detail="Predictions not found")
    
    match = df[df["equipment_id"] == equipment_id]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Equipment {equipment_id} not found")
    
    row = match.iloc[0]
    decision_summary = build_ai_decision_summary(row)
    for k, v in decision_summary.items():
        if isinstance(v, (list, dict, tuple)):
            continue
        if pd.isna(v):
            decision_summary[k] = None
    return decision_summary

@app.get("/api/crews")
def get_crews():
    crews_df = get_crews_df()
    df = get_predictions_df()
    if crews_df.empty:
        return []
    
    # Map currently assigned equipment
    assigned_map = {}
    if not df.empty and 'assigned_crew' in df.columns:
        valid_assigned = df[~df['assigned_crew'].astype(str).str.contains("N/A|No suitable", case=False, na=False)]
        for _, row in valid_assigned.iterrows():
            cid = str(row['assigned_crew'])
            if cid not in assigned_map:
                assigned_map[cid] = []
            assigned_map[cid].append({
                "equipment_id": row.get("equipment_id"),
                "type": row.get("type"),
                "risk_level": row.get("risk_level"),
                "priority_score": float(row.get("priority_score")) if pd.notna(row.get("priority_score")) else None,
                "distance_km": float(row.get("crew_distance_km")) if pd.notna(row.get("crew_distance_km")) else None,
                "action": row.get("maintenance_action")
            })
            
    records = crews_df.to_dict(orient="records")
    for r in records:
        for k, v in r.items():
            if isinstance(v, (list, dict, tuple)):
                continue
            if pd.isna(v):
                r[k] = None
        cid = str(r.get("crew_id"))
        r["assignments"] = assigned_map.get(cid, [])
        r["assigned_count"] = len(r["assignments"])
        
    return records

@app.get("/api/feature-importance")
def get_feature_importance_api():
    try:
        from preprocessing import preprocess, get_feature_columns
        from failure_prediction import train
        from explainability import global_feature_importance
        
        equipment, weather, incidents, crews, _ = load_all_data()
        model_input = preprocess(equipment, weather, incidents)
        model, _ = train(model_input, force_retrain=False)
        fi = global_feature_importance(model, get_feature_columns(), top_n=12)
        return fi.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

class SimulationRequest(BaseModel):
    equipment_id: Optional[str] = "T001"
    weather_wind: float
    weather_rainfall: float
    weather_temperature: float
    weather_storm: float
    weather_flood_risk: float
    load: float

@app.post("/api/simulate")
def simulate_scenario(req: SimulationRequest):
    df = get_predictions_df()
    if df.empty:
        raise HTTPException(status_code=404, detail="Predictions dataset not found")
        
    match = df[df["equipment_id"] == req.equipment_id]
    target_row = match.iloc[0] if not match.empty else df.iloc[0]
    
    # Extract baseline bounds
    EPS = 1e-9
    rain_min = float(df['weather_rainfall'].min()) if 'weather_rainfall' in df else 0.0
    rain_max = float(df['weather_rainfall'].max()) if 'weather_rainfall' in df else 120.0
    wind_min = float(df['weather_wind'].min()) if 'weather_wind' in df else 0.0
    wind_max = float(df['weather_wind'].max()) if 'weather_wind' in df else 90.0
    
    def norm(v, lo, hi):
        return ((v - lo) / (hi - lo + EPS)) * 100 if hi > lo else 50.0

    sim_rain_r = norm(req.weather_rainfall, rain_min, rain_max)
    sim_wind_r = norm(req.weather_wind, wind_min, wind_max)
    sim_temp_r = max(0, (req.weather_temperature - 35) / max(1, 45 - 35)) * 100
    sim_storm_r = float(req.weather_storm) * 60 + float(req.weather_flood_risk) * 40
    
    sim_wr = min(100.0, max(0.0, 0.40 * sim_rain_r + 0.30 * sim_wind_r + 0.20 * sim_temp_r + 0.10 * sim_storm_r))
    
    base_fp = float(target_row['failure_probability'])
    base_gi = float(target_row['grid_impact'])
    base_load = max(1.0, float(target_row.get('load', 50)))
    
    load_ratio = req.load / base_load
    sim_gi = min(100.0, max(0.0, base_gi * load_ratio))
    
    # Calculate simulated priority score
    sim_ps = min(100.0, max(0.0, 0.50 * (base_fp * 100) + 0.20 * sim_wr + 0.30 * sim_gi))
    
    # Classify risk level
    if sim_ps >= 80:
        sim_risk = "CRITICAL"
        sim_action = "Immediate Inspection"
    elif sim_ps >= 60:
        sim_risk = "HIGH"
        sim_action = "Preventive Maintenance"
    elif sim_ps >= 30:
        sim_risk = "MEDIUM"
        sim_action = "Monitor"
    else:
        sim_risk = "LOW"
        sim_action = "Normal Maintenance"
        
    return {
        "equipment_id": target_row["equipment_id"],
        "baseline": {
            "failure_probability": round(base_fp * 100, 1),
            "weather_risk": round(float(target_row.get("weather_risk", 0)), 1),
            "grid_impact": round(base_gi, 1),
            "priority_score": round(float(target_row.get("priority_score", 0)), 1),
            "risk_level": target_row.get("risk_level", "LOW"),
            "maintenance_action": target_row.get("maintenance_action", "Normal Maintenance"),
        },
        "simulated": {
            "weather_risk": round(sim_wr, 1),
            "grid_impact": round(sim_gi, 1),
            "priority_score": round(sim_ps, 1),
            "risk_level": sim_risk,
            "maintenance_action": sim_action,
            "weather_delta": round(sim_wr - float(target_row.get("weather_risk", 0)), 1),
            "priority_delta": round(sim_ps - float(target_row.get("priority_score", 0)), 1),
        }
    }

class PipelineRunRequest(BaseModel):
    force_retrain: bool = False

@app.post("/api/pipeline/run")
def trigger_pipeline(req: PipelineRunRequest = PipelineRunRequest()):
    try:
        from pipeline import run_pipeline
        df = run_pipeline(force_retrain=req.force_retrain)
        return {
            "status": "success",
            "message": "Pipeline completed successfully",
            "rows_processed": len(df),
            "risk_summary": df['risk_level'].value_counts().to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

RAW_EQUIPMENT_PATH = SRC_DIR / "data" / "raw" / "equipment.csv"

@app.post("/api/upload/equipment")
async def upload_equipment_csv(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported.")
    
    try:
        content = await file.read()
        import io
        test_df = pd.read_csv(io.BytesIO(content))
        if test_df.empty:
            raise HTTPException(status_code=400, detail="Uploaded CSV file is empty.")
        
        # Save to raw equipment dataset
        with open(RAW_EQUIPMENT_PATH, "wb") as f:
            f.write(content)
            
        # Re-run full end-to-end pipeline
        from pipeline import run_pipeline
        df = run_pipeline(force_retrain=False)
        
        return {
            "status": "success",
            "message": f"Successfully ingested {len(df)} equipment assets! Grid predictions and crew routes updated.",
            "rows_processed": len(df),
            "risk_summary": df['risk_level'].value_counts().to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded CSV: {str(e)}")

@app.get("/api/template/equipment")
def get_equipment_template():
    if RAW_EQUIPMENT_PATH.exists():
        df = pd.read_csv(RAW_EQUIPMENT_PATH)
        records = df.to_dict(orient="records")
        for r in records:
            for k, v in r.items():
                if pd.isna(v):
                    r[k] = None
        return records
    return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
