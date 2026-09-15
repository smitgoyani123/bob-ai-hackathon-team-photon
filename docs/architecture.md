# Architecture

## System Architecture Diagram

```mermaid
flowchart TD
    subgraph DATA["Data Layer"]
        EQ[("equipment.csv\nage · temp · load\nhealth · voltage\ncustomers · lat/lon")]
        WX[("weather.csv\nrainfall · wind\ntemperature · storm\nflood_risk")]
        INC[("incidents.csv\nprev_incidents · severity\nlast_failure_date\nfailure_next_7_days")]
        CR[("crews.csv\nlat/lon · status\nskill · capacity")]
    end

    subgraph PREP["Preprocessing (preprocessing.py)"]
        CLEAN["Clean & Validate\nMedian imputation\nClip & encode"]
        MERGE["Merge equipment\n+ incidents"]
        WXJOIN["Nearest-zone\nWeather Join\n(Haversine)"]
        FEAT["Feature Engineering\ntemp_stress\nincident_rate\nnetwork_importance"]
    end

    subgraph ML["ML Layer (failure_prediction.py)"]
        RF["RandomForestClassifier\nn_estimators=100\nclass_weight=balanced\nrandom_state=42"]
        FP["failure_probability\n(0.0 – 1.0 per asset)"]
        FI["feature_importances_\n(explainability)"]
    end

    subgraph RISK["Risk Engine"]
        WR["Weather Risk\n(weather_risk.py)\n0.40×rainfall\n+0.30×wind\n+0.20×temp_stress\n+0.10×storm"]
        GI["Grid Impact\n(grid_impact.py)\n0.40×customers\n+0.20×critical\n+0.20×load\n+0.20×network"]
    end

    subgraph DECISION["Decision Engine"]
        PRI["Priority Score\n(priority.py)\n0.50×failure\n+0.20×weather\n+0.30×grid_impact"]
        RL["Risk Level\nCRITICAL / HIGH\nMEDIUM / LOW"]
        MA["Maintenance Action\nImmediate Inspection\nPreventive Maintenance\nMonitor / Normal"]
        EXP["Explainability\n(explainability.py)\n16 threshold rules\nData-grounded reasons"]
    end

    subgraph CREW["Crew Assignment (crew_assignment.py)"]
        FILTER["Filter: available\n+ skill match\n+ capacity > 0"]
        DIST["Haversine Distance\nto all candidates"]
        ASSIGN["Select nearest\nqualified crew"]
    end

    subgraph OUT["Output"]
        CSV[("results/predictions.csv\n24 columns")]
        DASH["Streamlit Dashboard\n7 pages"]
    end

    subgraph BOB["IBM Bob (SDLC Partner)"]
        BOBDEV["Architecture Design\nCode Generation\nCode Review\nTesting\nDocumentation"]
    end

    EQ --> CLEAN
    WX --> WXJOIN
    INC --> CLEAN
    CLEAN --> MERGE
    MERGE --> WXJOIN
    WXJOIN --> FEAT
    FEAT --> RF
    RF --> FP
    RF --> FI
    FP --> PRI
    FEAT --> WR
    FEAT --> GI
    WR --> PRI
    GI --> PRI
    PRI --> RL
    RL --> MA
    FI --> EXP
    FEAT --> EXP
    RL --> FILTER
    FEAT --> FILTER
    FILTER --> DIST
    CR --> DIST
    DIST --> ASSIGN
    ASSIGN --> CSV
    MA --> CSV
    EXP --> DASH
    CSV --> DASH

    BOB -.->|"develops & reviews"| PREP
    BOB -.->|"develops & reviews"| ML
    BOB -.->|"develops & reviews"| RISK
    BOB -.->|"develops & reviews"| DECISION
    BOB -.->|"develops & reviews"| CREW
    BOB -.->|"develops & reviews"| DASH

    style BOB fill:#1e1b4b,stroke:#7c3aed,color:#c4b5fd
    style DATA fill:#0d1f3c,stroke:#1e3a5f,color:#60a5fa
    style ML fill:#0d2d1a,stroke:#166534,color:#4ade80
    style RISK fill:#2d1a0d,stroke:#92400e,color:#fb923c
    style DECISION fill:#1a0d2d,stroke:#5b21b6,color:#a78bfa
    style CREW fill:#0d2d2d,stroke:#065f46,color:#34d399
```

---

## Module Responsibilities

| Module | File | Responsibility |
|---|---|---|
| Data Loader | `src/data_loader.py` | Load & validate 4 raw CSVs |
| Preprocessing | `src/preprocessing.py` | Clean, merge, weather join, feature engineering |
| Failure Prediction | `src/failure_prediction.py` | Train/load RF model, predict failure_probability |
| Weather Risk | `src/weather_risk.py` | 0–100 weather risk score |
| Grid Impact | `src/grid_impact.py` | 0–100 grid impact score |
| Priority | `src/priority.py` | 0–100 priority score, risk level, maintenance action |
| Explainability | `src/explainability.py` | Data-grounded risk explanations, feature importance |
| Crew Assignment | `src/crew_assignment.py` | Haversine + skill matching, nearest crew selection |
| Pipeline | `src/pipeline.py` | Orchestrate all modules, write predictions.csv |
| Dashboard | `src/dashboard/app.py` | Streamlit entry point, routing, caching |
| Settings | `src/config/settings.py` | Centralised path configuration |

---

## Data Flow

```
equipment.csv  ──┐
weather.csv    ──┤──> preprocessing.py ──> model_input.csv (26 cols)
incidents.csv  ──┘
                                        |
                              failure_prediction.py
                                        |
                              failure_probability
                                    /       \
                          weather_risk    grid_impact
                                    \       /
                                  priority_score
                                        |
                              risk_level + maintenance_action
                                        |
                              explainability (risk reasons)
                                        |
crews.csv ──────────────────> crew_assignment.py
                                        |
                              predictions.csv (24 cols)
                                        |
                              Streamlit Dashboard (7 pages)
```

---

## IBM Bob as SDLC Partner

IBM Bob is used **exclusively** as a development and SDLC assistant, not as a runtime API:

- Designed the module architecture and data flow
- Generated all Python source code (Phases 2–10)
- Ran smoke-tests and validated outputs after each phase
- Reviewed code for bugs, edge cases and error handling
- Wrote all documentation

The application's AI logic (failure prediction, risk scoring, explainability) runs entirely on scikit-learn and deterministic Python formulas — not on a language model at runtime.
