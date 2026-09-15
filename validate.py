"""Final validation script for GridGuard AI."""
import sys, importlib.util, traceback
from pathlib import Path
import pandas as pd

sys.path.insert(0, 'src')

results = []

# ── 1. predictions.csv columns ────────────────────────────────
df = pd.read_csv('src/results/predictions.csv')
required_cols = [
    'equipment_id','type','failure_probability','weather_risk',
    'grid_impact','priority_score','risk_level','maintenance_action',
    'assigned_crew','crew_distance_km'
]
missing = [c for c in required_cols if c not in df.columns]
results.append(('predictions.csv columns', len(missing)==0,
                f'missing: {missing}' if missing else f'{len(df)} rows x {len(df.columns)} cols'))

# ── 2. No nulls in key columns ────────────────────────────────
key_nulls = int(df[required_cols[:8]].isnull().sum().sum())
results.append(('No nulls in key cols', key_nulls==0, f'{key_nulls} nulls'))

# ── 3. Risk level values ──────────────────────────────────────
valid_risks = {'CRITICAL','HIGH','MEDIUM','LOW'}
bad_risks = set(df['risk_level'].unique()) - valid_risks
rl_dist = df['risk_level'].value_counts().to_dict()
results.append(('Risk level values valid', len(bad_risks)==0, str(rl_dist)))

# ── 4. failure_probability in 0-1 ────────────────────────────
fp_min = float(df['failure_probability'].min())
fp_max = float(df['failure_probability'].max())
fp_ok = fp_min >= 0 and fp_max <= 1
results.append(('failure_probability 0-1', fp_ok, f'range: {fp_min:.3f} - {fp_max:.3f}'))

# ── 5. priority_score in 0-100 ───────────────────────────────
ps_min = float(df['priority_score'].min())
ps_max = float(df['priority_score'].max())
ps_ok = ps_min >= 0 and ps_max <= 100
results.append(('priority_score 0-100', ps_ok, f'range: {ps_min:.1f} - {ps_max:.1f}'))

# ── 6. weather_risk in 0-100 ─────────────────────────────────
wr_min = float(df['weather_risk'].min())
wr_max = float(df['weather_risk'].max())
wr_ok = wr_min >= 0 and wr_max <= 100
results.append(('weather_risk 0-100', wr_ok, f'range: {wr_min:.1f} - {wr_max:.1f}'))

# ── 7. grid_impact in 0-100 ──────────────────────────────────
gi_min = float(df['grid_impact'].min())
gi_max = float(df['grid_impact'].max())
gi_ok = gi_min >= 0 and gi_max <= 100
results.append(('grid_impact 0-100', gi_ok, f'range: {gi_min:.1f} - {gi_max:.1f}'))

# ── 8. HIGH/CRITICAL all assigned ────────────────────────────
high_crit = df[df['risk_level'].isin(['HIGH','CRITICAL'])]
no_crew_mask = high_crit['assigned_crew'] == 'No suitable crew available'
results.append(('HIGH/CRITICAL all assigned', not no_crew_mask.any(),
                f'{len(high_crit)} assets, {no_crew_mask.sum()} unassigned'))

# ── 9. Model file ─────────────────────────────────────────────
model_path = Path('src/models/failure_model.pkl')
model_ok = model_path.exists()
results.append(('Model file exists', model_ok,
                f'{model_path.stat().st_size} bytes' if model_ok else 'MISSING'))

# ── 10. Model loads and predicts ──────────────────────────────
try:
    import joblib
    model = joblib.load(model_path)
    results.append(('Model loads cleanly', True,
                    f'n_estimators={model.n_estimators}'))
except Exception as e:
    results.append(('Model loads cleanly', False, str(e)))

# ── 11. All 7 dashboard pages have render() ───────────────────
pages = ['overview','risk_command','grid_map','equipment',
         'crew_operations','ai_insights','alert_center']
