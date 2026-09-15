# GridGuard AI — Presentation Content

IBM Bob Hackathon 2025 | Team Photon

---

## SLIDE 1: THE PROBLEM

**Title:** Power Grids Fail Without Warning

**Core message:**
Power utilities operate in the dark.
Equipment fails unpredictably.
Crews are dispatched reactively.
Customers pay the price.

**Key points:**
- Grid equipment (transformers, switches, lines) fails from combinations of age, load, heat, weather exposure, and prior incident history
- No single system connects these signals into an operational decision
- When failure happens, operators scramble — wrong crews, wrong locations, delayed response

**Visual:** Timeline showing: Equipment degrades → Silent → Failure → Reactive dispatch → Customer outage

---

## SLIDE 2: WHY EXISTING APPROACHES FALL SHORT

**Title:** Prediction Without Decision Is Useless

| What utilities do today | What's missing |
|---|---|
| Fixed maintenance schedules (age only) | No failure probability signal |
| Manual inspections | No weather-equipment correlation |
| Spreadsheet crew tracking | No network impact scoring |
| Reactive dispatch | No automated crew pre-positioning |
| Expert intuition | No explainable AI decision |

**Key insight:**
A model that says "89% failure probability" is not operational intelligence.
The question is: *What do we do about it, right now, with which crew?*

---

## SLIDE 3: THE GRIDGUARD AI SOLUTION

**Title:** Predict. Assess. Prioritize. Assign. Act.

**One sentence:** GridGuard AI converts raw equipment, weather, and incident data into fully explainable operational field assignments in under 1 second.

**The pipeline:**
```
DATA  →  ML PREDICTION  →  WEATHER RISK  →  GRID IMPACT
     →  PRIORITY SCORE  →  EXPLANATION  →  CREW ASSIGNMENT  →  DASHBOARD
```

**Output example for T001:**
- Failure Probability: 92%
- Weather Risk: 30/100
- Grid Impact: 83/100
- Priority Score: 77/100
- Risk Level: HIGH
- Action: Preventive Maintenance
- Crew: C008 (8.5 km away)
- Why: Aging equipment, high temperature, high load, low health, 11 prior incidents, critical facility

---

## SLIDE 4: SYSTEM ARCHITECTURE

**Title:** End-to-End Intelligence Pipeline

```
CSV DATA (Equipment / Weather / Incidents / Crews)
         |
         v
    PREPROCESSING
    Clean · Merge · Weather-join · Feature engineering
         |
         v
    ML MODEL (RandomForestClassifier)
    21 features · failure_next_7_days · class_weight=balanced
         |
         v
    RISK ENGINE
    Weather Risk (4-component) · Grid Impact (4-component)
         |
         v
    DECISION ENGINE
    Priority Score · Risk Level · Maintenance Action · Explainability
         |
         v
    CREW ASSIGNMENT
    Haversine distance · Skill match · Availability
         |
         v
    DASHBOARD (Streamlit · Plotly · Folium)
    7 pages · Risk matrix · Map · AI Decision Card · Simulator
```

**IBM Bob** used as AI SDLC partner across all phases (not a runtime component)

---

## SLIDE 5: MACHINE LEARNING

**Title:** Random Forest Failure Prediction

**Algorithm:** RandomForestClassifier (scikit-learn)
**Target:** failure_next_7_days (binary)
**Features (21):**

| Category | Features |
|---|---|
| Equipment | age, temperature, load, health, voltage, customers_served, critical_facility |
| Incidents | previous_incidents, severity_encoded, days_since_last_failure |
| Weather | rainfall, wind, temperature, storm, flood_risk |
| Engineered | age_risk_flag, health_risk_flag, load_risk_flag, temp_stress, incident_rate, network_importance |

**Key design decisions:**
- `class_weight="balanced"` — handles class imbalance without oversampling
- `random_state=42` — fully reproducible
- Top features: health → age → load → weather_storm → weather_rainfall

---

## SLIDE 6: RISK & DECISION ENGINE

**Title:** Three-Layer Risk Scoring

**Weather Risk (0–100):**
```
0.40 × rainfall_risk  +  0.30 × wind_risk
+ 0.20 × temperature_stress  +  0.10 × storm_risk
```
Temperature stress = deviation above 35°C safe threshold (not raw temperature)

