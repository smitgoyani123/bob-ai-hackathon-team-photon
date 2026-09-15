"""
pipeline.py
-----------
Orchestrates the full GridGuard AI pipeline end-to-end:

  DATA LOAD  →  PREPROCESS  →  ML PREDICTION  →  WEATHER RISK
  →  GRID IMPACT  →  PRIORITY  →  CREW ASSIGNMENT  →  RESULTS CSV

Output
------
  results/predictions.csv

  Columns:
    equipment_id, type, age, health, load, temperature,
    voltage, customers_served, critical_facility,
    latitude, longitude,
    failure_probability, weather_risk, grid_impact,
    priority_score, risk_level, maintenance_action,
    assigned_crew, crew_distance_km

Usage
-----
  From Python  : from pipeline import run_pipeline; results = run_pipeline()
  From CLI     : python pipeline.py
  Via main.py  : python main.py   (from project root)
"""

import sys
import time
import traceback
from pathlib import Path

import pandas as pd

# Ensure src/ is on the path when run directly
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.settings import RESULTS_DIR
from data_loader import load_all_data
from preprocessing import preprocess
from failure_prediction import train, predict, get_feature_importance
from weather_risk import calculate_weather_risk
from grid_impact import calculate_grid_impact
from priority import calculate_priority
from crew_assignment import assign_crews
from explainability import global_feature_importance
from preprocessing import get_feature_columns

RESULTS_PATH = Path(RESULTS_DIR) / "predictions.csv"

# Final output columns — guaranteed in this order
OUTPUT_COLUMNS = [
    "equipment_id", "type", "age", "health", "load", "temperature",
    "voltage", "customers_served", "critical_facility",
    "latitude", "longitude",
    "weather_rainfall", "weather_wind", "weather_temperature",
    "weather_storm", "weather_flood_risk",
    "failure_probability", "weather_risk", "grid_impact",
    "priority_score", "risk_level", "maintenance_action",
    "assigned_crew", "crew_distance_km",
]


def _log(msg: str) -> None:
    print(f"  [pipeline] {msg}")


