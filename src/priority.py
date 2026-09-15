"""
priority.py
-----------
Computes a 0–100 Priority Score for each equipment row and derives
Risk Level and Maintenance Action.

Formula
-------
  priority_score = 0.50 × (failure_probability × 100)
                 + 0.20 × weather_risk
                 + 0.30 × grid_impact

Risk levels
-----------
   0 – 30  →  LOW
  30 – 60  →  MEDIUM
  60 – 80  →  HIGH
  80 – 100 →  CRITICAL

Maintenance actions
-------------------
  CRITICAL →  Immediate Inspection
  HIGH     →  Preventive Maintenance
  MEDIUM   →  Monitor
  LOW      →  Normal Maintenance
"""

import pandas as pd
from typing import Tuple


# ── Risk level thresholds ─────────────────────────────────────────────────

def get_risk_level(score: float) -> str:
    """Map a 0–100 priority score to a risk level string."""
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "HIGH"
    elif score >= 30:
        return "MEDIUM"
    else:
        return "LOW"


def get_maintenance_action(risk_level: str) -> str:
    """Map a risk level to the recommended maintenance action."""
    actions = {
        "CRITICAL": "Immediate Inspection",
        "HIGH":     "Preventive Maintenance",
        "MEDIUM":   "Monitor",
        "LOW":      "Normal Maintenance",
    }
    return actions.get(risk_level, "Monitor")


# ── Public API ────────────────────────────────────────────────────────────

def calculate_priority(
    model_input: pd.DataFrame,
    failure_probability: pd.Series,
    weather_risk: pd.Series,
    grid_impact: pd.Series,
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Compute priority score, risk level and maintenance action.

    Parameters
    ----------
    model_input         : preprocessed DataFrame (index must align)
    failure_probability : Series (0.0–1.0) from failure_prediction.predict()
    weather_risk        : Series (0–100)   from weather_risk.calculate_weather_risk()
    grid_impact         : Series (0–100)   from grid_impact.calculate_grid_impact()

    Returns
    -------
    priority_score      : pd.Series (0–100, rounded to 2 dp)
    risk_level          : pd.Series of strings
    maintenance_action  : pd.Series of strings
    """
    fp_score = (failure_probability.values * 100.0).clip(0, 100)
    wr_score = weather_risk.values.clip(0, 100)
    gi_score = grid_impact.values.clip(0, 100)

    raw = (
        0.50 * fp_score
        + 0.20 * wr_score
        + 0.30 * gi_score
    ).clip(0, 100).round(2)

    priority_score     = pd.Series(raw,                               index=model_input.index, name="priority_score")
    risk_level         = pd.Series([get_risk_level(s) for s in raw],  index=model_input.index, name="risk_level")
    maintenance_action = pd.Series(
        [get_maintenance_action(r) for r in risk_level],
        index=model_input.index,
        name="maintenance_action",
    )

    return priority_score, risk_level, maintenance_action


# ── Smoke-test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from data_loader import load_all_data
    from preprocessing import preprocess
    from failure_prediction import train, predict
    from weather_risk import calculate_weather_risk
    from grid_impact import calculate_grid_impact

    eq, wt, inc, cr, _ = load_all_data()
    mi = preprocess(eq, wt, inc)

    model, _ = train(mi)
    fp = predict(model, mi)
    wr = calculate_weather_risk(mi)
    gi = calculate_grid_impact(mi)
    ps, rl, ma = calculate_priority(mi, fp, wr, gi)

    result = (
        mi[["equipment_id", "type"]]
        .assign(
            failure_prob=fp.round(2).values,
            weather_risk=wr.values,
            grid_impact=gi.values,
            priority_score=ps.values,
            risk_level=rl.values,
            maintenance=ma.values,
        )
        .sort_values("priority_score", ascending=False)
    )
    print("=== Priority Scores (all equipment, sorted) ===")
    print(result.to_string(index=False))

    print("\n=== Risk Level Distribution ===")
    print(rl.value_counts().to_dict())

    print("[OK] priority: complete")
