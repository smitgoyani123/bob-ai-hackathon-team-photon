"""
grid_impact.py
--------------
Computes a 0–100 Grid Impact score for each equipment row.

Formula
-------
  grid_impact = 0.40 × customer_impact
              + 0.20 × critical_facility_impact
              + 0.20 × load_impact
              + 0.20 × network_importance_impact

Sub-score derivation
--------------------
customer_impact          : min-max normalised customers_served     → 0-100
critical_facility_impact : binary (0 or 1) × 100                   → 0 or 100
load_impact              : min-max normalised load                  → 0-100
network_importance_impact: network_importance column from
                           preprocessing (already 0–100)

network_importance is derived transparently in preprocessing from:
  voltage (40 %) + customers_served (40 %) + critical_facility (20 %)
This is documented in preprocessing.py.

All normalisation uses epsilon-guard safe division.
"""

import numpy as np
import pandas as pd

_EPS = 1e-9


def _minmax_norm(series: pd.Series) -> pd.Series:
    """Min-max normalise a Series to 0–100; safe against constant input."""
    s = series.astype(float).clip(lower=0)
    s_min, s_max = s.min(), s.max()
    if (s_max - s_min) < _EPS:
        return pd.Series(50.0, index=series.index)
    return ((s - s_min) / (s_max - s_min + _EPS)) * 100.0


def calculate_grid_impact(model_input: pd.DataFrame) -> pd.Series:
    """
    Compute grid impact (0–100) for every row in model_input.

    Required columns:
        customers_served, critical_facility, load, network_importance

    Returns
    -------
    pd.Series named 'grid_impact', index aligned with model_input.
    """
    required = ["customers_served", "critical_facility", "load", "network_importance"]
    missing = [c for c in required if c not in model_input.columns]
    if missing:
        raise ValueError(
            f"[grid_impact] Missing columns: {missing}. "
            "Ensure preprocessing.preprocess() has been called."
        )

    customer_impact   = _minmax_norm(model_input["customers_served"])
    critical_impact   = model_input["critical_facility"].astype(float).clip(0, 1) * 100.0
    load_impact       = _minmax_norm(model_input["load"])
    # network_importance is already 0–100 from preprocessing; clip to be safe
    network_impact    = model_input["network_importance"].astype(float).clip(0, 100)

    grid_impact = (
        0.40 * customer_impact
        + 0.20 * critical_impact
        + 0.20 * load_impact
        + 0.20 * network_impact
    ).clip(0, 100).round(2)

    return pd.Series(grid_impact.values, index=model_input.index, name="grid_impact")


# ── Smoke-test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from data_loader import load_all_data
    from preprocessing import preprocess

    eq, wt, inc, cr, _ = load_all_data()
    model_input = preprocess(eq, wt, inc)

    gi = calculate_grid_impact(model_input)

    result = (
        model_input[["equipment_id", "type", "customers_served", "critical_facility"]]
        .assign(grid_impact=gi.values)
        .sort_values("grid_impact", ascending=False)
    )
    print("=== Grid Impact (all equipment, sorted) ===")
    print(result.to_string(index=False))
    print(f"\nMin : {gi.min():.2f}   Max : {gi.max():.2f}   Mean : {gi.mean():.2f}")
    print("[OK] grid_impact: complete")
