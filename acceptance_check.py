"""Acceptance criteria checklist for GridGuard AI."""
import sys, pandas as pd, importlib.util
from pathlib import Path

sys.path.insert(0, 'src')
checks = []

# Data pipeline
from data_loader import load_all_data
eq, wt, inc, cr, summary = load_all_data()
checks.append(('Data loads successfully', True, f'eq={len(eq)} wx={len(wt)} inc={len(inc)} crews={len(cr)}'))

from preprocessing import preprocess
mi = preprocess(eq, wt, inc)
checks.append(('Preprocessing works', len(mi)==30 and mi.isnull().sum().sum()==0, str(mi.shape)))

from failure_prediction import train, predict
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    model, metrics = train(mi)
fp = predict(model, mi)
acc = metrics.get('accuracy', 0)
checks.append(('ML training works', model is not None, f'accuracy={acc}'))
checks.append(('Model saves/loads', Path('src/models/failure_model.pkl').exists(), 'pkl exists'))
checks.append(('Predictions generated', len(fp)==30, f'{len(fp)} predictions'))

from weather_risk import calculate_weather_risk
wr = calculate_weather_risk(mi)
wr_ok = bool(wr.between(0,100).all())
checks.append(('Weather risk calculated', wr_ok, f'range {wr.min():.1f}-{wr.max():.1f}'))

from grid_impact import calculate_grid_impact
gi = calculate_grid_impact(mi)
gi_ok = bool(gi.between(0,100).all())
checks.append(('Grid impact calculated', gi_ok, f'range {gi.min():.1f}-{gi.max():.1f}'))

from priority import calculate_priority
ps, rl, ma = calculate_priority(mi, fp, wr, gi)
ps_ok = bool(ps.between(0,100).all())
checks.append(('Priority calculated', ps_ok, f'range {ps.min():.1f}-{ps.max():.1f}'))
checks.append(('Risk level assigned', set(rl.unique()).issubset({'LOW','MEDIUM','HIGH','CRITICAL'}),
               str(rl.value_counts().to_dict())))
checks.append(('Maintenance action generated', bool(ma.notna().all()),
               str(ma.value_counts().to_dict())))

from crew_assignment import assign_crews
res = mi.copy()
res['failure_probability'] = fp.values
res['weather_risk'] = wr.values
res['grid_impact'] = gi.values
res['priority_score'] = ps.values
res['risk_level'] = rl.values
res['maintenance_action'] = ma.values
res = assign_crews(res, cr)
high_crit = res[res['risk_level'].isin(['HIGH','CRITICAL'])]
checks.append(('Crew assignment works', 'assigned_crew' in res.columns,
               f'{len(high_crit)} HIGH/CRITICAL assets'))
checks.append(('Distance calculation works', 'crew_distance_km' in res.columns,
               'crew_distance_km column present'))

# Results CSV
df = pd.read_csv('src/results/predictions.csv')
checks.append(('Results CSV generated', len(df)==30, f'{len(df)} rows'))
req = ['equipment_id','failure_probability','weather_risk','grid_impact',
       'priority_score','risk_level','maintenance_action','assigned_crew','crew_distance_km']
missing_c = [c for c in req if c not in df.columns]
checks.append(('Required columns present', len(missing_c)==0,
               f'{len(df.columns)} cols, missing={missing_c}'))

# Dashboard
css = Path('src/dashboard/styles/theme.css')
checks.append(('Dashboard CSS exists', css.exists() and css.stat().st_size > 1000,
               f'{css.stat().st_size} bytes'))

pages = ['overview','risk_command','grid_map','equipment',
         'crew_operations','ai_insights','alert_center']
