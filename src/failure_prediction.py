"""
failure_prediction.py
---------------------
Trains (or loads) a RandomForestClassifier to predict
failure_next_7_days, then returns per-equipment failure
probabilities and model metadata.

Responsibilities
----------------
- Train / load model from  models/failure_model.pkl
- Evaluate: Accuracy, Precision, Recall, F1
  (ROC-AUC only when both classes are present in the test split)
- Predict failure_probability for all equipment rows
- Expose feature_importances_ for the explainability layer

Safeguards
----------
- One-class target: skips ROC-AUC, logs a warning
- Small dataset: uses stratified split when possible, falls back to
  random split if stratification fails
- Missing feature columns: raises a descriptive ValueError
- Saved model mismatch: retrains automatically
"""

import warnings
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

from config.settings import MODEL_DIR
from preprocessing import get_feature_columns

MODEL_PATH = Path(MODEL_DIR) / "failure_model.pkl"
RANDOM_STATE = 42


# ── Internal helpers ──────────────────────────────────────────────────────

def _validate_features(df: pd.DataFrame, feature_cols: list) -> None:
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"[failure_prediction] DataFrame is missing feature columns: {missing}\n"
            "Run preprocessing.preprocess() before calling this module."
        )


def _safe_train_test_split(
    X: pd.DataFrame, y: pd.Series
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Stratified split when possible; random split as fallback."""
    try:
        return train_test_split(
            X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
        )
    except ValueError:
        warnings.warn(
            "[failure_prediction] Stratified split failed (too few samples per class). "
            "Falling back to random split.",
            UserWarning,
        )
        return train_test_split(
            X, y, test_size=0.2, random_state=RANDOM_STATE
        )


def _evaluate(
    model: RandomForestClassifier,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> Dict[str, Any]:
    """Return a metrics dict; ROC-AUC omitted for one-class test splits."""
    y_pred = model.predict(X_test)
    metrics: Dict[str, Any] = {
        "accuracy":  round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall":    round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1":        round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "roc_auc":   None,
        "test_samples": len(y_test),
        "train_samples": None,   # filled by caller
    }

    classes_in_test = y_test.nunique()
    if classes_in_test >= 2:
        y_prob = model.predict_proba(X_test)[:, 1]
        metrics["roc_auc"] = round(float(roc_auc_score(y_test, y_prob)), 4)
    else:
        warnings.warn(
            "[failure_prediction] ROC-AUC not calculated: "
            "only one class present in the test split.",
            UserWarning,
        )

    return metrics


# ── Core training ─────────────────────────────────────────────────────────

def train(
    model_input: pd.DataFrame,
    force_retrain: bool = False,
) -> Tuple[RandomForestClassifier, Dict[str, Any]]:
    """
    Train a RandomForestClassifier on model_input.

    Parameters
    ----------
    model_input   : output of preprocessing.preprocess()
    force_retrain : ignore saved model and retrain from scratch

    Returns
    -------
    model   : fitted RandomForestClassifier
    metrics : evaluation dict
    """
    feature_cols = get_feature_columns()
    _validate_features(model_input, feature_cols)

    X = model_input[feature_cols]
    y = model_input["failure_next_7_days"]

    # ── Load cached model if valid ────────────────────────────────────────
    if not force_retrain and MODEL_PATH.exists():
        try:
            cached = joblib.load(MODEL_PATH)
            # Verify feature compatibility
            if hasattr(cached, "feature_names_in_"):
                if list(cached.feature_names_in_) == feature_cols:
                    print("[failure_prediction] Loaded model from cache.")
                    # Re-evaluate on full dataset for metrics display
                    y_prob_full = cached.predict_proba(X)[:, 1]
                    y_pred_full = cached.predict(X)
                    metrics = {
                        "accuracy":      round(float(accuracy_score(y, y_pred_full)), 4),
                        "precision":     round(float(precision_score(y, y_pred_full, zero_division=0)), 4),
                        "recall":        round(float(recall_score(y, y_pred_full, zero_division=0)), 4),
                        "f1":            round(float(f1_score(y, y_pred_full, zero_division=0)), 4),
                        "roc_auc":       round(float(roc_auc_score(y, y_prob_full)), 4) if y.nunique() >= 2 else None,
                        "test_samples":  len(y),
                        "train_samples": len(y),
                        "note":          "Metrics computed on full dataset (cached model)",
                    }
                    return cached, metrics
        except Exception as exc:
            warnings.warn(
                f"[failure_prediction] Cached model load failed ({exc}). Retraining.",
                UserWarning,
            )

    # ── Train ─────────────────────────────────────────────────────────────
    print("[failure_prediction] Training RandomForestClassifier...")

    X_train, X_test, y_train, y_test = _safe_train_test_split(X, y)

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=None,
        min_samples_leaf=1,
        random_state=RANDOM_STATE,
        class_weight="balanced",   # handles class imbalance
    )
    model.fit(X_train, y_train)

    # ── Evaluate ──────────────────────────────────────────────────────────
    metrics = _evaluate(model, X_test, y_test)
    metrics["train_samples"] = len(X_train)

    # ── Save ──────────────────────────────────────────────────────────────
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"[failure_prediction] Model saved to {MODEL_PATH}")

    return model, metrics


# ── Prediction ────────────────────────────────────────────────────────────

def predict(
    model: RandomForestClassifier,
    model_input: pd.DataFrame,
) -> pd.Series:
    """
    Return failure_probability (0.0–1.0) for every row in model_input.

    Parameters
    ----------
    model       : fitted RandomForestClassifier
    model_input : output of preprocessing.preprocess()

    Returns
    -------
    pd.Series of float — index aligned with model_input
    """
    feature_cols = get_feature_columns()
    _validate_features(model_input, feature_cols)

    X = model_input[feature_cols]
    proba = model.predict_proba(X)[:, 1]
    return pd.Series(proba, index=model_input.index, name="failure_probability")


def get_feature_importance(model: RandomForestClassifier) -> pd.DataFrame:
    """
    Return a DataFrame of feature names and their importance scores,
    sorted descending.
    """
    feature_cols = get_feature_columns()
    importance_df = pd.DataFrame({
        "feature":    feature_cols,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False).reset_index(drop=True)
    importance_df["importance"] = importance_df["importance"].round(4)
    return importance_df


# ── Smoke-test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from data_loader import load_all_data
    from preprocessing import preprocess

    equipment, weather, incidents, crews, _ = load_all_data()
    model_input = preprocess(equipment, weather, incidents)

    model, metrics = train(model_input, force_retrain=True)

    print("\n=== Model Evaluation ===")
    for k, v in metrics.items():
        print(f"  {k:<18}: {v}")

    failure_proba = predict(model, model_input)
    print(f"\n=== Failure Probabilities (top 5) ===")
    top5 = (
        model_input[["equipment_id", "type"]]
        .assign(failure_probability=failure_proba.values)
        .sort_values("failure_probability", ascending=False)
        .head(5)
    )
    print(top5.to_string(index=False))

    print("\n=== Top 5 Feature Importances ===")
    print(get_feature_importance(model).head(5).to_string(index=False))

    print("\n[OK] failure_prediction: complete")
