"""
preprocessing.py
----------------
Cleans, merges and feature-engineers the four raw DataFrames into a
single model-ready DataFrame that is also saved as
  data/processed/model_input.csv

Pipeline
--------
1. Clean equipment
   - drop full duplicates
   - coerce numerics; fill missing with column median
   - encode critical_facility  Yes → 1, No → 0
   - clip age / health / load / temperature to sane ranges

2. Clean incidents
   - coerce numeric columns
   - fill missing previous_incidents with 0
   - encode severity  Low/Medium/High/Critical → 1/2/3/4
   - coerce failure_next_7_days to binary int

3. Join equipment ← incidents on equipment_id (left join)
   - equipment with no incident row gets 0 incidents, severity=1, target=0

4. Assign weather to equipment
   - find nearest weather zone by Haversine distance
   - attach rainfall / wind / weather_temperature / storm / flood_risk

5. Feature engineering
   - age_risk_flag        : age > 20 → 1
   - health_risk_flag     : health < 40 → 1
   - load_risk_flag       : load > 80 → 1
   - temp_stress          : equipment temperature deviation from 60 °C baseline
   - incident_rate        : previous_incidents / (age + 1)
   - network_importance   : derived from voltage + customers_served + critical_facility

6. Save  data/processed/model_input.csv
"""

import numpy as np
import pandas as pd
from pathlib import Path
from math import radians, cos, sin, asin, sqrt
from typing import Tuple

from config.settings import PROCESSED_DATA_DIR


# ── Haversine helper ──────────────────────────────────────────────────────

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in km between two (lat, lon) points."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * R * asin(sqrt(max(0.0, min(1.0, a))))


# ── Severity encoding ─────────────────────────────────────────────────────

SEVERITY_MAP = {
    "low": 1, "medium": 2, "high": 3, "critical": 4,
    "Low": 1, "Medium": 2, "High": 3, "Critical": 4,
}


# ── Step 1 – Clean equipment ──────────────────────────────────────────────

