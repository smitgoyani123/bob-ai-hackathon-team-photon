"""
pages/alert_center.py — Alert Center
Grouped alerts by risk level with asset details and actions.
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from explainability import explain_equipment


_ALERT_ICONS = {
    "CRITICAL": "🔴",
    "HIGH":     "🟠",
    "MEDIUM":   "🟡",
    "LOW":      "🟢",
}


def render(ctx: dict) -> None:
    df: pd.DataFrame = ctx.get("results_df")
    risk_badge = ctx["risk_badge"]
    RISK_COLORS = ctx["RISK_COLORS"]

    st.markdown("""
    <div style="margin-bottom:1rem;">
        <div style="font-size:1.3rem;font-weight:700;color:#60a5fa;">Alert Center</div>
        <div style="font-size:0.75rem;color:#64748b;letter-spacing:0.1em;text-transform:uppercase;">
            Active alerts sorted by priority — all values calculated from pipeline
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df is None:
        st.warning("No predictions available. Run the pipeline first.")
        return

    sorted_df = df.sort_values("priority_score", ascending=False)

    # ── Alert summary KPIs ───────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    for col, level in zip([k1, k2, k3, k4], ["CRITICAL", "HIGH", "MEDIUM", "LOW"]):
        cnt = int((sorted_df["risk_level"] == level).sum())
        icon = _ALERT_ICONS[level]
        color = RISK_COLORS[level]
        col.markdown(f"""
        <div class="gg-kpi-card">
            <div class="gg-kpi-label">{icon} {level}</div>
            <div class="gg-kpi-value" style="color:{color};">{cnt}</div>
            <div class="gg-kpi-sub">alerts</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filters ──────────────────────────────────────────────────────────
    af1, af2 = st.columns([2, 1])
    with af1:
        level_filter = st.multiselect(
            "Alert Levels",
            ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            default=["CRITICAL", "HIGH", "MEDIUM"],
        )
    with af2:
        type_filter = st.multiselect(
            "Equipment Type",
            sorted(sorted_df["type"].unique()),
            default=sorted(sorted_df["type"].unique()),
        )

    fdf = sorted_df[
        sorted_df["risk_level"].isin(level_filter) &
        sorted_df["type"].isin(type_filter)
    ]

    if fdf.empty:
        st.info("No alerts match the selected filters.")
        return

    st.markdown(
        f'<div class="gg-section-title">ACTIVE ALERTS ({len(fdf)} TOTAL)</div>',
        unsafe_allow_html=True,
    )

    # ── Alert cards ──────────────────────────────────────────────────────
    for _, row in fdf.iterrows():
        rl = str(row["risk_level"])
        fp_pct = round(float(row["failure_probability"]) * 100, 1)
        ps = round(float(row["priority_score"]), 1)
        color = RISK_COLORS.get(rl, "#60a5fa")
        icon = _ALERT_ICONS.get(rl, "⚪")
        reasons = explain_equipment(row)
        top_reasons = reasons[:3]  # show top 3 in alert

        dist = row.get("crew_distance_km")
        import pandas as _pd
        dist_str = f"{float(dist):.1f} km" if _pd.notna(dist) else "-"
        crew = str(row.get("assigned_crew", "-"))

        action_colors = {
            "Immediate Inspection": "#ef4444",
            "Preventive Maintenance": "#f97316",
            "Monitor": "#eab308",
            "Normal Maintenance": "#10b981",
        }
        action_color = action_colors.get(str(row["maintenance_action"]), "#60a5fa")

        reasons_html = "".join(
            f'<span style="font-size:0.75rem;color:#94a3b8;">'
            f'&#10003; {r}</span><br>' for r in top_reasons
        )

        st.markdown(f"""
        <div class="gg-card" style="border-left:3px solid {color};">
            <div style="display:flex;justify-content:space-between;
                        align-items:flex-start;gap:1rem;flex-wrap:wrap;">
                <!-- Left: ID + type + badge -->
                <div style="min-width:130px;">
                    <div style="font-size:0.95rem;font-weight:700;color:#e2e8f0;">
                        {icon} {row['equipment_id']}</div>
                    <div style="font-size:0.72rem;color:#94a3b8;text-transform:uppercase;
                                letter-spacing:0.08em;">{row['type']}</div>
                    <div style="margin-top:0.4rem;">{risk_badge(rl)}</div>
                </div>
                <!-- Metrics -->
                <div style="display:flex;gap:1.2rem;flex-wrap:wrap;">
                    <div class="gg-card-metric">
                        <span class="gg-card-metric-val">{fp_pct}%</span>
                        <span class="gg-card-metric-lbl">Fail Prob</span>
                    </div>
                    <div class="gg-card-metric">
                        <span class="gg-card-metric-val">{round(float(row['weather_risk']),1)}</span>
                        <span class="gg-card-metric-lbl">Wx Risk</span>
                    </div>
                    <div class="gg-card-metric">
                        <span class="gg-card-metric-val">{round(float(row['grid_impact']),1)}</span>
                        <span class="gg-card-metric-lbl">Grid Imp</span>
                    </div>
                    <div class="gg-card-metric">
                        <span class="gg-card-metric-val" style="color:{color};">{ps}</span>
                        <span class="gg-card-metric-lbl">Priority</span>
                    </div>
                </div>
                <!-- Reasons -->
                <div style="min-width:180px;flex:1;">
                    <div style="font-size:0.68rem;color:#64748b;text-transform:uppercase;
                                letter-spacing:0.08em;margin-bottom:0.3rem;">Risk Factors</div>
                    {reasons_html}
                </div>
                <!-- Action + Crew -->
                <div style="min-width:160px;">
                    <div style="font-size:0.68rem;color:#64748b;text-transform:uppercase;
                                letter-spacing:0.08em;">Recommended Action</div>
                    <div style="font-size:0.82rem;font-weight:600;
                                color:{action_color};margin:0.2rem 0;">
                        {row['maintenance_action']}</div>
                    <div style="font-size:0.68rem;color:#64748b;margin-top:0.4rem;">Crew</div>
                    <div style="font-size:0.78rem;color:#34d399;">{crew} ({dist_str})</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Download button ──────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    csv_data = fdf[["equipment_id","type","risk_level","failure_probability",
                     "weather_risk","grid_impact","priority_score",
                     "maintenance_action","assigned_crew","crew_distance_km"]].to_csv(index=False)
    st.download_button(
        label="Download Alerts as CSV",
        data=csv_data,
        file_name="gridguard_alerts.csv",
        mime="text/csv",
    )
