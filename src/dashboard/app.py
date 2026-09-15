"""
dashboard/app.py
----------------
GridGuard AI — Grid Operations Command Center

Entry point for the Streamlit dashboard.
Handles:
  - CSS injection
  - Cached data loading
  - Page routing via sidebar
  - Graceful error display when pipeline has not been run
"""

import sys
import warnings
from pathlib import Path

import pandas as pd
import streamlit as st

# ── Path setup ────────────────────────────────────────────────────────────
SRC_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC_DIR))

# ── Streamlit page config — MUST be first st call ────────────────────────
st.set_page_config(
    page_title="GridGuard AI — Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS injection ─────────────────────────────────────────────────────────
def _inject_css() -> None:
    css_path = Path(__file__).parent / "styles" / "theme.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

_inject_css()

# ── Cached data loaders ───────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_results() -> pd.DataFrame:
    """Load predictions.csv — cached so it is read only once per session."""
    from pipeline import load_results as _load
    return _load()


@st.cache_data(show_spinner=False)
def load_raw_data():
    """Load all four raw CSVs — cached."""
    from data_loader import load_all_data
    return load_all_data()


@st.cache_resource(show_spinner=False)
def load_model_and_meta():
    """
    Load (or train) the model and return (model, metrics, feature_importance).
    Uses cache_resource so the model object is not re-serialised on every rerun.
    """
    from data_loader import load_all_data
    from preprocessing import preprocess, get_feature_columns
    from failure_prediction import train, predict
    from explainability import global_feature_importance

    equipment, weather, incidents, crews, _ = load_all_data()
    model_input = preprocess(equipment, weather, incidents)
    model, metrics = train(model_input, force_retrain=False)
    fi = global_feature_importance(model, get_feature_columns(), top_n=10)
    return model, metrics, fi


# ── Risk colour helpers (used by multiple pages) ──────────────────────────

RISK_COLORS = {
    "CRITICAL": "#ef4444",
    "HIGH":     "#f97316",
    "MEDIUM":   "#eab308",
    "LOW":      "#10b981",
}

RISK_BADGE_CLASS = {
    "CRITICAL": "gg-badge gg-badge-critical",
    "HIGH":     "gg-badge gg-badge-high",
    "MEDIUM":   "gg-badge gg-badge-medium",
    "LOW":      "gg-badge gg-badge-low",
}

def risk_badge(level: str) -> str:
    cls = RISK_BADGE_CLASS.get(str(level).upper(), "gg-badge gg-badge-low")
    return f'<span class="{cls}">{level}</span>'


def risk_color(level: str) -> str:
    return RISK_COLORS.get(str(level).upper(), "#10b981")


# ── Sidebar navigation ────────────────────────────────────────────────────

PAGES = [
    ("Overview",            "overview"),
    ("Risk Command Center", "risk_command"),
    ("Live Grid Map",       "grid_map"),
    ("Equipment Intel",     "equipment"),
    ("Crew Operations",     "crew_operations"),
    ("AI Insights",         "ai_insights"),
    ("Alert Center",        "alert_center"),
]

PAGE_ICONS = {
    "overview":        "⚡",
    "risk_command":    "📊",
    "grid_map":        "🗺️",
    "equipment":       "🔧",
    "crew_operations": "👷",
    "ai_insights":     "🤖",
    "alert_center":    "🚨",
}

with st.sidebar:
    # Logo / brand
    st.markdown(
        """
        <div style="padding:1rem 0 0.5rem 0; border-bottom:1px solid #1e3a5f; margin-bottom:1rem;">
            <div style="font-size:1.3rem;font-weight:800;color:#60a5fa;letter-spacing:0.05em;">
                ⚡ GRIDGUARD AI
            </div>
            <div style="font-size:0.65rem;color:#64748b;letter-spacing:0.14em;
                        text-transform:uppercase;margin-top:0.2rem;">
                Grid Operations Intelligence
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Navigation
    if "page" not in st.session_state:
        st.session_state.page = "overview"

    for label, key in PAGES:
        icon = PAGE_ICONS.get(key, "•")
        active = st.session_state.page == key
        btn_type = "primary" if active else "secondary"
        if st.button(
            f"{icon}  {label}",
            key=f"nav_{key}",
            use_container_width=True,
            type=btn_type,
        ):
            st.session_state.page = key
            st.rerun()

    st.markdown("<hr style='border-color:#1e3a5f;margin:1rem 0;'>", unsafe_allow_html=True)

    # Run pipeline button
    if st.button("▶  Run Pipeline", use_container_width=True, key="run_pipeline_btn"):
        with st.spinner("Running GridGuard AI pipeline..."):
            try:
                from pipeline import run_pipeline
                load_results.clear()
                run_pipeline(force_retrain=False)
                st.success("Pipeline complete!")
                st.rerun()
            except Exception as e:
                st.error(f"Pipeline error: {e}")

    st.markdown(
        "<div style='font-size:0.65rem;color:#334155;text-align:center;margin-top:1rem;'>"
        "DEMO DATA — Synthetic<br>IBM Bob Hackathon 2025"
        "</div>",
        unsafe_allow_html=True,
    )


# ── Load data — with graceful error handling ──────────────────────────────

results_df = None
raw_data   = None
_pipeline_error = None

try:
    results_df = load_results()
except FileNotFoundError:
    _pipeline_error = "pipeline_not_run"
except Exception as e:
    _pipeline_error = str(e)

try:
    equipment_df, weather_df, incidents_df, crews_df, load_summary = load_raw_data()
    raw_data = {
        "equipment": equipment_df,
        "weather":   weather_df,
        "incidents": incidents_df,
        "crews":     crews_df,
        "summary":   load_summary,
    }
except Exception as e:
    raw_data = None

model_obj   = None
ml_metrics  = None
feat_import = None
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model_obj, ml_metrics, feat_import = load_model_and_meta()
except Exception:
    pass  # AI Insights page will show a fallback message


# ── Pipeline-not-run banner ───────────────────────────────────────────────

if _pipeline_error == "pipeline_not_run":
    st.markdown(
        """
        <div style="background:rgba(234,179,8,0.1);border:1px solid rgba(234,179,8,0.3);
                    border-radius:10px;padding:1.2rem 1.5rem;margin-bottom:1.5rem;">
            <div style="font-size:0.95rem;font-weight:700;color:#fbbf24;margin-bottom:0.4rem;">
                Pipeline Not Yet Run
            </div>
            <div style="font-size:0.82rem;color:#94a3b8;">
                Click <strong style="color:#fbbf24;">Run Pipeline</strong> in the sidebar to
                generate predictions, or run <code>python src/main.py</code> from the terminal.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
elif _pipeline_error:
    st.error(f"Could not load predictions: {_pipeline_error}")


# ── Page routing ──────────────────────────────────────────────────────────

page = st.session_state.get("page", "overview")

ctx = {
    "results_df":   results_df,
    "raw_data":     raw_data,
    "model":        model_obj,
    "ml_metrics":   ml_metrics,
    "feat_import":  feat_import,
    "risk_badge":   risk_badge,
    "risk_color":   risk_color,
    "RISK_COLORS":  RISK_COLORS,
}

if page == "overview":
    from dashboard.pages.overview import render
    render(ctx)

elif page == "risk_command":
    from dashboard.pages.risk_command import render
    render(ctx)

elif page == "grid_map":
    from dashboard.pages.grid_map import render
    render(ctx)

elif page == "equipment":
    from dashboard.pages.equipment import render
    render(ctx)

elif page == "crew_operations":
    from dashboard.pages.crew_operations import render
    render(ctx)

elif page == "ai_insights":
    from dashboard.pages.ai_insights import render
    render(ctx)

elif page == "alert_center":
    from dashboard.pages.alert_center import render
    render(ctx)
