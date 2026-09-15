"""Pre-launch UI diagnostic — simulates what every dashboard page does."""
import sys, warnings
sys.path.insert(0, 'src')
warnings.filterwarnings('ignore')

errors = []

# ── Load pipeline outputs ─────────────────────────────────────
try:
    from pipeline import load_results
    df = load_results()
    print(f"results_df: {df.shape}  cols={len(df.columns)}")
except Exception as e:
    errors.append(f"load_results: {e}")
    df = None

try:
    from data_loader import load_all_data
    eq, wt, inc, cr, summary = load_all_data()
    print(f"raw data: eq={len(eq)} wt={len(wt)} inc={len(inc)} cr={len(cr)}")
except Exception as e:
    errors.append(f"load_all_data: {e}")
    eq = wt = inc = cr = None

try:
    from preprocessing import preprocess, get_feature_columns
    from failure_prediction import train
    from explainability import global_feature_importance
    mi = preprocess(eq, wt, inc)
    model, metrics = train(mi)
    fi = global_feature_importance(model, get_feature_columns(), top_n=10)
    print(f"model: n_estimators={model.n_estimators}  acc={metrics.get('accuracy')}")
except Exception as e:
    errors.append(f"model load: {e}")
    model = metrics = fi = None

# ── Column check ──────────────────────────────────────────────
print("\n=== Column presence check ===")
needed = [
    'equipment_id','type','age','health','load','temperature',
    'voltage','customers_served','critical_facility','latitude','longitude',
    'weather_rainfall','weather_wind','weather_temperature',
    'weather_storm','weather_flood_risk',
    'failure_probability','weather_risk','grid_impact',
    'priority_score','risk_level','maintenance_action',
    'assigned_crew','crew_distance_km'
]
if df is not None:
    for c in needed:
        status = "OK" if c in df.columns else "MISSING"
        if status == "MISSING":
            errors.append(f"Column missing from predictions.csv: {c}")
        print(f"  {status}  {c}")

# ── Overview page ─────────────────────────────────────────────
print("\n=== Overview page ===")
try:
    import pandas as pd
    total = len(df)
    critical = int((df['risk_level']=='CRITICAL').sum())
    high = int((df['risk_level']=='HIGH').sum())
    avg_fp = round(float(df['failure_probability'].mean())*100, 1)
    avail_crews = int((cr['status']=='available').sum())
    avg_pr = float(df['priority_score'].mean())
    health_score = round(100 - avg_pr, 1)
    print(f"  total={total} critical={critical} high={high} avg_fp={avg_fp}%")
    print(f"  health_score={health_score}  avail_crews={avail_crews}")
    # Top 5 sort
    top5 = df.sort_values('priority_score', ascending=False).head(5)
    print(f"  top asset: {top5.iloc[0]['equipment_id']}  priority={top5.iloc[0]['priority_score']}")
    # Progress bar float parse
    for label, val, color in [
        ("Failure Risk", f"{avg_fp}%", "#a78bfa"),
        ("Weather Risk", round(float(df['weather_risk'].mean()),1), "#60a5fa"),
        ("Grid Impact",  round(float(df['grid_impact'].mean()),1), "#f97316"),
    ]:
        pct = float(str(val).replace('%',''))
        _ = min(pct, 100)
    print("  progress bars OK")
except Exception as e:
    errors.append(f"overview page: {e}")
    import traceback; traceback.print_exc()

# ── Equipment page ────────────────────────────────────────────
print("\n=== Equipment page ===")
try:
    from explainability import build_ai_decision_summary, explain_equipment
    for eq_id in df.sort_values('priority_score', ascending=False)['equipment_id'].head(5):
        row = df[df['equipment_id']==eq_id].iloc[0]
        summary = build_ai_decision_summary(row)
        reasons = explain_equipment(row)
        # radar chart hex parse
        from priority import get_risk_level
        rc_map = {'CRITICAL':'#ef4444','HIGH':'#f97316','MEDIUM':'#eab308','LOW':'#10b981'}
        rc = rc_map.get(summary['risk_level'], '#60a5fa')
        r = int(rc[1:3], 16)
        g = int(rc[3:5], 16)
        b = int(rc[5:7], 16)
        # crew dist parse
        dist = summary.get('crew_distance_km')
        dist_str = f"{dist:.1f} km" if dist and str(dist) != 'nan' else "—"
        # action icon lookup
        action_icons = {
            "Immediate Inspection": "xx",
            "Preventive Maintenance": "xx",
            "Monitor": "xx",
            "Normal Maintenance": "xx",
        }
        _ = action_icons.get(summary['maintenance_action'], "xx")
    print(f"  {len(df)} assets processed OK")
except Exception as e:
    errors.append(f"equipment page: {e}")
    import traceback; traceback.print_exc()