**Grid Impact (0–100):**
```
0.40 × customer_impact  +  0.20 × critical_facility
+ 0.20 × load_impact  +  0.20 × network_importance
```
network_importance derived from voltage + customers + criticality (transparent)

**Priority Score (0–100):**
```
0.50 × failure_probability  +  0.20 × weather_risk  +  0.30 × grid_impact
```

**Risk thresholds:** LOW (0–30) · MEDIUM (30–60) · HIGH (60–80) · CRITICAL (80–100)

---

## SLIDE 7: CREW PRE-POSITIONING

**Title:** Right Crew. Right Place. Right Time.

**Assignment only triggers for HIGH and CRITICAL assets**

Process for each eligible asset:
1. Filter crews: status = available
2. Match skill to equipment type
   - Electrical → Transformer, Switch
   - Mechanical → Switch, Line
   - Civil → Line, Transformer
3. Filter: capacity > 0
4. Compute Haversine distance to all candidates
5. Select nearest suitable crew

**Result example:**
- T001 (Transformer, HIGH) → C008, 8.5 km
- S001 (Switch, HIGH) → C001, 1.5 km
- L001 (Line, HIGH) → C004, 19.2 km

**9/9 HIGH-risk assets successfully assigned**

---

## SLIDE 8: DASHBOARD DEMO

**Title:** Grid Operations Command Center

**7 pages:**

1. **Overview** — Grid Health gauge, KPI cards, critical attention list
2. **Risk Command Center** — Risk matrix (failure prob vs grid impact, bubble=weather risk)
3. **Live Grid Map** — Folium dark map, risk-coded markers, crew positions, click popups
4. **Equipment Intelligence** — Full AI Decision Card with WHY AT RISK + crew assignment
5. **Crew Operations** — Crew roster, skill distribution, active assignment table
6. **AI Insights** — Model metrics, feature importance, What-If Scenario Simulator
7. **Alert Center** — Filtered alerts by severity with CSV download

**Key interaction:** Select any asset → see exactly why it is at risk → see recommended action → see assigned crew

---

## SLIDE 9: IBM BOB DEVELOPMENT WORKFLOW

**Title:** Built Entirely with IBM Bob as AI SDLC Partner

| Phase | Bob Mode | What Bob Did |
|---|---|---|
| Architecture design | Ask → Plan | Investigated codebase, designed module flow |
| Data pipeline | Agent | Wrote data_loader.py, preprocessing.py |
| ML model | Agent | Wrote failure_prediction.py with safeguards |
| Risk engine | Agent | Wrote weather_risk.py, grid_impact.py, priority.py |
| Explainability | Agent | Wrote deterministic 16-rule explainability.py |
| Crew assignment | Agent | Wrote Haversine + skill matching crew_assignment.py |
| Pipeline orchestration | Agent | Wrote pipeline.py + main.py |
| Dashboard (7 pages) | Agent | Wrote all Streamlit pages + CSS theme |
| Testing | Shell | Ran smoke-tests after every module |
| Code review | Review | Identified and fixed NaN bugs, encoding issues |
| Documentation | Agent | Wrote all 4 docs + README + submission.yaml |

**Important:** IBM Bob is used as a development tool, NOT as a runtime component.
All AI decisions in GridGuard AI run on scikit-learn and deterministic Python.

---

## SLIDE 10: IMPACT AND FUTURE SCOPE

**Title:** From Demo to Production

**What GridGuard AI demonstrates today:**
- Prediction → Decision → Action in a single pipeline
- Fully explainable, data-grounded recommendations
- Honest limitations clearly documented (synthetic data, simplified formulas)
- Professional grid operations UI judges and operators can immediately understand

**Core innovation:**
GridGuard AI doesn't just predict failure.
It answers: *What does it mean? What should we do? Who should go? How far?*

**Future scope for production:**
- Real-time SCADA/IoT data ingestion
- Calibrated models on historical outage data
- Network topology graph for true network importance
- Multi-crew optimised dispatch
- IBM watsonx integration for operator Q&A
- Mobile dispatch interface for field crews
- Automated escalation and alerting workflows

---

## CORE STORY (for all slides)

```
DATA  →  AI  →  RISK  →  IMPACT  →  PRIORITY
     →  EXPLANATION  →  MAINTENANCE  →  CREW  →  ACTION
```

This system doesn't just predict equipment failure.
**It turns risk into an operational decision.**
