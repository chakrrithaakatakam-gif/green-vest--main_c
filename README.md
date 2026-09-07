# GreenVest — Land-to-Carbon Intelligence & Investment Planner

> **Tagline**: Land-to-Carbon Intelligence & Investment Planner  
> **Core Principle**: *"Which plantation strategy makes the most environmental and financial sense for this specific land and investor?"*

---

## 🌲 Overview

**GreenVest** is an environmental intelligence and agroforestry investment engine that bridges the gap between raw physical geospatial telemetry, botanical constraints (FAO ECOCROP), biophysical carbon accumulation models, and institutional 20-year discounted cash flow financial modeling.

---

## 🎯 MVP Environmental Scope

GreenVest MVP strictly models the three primary physical environmental determinants:
1. **Annual Rainfall** (mm/year) — derived from Open-Meteo Historical Climate Reanalysis
2. **Temperature** (Mean, Min, Max °C) — derived from Open-Meteo Historical Climate Reanalysis
3. **Soil pH** (0-30cm Topsoil) — derived from ISRIC SoilGrids v2.0 REST API

---

## 🏛️ Architecture & Two-Stage Suitability Engine

```text
User selects coordinate on Map
        ↓
Latitude + Longitude
        ↓
Open-Meteo Historical Climate (Rainfall, Temp) + SoilGrids (Soil pH)
        ↓
Canonical Land Profile (Zero fabricated fallbacks, audited confidence)
        ↓
FAO ECOCROP Botanical Knowledge Base (RMIN..RMAX, TMIN..TMAX, PHMIN..PHMAX)
        ↓
Stage 1: Hard Feasibility Filter (Eliminates environmentally impossible plants)
        ↓
Stage 2: Continuous Trapezoidal Suitability Scoring (Rainfall 40%, Temp 35%, pH 25%)
        ↓
Ranked Plantation Candidates
        ↓
PlantCarbonProfile (Decoupled Biomass Growth Curves & Labeled Assumptions)
        ↓
20-Year Financial Model (DCF, NPV, IRR, ROI, Payback Period)
        ↓
Risk Modeling & Investor Modes (Carbon-First, Return-First, Balanced)
        ↓
GreenVest Multi-Objective Recommendation & Audit Explanation
```

---

## 🚀 Quickstart

### Prerequisites
- Python 3.10+
- Node.js 18+ / npm

### Backend Setup
```bash
# Navigate to workspace root
pip install -r backend/requirements.txt

# Run pytest verification
python -m pytest backend/tests

# Start FastAPI backend server
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173` and the backend interactive API documentation at `http://localhost:8000/docs`.

---

## 📜 Regulatory & Scientific Disclaimer

All carbon sequestration figures are reported as **Estimated Biophysical Carbon Sequestration** based on ecological growth modeling assumptions and do not constitute certified carbon credits or guaranteed offset revenue. Financial metrics are modeled discounted cash flow projections based on transparent user assumptions.
