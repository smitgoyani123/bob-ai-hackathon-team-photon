# 🎬 GridGuard AI — Demonstration Script (3–5 Minutes)

This script outlines the demonstration flow shown in the official submission video ([Watch Video](https://drive.google.com/file/d/1cLAg9iycwF9eLyQStQmlIF8E8s5egSnu/view?usp=sharing)).

---

## ⏱️ Video Timeline & Narration Flow

### 1. Introduction & Grid Health Executive Overview (0:00 – 0:45)
- **Visual**: Navigate to **Command Center** (`http://localhost:5173/`).
- **Key Highlights**:
  - Point out the executive KPIs: Overall Grid Health Index (55.3%), Total Monitored Equipment (30), Active High-Priority Alerts (15), and Field Crew Fleet Status (8 crews / 5 available).
  - Highlight the Emergency Alert Ticker broadcasting critical asset conditions.
  - Review the Multi-Signal Risk Matrix displaying equipment dispersion across Failure Probability vs. Consequence Severity.

### 2. Multi-Dimensional Risk Command & Analytics (0:45 – 1:30)
- **Visual**: Click **Risk Command** in the sidebar.
- **Key Highlights**:
  - Filter equipment by Risk Level (`CRITICAL`, `HIGH`), Equipment Type (Transformers, Switches, High-Voltage Lines), and Critical Facility Dependency (Hospitals, Water Plants, Emergency Services).
  - Inspect the Risk Distribution Bar Chart and Priority Ranking Table.
  - Highlight that assets like `T001` (Critical Transformer) rank at the top due to compound age, thermal stress, and hospital power reliance.

### 3. Equipment Intelligence & Zero-Hallucination Explainability (1:30 – 2:15)
- **Visual**: Open **Equipment Intelligence** and select Asset `T001`.
- **Key Highlights**:
  - Display the 6-Vector Radar Signature (Age, Temperature, Load, Incidents, Weather Risk, Grid Impact).
  - Walk through the **Deterministic AI Decision Card**:
    - Shows exact mathematical reasons why this asset is CRITICAL: `Operating temperature (78°C) exceeds 70°C threshold`, `Grid load (88%) exceeds 75%`, `Direct supply link to hospital critical facility`.
    - Zero hallucination — every reason is grounded directly in SCADA telemetry and engineering thresholds.
  - Show the recommended maintenance action: `Immediate Inspection`.

### 4. Real-Time Leaflet GIS Grid Map & Doppler Radar (2:15 – 3:15)
- **Visual**: Navigate to **Live Grid Map**.
- **Key Highlights**:
  - Demonstrate cartographic switching: **OpenStreetMap**, **Esri World Satellite Imagery**, and **Tactical Dark Ops**.
  - Toggle the live Doppler precipitation radar overlay (powered by the RainViewer API) showing monsoon storm fronts.
  - Inspect the animated crew dispatch flight paths connecting depots to prioritized high-risk assets.
  - Click on `T001` marker on the map: popup shows live telemetry, priority score, and assigned field crew.

### 5. Crew Operations & Automated Skill Pre-Positioning (3:15 – 3:45)
- **Visual**: Navigate to **Crew Operations**.
- **Key Highlights**:
  - Review crew roster: skill certification (`Electrical`, `Mechanical`, `Civil`), vehicle type, and current assignment status.
  - Show how Crew `C001` (Electrical specialist) is automatically pre-positioned to `T001` using geodesic Haversine distance (1.4 km away), cutting dispatch delay from hours to minutes.

### 6. AI Insights & Parametric Scenario Simulator (3:45 – 4:30)
- **Visual**: Navigate to **AI Insights & Sim**.
- **Key Highlights**:
  - Inspect Random Forest model architecture and Top 10 global feature importances (`temp_stress`, `incident_rate`, `network_importance`).
  - Open the **What-If Scenario Simulator**:
    - Increase Wind Speed to 75 km/h and Rainfall to 65 mm/h.
    - Click **Simulate Scenario**: watch priority scores and risk categories recalculate dynamically in real-time.

### 7. Alert Center & Conclusion (4:30 – 5:00)
- **Visual**: Open **Alert Center**.
- **Key Highlights**:
  - Demonstrate alert acknowledgement and export to CSV/JSON.
  - Summarize the value proposition: Transforming raw grid data into explainable, proactive field pre-positioning before outages occur.