def run_pipeline(force_retrain: bool = False) -> pd.DataFrame:
    """
    Execute the complete GridGuard AI pipeline.

    Parameters
    ----------
    force_retrain : if True, ignores any cached model and retrains from scratch.

    Returns
    -------
    results : pd.DataFrame — full predictions with all output columns.
              Also saved to results/predictions.csv.

    Raises
    ------
    Any unhandled exception is caught, printed with a traceback, and
    re-raised so the caller (or dashboard) can show a user-facing message.
    """
    t0 = time.time()
    print("\n" + "=" * 60)
    print("  GRIDGUARD AI — PIPELINE START")
    print("=" * 60)

    try:
        # ── Step 1: Load data ─────────────────────────────────────────
        _log("Step 1/7 — Loading raw data...")
        equipment, weather, incidents, crews, load_summary = load_all_data()
        _log(f"  equipment={len(equipment)} rows  weather={len(weather)} rows  "
             f"incidents={len(incidents)} rows  crews={len(crews)} rows")

        # ── Step 2: Preprocess ────────────────────────────────────────
        _log("Step 2/7 — Preprocessing & feature engineering...")
        model_input = preprocess(equipment, weather, incidents)
        _log(f"  model_input shape: {model_input.shape}  missing: {model_input.isnull().sum().sum()}")

        # ── Step 3: ML prediction ─────────────────────────────────────
        _log("Step 3/7 — Training / loading failure prediction model...")
        model, metrics = train(model_input, force_retrain=force_retrain)
        failure_probability = predict(model, model_input)
        _log(f"  accuracy={metrics['accuracy']}  f1={metrics['f1']}  "
             f"roc_auc={metrics.get('roc_auc', 'N/A')}")

        # ── Step 4: Weather risk ──────────────────────────────────────
        _log("Step 4/7 — Calculating weather risk...")
        weather_risk = calculate_weather_risk(model_input)
        _log(f"  weather_risk range: {weather_risk.min():.1f} – {weather_risk.max():.1f}")

        # ── Step 5: Grid impact ───────────────────────────────────────
        _log("Step 5/7 — Calculating grid impact...")
        grid_impact = calculate_grid_impact(model_input)
        _log(f"  grid_impact range: {grid_impact.min():.1f} – {grid_impact.max():.1f}")

        # ── Step 6: Priority, risk level, maintenance ─────────────────
        _log("Step 6/7 — Computing priority scores & risk levels...")
        priority_score, risk_level, maintenance_action = calculate_priority(
            model_input, failure_probability, weather_risk, grid_impact
        )
        dist = risk_level.value_counts().to_dict()
        _log(f"  risk distribution: {dist}")

        # ── Step 7: Crew assignment ───────────────────────────────────
        _log("Step 7/7 — Assigning crews...")
        results = model_input.copy()
        results["failure_probability"] = failure_probability.values
        results["weather_risk"]        = weather_risk.values
        results["grid_impact"]         = grid_impact.values
        results["priority_score"]      = priority_score.values
        results["risk_level"]          = risk_level.values
        results["maintenance_action"]  = maintenance_action.values

        results = assign_crews(results, crews)
        assigned_count = (
            results["assigned_crew"]
            .isin(["No suitable crew available", "N/A - below threshold"])
            .__invert__()
            .sum()
        )
        _log(f"  crews assigned: {assigned_count} / {len(results[results['risk_level'].isin(['HIGH','CRITICAL'])])} high-risk assets")

        # ── Finalise output ───────────────────────────────────────────
        # Ensure all output columns are present; fill any unexpected gaps
        for col in OUTPUT_COLUMNS:
            if col not in results.columns:
                results[col] = None

        output = results[OUTPUT_COLUMNS].copy()

        # Round floats for readability
        float_cols = ["failure_probability", "weather_risk", "grid_impact", "priority_score"]
        for col in float_cols:
            output[col] = output[col].round(4)

        # Save
        RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        output.to_csv(RESULTS_PATH, index=False)

        elapsed = time.time() - t0
        print("=" * 60)
        print(f"  PIPELINE COMPLETE  ({elapsed:.1f}s)")
        print(f"  Results saved -> {RESULTS_PATH}")
        print(f"  Total equipment: {len(output)}")
        print(f"  Risk summary   : {dist}")
        print("=" * 60 + "\n")

        return output

    except Exception as exc:
        print("\n[pipeline] ERROR — pipeline failed:")
        traceback.print_exc()
        raise


def load_results() -> pd.DataFrame:
    """
    Load the most-recently generated predictions.csv.

    Returns
    -------
    pd.DataFrame or raises FileNotFoundError if pipeline has not been run.
    """
    if not RESULTS_PATH.exists():
        raise FileNotFoundError(
            f"Results file not found at {RESULTS_PATH}.\n"
            "Run 'python main.py' to generate predictions first."
        )
    return pd.read_csv(RESULTS_PATH)


def get_pipeline_metadata(model) -> dict:
    """Return model + feature importance metadata for the AI Insights page."""
    fi = global_feature_importance(model, get_feature_columns(), top_n=10)
    return {
        "model_type":     "RandomForestClassifier",
        "n_estimators":   model.n_estimators,
        "feature_columns": get_feature_columns(),
        "feature_importance": fi,
    }


# ── CLI entry point ───────────────────────────────────────────────────────

if __name__ == "__main__":
    results = run_pipeline(force_retrain="--retrain" in sys.argv)

    print("=== Sample Output (top 5 by priority) ===")
    top5 = results.sort_values("priority_score", ascending=False).head(5)
    display_cols = [
        "equipment_id", "type", "failure_probability",
        "weather_risk", "grid_impact", "priority_score",
        "risk_level", "maintenance_action",
        "assigned_crew", "crew_distance_km",
    ]
    print(top5[display_cols].to_string(index=False))
