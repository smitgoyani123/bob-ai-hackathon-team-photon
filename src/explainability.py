"""
explainability.py
-----------------
Generates deterministic, data-driven risk explanations for each
equipment item.

Approach
--------
For each equipment row, actual feature values are compared against
risk thresholds. Only factors where the actual value breaches the
threshold are included in the explanation.

This produces honest per-asset explanations grounded in data —
no generated text, no hallucinated reasons.

Also exposes:
  - global_feature_importance()  : top features from the trained RF model
  - build_ai_decision_summary()  : full structured dict for the AI card
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any

from sklearn.ensemble import RandomForestClassifier


# ── Threshold definitions ─────────────────────────────────────────────────
# Each tuple: (column, operator, threshold, explanation_text)
# operator: 'gt' = greater than, 'lt' = less than

RISK_THRESHOLDS = [
    ("age",                  "gt", 20,   "Aging equipment (>20 years)"),
    ("temperature",          "gt", 70,   "High operating temperature (>70 deg C)"),
    ("load",                 "gt", 75,   "High load (>75%)"),
    ("health",               "lt", 40,   "Low equipment health (<40)"),
    ("previous_incidents",   "gt", 4,    "High historical incident count (>4)"),
    ("severity_encoded",     "gt", 2,    "High/Critical incident severity"),
    ("days_since_last_failure", "lt", 180, "Recent failure event (<180 days ago)"),
    ("weather_risk",         "gt", 55,   "Severe weather exposure (risk >55)"),
    ("weather_storm",        "gt", 0,    "Active storm conditions"),
    ("weather_flood_risk",   "gt", 0.6,  "High flood risk (>0.6)"),
    ("grid_impact",          "gt", 60,   "High grid impact (>60)"),
    ("customers_served",     "gt", 4000, "High customer dependency (>4000 customers)"),
    ("critical_facility",    "gt", 0,    "Critical facility dependency"),
    ("network_importance",   "gt", 50,   "High network importance (>50)"),
    ("incident_rate",        "gt", 0.3,  "High incident rate per year of service"),
    ("temp_stress",          "gt", 20,   "Significant temperature stress (>20 deg above baseline)"),
]


def _check_threshold(value: Any, operator: str, threshold: Any) -> bool:
    """Return True when the threshold is breached."""
    try:
        v = float(value)
        t = float(threshold)
    except (TypeError, ValueError):
        return False
    if operator == "gt":
        return v > t
    if operator == "lt":
        return v < t
    return False


# ── Public API ────────────────────────────────────────────────────────────

def explain_equipment(row: pd.Series) -> List[str]:
    """
    Return a list of plain-English risk factors for a single equipment row.

    Only factors that are actually breached are returned.
    Returns at least one entry even for very low-risk equipment.
    """
    reasons = []
    for col, op, threshold, text in RISK_THRESHOLDS:
        if col in row.index:
            if _check_threshold(row[col], op, threshold):
                reasons.append(text)

    if not reasons:
        reasons.append("No significant risk factors detected at current thresholds")

    return reasons


def explain_all(results_df: pd.DataFrame) -> pd.Series:
    """
    Apply explain_equipment to every row of results_df.

    Returns a pd.Series of lists (one list per equipment).
    """
    return results_df.apply(explain_equipment, axis=1)


def global_feature_importance(
    model: RandomForestClassifier,
    feature_cols: list,
    top_n: int = 10,
) -> pd.DataFrame:
    """
    Return top-N feature importances from the trained Random Forest.

    Parameters
    ----------
    model       : fitted RandomForestClassifier
    feature_cols: ordered list of feature names (from preprocessing.get_feature_columns())
    top_n       : how many top features to return

    Returns
    -------
    pd.DataFrame with columns [feature, importance, importance_pct]
    sorted descending by importance.
    """
    importances = model.feature_importances_
    df = pd.DataFrame({
        "feature":    feature_cols,
        "importance": importances,
    }).sort_values("importance", ascending=False).head(top_n).reset_index(drop=True)

    df["importance"]     = df["importance"].round(4)
    df["importance_pct"] = (df["importance"] / importances.sum() * 100).round(1)
    return df


def build_ai_decision_summary(row: pd.Series) -> Dict[str, Any]:
    """
    Build the full structured dict that powers the AI Decision Card
    in the dashboard.

    Parameters
    ----------
    row : a single row from results_df (must contain all pipeline columns)

    Returns
    -------
    dict with all fields needed by the dashboard decision card.
    """
    risk_reasons = explain_equipment(row)

    return {
        "equipment_id":        row.get("equipment_id", "N/A"),
        "type":                row.get("type", "N/A"),
        "failure_probability": round(float(row.get("failure_probability", 0)) * 100, 1),
        "weather_risk":        round(float(row.get("weather_risk", 0)), 1),
        "grid_impact":         round(float(row.get("grid_impact", 0)), 1),
        "priority_score":      round(float(row.get("priority_score", 0)), 1),
        "risk_level":          row.get("risk_level", "LOW"),
        "maintenance_action":  row.get("maintenance_action", "Normal Maintenance"),
        "assigned_crew":       row.get("assigned_crew", "N/A"),
        "crew_distance_km":    row.get("crew_distance_km", None),
        "risk_reasons":        risk_reasons,
        "age":                 row.get("age", "N/A"),
        "health":              row.get("health", "N/A"),
        "load":                row.get("load", "N/A"),
        "temperature":         row.get("temperature", "N/A"),
        "customers_served":    row.get("customers_served", "N/A"),
        "critical_facility":   row.get("critical_facility", 0),
        "previous_incidents":  row.get("previous_incidents", 0),
    }


# ── Smoke-test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from data_loader import load_all_data
    from preprocessing import preprocess, get_feature_columns
    from failure_prediction import train, predict
    from weather_risk import calculate_weather_risk
    from grid_impact import calculate_grid_impact
    from priority import calculate_priority

    eq, wt, inc, cr, _ = load_all_data()
    mi = preprocess(eq, wt, inc)

    model, _ = train(mi)
    fp = predict(model, mi)
    wr = calculate_weather_risk(mi)
    gi = calculate_grid_impact(mi)
    ps, rl, ma = calculate_priority(mi, fp, wr, gi)

    results_df = mi.copy()
    results_df["failure_probability"] = fp.values
    results_df["weather_risk"]        = wr.values
    results_df["grid_impact"]         = gi.values
    results_df["priority_score"]      = ps.values
    results_df["risk_level"]          = rl.values
    results_df["maintenance_action"]  = ma.values

    # Show explanation for top-3 priority assets
    top3 = results_df.sort_values("priority_score", ascending=False).head(3)
    for _, row in top3.iterrows():
        print(f"\n--- {row['equipment_id']} ({row['type']}) ---")
        print(f"  Priority     : {row['priority_score']} | {row['risk_level']}")
        print(f"  WHY AT RISK  :")
        for reason in explain_equipment(row):
            print(f"    * {reason}")

    print("\n=== Global Feature Importance (top 10) ===")
    fi = global_feature_importance(model, get_feature_columns())
    print(fi.to_string(index=False))

    print("\n=== AI Decision Summary (T001) ===")
    t001 = results_df[results_df["equipment_id"] == "T001"].iloc[0]
    summary = build_ai_decision_summary(t001)
    for k, v in summary.items():
        print(f"  {k:<22}: {v}")

    print("\n[OK] explainability: complete")
