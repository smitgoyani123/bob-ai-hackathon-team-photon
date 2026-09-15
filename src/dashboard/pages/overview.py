"""
pages/overview.py — GridGuard AI Command Center overview page.
Shows: header, KPI cards, grid health, critical attention required.
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def render(ctx: dict) -> None:
    df: pd.DataFrame = ctx.get("results_df")
    raw = ctx.get("raw_data")
    risk_badge = ctx["risk_badge"]
    risk_color = ctx["risk_color"]
    RISK_COLORS = ctx["RISK_COLORS"]

    # ── Header ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class="gg-header">
        <div>
            <div class="gg-header-title">⚡ GRIDGUARD AI</div>
            <div class="gg-header-sub">Grid Operations Intelligence Platform</div>
        </div>
        <div>
            <span class="gg-status-badge">
                <span class="gg-status-dot"></span> GRID OPERATIONAL
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df is None:
        st.warning("No predictions available. Run the pipeline first.")
        return

    # ── KPI metrics ─────────────────────────────────────────────────────
    total = len(df)
    critical = int((df["risk_level"] == "CRITICAL").sum())
    high     = int((df["risk_level"] == "HIGH").sum())
    medium   = int((df["risk_level"] == "MEDIUM").sum())
    avg_fp   = round(float(df["failure_probability"].mean()) * 100, 1)
    crews_df = raw["crews"] if raw else pd.DataFrame()
    avail_crews = int((crews_df["status"] == "available").sum()) if not crews_df.empty else 0

    st.markdown('<div class="gg-section-title">SYSTEM STATUS</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    def kpi(col, value, label, color="#60a5fa", sub="Current Scan"):
        col.markdown(f"""
        <div class="gg-kpi-card">
            <div class="gg-kpi-label">{label}</div>
            <div class="gg-kpi-value" style="color:{color};">{value}</div>
            <div class="gg-kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

    kpi(c1, total, "Total Equipment", "#60a5fa")
    kpi(c2, critical, "Critical", RISK_COLORS["CRITICAL"])
    kpi(c3, high, "High Risk", RISK_COLORS["HIGH"])
    kpi(c4, medium, "Medium Risk", RISK_COLORS["MEDIUM"])
    kpi(c5, f"{avg_fp}%", "Avg Failure Prob", "#a78bfa")
    kpi(c6, avail_crews, "Available Crews", "#10b981")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Grid Health + risk breakdown ────────────────────────────────────
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown('<div class="gg-section-title">GRID HEALTH</div>', unsafe_allow_html=True)

        avg_pr = float(df["priority_score"].mean())
        health_score = round(100 - avg_pr, 1)
        health_color = (
            "#ef4444" if health_score < 30 else
            "#f97316" if health_score < 50 else
            "#eab308" if health_score < 70 else
            "#10b981"
        )

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=health_score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Grid Health Score", "font": {"color": "#94a3b8", "size": 13}},
            number={"font": {"color": health_color, "size": 42}, "suffix": ""},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#334155",
                         "tickfont": {"color": "#64748b", "size": 10}},
                "bar": {"color": health_color},
                "bgcolor": "#0d1f3c",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 30],  "color": "rgba(239,68,68,0.1)"},
                    {"range": [30, 60], "color": "rgba(249,115,22,0.1)"},
                    {"range": [60, 80], "color": "rgba(234,179,8,0.1)"},
                    {"range": [80, 100],"color": "rgba(16,185,129,0.1)"},
                ],
            }
        ))
        fig_gauge.update_layout(
            height=220, margin=dict(l=20, r=20, t=40, b=10),
            paper_bgcolor="#0a1628", font_color="#e2e8f0",
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Sub-metrics
        avg_wr = round(float(df["weather_risk"].mean()), 1)
        avg_gi = round(float(df["grid_impact"].mean()), 1)
        for label, val, color in [
            ("Failure Risk", f"{avg_fp}%", "#a78bfa"),
            ("Weather Risk", avg_wr, "#60a5fa"),
            ("Grid Impact",  avg_gi, "#f97316"),
        ]:
            pct = val if isinstance(val, (int, float)) else avg_fp
            st.markdown(f"""
            <div style="margin:0.4rem 0;">
                <div style="display:flex;justify-content:space-between;
                            font-size:0.75rem;color:#94a3b8;margin-bottom:0.2rem;">
                    <span>{label}</span><span style="color:{color};font-weight:600;">{val}</span>
                </div>
                <div class="gg-progress-bar-bg">
                    <div class="gg-progress-bar-fill"
                         style="width:{min(float(str(pct).replace('%',''))  ,100)}%;
                                background:{color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="gg-section-title">RISK DISTRIBUTION</div>', unsafe_allow_html=True)

        risk_counts = df["risk_level"].value_counts().reindex(
            ["CRITICAL", "HIGH", "MEDIUM", "LOW"], fill_value=0
        )
        fig_risk = go.Figure(go.Bar(
            x=risk_counts.index.tolist(),
            y=risk_counts.values.tolist(),
            marker_color=[RISK_COLORS[r] for r in risk_counts.index],
            marker_line_width=0,
            text=risk_counts.values.tolist(),
            textposition="outside",
            textfont={"color": "#e2e8f0", "size": 13},
        ))
        fig_risk.update_layout(
            height=250, margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor="#0a1628", plot_bgcolor="#0a1628",
            font_color="#e2e8f0",
            xaxis=dict(tickfont=dict(color="#94a3b8")),
            yaxis=dict(gridcolor="#1e3a5f", tickfont=dict(color="#64748b")),
            showlegend=False,
        )
        st.plotly_chart(fig_risk, use_container_width=True)

        # Type breakdown
        type_counts = df["type"].value_counts()
        cols_t = st.columns(len(type_counts))
        for i, (etype, cnt) in enumerate(type_counts.items()):
            cols_t[i].markdown(f"""
            <div class="gg-kpi-card" style="padding:0.7rem;">
                <div class="gg-kpi-label">{etype}s</div>
                <div class="gg-kpi-value" style="font-size:1.5rem;color:#60a5fa;">{cnt}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Critical Attention Required ──────────────────────────────────
    st.markdown('<div class="gg-section-title">CRITICAL ATTENTION REQUIRED</div>',
                unsafe_allow_html=True)

    top_risk = df.sort_values("priority_score", ascending=False).head(5)

    for _, row in top_risk.iterrows():
        rl = str(row["risk_level"])
        fp_pct = round(float(row["failure_probability"]) * 100, 1)
        wr = round(float(row["weather_risk"]), 1)
        gi = round(float(row["grid_impact"]), 1)
        ps = round(float(row["priority_score"]), 1)
        crew = str(row.get("assigned_crew", "N/A"))
        dist = row.get("crew_distance_km")
        import pandas as _pd
        dist_str = f"{float(dist):.1f} km" if _pd.notna(dist) else "-"

        st.markdown(f"""
        <div class="gg-card">
            <div class="gg-card-header">
                <div>
                    <span class="gg-card-id">{row['equipment_id']}</span>
                    <span class="gg-card-type" style="margin-left:0.6rem;">{row['type']}</span>
                </div>
                {risk_badge(rl)}
            </div>
            <div style="display:flex;gap:1.5rem;flex-wrap:wrap;align-items:center;">
                <div class="gg-card-metric">
                    <span class="gg-card-metric-val">{fp_pct}%</span>
                    <span class="gg-card-metric-lbl">Failure Prob</span>
                </div>
                <div class="gg-card-metric">
                    <span class="gg-card-metric-val">{wr}</span>
                    <span class="gg-card-metric-lbl">Weather Risk</span>
                </div>
                <div class="gg-card-metric">
                    <span class="gg-card-metric-val">{gi}</span>
                    <span class="gg-card-metric-lbl">Grid Impact</span>
                </div>
                <div class="gg-card-metric">
                    <span class="gg-card-metric-val" style="color:#f97316;">{ps}</span>
                    <span class="gg-card-metric-lbl">Priority</span>
                </div>
                <div style="flex:1;min-width:140px;">
                    <div style="font-size:0.75rem;color:#94a3b8;">Action</div>
                    <div style="font-size:0.82rem;color:#93c5fd;font-weight:600;">
                        {row['maintenance_action']}</div>
                </div>
                <div style="min-width:100px;">
                    <div style="font-size:0.75rem;color:#94a3b8;">Crew</div>
                    <div style="font-size:0.82rem;color:#34d399;font-weight:600;">
                        {crew} &nbsp;{dist_str}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