page_errors = []
for p in pages:
    try:
        spec = importlib.util.spec_from_file_location(
            p, f'src/dashboard/pages/{p}.py')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if not hasattr(mod, 'render'):
            page_errors.append(f'{p}: no render()')
    except Exception as e:
        page_errors.append(f'{p}: {e}')
results.append(('All 7 pages importable + render()',
                len(page_errors)==0,
                '7/7 OK' if not page_errors else str(page_errors)))

# ── 12. CSS theme ─────────────────────────────────────────────
css = Path('src/dashboard/styles/theme.css')
css_ok = css.exists() and css.stat().st_size > 1000
results.append(('CSS theme exists', css_ok,
                f'{css.stat().st_size} bytes' if css.exists() else 'MISSING'))

# ── 13. app.py has set_page_config ───────────────────────────
app_content = Path('src/dashboard/app.py').read_text(encoding='utf-8')
results.append(('app.py has page_config', 'set_page_config' in app_content, 'set_page_config found'))
results.append(('app.py has caching', 'cache_data' in app_content, 'cache_data found'))
results.append(('app.py has 7-page routing', all(p in app_content for p in pages),
                'all page keys in routing'))

# ── 14. Raw CSVs ─────────────────────────────────────────────
for fname in ['equipment','weather','incidents','crews']:
    d = pd.read_csv(f'src/data/raw/{fname}.csv')
    results.append((f'{fname}.csv rows', len(d)>0, f'{len(d)} rows'))

# ── 15. Processed CSV ────────────────────────────────────────
proc = Path('src/data/processed/model_input.csv')
if proc.exists():
    mi = pd.read_csv(proc)
    results.append(('model_input.csv', True, f'{mi.shape[0]} rows x {mi.shape[1]} cols'))
else:
    results.append(('model_input.csv', False, 'MISSING'))

# ── 16. Docs ─────────────────────────────────────────────────
doc_files = [
    'README.md', 'submission.yaml',
    'docs/problem-statement.md', 'docs/solution-overview.md',
    'docs/architecture.md', 'docs/setup-guide.md',
]
for doc in doc_files:
    p = Path(doc)
    exists = p.exists() and p.stat().st_size > 200
    results.append((doc, exists,
                    f'{p.stat().st_size} bytes' if p.exists() else 'MISSING'))

# ── 17. No fake hard-coded values ────────────────────────────
fake_patterns = ['89% failure', '95 grid impact', '98% accuracy',
                 'crore saved', '70% outage reduction']
fake_found = []
for fp in fake_patterns:
    for py_file in Path('src').rglob('*.py'):
        content = py_file.read_text(encoding='utf-8', errors='ignore')
        if fp.lower() in content.lower():
            fake_found.append(f'{fp} in {py_file.name}')
results.append(('No fake hard-coded values', len(fake_found)==0,
                'clean' if not fake_found else str(fake_found)))

# ── 18. .gitignore has .venv and .env ────────────────────────
gi = Path('.gitignore').read_text(encoding='utf-8')
gi_ok = '.venv' in gi and '.env' in gi and '*.pkl' in gi
results.append(('.gitignore covers secrets+artifacts', gi_ok, 'venv, .env, *.pkl covered'))

# ── Print report ──────────────────────────────────────────────
print()
print('=' * 64)
print('  GRIDGUARD AI -- FINAL VALIDATION REPORT')
print('=' * 64)
passed = 0
failed = 0
for name, ok, detail in results:
    status = 'PASS' if ok else 'FAIL'
    if ok:
        passed += 1
    else:
        failed += 1
    mark = '[PASS]' if ok else '[FAIL]'
    print(f'  {mark}  {name}')
    print(f'          {detail}')

print('=' * 64)
print(f'  PASSED: {passed}   FAILED: {failed}   TOTAL: {len(results)}')
print('=' * 64)
if failed == 0:
    print('  ALL CHECKS PASSED -- GridGuard AI ready for demo')
else:
    print(f'  {failed} CHECKS NEED ATTENTION')
print('=' * 64)
