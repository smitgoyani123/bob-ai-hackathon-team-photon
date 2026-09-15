# 🔍 GridGuard AI — Deterministic Explainability & Auditable AI

In mission-critical power grid infrastructure, opaque black-box AI decisions and generative LLM hallucinations are dangerous and unacceptable. Grid operators must know **exactly why** an asset is prioritized before dispatching high-voltage crews and field resources.

GridGuard AI implements a **dual-layer explainability framework**:
1. **Global Feature Importances** derived from the underlying scikit-learn Random Forest model.
2. **Local Zero-Hallucination Deterministic Explainability** evaluated across 16 strict engineering threshold rules per individual asset.

---

## 1. Zero-Hallucination Deterministic Threshold Engine

Implemented in [`src/explainability.py`](file:///e:/bob-ai-hackathon-team-photon/src/explainability.py), every monitored asset is evaluated against 16 domain-specific engineering rules:

| ID | Rule Check | Operational Threshold | Grounded Reason Output |
|---|---|---|---|
| **R01** | `age > 20` | Equipment Age > 20 Years | `Aging equipment (>20 years)` |
| **R02** | `operating_temp > 70` | Temperature > 70°C | `High operating temperature (>70 deg C)` |
| **R03** | `load_pct > 75` | Grid Electrical Load > 75% | `High load (>75%)` |
| **R04** | `health_index < 40` | Asset Health Index < 40/100 | `Low equipment health (<40)` |
| **R05** | `previous_incidents >= 2` | Incident History $\ge 2$ | `History of recurring incidents (>=2)` |
| **R06** | `weather_risk > 55` | Weather Risk Score > 55 | `Severe weather exposure (risk >55)` |
| **R07** | `rainfall_mm > 50` | Rainfall > 50 mm/h | `Heavy rainfall zone (>50mm)` |
| **R08** | `wind_speed_kmh > 60` | Wind Speed > 60 km/h | `High wind exposure (>60 km/h)` |
| **R09** | `storm_alert == 1` | Active Meteorological Alert | `Active storm conditions` |
| **R10** | `flood_risk > 0.5` | Inundation Factor > 0.5 | `Elevated flood risk (>0.5)` |
| **R11** | `grid_impact > 60` | Grid Consequence Impact > 60 | `High grid impact (>60)` |
| **R12** | `customers > 4000` | Connected Base > 4,000 Customers | `High customer dependency (>4000 customers)` |
| **R13** | `critical_facility == 1`| Hospital / Water / Emergency Link | `Critical facility dependency` |
| **R14** | `temp_stress > 1.2` | Compound Thermal Stress > 1.2 | `High thermal stress ratio (>1.2)` |
| **R15** | `failure_probability > 0.7`| Model Failure Probability > 70% | `High ML failure probability (>70%)` |
| **R16** | `days_since_last_failure < 60`| Recent Failure History < 60 Days | `Recent failure history (<60 days)` |

### Why Deterministic Thresholds?
- **Auditable & Verifiable**: Every reason can be verified directly against telemetry logs.
- **Regulatory Compliance**: Transmission system operators (TSOs) require deterministic accountability for audit trails and regulatory filings.
- **Zero Hallucinations**: Eliminates probabilistic generative LLM text drift or fabricated equipment states.

---

## 2. Global Feature Importance

The Random Forest failure prediction model assigns weights to all 21 engineered feature vectors. The top features driving failure risk across the network are:

1. **`operating_temp` & `temp_stress`**: Primary thermal degradation drivers.
2. **`age`**: Material insulation wear and mechanical fatigue.
3. **`weather_storm` & `rainfall_mm`**: Environmental stress and dielectric breakdown vectors.
4. **`previous_incidents` & `incident_rate`**: Recurring component weakness.
5. **`load_pct`**: Prolonged peak capacity operation.

---

## 3. Presentation in the AI Decision Card

When an operator selects an asset in **Equipment Intelligence** or clicks an asset node on the **Live Grid Map**:
- The **6-Vector Multi-Signal Radar Chart** maps normalized dimensions (Age, Temp, Load, Incidents, Weather Risk, Grid Impact).
- The **AI Decision Explainability Card** renders color-coded badges for all triggered rules.
- Recommended maintenance protocols are automatically mapped:
  - `CRITICAL` $\rightarrow$ **Immediate Inspection**
  - `HIGH` $\rightarrow$ **Preventive Maintenance**
  - `MEDIUM` $\rightarrow$ **Continuous Monitoring**
  - `LOW` $\rightarrow$ **Normal Maintenance**
