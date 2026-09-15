"""
pages/risk_command.py — Risk Command Center
Charts: priority bar, failure dist, weather risk, risk matrix scatter.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def render(ctx: dict) -> None:
    df: pd.DataFrame = ctx.get("results_df")
    RISK_COLORS = ctx["RISK_COLORS"]
    risk_badge = ctx["risk_badge"]

    st.markdown("""
    <div style="margin-bottom:1.2rem;">
        <div style="font-size:1.3rem;font-weight:700;color:#60a5fa;">
            📊 Risk Command Center
        </div>
        <div style="font-size:0.75rem;color:#64748b;letter-spacing:0.1em;text-transform:uppercase;">
            Interactive risk analysis across all grid assets
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df is None:
        st.warning("No predictions available. Run the pipeline first.")
        return

    # ── Filters row ─────────────────────────────────────────────────────
    fc1, fc2 = st.columns([1, 1])
    with fc1:
        type_filter = st.multiselect(
            "Filter by Equipment Type",
            options=sorted(df["type"].unique()),
            default=sorted(df["type"].unique()),
        )
    with fc2:
        risk_filter = st.multiselect(
            "Filter by Risk Level",
            options=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            default=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        )

    fdf = df[df["type"].isin(type_filter) & df["risk_level"].isin(risk_filter)]

    if fdf.empty:
        st.info("No equipment matches the selected filters.")
        return

    # ── Row 1: Priority bar + Failure dist ──────────────────────────────
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="gg-section-title">PRIORITY SCORE BY EQUIPMENT</div>',
                    unsafe_allow_html=True)
        sorted_df = fdf.sort_values("priority_score", ascending=False)
        fig_bar = go.Figure(go.Bar(
            x=sorted_df["equipment_id"].tolist(),
            y=sorted_df["priority_score"].tolist(),
            marker_color=[RISK_COLORS.get(r, "#60a5fa") for r in sorted_df["risk_level"]],
            marker_line_width=0,
            hovertemplate=(
                "<b>%{x}</b><br>Priority: %{y:.1f}<extra></extra>"
            ),
        ))
        fig_bar.update_layout(
            height=280, margin=dict(l=10, r=10, t=10, b=60),
            paper_bgcolor="#0a1628", plot_bgcolor="#0a1628",
            xaxis=dict(tickangle=-45, tickfont=dict(color="#94a3b8", size=9)),
            yaxis=dict(gridcolor="#1e3a5f", tickfont=dict(color="#64748b"), range=[0, 105]),
            font_color="#e2e8f0",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.markdown('<div class="gg-section-title">FAILURE PROBABILITY DISTRIBUTION</div>',
                    unsafe_allow_html=True)
        fig_hist = go.Figure(go.Histogram(
            x=(fdf["failure_probability"] * 100).tolist(),
            nbinsx=15,
            marker_color="#3b82f6",
            marker_line_color="#1d4ed8",
            marker_line_width=1,
            opacity=0.85,
        ))
        fig_hist.update_layout(
            height=280, margin=dict(l=10, r=10, t=10, b=30),
            paper_bgcolor="#0a1628", plot_bgcolor="#0a1628",
            xaxis=dict(title="Failure Probability (%)", tickfont=dict(color="#94a3b8"),
                       titlefont=dict(color="#64748b")),
            yaxis=dict(title="Count", gridcolor="#1e3a5f", tickfont=dict(color="#64748b"),
                       titlefont=dict(color="#64748b")),
            font_color="#e2e8f0",
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # ── Row 2: Weather risk + Grid impact bars ──────────────────────────
    c3, c4 = st.columns(2)

    with c3:
        st.markdown('<div class="gg-section-title">WEATHER RISK BY EQUIPMENT</div>',
                    unsafe_allow_html=True)
        wr_sorted = fdf.sort_values("weather_risk", ascending=False)
        fig_wr = go.Figure(go.Bar(
            x=wr_sorted["equipment_id"].tolist(),
            y=wr_sorted["weather_risk"].tolist(),
            marker_color="#38bdf8",
            marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>Weather Risk: %{y:.1f}<extra></extra>",
        ))
        fig_wr.update_layout(
            height=240, margin=dict(l=10, r=10, t=10, b=60),
            paper_bgcolor="#0a1628", plot_bgcolor="#0a1628",
            xaxis=dict(tickangle=-45, tickfont=dict(color="#94a3b8", size=9)),
            yaxis=dict(gridcolor="#1e3a5f", tickfont=dict(color="#64748b"), range=[0, 110]),
            font_color="#e2e8f0",
        )
        st.plotly_chart(fig_wr, use_container_width=True)

    with c4:
        st.markdown('<div class="gg-section-title">GRID IMPACT BY EQUIPMENT</div>',
                    unsafe_allow_html=True)
        gi_sorted = fdf.sort_values("grid_impact", ascending=False)
        fig_gi = go.Figure(go.Bar(
            x=gi_sorted["equipment_id"].tolist(),
            y=gi_sorted["grid_impact"].tolist(),
            marker_color="#f97316",
            marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>Grid Impact: %{y:.1f}<extra></extra>",
        ))
        fig_gi.update_layout(
            height=240, margin=dict(l=10, r=10, t=10, b=60),
            paper_bgcolor="#0a1628", plot_bgcolor="#0a1628",
            xaxis=dict(tickangle=-45, tickfont=dict(color="#94a3b8", size=9)),
            yaxis=dict(gridcolor="#1e3a5f", tickfont=dict(color="#64748b"), range=[0, 110]),
            font_color="#e2e8f0",
        )
        st.plotly_chart(fig_gi, use_container_width=True)

    # ── Risk Matrix ─────────────────────────────────────────────────────
    st.markdown('<div class="gg-section-title">RISK MATRIX — Failure Probability vs Grid Impact</div>',
                unsafe_allow_html=True)

    plot_df = fdf.copy()
    plot_df["fp_pct"]  = (plot_df["failure_probability"] * 100).round(1)
    plot_df["bubble"]  = plot_df["weather_risk"].clip(5, 100)
    plot_df["color"]   = plot_df["risk_level"].map(RISK_COLORS).fillna("#60a5fa")

    fig_matrix = go.Figure()
    for rl, grp in plot_df.groupby("risk_level"):
        fig_matrix.add_trace(go.Scatter(
            x=grp["fp_pct"].tolist(),
            y=grp["grid_impact"].tolist(),
            mode="markers+text",
            name=rl,
            marker=dict(
                size=(grp["bubble"] / 4).clip(8, 30).tolist(),
                color=RISK_COLORS.get(rl, "#60a5fa"),
                opacity=0.80,
                line=dict(width=1, color="rgba(255,255,255,0.2)"),
            ),
            text=grp["equipment_id"].tolist(),
            textposition="top center",
            textfont=dict(size=9, color="#94a3b8"),
            customdata=list(zip(
                grp["equipment_id"], grp["fp_pct"],
                grp["weather_risk"].round(1), grp["grid_impact"].round(1),
                grp["priority_score"].round(1),
            )),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Failure Prob: %{customdata[1]}%<br>"
                "Weather Risk: %{customdata[2]}<br>"
                "Grid Impact: %{customdata[3]}<br>"
                "Priority: %{customdata[4]}"
                "<extra></extra>"
            ),
        ))

    fig_matrix.update_layout(
        height=420, margin=dict(l=40, r=20, t=20, b=40),
        paper_bgcolor="#0a1628", plot_bgcolor="#0d1f3c",
        xaxis=dict(
            title="Failure Probability (%)",
            gridcolor="#1e3a5f", tickfont=dict(color="#94a3b8"),
            titlefont=dict(color="#64748b"), range=[-5, 105],
        ),
        yaxis=dict(
            title="Grid Impact (0-100)",
            gridcolor="#1e3a5f", tickfont=dict(color="#94a3b8"),
            titlefont=dict(color="#64748b"), range=[-5, 105],
        ),
        legend=dict(
            font=dict(color="#94a3b8"),
            bgcolor="rgba(13,31,60,0.8)",
            bordercolor="#1e3a5f",
        ),
        font_color="#e2e8f0",
    )
    st.plotly_chart(fig_matrix, use_container_width=True)
    st.caption("Bubble size = Weather Risk  |  Color = Risk Level")

    # ── Summary table ───────────────────────────────────────────────────
    st.markdown('<div class="gg-section-title">FULL RISK TABLE</div>', unsafe_allow_html=True)
    display_cols = ["equipment_id", "type", "failure_probability",
                    "weather_risk", "grid_impact", "priority_score",
                    "risk_level", "maintenance_action", "assigned_crew", "crew_distance_km"]
    tbl = fdf[display_cols].sort_values("priority_score", ascending=False).copy()
    tbl["failure_probability"] = (tbl["failure_probability"] * 100).round(1).astype(str) + "%"
    tbl.columns = ["ID", "Type", "Fail Prob", "Weather Risk",
                   "Grid Impact", "Priority", "Risk", "Action", "Crew", "Dist (km)"]
    st.dataframe(tbl, use_container_width=True, hide_index=True)
