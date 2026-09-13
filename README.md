# FloodWatch AI: Autonomous Urban Inundation & Asset Risk Intelligence Agent

**Author:** Vartika Verma  
**System Architecture:** Autonomous Spatial AI Agent, Geodesic Engine & Verification Suite  
**Inspiration:** Google Flood Hub & Google Crisis Response Architecture  

---

## Core Technical Concepts & System Architecture

```mermaid
flowchart TD
    %% Architecture Styling
    classDef inputStyle fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef reactStyle fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#f8fafc;
    classDef safetyStyle fill:#450a0a,stroke:#f43f5e,stroke-width:2px,color:#fecdd3;
    classDef mathStyle fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#ecfdf5;
    classDef mlStyle fill:#0c4a6e,stroke:#0284c7,stroke-width:2px,color:#e0f2fe;
    classDef verifyStyle fill:#14532d,stroke:#22c55e,stroke-width:2px,color:#f0fdf4;
    classDef mapStyle fill:#312e81,stroke:#a855f7,stroke-width:2px,color:#faf5ff;

    subgraph SEC1["1. INGESTION & BOUNDARY DEFINITION"]
        C1["<b>Constraint-Driven Prompt Architecture</b><br/>• <i>Role:</i> Deterministic schema boundaries and negative constraints<br/>• <i>Where:</i> agent.py (System Prompt and Schema Enforcers)"]:::inputStyle
    end

    subgraph SEC2["2. AUTONOMOUS REASONING & HITL SAFETY"]
        C2["<b>Autonomous ReAct Feedback Loops</b><br/>• <i>Role:</i> Dynamic Observe ➔ Reason ➔ Act ➔ Adjust execution cycle<br/>• <i>Where:</i> agent.py (run_autonomous_pipeline)"]:::reactStyle
        C3["<b>Human-in-the-Loop Exception Quarantine</b><br/>• <i>Role:</i> Gating for unrecoverable sensor dropouts (0,0)<br/>• <i>Where:</i> agent.py (quarantine_unrecoverable_records) ➔ audit CSV"]:::safetyStyle
    end

    subgraph SEC3["3. MATHEMATICAL GROUNDING & SPATIAL ML"]
        C4["<b>Deterministic Geodesic Grounding</b><br/>• <i>Role:</i> Eliminates spatial hallucinations via spherical trigonometry<br/>• <i>Where:</i> agent.py (haversine_distance)"]:::mathStyle
        C5["<b>Unsupervised Spatial Clustering (DBSCAN)</b><br/>• <i>Role:</i> Density hazard corridor discovery (eps=650m, min_samples=3)<br/>• <i>Where:</i> agent.py (cluster_inundation_zones)"]:::mlStyle
    end

    subgraph SEC4["4. INVARIANT TESTING & SITUATION DISPLAY"]
        C6["<b>Automated Invariant Verification</b><br/>• <i>Role:</i> 5 independent automated unit tests (Bounds, Invariants, Precision)<br/>• <i>Where:</i> tests/test_floodwatch_verification.py"]:::verifyStyle
        C7["<b>Interactive Geospatial Intelligence</b><br/>• <i>Role:</i> Multi-layer situation map and asset proximity buffers<br/>• <i>Where:</i> visualizer.py ➔ output/floodwatch_dashboard.html"]:::mapStyle
    end

    %% Execution and Data Flow
    C1 -->|"Validated Telemetry Stream (20 Rows)"| C2
    C2 -->|"Unrecoverable (0,0) Null Records"| C3
    C2 -->|"Self-Healed [Lat, Lon] Coordinates"| C4
    C4 -->|"Spherical Distance Matrix (Sub-meter)"| C5
    C5 -->|"Discovered Flood Corridors"| C6
    C5 -->|"Risk Clusters and Infrastructure"| C7
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
