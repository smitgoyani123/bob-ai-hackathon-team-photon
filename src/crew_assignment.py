"""
crew_assignment.py
------------------
Assigns the nearest suitable available crew to HIGH and CRITICAL
equipment using Haversine distance.

Assignment logic
----------------
1. Only assign to equipment with risk_level in {HIGH, CRITICAL}.
2. Filter crews by:
   a. status == 'available'
   b. skill is compatible with equipment type
   c. capacity > 0
3. Compute Haversine distance from equipment (lat, lon) to each
   candidate crew (lat, lon).
4. Select the crew with the minimum distance.
5. Return crew_id and distance_km.
6. If no suitable crew exists: return ("No suitable crew available", None)

Skill → Equipment type mapping
-------------------------------
  electrical  → Transformer, Switch
  mechanical  → Switch, Line
  civil       → Line

The mapping is broad enough to allow cross-coverage and can be
extended in SKILL_MAP below.
"""

import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
from typing import Tuple, Optional

# ── Skill compatibility ───────────────────────────────────────────────────

SKILL_MAP = {
    "electrical": {"transformer", "switch"},
    "mechanical": {"switch", "line"},
    "civil":      {"line", "transformer"},
}

# Risk levels that trigger crew assignment
ASSIGNMENT_RISK_LEVELS = {"HIGH", "CRITICAL"}


# ── Haversine distance ────────────────────────────────────────────────────

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in km between two lat/lon points."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * R * asin(sqrt(max(0.0, min(1.0, a))))


# ── Single-equipment assignment ───────────────────────────────────────────

def assign_crew_to_equipment(
    eq_lat: float,
    eq_lon: float,
    eq_type: str,
    crews: pd.DataFrame,
) -> Tuple[str, Optional[float]]:
    """
    Find the nearest available, skill-compatible crew for one equipment item.

    Parameters
    ----------
    eq_lat  : equipment latitude
    eq_lon  : equipment longitude
    eq_type : equipment type string (e.g. 'Transformer', 'Switch', 'Line')
    crews   : raw crews DataFrame

    Returns
    -------
    (crew_id, distance_km)
    or ("No suitable crew available", None) if no match found.
    """
    # Normalise equipment type for comparison
    eq_type_norm = eq_type.strip().lower()

    # ── Filter: available crews only ────────────────────────────────────
    available = crews[
        crews["status"].astype(str).str.strip().str.lower() == "available"
    ].copy()

    if available.empty:
        return ("No suitable crew available", None)

    # ── Filter: skill compatibility ─────────────────────────────────────
    def _is_compatible(skill: str) -> bool:
        skill_norm = str(skill).strip().lower()
        compatible_types = SKILL_MAP.get(skill_norm, set())
        return eq_type_norm in compatible_types

    available = available[available["skill"].apply(_is_compatible)]

    if available.empty:
        return ("No suitable crew available", None)

    # ── Filter: positive capacity ────────────────────────────────────────
    available = available[
        pd.to_numeric(available["capacity"], errors="coerce").fillna(0) > 0
    ]

    if available.empty:
        return ("No suitable crew available", None)

    # ── Validate coordinates ─────────────────────────────────────────────
    available = available.copy()
    available["latitude"]  = pd.to_numeric(available["latitude"],  errors="coerce")
    available["longitude"] = pd.to_numeric(available["longitude"], errors="coerce")
    available = available.dropna(subset=["latitude", "longitude"])

    if available.empty:
        return ("No suitable crew available", None)

    # ── Compute distances and pick nearest ───────────────────────────────
    available["distance_km"] = available.apply(
        lambda row: _haversine_km(eq_lat, eq_lon, row["latitude"], row["longitude"]),
        axis=1,
    )

    nearest = available.loc[available["distance_km"].idxmin()]
    return (str(nearest["crew_id"]), round(float(nearest["distance_km"]), 2))


# ── Batch assignment ──────────────────────────────────────────────────────

def assign_crews(
    results_df: pd.DataFrame,
    crews: pd.DataFrame,
) -> pd.DataFrame:
    """
    Assign crews to all HIGH and CRITICAL equipment in results_df.

    Parameters
    ----------
    results_df : DataFrame containing at minimum:
                 equipment_id, type, latitude, longitude, risk_level
    crews      : raw crews DataFrame

    Returns
    -------
    results_df with two new columns: assigned_crew, crew_distance_km
    """
    df = results_df.copy()

    assigned_crews    = []
    crew_distances    = []

    for _, row in df.iterrows():
        risk = str(row.get("risk_level", "LOW")).strip().upper()

        if risk not in ASSIGNMENT_RISK_LEVELS:
            assigned_crews.append("N/A - below threshold")
            crew_distances.append(None)
            continue

        # Guard against missing/invalid coordinates
        try:
            eq_lat = float(row["latitude"])
            eq_lon = float(row["longitude"])
        except (TypeError, ValueError):
            assigned_crews.append("No suitable crew available")
            crew_distances.append(None)
            continue

        crew_id, dist_km = assign_crew_to_equipment(
            eq_lat, eq_lon, str(row.get("type", "")), crews
        )
        assigned_crews.append(crew_id)
        crew_distances.append(dist_km)

    df["assigned_crew"]    = assigned_crews
    df["crew_distance_km"] = crew_distances

    return df


# ── Smoke-test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from data_loader import load_all_data
    from preprocessing import preprocess
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

    results_df = assign_crews(results_df, cr)

    assigned = results_df[results_df["risk_level"].isin(ASSIGNMENT_RISK_LEVELS)]
    print("=== Crew Assignments (HIGH / CRITICAL equipment) ===")
    cols = ["equipment_id", "type", "risk_level", "priority_score",
            "assigned_crew", "crew_distance_km"]
    print(assigned[cols].sort_values("priority_score", ascending=False).to_string(index=False))

    print(f"\nTotal assigned : {(assigned['assigned_crew'] != 'No suitable crew available').sum()}")
    print(f"No crew found  : {(assigned['assigned_crew'] == 'No suitable crew available').sum()}")
    print("[OK] crew_assignment: complete")