# ── Crew operations page ──────────────────────────────────────
print("\n=== Crew operations page ===")
try:
    bad_crews = ['N/A \u2014 below threshold','No suitable crew available','N/A']
    assigned_df = df[~df['assigned_crew'].isin(bad_crews)]
    print(f"  assigned: {len(assigned_df)} rows")
    # Check the N/A em-dash variant in actual data
    sample_crews = df['assigned_crew'].unique()
    print(f"  unique crew values: {list(sample_crews)[:8]}")
except Exception as e:
    errors.append(f"crew_operations page: {e}")
    import traceback; traceback.print_exc()

# ── Alert center page ─────────────────────────────────────────
print("\n=== Alert center page ===")
try:
    from explainability import explain_equipment
    for _, row in df.head(3).iterrows():
        reasons = explain_equipment(row)
        top3 = reasons[:3]
        dist = row.get('crew_distance_km')
        dist_str = f"{dist:.1f} km" if dist and str(dist) != 'nan' else "—"
    print("  alert cards render OK")
except Exception as e:
    errors.append(f"alert_center page: {e}")
    import traceback; traceback.print_exc()

# ── AI insights / simulator ───────────────────────────────────
print("\n=== AI Insights / Simulator ===")
try:
    t001 = df[df['equipment_id']=='T001'].iloc[0]
    sim_cols = ['weather_wind','weather_rainfall','weather_temperature',
                'weather_storm','weather_flood_risk','load']
    for c in sim_cols:
        v = t001.get(c, None)
        if v is None:
            errors.append(f"Simulator missing col: {c}")
        print(f"  {c} = {v}")
    # Simulate the calc
    EPS = 1e-9
    rain_min = float(df['weather_rainfall'].min())
    rain_max = float(df['weather_rainfall'].max())
    wind_min = float(df['weather_wind'].min())
    wind_max = float(df['weather_wind'].max())
    sim_wind = int(t001.get('weather_wind', 30))
    sim_rain = int(t001.get('weather_rainfall', 20))
    sim_temp = int(t001.get('weather_temperature', 32))
    sim_load = int(t001.get('load', 50))
    def norm(v, lo, hi):
        return ((v - lo) / (hi - lo + EPS)) * 100 if hi > lo else 50.0
    sim_rain_r = norm(sim_rain, rain_min, rain_max)
    sim_wind_r = norm(sim_wind, wind_min, wind_max)
    sim_temp_r = max(0, (sim_temp - 35) / max(1, 45 - 35)) * 100
    sim_storm_r = float(t001.get('weather_storm', 0)) * 60 + float(t001.get('weather_flood_risk', 0)) * 40
    sim_wr = min(100, max(0, 0.40*sim_rain_r + 0.30*sim_wind_r + 0.20*sim_temp_r + 0.10*sim_storm_r))
    base_fp = float(t001['failure_probability'])
    base_gi = float(t001['grid_impact'])
    load_ratio = sim_load / max(1, float(t001.get('load', 50)))
    sim_gi = min(100, base_gi * load_ratio)
    sim_ps = min(100, max(0, 0.50*base_fp*100 + 0.20*sim_wr + 0.30*sim_gi))
    print(f"  sim_ps={round(sim_ps,1)}  sim_wr={round(sim_wr,1)}")
    print("  simulator calculation OK")
except Exception as e:
    errors.append(f"ai_insights/simulator: {e}")
    import traceback; traceback.print_exc()

# ── Risk command page ─────────────────────────────────────────
print("\n=== Risk command page ===")
try:
    import pandas as pd
    fdf = df.copy()
    fdf['fp_pct'] = (fdf['failure_probability'] * 100).round(1)
    fdf['bubble'] = fdf['weather_risk'].clip(5, 100)
    RISK_COLORS = {'CRITICAL':'#ef4444','HIGH':'#f97316','MEDIUM':'#eab308','LOW':'#10b981'}
    for rl, grp in fdf.groupby('risk_level'):
        sizes = (grp['bubble'] / 4).clip(8, 30).tolist()
        _ = [RISK_COLORS.get(rl, '#60a5fa')] * len(grp)
    print(f"  risk matrix: {len(fdf)} points OK")
except Exception as e:
    errors.append(f"risk_command page: {e}")
    import traceback; traceback.print_exc()

# ── Summary ───────────────────────────────────────────────────
print()
print('=' * 60)
print('  UI PRE-LAUNCH DIAGNOSTIC')
print('=' * 60)
if errors:
    print(f'  ERRORS FOUND: {len(errors)}')
    for i, err in enumerate(errors, 1):
        print(f'  [{i}] {err}')
else:
    print('  ALL CHECKS PASSED - dashboard ready to launch')
print('=' * 60)