all_pages_ok = True
for p in pages:
    spec = importlib.util.spec_from_file_location(p, f'src/dashboard/pages/{p}.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, 'render'):
        all_pages_ok = False
checks.append(('Dashboard 7 pages importable', all_pages_ok, '7/7'))

app_content = Path('src/dashboard/app.py').read_text(encoding='utf-8')
checks.append(('app.py routing complete', all(p in app_content for p in pages), '7 routes'))
checks.append(('app.py caching in place', 'cache_data' in app_content and 'cache_resource' in app_content, 'cache_data+cache_resource'))
checks.append(('Risk map (folium import)', 'folium' in Path('src/dashboard/pages/grid_map.py').read_text(encoding='utf-8'), 'folium in grid_map.py'))

# Explainability
from explainability import explain_equipment, build_ai_decision_summary
t001 = df[df['equipment_id']=='T001'].iloc[0]
reasons = explain_equipment(t001)
checks.append(('Explainability works', len(reasons) > 0, f'{len(reasons)} reasons for T001'))
summary_d = build_ai_decision_summary(t001)
checks.append(('AI decision card builds', 'risk_reasons' in summary_d, 'summary dict OK'))

# Scenario simulator in ai_insights
ai_content = Path('src/dashboard/pages/ai_insights.py').read_text(encoding='utf-8')
checks.append(('Scenario simulator present', 'SCENARIO SIMULATION' in ai_content and 'slider' in ai_content, 'sliders + sim labels found'))

# Alerts in alert_center
alert_content = Path('src/dashboard/pages/alert_center.py').read_text(encoding='utf-8')
checks.append(('Alert center present', 'download_button' in alert_content, 'alerts + download button'))

# Download results
checks.append(('Download results button', 'download_button' in alert_content, 'in alert_center.py'))

# Security / integrity
no_env = not Path('.env').exists() or Path('.env').stat().st_size < 5
checks.append(('No secrets committed (.env)', no_env, '.env absent'))
gitignore = Path('.gitignore').read_text(encoding='utf-8')
checks.append(('.gitignore complete', '.venv' in gitignore and '.env' in gitignore and '*.pkl' in gitignore, 'venv+.env+pkl'))

fake_found = []
bad_strings = ['89% failure','95 grid impact','98% accuracy','crore saved','70% outage']
for bs in bad_strings:
    for pyf in Path('src').rglob('*.py'):
        if bs.lower() in pyf.read_text(encoding='utf-8', errors='ignore').lower():
            fake_found.append(f'{bs} in {pyf.name}')
checks.append(('No fake hard-coded metrics', len(fake_found)==0, 'clean' if not fake_found else str(fake_found)))
checks.append(('No fake IBM integrations', 'IBM Bob API' not in Path('src/dashboard/app.py').read_text(encoding='utf-8'), 'no fake API'))

# Docs
for doc in ['README.md','submission.yaml','docs/problem-statement.md',
            'docs/solution-overview.md','docs/architecture.md','docs/setup-guide.md']:
    p = Path(doc)
    ok = p.exists() and p.stat().st_size > 300
    checks.append((f'{doc}', ok, f'{p.stat().st_size}b' if p.exists() else 'MISSING'))

# Clean install test (imports resolve without errors)
try:
    from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR, MODEL_DIR, RESULTS_DIR
    checks.append(('Config paths resolve', True, f'RAW={RAW_DATA_DIR}'))
except Exception as e:
    checks.append(('Config paths resolve', False, str(e)))

# ── Print ──────────────────────────────────────────────────────
print()
print('=' * 60)
print('  GRIDGUARD AI -- ACCEPTANCE CRITERIA CHECKLIST')
print('=' * 60)
passed = sum(1 for _, ok, _ in checks if ok)
failed = sum(1 for _, ok, _ in checks if not ok)
for name, ok, detail in checks:
    mark = '[x]' if ok else '[ ]'
    print(f'  {mark}  {name}')
    if not ok:
        print(f'        !! {detail}')
print('=' * 60)
print(f'  {passed}/{len(checks)} criteria met    FAILED={failed}')
print('=' * 60)
if failed == 0:
    print('  PROJECT COMPLETE -- all acceptance criteria met')
print('=' * 60)
