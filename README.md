# FloodWatch AI: Autonomous Urban Inundation & Asset Risk Intelligence Agent

**Author:** Vartika Verma  
**System Architecture:** Autonomous Spatial AI Agent, Geodesic Engine & Verification Suite  
**Inspiration:** Google Flood Hub & Google Crisis Response Architecture  

---

## Core Technical Concepts & System Implementation

| Concept | Architectural Role | Where & How Implemented |
| :--- | :--- | :--- |
| **Unsupervised Spatial Clustering (DBSCAN)** | Density-based corridor & anomaly discovery without pre-classified boundary zones | **`agent.py` (`cluster_inundation_zones`)**<br>Executes density-based spatial clustering with $\varepsilon = 650\,\text{m}$ and $\text{min\_samples} = 3$ to detect emergent urban flood corridors from noisy telemetry without requiring static polygon boundaries. |
| **Deterministic Geodesic Grounding** | Elimination of LLM spatial hallucinations via rigorous spherical mathematics | **`agent.py` (`haversine_distance`) & `tests/test_floodwatch_verification.py`**<br>Employs spherical Haversine trigonometry ($R = 6,371\,\text{km}$) rather than planar Euclidean approximations, guaranteeing sub-meter proximity calculations between flood clusters and critical infrastructure assets. |
| **Constraint-Driven Prompt Architecture** | Deterministic schema boundaries, negative constraints, and output validation | **`agent.py` (System Prompt & Schema Enforcers)**<br>Embeds explicit negative constraints (*"Do NOT silently drop malformed data"*) and structured delegation contracts, ensuring robust handling of coordinate formats and schema compliance. |
| **Autonomous ReAct Feedback Loops** | Dynamic Observe ➔ Reason ➔ Act ➔ Adjust execution cycle | **`agent.py` (`run_autonomous_pipeline`)**<br>Autonomously audits raw telemetry feeds, identifies inverted coordinate pairs `[Lon, Lat]`, self-heals spatial orientation against geographic bounds, and pivots execution strategies dynamically without human intervention. |
| **Human-in-the-Loop (HITL) Exception Quarantine** | Safety gating for unrecoverable hardware dropouts | **`agent.py` (`quarantine_unrecoverable_records`) ➔ `output/floodwatch_quarantine_audit.csv`**<br>Isolates fatal telemetry failures (such as `(0.0, 0.0)` Null Island sensor dropouts) into a quarantined audit queue for specialist review, maintaining 100% total record conservation. |
| **Automated Invariant Verification** | Independent automated test-driven validation | **`tests/test_floodwatch_verification.py` (Pytest Suite)**<br>Executes 5 automated verification tests enforcing boundary invariants, quarantine-exclusivity, full record conservation ($N_{\text{clean}} + N_{\text{quarantined}} = N_{\text{raw}}$), and Haversine sub-meter ground truth. |
| **Interactive Geospatial Intelligence** | Situation map rendering and proximity visualization | **`visualizer.py` ➔ `output/floodwatch_dashboard.html`**<br>Generates an interactive GIS command dashboard using Leaflet and Esri Dark Canvas, plotting sensor clusters, severity markers, and infrastructure risk buffers. |

---

## System Pipeline & Execution Flow

```
[Raw Sensor Telemetry]
        │
        ▼
[Autonomous Agent Audit] ──(Observe: Out-of-bounds or Null Coordinates)
        │
        ├── Inverted [Lon, Lat] ──────────► [Self-Healing Geodesic Transform]
        │                                             │
        └── Fatal (0,0) Dropout ──► [HITL Quarantine] │
                                          │           │
                                          ▼           ▼
                                     [Quarantine] [Cleaned Telemetry]
                                       Audit CSV      │
                                                      ▼
                                            [DBSCAN Clustering]
                                             (eps=650m, min=3)
                                                      │
                                                      ▼
                                            [Risk Corridor Analysis]
                                            (Asset Proximity Engine)
                                                      │
                                    ┌─────────────────┴─────────────────┐
                                    ▼                                   ▼
                         [Interactive Dashboard]           [Pytest Invariant Suite]
                          (Esri Dark GIS Canvas)            (5 Automated Tests Passed)
```

---

## Quickstart & Operational Verification

### 1. Ingest & Run Autonomous Agent
```bash
python floodwatch/agent.py
```
- Ingests 20 raw sensor records from `floodwatch/data/raw_inundation_telemetry.csv`.
- Self-heals 4 inverted coordinate pairs `[Lon, Lat]` -> `[Lat, Lon]`.
- Quarantines 2 `(0,0)` Null Island dropouts into `floodwatch_quarantine_audit.csv`.
- Discovers 3 high-risk inundation corridors via DBSCAN.

### 2. Run Independent Verification Test Suite
```bash
python -m pytest floodwatch/tests/test_floodwatch_verification.py -v
```
- Executes 5 automated unit tests verifying coordinate bounds, quarantine invariants, quarantine-exclusivity, record conservation, and Haversine precision (2,352.8m ground truth).

### 3. Launch Interactive Command Map
```bash
python floodwatch/visualizer.py
```
- Generates `floodwatch/output/floodwatch_dashboard.html` using clean Esri Dark Gray GIS canvas with zero watermarks.
