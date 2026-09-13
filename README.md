# FloodWatch AI: Autonomous Urban Inundation & Asset Risk Intelligence Agent
**Candidate:** Vartika Verma  
**Course:** Sparta Global AI & Tech Institute - AI Training Fundamentals  
**Module:** Session 5: Agentic AI - Autonomy, Feedback Loops & Operational Control  
**Inspiration:** Google Flood Hub & Google Crisis Response Architecture  

---

## 5-Week Curriculum Synthesis: How Every Module is Embodied

| Module | Core Concepts Taught | Implementation in FloodWatch AI |
| :--- | :--- | :--- |
| **Week 1: AI Foundations & Machine Learning** | Supervised vs Unsupervised ML; The 4 AI Actions (Identify, Analyse, Manipulate, Create); Early Warning Sentry systems. | Employs **Unsupervised Machine Learning (DBSCAN)** to discover emergent spatial inundation corridors from unlabelled sensor data without pre-set zones. Acts as an early-warning crisis sentry before culverts flood critical assets. |
| **Week 2: Modern AI & LLM Architectures** | Probabilistic vs Deterministic logic; Tokens & Context Windows; Grounding models with deterministic tools. | Combines the probabilistic reasoning of an LLM (interpreting noisy, unedited telemetry logs) with **strictly grounded deterministic tools** (Haversine trigonometry, bounding box assertions) to eliminate spatial hallucinations. |
| **Week 3: Prompt Engineering & The 4Ds** | 4Ds Framework (Delegation, Description, Discernment, Diligence); Negative constraints; Avoiding AI sycophancy. | Features explicit **negative constraints** ("Do NOT silently drop malformed data"). Employs all 4Ds: delegated the spatial math, described the schemas, discerned planar metric distortions, and verified with diligence. |
| **Week 4: Workflows vs Agents & HITL** | Rule vs AI vs Human steps; Fixed A -> B -> C limits; Human-in-the-Loop (HITL) approval gates. | Directly contrasts with Session 4's predetermined Power Automate flow. Introduces autonomous self-branching ReAct loops and an explicit **Human-in-the-Loop Quarantine Gate** for unrecoverable sensor dropouts. |
| **Week 5: Agentic AI & Retaining Ownership** | Four-Yeses Test (Goal, Tools, Sequence, Self-Check); Observe -> Adjust loops; 5 Safety Questions; Blast Radius. | Complete execution of the Four-Yeses test, demonstrable Observe -> Adjust pivot (Euclidean -> Haversine), sandboxed blast radius containment, and deep intellectual ownership of the mathematics. |

---

## Project Architecture & Quickstart

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
- 5 automated unit tests independently verifying coordinate bounds, quarantine invariants, quarantine-exclusivity, record conservation, and Haversine precision (2,352.8m ground truth).

### 3. Launch Interactive Command Map
```bash
python floodwatch/visualizer.py
```
- Generates `floodwatch/output/floodwatch_dashboard.html` using clean Esri Dark Gray GIS canvas with zero watermarks.
