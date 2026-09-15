"""
pages/equipment.py — Equipment Intelligence + AI Decision Card
Full per-asset analysis with explainability.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from explainability import explain_equipment, build_ai_decision_summary


def render(ctx: dict) -> None:
    df: pd.DataFrame = ctx.get("results_df")
    risk_badge = ctx["risk_badge"]
    RISK_COLORS = ctx["RISK_COLORS"]
    risk_color = ctx["risk_color"]

    st.markdown("""
    <div style="margin-bottom:1rem;">
        <div style="font-size:1.3rem;font-weight:700;color:#60a5fa;">
            Equipment Intelligence
        </div>
        <div style="font-size:0.75rem;color:#64748b;letter-spacing:0.1em;text-transform:uppercase;">
            Per-asset AI decision & explainability
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df is None:
        st.warning("No predictions available. Run the pipeline first.")
        return

    # ── Equipment selector ───────────────────────────────────────────────
    sorted_df = df.sort_values("priority_score", ascending=False)
    eq_options = sorted_df["equipment_id"].tolist()

    def _fmt(x):
        rows = df.loc[df["equipment_id"] == x]
        if rows.empty:
            return x
        return f"{x} - {rows['type'].values[0]} [{rows['risk_level'].values[0]}]"

    sel = st.selectbox("Select Equipment Asset", eq_options, format_func=_fmt)

    matches = df[df["equipment_id"] == sel]
    if matches.empty:
        st.warning(f"No data found for {sel}.")
        return
    row = matches.iloc[0]
    summary = build_ai_decision_summary(row)
    rl = summary["risk_level"]
    fp_pct = summary["failure_probability"]
    rc = risk_color(rl)

    # ── Layout: decision card left, charts right ─────────────────────────
    col_card, col_charts = st.columns([1, 1])

    with col_card:
        # ── AI Decision Card ─────────────────────────────────────────────
        st.markdown(f"""
        <div class="gg-decision-card">
            <div class="gg-decision-header">
                <div class="gg-decision-title">AI DECISION — {summary['equipment_id']}</div>
                <div class="gg-decision-subtitle">{summary['type']}</div>
            </div>

            <div class="gg-metric-row">
                <div class="gg-metric-block">
                    <div class="gg-metric-block-val">{fp_pct}%</div>
                    <div class="gg-metric-block-lbl">Failure Probability</div>
                </div>
                <div class="gg-metric-block">
                    <div class="gg-metric-block-val">{summary['weather_risk']}</div>
                    <div class="gg-metric-block-lbl">Weather Risk</div>
                </div>
                <div class="gg-metric-block">
                    <div class="gg-metric-block-val">{summary['grid_impact']}</div>
                    <div class="gg-metric-block-lbl">Grid Impact</div>
                </div>
            </div>

            <div class="gg-priority-display">
                <div class="gg-priority-lbl">Priority Score</div>
                <div class="gg-priority-val" style="color:{rc};">
                    {summary['priority_score']}</div>
                <div style="margin-top:0.5rem;">{risk_badge(rl)}</div>
            </div>

            <div class="gg-section-title" style="margin-top:1rem;">
                WHY THIS ASSET IS AT RISK</div>
            <div class="gg-risk-reasons">
        """, unsafe_allow_html=True)

        for reason in summary["risk_reasons"]:
            st.markdown(
                f'<div class="gg-risk-reason-item">&#10003; {reason}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("""
            </div>

            <div class="gg-section-title">RECOMMENDED ACTION</div>
        """, unsafe_allow_html=True)

        action_icon = {
            "Immediate Inspection": "🔴",
            "Preventive Maintenance": "🟠",
            "Monitor": "🟡",
            "Normal Maintenance": "🟢",
        }.get(summary["maintenance_action"], "🔵")

        st.markdown(f"""
            <div class="gg-action-box">
                {action_icon} &nbsp; {summary['maintenance_action']}
            </div>
        """, unsafe_allow_html=True)

        # Crew
        crew = summary.get("assigned_crew", "N/A")
        dist = summary.get("crew_distance_km")
        import pandas as _pd
        dist_str = f"{float(dist):.1f} km" if _pd.notna(dist) else "-"

        if crew and crew not in ("N/A", "N/A - below threshold", "No suitable crew available"):
            st.markdown(f"""
            <div class="gg-section-title">CREW PRE-POSITIONING</div>
            <div class="gg-crew-box">
                <div style="font-size:1rem;font-weight:700;color:#34d399;">{crew}</div>
                <div style="font-size:0.78rem;color:#94a3b8;margin-top:0.3rem;">
                    AVAILABLE &nbsp;|&nbsp; {dist_str} away
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="gg-section-title">CREW PRE-POSITIONING</div>
            <div class="gg-crew-box">
                <div style="font-size:0.85rem;color:#94a3b8;">{crew}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_charts:
        st.markdown('<div class="gg-section-title">ASSET METRICS</div>',
                    unsafe_allow_html=True)

        # Radar chart of normalised asset metrics
        categories = ["Health", "Load", "Temperature", "Age (norm)", "Incidents"]
        vals = [
            100 - float(row.get("health", 50)),           # inverse: low health = high risk
            float(row.get("load", 50)),
            min(float(row.get("temperature", 50)), 100),
            min(float(row.get("age", 10)) / 50 * 100, 100),
            min(float(row.get("previous_incidents", 0)) / 12 * 100, 100),
        ]
        categories_closed = categories + [categories[0]]
        vals_closed = vals + [vals[0]]

        fig_radar = go.Figure(go.Scatterpolar(
            r=vals_closed,
            theta=categories_closed,
            fill="toself",
            fillcolor=f"rgba({int(rc[1:3],16)},{int(rc[3:5],16)},{int(rc[5:7],16)},0.15)",
            line=dict(color=rc, width=2),
            name=sel,
        ))
        fig_radar.update_layout(
            height=280,
            polar=dict(
                bgcolor="#0d1f3c",
                radialaxis=dict(visible=True, range=[0, 100],
                                tickfont=dict(color="#64748b", size=9),
                                gridcolor="#1e3a5f"),
                angularaxis=dict(tickfont=dict(color="#94a3b8", size=11),
                                 gridcolor="#1e3a5f"),
            ),
            paper_bgcolor="#0a1628",
            font_color="#e2e8f0",
            margin=dict(l=40, r=40, t=30, b=20),
            showlegend=False,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # Detail table
        st.markdown('<div class="gg-section-title">ASSET DETAILS</div>',
                    unsafe_allow_html=True)
        details = {
            "Age (years)":        str(int(row.get("age", 0))),
            "Health Score":       str(round(float(row.get("health", 0)), 1)),
            "Load (%)":           str(round(float(row.get("load", 0)), 1)),
            "Temperature (C)":    str(round(float(row.get("temperature", 0)), 1)),
            "Voltage (kV)":       str(int(row.get("voltage", 0))),
            "Customers Served":   str(int(row.get("customers_served", 0))),
            "Critical Facility":  "Yes" if row.get("critical_facility", 0) else "No",
            "Previous Incidents": str(int(row.get("previous_incidents", 0))),
        }
        details_df = pd.DataFrame(
            list(details.items()), columns=["Attribute", "Value"]
        )
        # column_config ensures both columns are treated as strings — avoids PyArrow type error
        st.dataframe(
            details_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Attribute": st.column_config.TextColumn("Attribute"),
                "Value":     st.column_config.TextColumn("Value"),
            },
        )

        # AI Pipeline visualization
        st.markdown('<div class="gg-section-title">AI DECISION PIPELINE</div>',
                    unsafe_allow_html=True)
        steps = [
            ("FAILURE PROBABILITY", f"{fp_pct}%"),
            ("WEATHER RISK",        f"{summary['weather_risk']}"),
            ("GRID IMPACT",         f"{summary['grid_impact']}"),
            ("PRIORITY SCORE",      f"{summary['priority_score']}"),
            ("RISK LEVEL",          rl),
            ("MAINTENANCE ACTION",  summary['maintenance_action']),
            ("CREW ASSIGNED",       crew),
        ]
        for i, (step, val) in enumerate(steps):
            st.markdown(f"""
            <div class="gg-pipeline-step">
                <span style="color:#64748b;font-size:0.65rem;">{step}</span><br>
                <span style="font-size:0.9rem;color:#e2e8f0;">{val}</span>
            </div>
            {"<div class='gg-pipeline-arrow'>|</div>" if i < len(steps)-1 else ""}
            """, unsafe_allow_html=True)
