"""
weather_risk.py
---------------
Computes a 0–100 Weather Risk score for each equipment row.

Formula
-------
  weather_risk = 0.40 × rainfall_risk
               + 0.30 × wind_risk
               + 0.20 × temp_stress_risk
               + 0.10 × storm_risk

Sub-score derivation
--------------------
rainfall_risk   : min-max normalised rainfall          → 0-100
wind_risk       : min-max normalised wind speed        → 0-100
temp_stress_risk: deviation of weather temperature
                  above a 35 °C safe threshold,
                  normalised over the observed range   → 0-100
storm_risk      : binary storm flag × 100 (0 or 100)
                  blended with flood_risk × 100

All normalisation uses safe division (epsilon guard) so the module
never raises ZeroDivisionError regardless of input data.
"""

import numpy as np
import pandas as pd
from typing import Union


# ── Normalisation helpers ─────────────────────────────────────────────────

_EPS = 1e-9   # prevents division-by-zero in degenerate datasets


def _minmax_norm(series: pd.Series, low: float = None, high: float = None) -> pd.Series:
    """
    Normalise series to 0-100 using min-max scaling.
    If low/high are supplied they act as clipping bounds before scaling.
    Returns a float Series; safe against constant-value series.
    """
    s = series.copy().astype(float)
    if low is not None:
        s = s.clip(lower=low)
    if high is not None:
        s = s.clip(upper=high)
    s_min = s.min()
    s_max = s.max()
    if (s_max - s_min) < _EPS:
        # Constant series — map to midpoint (50) so it doesn't dominate
        return pd.Series(50.0, index=series.index)
    return ((s - s_min) / (s_max - s_min + _EPS)) * 100.0


def _temp_stress(series: pd.Series, threshold: float = 35.0) -> pd.Series:
    """
    Measure temperature stress as degrees above the safe threshold.
    Values at or below threshold → 0 stress.
    Normalise the excess over the observed max excess.
    """
    excess = (series.astype(float) - threshold).clip(lower=0)
    max_excess = excess.max()
    if max_excess < _EPS:
        return pd.Series(0.0, index=series.index)
    return (excess / (max_excess + _EPS)) * 100.0


# ── Public API ────────────────────────────────────────────────────────────

def calculate_weather_risk(model_input: pd.DataFrame) -> pd.Series:
    """
    Compute weather risk (0–100) for every row in model_input.

    Expected columns (added by preprocessing._assign_weather):
        weather_rainfall, weather_wind, weather_temperature,
        weather_storm, weather_flood_risk

    Returns
    -------
    pd.Series named 'weather_risk', index aligned with model_input.
    """
    required = [
        "weather_rainfall", "weather_wind",
        "weather_temperature", "weather_storm", "weather_flood_risk",
    ]
    missing = [c for c in required if c not in model_input.columns]
    if missing:
        raise ValueError(
            f"[weather_risk] Missing columns: {missing}. "
            "Ensure preprocessing.preprocess() has been called."
        )

    df = model_input[required].copy().astype(float)

    rainfall_risk    = _minmax_norm(df["weather_rainfall"], low=0)
    wind_risk        = _minmax_norm(df["weather_wind"],     low=0)
    temp_stress_risk = _temp_stress(df["weather_temperature"], threshold=35.0)

    # storm_risk: blend the binary storm flag with continuous flood_risk
    storm_risk = (
        0.6 * df["weather_storm"].clip(0, 1) * 100.0
        + 0.4 * df["weather_flood_risk"].clip(0, 1) * 100.0
    )

    weather_risk = (
        0.40 * rainfall_risk
        + 0.30 * wind_risk
        + 0.20 * temp_stress_risk
        + 0.10 * storm_risk
    ).clip(0, 100).round(2)

    return pd.Series(weather_risk.values, index=model_input.index, name="weather_risk")


# ── Smoke-test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from data_loader import load_all_data
    from preprocessing import preprocess

    eq, wt, inc, cr, _ = load_all_data()
    model_input = preprocess(eq, wt, inc)

    wr = calculate_weather_risk(model_input)

    result = (
        model_input[["equipment_id", "type"]]
        .assign(weather_risk=wr.values)
        .sort_values("weather_risk", ascending=False)
    )
    print("=== Weather Risk (all equipment, sorted) ===")
    print(result.to_string(index=False))
    print(f"\nMin : {wr.min():.2f}   Max : {wr.max():.2f}   Mean : {wr.mean():.2f}")
    print("[OK] weather_risk: complete")
