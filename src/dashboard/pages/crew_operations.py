"""
pages/crew_operations.py — Crew Operations Management
KPIs, crew cards, assignment table sorted by priority.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def render(ctx: dict) -> None:
    df: pd.DataFrame = ctx.get("results_df")
    raw = ctx.get("raw_data")
    risk_badge = ctx["risk_badge"]
    RISK_COLORS = ctx["RISK_COLORS"]

    st.markdown("""
    <div style="margin-bottom:1rem;">
        <div style="font-size:1.3rem;font-weight:700;color:#60a5fa;">Crew Operations</div>
        <div style="font-size:0.75rem;color:#64748b;letter-spacing:0.1em;text-transform:uppercase;">
            Crew status, skill coverage & field assignments
        </div>
    </div>
    """, unsafe_allow_html=True)

    crews_df = raw["crews"].copy() if (raw and raw.get("crews") is not None) else pd.DataFrame()

    if crews_df.empty:
        st.warning("Crew data unavailable.")
        return

    # ── Crew KPIs ─────────────────────────────────────────────────────
    total_c   = len(crews_df)
    avail_c   = int((crews_df["status"] == "available").sum())
    busy_c    = int((crews_df["status"] == "busy").sum())
    assigned_c = 0
    if df is not None:
        assigned_ids = df.loc[
            ~df["assigned_crew"].isin(["N/A - below threshold", "No suitable crew available", "N/A"]),
            "assigned_crew"
        ].unique().tolist()
        assigned_c = len(assigned_ids)

    st.markdown('<div class="gg-section-title">CREW STATUS OVERVIEW</div>',
                unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    for col, label, val, color in [
        (k1, "Total Crews",    total_c,    "#60a5fa"),
        (k2, "Available",      avail_c,    "#10b981"),
        (k3, "Busy",           busy_c,     "#94a3b8"),
        (k4, "Assigned",       assigned_c, "#f97316"),
    ]:
        col.markdown(f"""
        <div class="gg-kpi-card">
            <div class="gg-kpi-label">{label}</div>
            <div class="gg-kpi-value" style="color:{color};">{val}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([1, 1])

    # ── Crew cards ─────────────────────────────────────────────────────
    with cl:
        st.markdown('<div class="gg-section-title">CREW ROSTER</div>',
                    unsafe_allow_html=True)
        for _, crew in crews_df.iterrows():
            status = str(crew.get("status", "available")).lower()
            sc = "#10b981" if status == "available" else "#64748b"
            crew_id = crew["crew_id"]

            # find assignment
            assigned_eq = "—"
            assigned_priority = "—"
            if df is not None:
                matches = df[df["assigned_crew"] == crew_id]
                if not matches.empty:
                    top_eq = matches.sort_values("priority_score", ascending=False).iloc[0]
                    assigned_eq = top_eq["equipment_id"]
                    assigned_priority = str(round(float(top_eq["priority_score"]), 1))

            st.markdown(f"""
            <div class="gg-card" style="border-left:3px solid {sc};">
                <div class="gg-card-header">
                    <div>
                        <span class="gg-card-id">{crew_id}</span>
                        <span class="gg-card-type" style="margin-left:0.6rem;">
                            {str(crew.get('skill','')).upper()}</span>
                    </div>
                    <span class="gg-badge" style="
                        background:{'rgba(16,185,129,0.12)' if status=='available'
                                    else 'rgba(100,116,139,0.12)'};
                        border:1px solid {'rgba(16,185,129,0.3)' if status=='available'
                                          else 'rgba(100,116,139,0.3)'};
                        color:{sc};">
                        {status.upper()}
                    </span>
                </div>
                <div style="display:flex;gap:1.5rem;font-size:0.78rem;color:#94a3b8;">
                    <span>Capacity: <b style="color:#e2e8f0;">{crew.get('capacity','—')}</b></span>
                    <span>Assigned: <b style="color:#60a5fa;">{assigned_eq}</b></span>
                    <span>Priority: <b style="color:#f97316;">{assigned_priority}</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Skill distribution chart ────────────────────────────────────────
    with cr:
        st.markdown('<div class="gg-section-title">SKILL DISTRIBUTION</div>',
                    unsafe_allow_html=True)
        skill_counts = crews_df["skill"].value_counts()
        fig_skills = go.Figure(go.Pie(
            labels=skill_counts.index.tolist(),
            values=skill_counts.values.tolist(),
            hole=0.45,
            marker=dict(
                colors=["#3b82f6", "#10b981", "#f97316", "#a78bfa"],
                line=dict(color="#0a1628", width=2),
            ),
            textfont=dict(color="#e2e8f0", size=12),
        ))
        fig_skills.update_layout(
            height=220, margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="#0a1628",
            legend=dict(font=dict(color="#94a3b8"), bgcolor="rgba(0,0,0,0)"),
            font_color="#e2e8f0",
        )
        st.plotly_chart(fig_skills, use_container_width=True)

        # Status bar
        st.markdown('<div class="gg-section-title">STATUS BREAKDOWN</div>',
                    unsafe_allow_html=True)
        status_counts = crews_df["status"].value_counts()
        for s, cnt in status_counts.items():
            sc = "#10b981" if s == "available" else "#64748b"
            pct = round(cnt / total_c * 100)
            st.markdown(f"""
            <div style="margin:0.5rem 0;">
                <div style="display:flex;justify-content:space-between;
                            font-size:0.75rem;color:#94a3b8;margin-bottom:0.2rem;">
                    <span>{str(s).upper()}</span>
                    <span style="color:{sc};font-weight:600;">{cnt} ({pct}%)</span>
                </div>
                <div class="gg-progress-bar-bg">
                    <div class="gg-progress-bar-fill"
                         style="width:{pct}%;background:{sc};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Assignment table ────────────────────────────────────────────────
    if df is not None:
        st.markdown('<div class="gg-section-title">ACTIVE CREW ASSIGNMENTS</div>',
                    unsafe_allow_html=True)

        assigned_df = df[
            ~df["assigned_crew"].isin(
                ["N/A - below threshold", "No suitable crew available", "N/A"]
            )
        ].copy()

        if assigned_df.empty:
            st.info("No active crew assignments.")
        else:
            assigned_df = assigned_df.sort_values("priority_score", ascending=False)

            for _, row in assigned_df.iterrows():
                rl = str(row["risk_level"])
                crew = str(row["assigned_crew"])
                dist = row.get("crew_distance_km")
                import pandas as _pd
                dist_str = f"{float(dist):.1f} km" if _pd.notna(dist) else "-"

                # Get crew skill
                crew_skill = "—"
                if not crews_df.empty and crew in crews_df["crew_id"].values:
                    crew_skill = crews_df[crews_df["crew_id"] == crew]["skill"].values[0]

                st.markdown(f"""
                <div class="gg-card" style="border-left:3px solid
                    {RISK_COLORS.get(rl,'#60a5fa')};">
                    <div style="display:flex;align-items:center;
                                gap:1.5rem;flex-wrap:wrap;">
                        <div style="min-width:80px;">
                            <div class="gg-card-id">{row['equipment_id']}</div>
                            <div class="gg-card-type">{row['type']}</div>
                        </div>
                        <div>{risk_badge(rl)}</div>
                        <div class="gg-card-metric">
                            <span class="gg-card-metric-val" style="color:#f97316;">
                                {round(float(row['priority_score']),1)}</span>
                            <span class="gg-card-metric-lbl">Priority</span>
                        </div>
                        <div class="gg-card-metric">
                            <span class="gg-card-metric-val" style="color:#34d399;">{crew}</span>
                            <span class="gg-card-metric-lbl">Crew</span>
                        </div>
                        <div class="gg-card-metric">
                            <span class="gg-card-metric-val">{crew_skill}</span>
                            <span class="gg-card-metric-lbl">Skill</span>
                        </div>
                        <div class="gg-card-metric">
                            <span class="gg-card-metric-val">{dist_str}</span>
                            <span class="gg-card-metric-lbl">Distance</span>
                        </div>
                        <div style="flex:1;font-size:0.78rem;color:#93c5fd;">
                            {row['maintenance_action']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
