"""
data_loader.py
--------------
Loads and validates the four raw GridGuard CSV files.

Returns raw DataFrames and a summary dict that includes record counts,
column lists, and per-file missing-value counts.

Never silently swallows errors — callers receive a clear message when a
file is missing, unreadable, or structurally invalid.
"""

import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any

from config.settings import RAW_DATA_DIR

# ── Expected columns per file ─────────────────────────────────────────────
REQUIRED_COLUMNS: Dict[str, list] = {
    "equipment": [
        "equipment_id", "type", "age", "temperature", "load",
        "health", "voltage", "customers_served", "critical_facility",
        "latitude", "longitude",
    ],
    "weather": [
        "location", "rainfall", "wind", "temperature",
        "storm", "flood_risk", "latitude", "longitude",
    ],
    "incidents": [
        "equipment_id", "previous_incidents", "severity",
        "last_failure_date", "failure_next_7_days",
    ],
    "crews": [
        "crew_id", "latitude", "longitude", "status",
        "skill", "capacity", "available_from",
    ],
}

FILE_MAP: Dict[str, str] = {
    "equipment": "equipment.csv",
    "weather":   "weather.csv",
    "incidents": "incidents.csv",
    "crews":     "crews.csv",
}


# ── Internal helpers ──────────────────────────────────────────────────────

def _load_csv(name: str) -> pd.DataFrame:
    """Load a single CSV and perform basic structural validation."""
    path = Path(RAW_DATA_DIR) / FILE_MAP[name]

    if not path.exists():
        raise FileNotFoundError(
            f"[data_loader] Required file not found: {path}\n"
            f"Please place '{FILE_MAP[name]}' in data/raw/"
        )

    try:
        df = pd.read_csv(path)
    except Exception as exc:
        raise ValueError(f"[data_loader] Could not parse '{path}': {exc}") from exc

    if df.empty:
        raise ValueError(
            f"[data_loader] '{FILE_MAP[name]}' has no data rows. "
            "Please populate the file before running the pipeline."
        )

    # Column presence check
    missing_cols = [c for c in REQUIRED_COLUMNS[name] if c not in df.columns]
    if missing_cols:
        raise ValueError(
            f"[data_loader] '{FILE_MAP[name]}' is missing required columns: "
            f"{missing_cols}\nFound columns: {df.columns.tolist()}"
        )

    return df


def _file_summary(name: str, df: pd.DataFrame) -> Dict[str, Any]:
    """Return a quality summary dict for one DataFrame."""
    return {
        "file":           FILE_MAP[name],
        "rows":           len(df),
        "columns":        df.columns.tolist(),
        "missing_values": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }


# ── Public API ────────────────────────────────────────────────────────────

def load_all_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Load all four raw CSVs.

    Returns
    -------
    equipment  : pd.DataFrame
    weather    : pd.DataFrame
    incidents  : pd.DataFrame
    crews      : pd.DataFrame
    summary    : dict  — per-file quality metadata
    """
    equipment = _load_csv("equipment")
    weather   = _load_csv("weather")
    incidents = _load_csv("incidents")
    crews     = _load_csv("crews")

    summary = {
        "equipment": _file_summary("equipment", equipment),
        "weather":   _file_summary("weather",   weather),
        "incidents": _file_summary("incidents", incidents),
        "crews":     _file_summary("crews",     crews),
        "total_records": len(equipment) + len(weather) + len(incidents) + len(crews),
    }

    return equipment, weather, incidents, crews, summary


def load_equipment() -> pd.DataFrame:
    return _load_csv("equipment")

def load_weather() -> pd.DataFrame:
    return _load_csv("weather")

def load_incidents() -> pd.DataFrame:
    return _load_csv("incidents")

def load_crews() -> pd.DataFrame:
    return _load_csv("crews")


# ── Smoke-test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    eq, wt, inc, cr, summary = load_all_data()
    print("=== Data Load Summary ===")
    for key, meta in summary.items():
        if key == "total_records":
            print(f"\nTotal records across all files: {meta}")
        else:
            print(
                f"\n[{key}] rows={meta['rows']}  "
                f"missing={meta['missing_values']}  "
                f"duplicates={meta['duplicate_rows']}"
            )
            print(f"  columns: {meta['columns']}")
    print("\n[OK] data_loader: all files loaded successfully")
