"""
pages/ai_insights.py — AI Model Insights
Model metrics, feature importance, data quality, scenario simulator.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from weather_risk import calculate_weather_risk
from grid_impact import calculate_grid_impact
from priority import calculate_priority, get_risk_level


def render(ctx: dict) -> None:
    df: pd.DataFrame = ctx.get("results_df")
    raw = ctx.get("raw_data")
    model = ctx.get("model")
    ml_metrics = ctx.get("ml_metrics")
    feat_import = ctx.get("feat_import")
    RISK_COLORS = ctx["RISK_COLORS"]

    st.markdown("""
    <div style="margin-bottom:1rem;">
        <div style="font-size:1.3rem;font-weight:700;color:#60a5fa;">AI Insights</div>
        <div style="font-size:0.75rem;color:#64748b;letter-spacing:0.1em;text-transform:uppercase;">
            Model performance, explainability & what-if simulation
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["Model Performance", "Feature Importance", "Data Quality"])

    # ── TAB 1: Model performance ─────────────────────────────────────────
    with tab1:
        st.markdown('<div class="gg-section-title">ML MODEL</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="gg-card" style="margin-bottom:1rem;">
            <div style="display:flex;gap:2rem;flex-wrap:wrap;">
                <div>
                    <div style="font-size:0.68rem;color:#64748b;text-transform:uppercase;
                                letter-spacing:0.1em;">Algorithm</div>
                    <div style="font-size:0.95rem;font-weight:600;color:#a78bfa;">
                        Random Forest Classifier</div>
                </div>
                <div>
                    <div style="font-size:0.68rem;color:#64748b;text-transform:uppercase;
                                letter-spacing:0.1em;">Target</div>
                    <div style="font-size:0.95rem;font-weight:600;color:#e2e8f0;">
                        failure_next_7_days</div>
                </div>
                <div>
                    <div style="font-size:0.68rem;color:#64748b;text-transform:uppercase;
                                letter-spacing:0.1em;">Trees</div>
                    <div style="font-size:0.95rem;font-weight:600;color:#e2e8f0;">100</div>
                </div>
                <div>
                    <div style="font-size:0.68rem;color:#64748b;text-transform:uppercase;
                                letter-spacing:0.1em;">Class Weight</div>
                    <div style="font-size:0.95rem;font-weight:600;color:#e2e8f0;">Balanced</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if ml_metrics:
            st.markdown('<div class="gg-section-title">EVALUATION METRICS</div>',
                        unsafe_allow_html=True)
            m1, m2, m3, m4, m5 = st.columns(5)
            metric_data = [
                (m1, "Accuracy",  ml_metrics.get("accuracy", "—"),  "#10b981"),
                (m2, "Precision", ml_metrics.get("precision", "—"), "#3b82f6"),
                (m3, "Recall",    ml_metrics.get("recall", "—"),    "#f97316"),
                (m4, "F1 Score",  ml_metrics.get("f1", "—"),        "#a78bfa"),
                (m5, "ROC-AUC",   ml_metrics.get("roc_auc", "N/A") or "N/A", "#eab308"),
            ]
            for col, label, val, color in metric_data:
                display = f"{float(val):.4f}" if isinstance(val, float) else str(val)
                col.markdown(f"""
                <div class="gg-kpi-card">
                    <div class="gg-kpi-label">{label}</div>
                    <div class="gg-kpi-value" style="color:{color};font-size:1.5rem;">
                        {display}</div>
                    <div class="gg-kpi-sub">
                        Train: {ml_metrics.get('train_samples','—')} |
                        Test: {ml_metrics.get('test_samples','—')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            note = ml_metrics.get("note", "")
            if note:
                st.caption(f"Note: {note}")
        else:
            st.info("Model metrics unavailable. Run the pipeline to train the model.")

        # ── Scenario Simulator ───────────────────────────────────────────
        st.markdown('<div class="gg-section-title">WHAT-IF SCENARIO SIMULATOR</div>',
                    unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(167,139,250,0.06);border:1px solid rgba(167,139,250,0.2);
                    border-radius:8px;padding:0.7rem 1rem;margin-bottom:1rem;
                    font-size:0.78rem;color:#94a3b8;">
            SCENARIO SIMULATION — Adjust parameters to explore risk changes.
            This is a deterministic what-if calculation, not a production forecast.
        </div>
        """, unsafe_allow_html=True)

        if df is not None:
            sel_eq = st.selectbox(
                "Select Equipment to Simulate",
                df.sort_values("priority_score", ascending=False)["equipment_id"].tolist(),
                key="sim_eq",
            )
            base_row = df[df["equipment_id"] == sel_eq].iloc[0]

            # Safe scalar getters from a pandas Series
            def _get(col, default):
                v = base_row[col] if col in base_row.index else default
                return default if pd.isna(v) else v

            sc1, sc2, sc3, sc4 = st.columns(4)
            with sc1:
                sim_wind = st.slider("Wind (km/h)", 0, 120,
                                     int(_get("weather_wind", 30)), key="sim_wind")
            with sc2:
                sim_rain = st.slider("Rainfall (mm)", 0, 150,
                                     int(_get("weather_rainfall", 20)), key="sim_rain")
            with sc3:
                sim_temp = st.slider("Temp (C)", 20, 50,
                                     int(_get("weather_temperature", 32)), key="sim_temp")
            with sc4:
                sim_load = st.slider("Load (%)", 0, 100,
                                     int(_get("load", 50)), key="sim_load")

            # Recalculate weather risk with simulated values
            EPS = 1e-9
            rain_min = float(df["weather_rainfall"].min()) if "weather_rainfall" in df.columns else 0.0
            rain_max = float(df["weather_rainfall"].max()) if "weather_rainfall" in df.columns else 120.0
            wind_min = float(df["weather_wind"].min()) if "weather_wind" in df.columns else 0.0
            wind_max = float(df["weather_wind"].max()) if "weather_wind" in df.columns else 90.0

            def norm(v, lo, hi):
                return ((v - lo) / (hi - lo + EPS)) * 100 if hi > lo else 50.0

            sim_rain_r = norm(sim_rain, rain_min, rain_max)
            sim_wind_r = norm(sim_wind, wind_min, wind_max)
            sim_temp_r = max(0.0, (sim_temp - 35) / max(1, 45 - 35)) * 100
            sim_storm_r = float(_get("weather_storm", 0)) * 60 + float(_get("weather_flood_risk", 0)) * 40

            sim_wr = min(100.0, max(0.0,
                0.40 * sim_rain_r + 0.30 * sim_wind_r +
                0.20 * sim_temp_r + 0.10 * sim_storm_r
            ))

            base_fp   = float(_get("failure_probability", 0))
            base_gi   = float(_get("grid_impact", 0))
            base_wr   = float(_get("weather_risk", 0))
            base_ps   = float(_get("priority_score", 0))
            base_rl   = str(_get("risk_level", "LOW"))

            # Simulate load impact on grid impact (proportional)
            load_ratio = sim_load / max(1, float(_get("load", 50)))
            sim_gi = min(100, base_gi * load_ratio)

            sim_ps = min(100, max(0,
                0.50 * base_fp * 100 + 0.20 * sim_wr + 0.30 * sim_gi
            ))
            sim_rl = get_risk_level(sim_ps)

            delta_ps = round(sim_ps - base_ps, 1)
            delta_color = "#ef4444" if delta_ps > 0 else "#10b981"
            escalated = (sim_rl != base_rl)

            sr1, sr2, sr3 = st.columns(3)
            sr1.markdown(f"""
            <div class="gg-kpi-card">
                <div class="gg-kpi-label">Current Priority</div>
                <div class="gg-kpi-value" style="color:{RISK_COLORS.get(base_rl,'#60a5fa')};">
                    {round(base_ps,1)}</div>
                <div class="gg-kpi-sub">{base_rl}</div>
            </div>
            """, unsafe_allow_html=True)
            sr2.markdown(f"""
            <div class="gg-kpi-card">
                <div class="gg-kpi-label">Simulated Priority</div>
                <div class="gg-kpi-value" style="color:{RISK_COLORS.get(sim_rl,'#60a5fa')};">
                    {round(sim_ps,1)}</div>
                <div class="gg-kpi-sub">{sim_rl}</div>
            </div>
            """, unsafe_allow_html=True)
            sr3.markdown(f"""
            <div class="gg-kpi-card">
                <div class="gg-kpi-label">Risk Change</div>
                <div class="gg-kpi-value" style="color:{delta_color};">
                    {'+' if delta_ps>=0 else ''}{delta_ps}</div>
                <div class="gg-kpi-sub">
                    {'ESCALATION: ' + base_rl + ' -> ' + sim_rl if escalated else 'No level change'}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── TAB 2: Feature importance ────────────────────────────────────────
    with tab2:
        st.markdown('<div class="gg-section-title">RANDOM FOREST FEATURE IMPORTANCE</div>',
                    unsafe_allow_html=True)
        if feat_import is not None and not feat_import.empty:
            fig_fi = go.Figure(go.Bar(
                x=feat_import["importance"].tolist(),
                y=feat_import["feature"].tolist(),
                orientation="h",
                marker_color="#a78bfa",
                marker_line_width=0,
                text=[f"{v:.1%}" for v in feat_import["importance"].tolist()],
                textposition="outside",
                textfont=dict(color="#94a3b8", size=10),
            ))
            fig_fi.update_layout(
                height=400, margin=dict(l=10, r=80, t=10, b=20),
                paper_bgcolor="#0a1628", plot_bgcolor="#0a1628",
                xaxis=dict(gridcolor="#1e3a5f", tickfont=dict(color="#64748b")),
                yaxis=dict(autorange="reversed", tickfont=dict(color="#e2e8f0")),
                font_color="#e2e8f0",
            )
            st.plotly_chart(fig_fi, use_container_width=True)
            st.markdown('<div class="gg-section-title">IMPORTANCE TABLE</div>',
                        unsafe_allow_html=True)
            st.dataframe(feat_import, use_container_width=True, hide_index=True)
        else:
            st.info("Feature importance unavailable. Run the pipeline first.")

    # ── TAB 3: Data quality ──────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="gg-section-title">DATA QUALITY REPORT</div>',
                    unsafe_allow_html=True)
        if raw:
            summary = raw.get("summary", {})
            rows = []
            for key in ["equipment", "weather", "incidents", "crews"]:
                meta = summary.get(key, {})
                rows.append({
                    "Dataset":        meta.get("file", key),
                    "Records":        meta.get("rows", "—"),
                    "Columns":        len(meta.get("columns", [])),
                    "Missing Values": meta.get("missing_values", 0),
                    "Duplicates":     meta.get("duplicate_rows", 0),
                    "Status": "OK" if meta.get("missing_values", 0) == 0 else "Has Missing",
                })
            quality_df = pd.DataFrame(rows)
            st.dataframe(quality_df, use_container_width=True, hide_index=True)

            if df is not None:
                st.markdown('<div class="gg-section-title">PROCESSED OUTPUT QUALITY</div>',
                            unsafe_allow_html=True)
                q1, q2, q3 = st.columns(3)
                q1.metric("Total Records",  len(df))
                q2.metric("Missing Values", int(df[["failure_probability","weather_risk",
                                                      "grid_impact","priority_score"]].isnull().sum().sum()))
                q3.metric("Risk Levels Found", df["risk_level"].nunique())
        else:
            st.info("Raw data unavailable.")