def _clean_equipment(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.drop_duplicates(inplace=True)

    # Coerce all numeric columns
    numeric_cols = ["age", "temperature", "load", "health",
                    "voltage", "customers_served", "latitude", "longitude"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Clip to physically sensible ranges before computing medians
    df["age"]             = df["age"].clip(lower=0, upper=100)
    df["temperature"]     = df["temperature"].clip(lower=-20, upper=200)
    df["load"]            = df["load"].clip(lower=0, upper=100)
    df["health"]          = df["health"].clip(lower=0, upper=100)
    df["voltage"]         = df["voltage"].clip(lower=0)
    df["customers_served"]= df["customers_served"].clip(lower=0)

    # Fill missing values with column medians
    for col in numeric_cols:
        median_val = df[col].median()
        if pd.isna(median_val):
            median_val = 0.0
        df[col] = df[col].fillna(median_val)

    # Encode critical_facility
    df["critical_facility"] = (
        df["critical_facility"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({"yes": 1, "no": 0, "1": 1, "0": 0, "true": 1, "false": 0})
        .fillna(0)
        .astype(int)
    )

    # Normalise type text
    df["type"] = df["type"].astype(str).str.strip().str.title()

    return df


# ── Step 2 – Clean incidents ──────────────────────────────────────────────

def _clean_incidents(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.drop_duplicates(subset=["equipment_id"], keep="first", inplace=True)

    df["previous_incidents"] = pd.to_numeric(
        df["previous_incidents"], errors="coerce"
    ).fillna(0).clip(lower=0).astype(int)

    df["severity_encoded"] = (
        df["severity"]
        .astype(str).str.strip().str.lower()
        .map({"low": 1, "medium": 2, "high": 3, "critical": 4})
        .fillna(1)
        .astype(int)
    )

    df["failure_next_7_days"] = (
        pd.to_numeric(df["failure_next_7_days"], errors="coerce")
        .fillna(0)
        .clip(lower=0, upper=1)
        .astype(int)
    )

    # Parse last_failure_date – keep as string; derive days_since_last_failure
    df["last_failure_date"] = pd.to_datetime(
        df["last_failure_date"], errors="coerce"
    )
    reference_date = pd.Timestamp("2025-01-01")
    df["days_since_last_failure"] = (
        (reference_date - df["last_failure_date"])
        .dt.days
        .fillna(365)
        .clip(lower=0)
        .astype(int)
    )

    return df[
        ["equipment_id", "previous_incidents", "severity_encoded",
         "days_since_last_failure", "failure_next_7_days"]
    ]


# ── Step 3 – Join equipment + incidents ──────────────────────────────────

def _merge_equipment_incidents(
    equipment: pd.DataFrame, incidents: pd.DataFrame
) -> pd.DataFrame:
    merged = equipment.merge(incidents, on="equipment_id", how="left")

    # Equipment with no incident record → safe defaults
    merged["previous_incidents"]   = merged["previous_incidents"].fillna(0).astype(int)
    merged["severity_encoded"]     = merged["severity_encoded"].fillna(1).astype(int)
    merged["days_since_last_failure"] = merged["days_since_last_failure"].fillna(365).astype(int)
    merged["failure_next_7_days"]  = merged["failure_next_7_days"].fillna(0).astype(int)

    return merged


# ── Step 4 – Assign nearest weather zone ─────────────────────────────────

def _assign_weather(merged: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    weather = weather.copy()

    # Coerce weather numerics
    for col in ["rainfall", "wind", "temperature", "storm", "flood_risk",
                "latitude", "longitude"]:
        weather[col] = pd.to_numeric(weather[col], errors="coerce").fillna(0)

    def _nearest_weather(eq_lat: float, eq_lon: float) -> pd.Series:
        distances = weather.apply(
            lambda row: _haversine_km(eq_lat, eq_lon, row["latitude"], row["longitude"]),
            axis=1,
        )
        nearest = weather.loc[distances.idxmin()]
        return pd.Series({
            "weather_rainfall":    nearest["rainfall"],
            "weather_wind":        nearest["wind"],
            "weather_temperature": nearest["temperature"],
            "weather_storm":       nearest["storm"],
            "weather_flood_risk":  nearest["flood_risk"],
        })

    weather_features = merged.apply(
        lambda row: _nearest_weather(row["latitude"], row["longitude"]),
        axis=1,
    )
    return pd.concat([merged, weather_features], axis=1)


# ── Step 5 – Feature engineering ─────────────────────────────────────────

def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Binary risk flags
    df["age_risk_flag"]    = (df["age"] > 20).astype(int)
    df["health_risk_flag"] = (df["health"] < 40).astype(int)
    df["load_risk_flag"]   = (df["load"] > 80).astype(int)

    # Temperature stress — deviation above 60 °C baseline (equipment rated)
    df["temp_stress"] = (df["temperature"] - 60.0).clip(lower=0)

    # Incident rate per year of service
    df["incident_rate"] = (df["previous_incidents"] / (df["age"] + 1)).round(4)

    # Network importance derived from voltage, customers, and criticality
    # Logic (transparent): higher voltage + more customers + critical facility → more important
    v_max = df["voltage"].max() if df["voltage"].max() > 0 else 1.0
    c_max = df["customers_served"].max() if df["customers_served"].max() > 0 else 1.0

    df["network_importance"] = (
        0.4 * (df["voltage"] / v_max) * 100
        + 0.4 * (df["customers_served"] / c_max) * 100
        + 0.2 * df["critical_facility"] * 100
    ).round(2)

    return df


# ── Public API ────────────────────────────────────────────────────────────

def preprocess(
    equipment: pd.DataFrame,
    weather: pd.DataFrame,
    incidents: pd.DataFrame,
) -> pd.DataFrame:
    """
    Run the full preprocessing pipeline.

    Parameters
    ----------
    equipment  : raw equipment DataFrame
    weather    : raw weather DataFrame
    incidents  : raw incidents DataFrame

    Returns
    -------
    model_input : pd.DataFrame  — cleaned, merged, feature-engineered
    """
    eq_clean  = _clean_equipment(equipment)
    inc_clean = _clean_incidents(incidents)
    merged    = _merge_equipment_incidents(eq_clean, inc_clean)
    with_wx   = _assign_weather(merged, weather)
    final     = _engineer_features(with_wx)

    # Persist
    out_path = Path(PROCESSED_DATA_DIR) / "model_input.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.to_csv(out_path, index=False)

    return final


def get_feature_columns() -> list:
    """Return the ordered list of ML feature columns used for training/inference."""
    return [
        "age", "temperature", "load", "health", "voltage",
        "customers_served", "critical_facility",
        "previous_incidents", "severity_encoded", "days_since_last_failure",
        "weather_rainfall", "weather_wind", "weather_temperature",
        "weather_storm", "weather_flood_risk",
        "age_risk_flag", "health_risk_flag", "load_risk_flag",
        "temp_stress", "incident_rate", "network_importance",
    ]


# ── Smoke-test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from data_loader import load_all_data

    equipment, weather, incidents, crews, _ = load_all_data()
    model_input = preprocess(equipment, weather, incidents)

    print("=== Preprocessing Summary ===")
    print(f"Output shape : {model_input.shape}")
    print(f"Feature cols : {get_feature_columns()}")
    print(f"Target dist  : {model_input['failure_next_7_days'].value_counts().to_dict()}")
    print(f"Missing vals : {model_input.isnull().sum().sum()}")
    print(f"\nFirst 3 rows (key columns):")
    cols = ["equipment_id", "type", "age", "health", "load",
            "failure_next_7_days", "network_importance"]
    print(model_input[cols].head(3).to_string(index=False))
    print("\n[OK] preprocessing: model_input.csv written successfully")
