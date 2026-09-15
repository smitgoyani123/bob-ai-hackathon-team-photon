"""
pages/grid_map.py — Live Grid Map with Folium
Equipment markers (color by risk) + crew markers + click popups.
"""
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium


_RISK_FOLIUM = {
    "CRITICAL": "red",
    "HIGH":     "orange",
    "MEDIUM":   "beige",
    "LOW":      "green",
}

_CREW_ICON_COLOR = {
    "available": "blue",
    "busy":      "gray",
}


def _eq_popup(row) -> str:
    import pandas as _pd
    fp = round(float(row["failure_probability"]) * 100, 1)
    dist = row.get("crew_distance_km")
    dist_str = f"{float(dist):.1f} km" if _pd.notna(dist) else "-"
    return f"""
    <div style="font-family:sans-serif;min-width:200px;">
        <b style="font-size:14px;">{row['equipment_id']}</b>
        <span style="color:#888;margin-left:6px;font-size:11px;">{row['type']}</span>
        <hr style="margin:6px 0;border-color:#ddd;">
        <table style="font-size:12px;width:100%;">
            <tr><td style="color:#555;">Failure Prob</td>
                <td style="font-weight:600;">{fp}%</td></tr>
            <tr><td style="color:#555;">Weather Risk</td>
                <td>{round(float(row['weather_risk']),1)}</td></tr>
            <tr><td style="color:#555;">Grid Impact</td>
                <td>{round(float(row['grid_impact']),1)}</td></tr>
            <tr><td style="color:#555;">Priority</td>
                <td style="font-weight:600;color:#f97316;">
                    {round(float(row['priority_score']),1)}</td></tr>
            <tr><td style="color:#555;">Risk</td>
                <td><b>{row['risk_level']}</b></td></tr>
            <tr><td style="color:#555;">Action</td>
                <td style="color:#3b82f6;">{row['maintenance_action']}</td></tr>
            <tr><td style="color:#555;">Crew</td>
                <td style="color:#10b981;">{row.get('assigned_crew','N/A')} ({dist_str})</td></tr>
        </table>
    </div>
    """


def _crew_popup(row) -> str:
    return f"""
    <div style="font-family:sans-serif;min-width:160px;">
        <b style="font-size:13px;">{row['crew_id']}</b>
        <hr style="margin:6px 0;border-color:#ddd;">
        <table style="font-size:12px;">
            <tr><td style="color:#555;">Status</td>
                <td><b style="color:{'#10b981' if row['status']=='available' else '#94a3b8'};">
                    {str(row['status']).upper()}</b></td></tr>
            <tr><td style="color:#555;">Skill</td><td>{row['skill']}</td></tr>
            <tr><td style="color:#555;">Capacity</td><td>{row['capacity']}</td></tr>
        </table>
    </div>
    """


def render(ctx: dict) -> None:
    df: pd.DataFrame = ctx.get("results_df")
    raw = ctx.get("raw_data")
    RISK_COLORS = ctx["RISK_COLORS"]
    risk_badge = ctx["risk_badge"]

    st.markdown("""
    <div style="margin-bottom:1rem;">
        <div style="font-size:1.3rem;font-weight:700;color:#60a5fa;">Live Grid Map</div>
        <div style="font-size:0.75rem;color:#64748b;letter-spacing:0.1em;text-transform:uppercase;">
            Equipment & crew positions — color coded by risk level
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df is None:
        st.warning("No predictions available. Run the pipeline first.")
        return

    crews_df = raw["crews"] if raw else pd.DataFrame()

    # ── Map controls ────────────────────────────────────────────────────
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        show_crews = st.checkbox("Show Crews", value=True)
    with mc2:
        risk_filter = st.multiselect(
            "Show Risk Levels",
            ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            default=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        )
    with mc3:
        type_filter = st.multiselect(
            "Equipment Type",
            sorted(df["type"].unique()),
            default=sorted(df["type"].unique()),
        )

    fdf = df[df["risk_level"].isin(risk_filter) & df["type"].isin(type_filter)]

    # ── Build map ───────────────────────────────────────────────────────
    center_lat = float(df["latitude"].mean())
    center_lon = float(df["longitude"].mean())

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles="CartoDB dark_matter",
    )

    # Equipment markers
    for _, row in fdf.iterrows():
        rl = str(row["risk_level"]).upper()
        icon_color = _RISK_FOLIUM.get(rl, "blue")
        folium.Marker(
            location=[float(row["latitude"]), float(row["longitude"])],
            popup=folium.Popup(_eq_popup(row), max_width=280),
            tooltip=f"{row['equipment_id']} — {rl}",
            icon=folium.Icon(
                color=icon_color,
                icon="bolt",
                prefix="fa",
            ),
        ).add_to(m)

    # Crew markers
    if show_crews and not crews_df.empty:
        for _, crew in crews_df.iterrows():
            try:
                clat = float(crew["latitude"])
                clon = float(crew["longitude"])
            except (TypeError, ValueError):
                continue
            status = str(crew.get("status", "available")).lower()
            icon_color = _CREW_ICON_COLOR.get(status, "gray")
            folium.Marker(
                location=[clat, clon],
                popup=folium.Popup(_crew_popup(crew), max_width=220),
                tooltip=f"{crew['crew_id']} — {str(crew['skill']).upper()}",
                icon=folium.Icon(color=icon_color, icon="users", prefix="fa"),
            ).add_to(m)

    # ── Legend ──────────────────────────────────────────────────────────
    legend_html = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
                background:rgba(13,31,60,0.92);border:1px solid #1e3a5f;
                border-radius:8px;padding:10px 14px;font-family:sans-serif;">
        <div style="font-size:11px;font-weight:700;color:#60a5fa;
                    margin-bottom:6px;letter-spacing:0.1em;">RISK LEVEL</div>
        <div style="font-size:11px;color:#e2e8f0;margin:3px 0;">
            <span style="color:#ef4444;">&#9679;</span> CRITICAL</div>
        <div style="font-size:11px;color:#e2e8f0;margin:3px 0;">
            <span style="color:#f97316;">&#9679;</span> HIGH</div>
        <div style="font-size:11px;color:#e2e8f0;margin:3px 0;">
            <span style="color:#eab308;">&#9679;</span> MEDIUM</div>
        <div style="font-size:11px;color:#e2e8f0;margin:3px 0;">
            <span style="color:#10b981;">&#9679;</span> LOW</div>
        <div style="font-size:11px;color:#e2e8f0;margin:6px 0 3px 0;">
            <span style="color:#3b82f6;">&#9679;</span> CREW (available)</div>
        <div style="font-size:11px;color:#e2e8f0;margin:3px 0;">
            <span style="color:#64748b;">&#9679;</span> CREW (busy)</div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # ── Render map ──────────────────────────────────────────────────────
    st_folium(m, width="100%", height=520, returned_objects=[])

    # ── Stats below map ─────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    for col, label, val, color in [
        (s1, "Showing", f"{len(fdf)} assets", "#60a5fa"),
        (s2, "Critical", int((fdf["risk_level"]=="CRITICAL").sum()), "#ef4444"),
        (s3, "High",     int((fdf["risk_level"]=="HIGH").sum()),     "#f97316"),
        (s4, "Crews",    len(crews_df) if not crews_df.empty else 0, "#10b981"),
    ]:
        col.markdown(f"""
        <div class="gg-kpi-card" style="padding:0.6rem;">
            <div class="gg-kpi-label">{label}</div>
            <div class="gg-kpi-value" style="color:{color};font-size:1.5rem;">{val}</div>
        </div>
        """, unsafe_allow_html=True)
