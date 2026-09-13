"""
FloodWatch AI - Interactive Command Dashboard Generator
Visualizes flood inundation telemetry, healed coordinates, critical assets, and DBSCAN corridors.
Inspired by Google Flood Hub & Google Crisis Response.
"""

import os
import sys
import csv
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def build_dashboard(
    curated_csv: str = "floodwatch/output/floodwatch_curated_telemetry.csv",
    quarantine_csv: str = "floodwatch/output/floodwatch_quarantine_audit.csv",
    clusters_json: str = "floodwatch/output/floodwatch_clusters.json",
    assets_csv: str = "floodwatch/data/critical_assets.csv",
    output_html: str = "floodwatch/output/floodwatch_dashboard.html"
):
    # Load Curated Incidents
    curated = []
    with open(curated_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            curated.append(row)

    # Load Quarantine
    quarantine = []
    with open(quarantine_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            quarantine.append(row)

    # Load Clusters
    with open(clusters_json, mode="r", encoding="utf-8") as f:
        cluster_data = json.load(f)

    # Load Assets
    assets = []
    with open(assets_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            assets.append(row)

    # Metrics
    total_telemetry = len(curated) + len(quarantine)
    healed_count = sum(1 for r in curated if r["data_lineage"] == "HEALED_INVERTED_COORDINATES")
    critical_count = sum(1 for r in curated if "P1_CRITICAL" in r["triage_priority"])
    quarantine_count = len(quarantine)
    active_corridors = cluster_data["total_clusters"]

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FloodWatch AI | Urban Inundation & Asset Risk Command Center</title>
    <!-- Google Fonts & Leaflet CDN -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    <style>
        :root {{
            --bg-base: #0a0f1d;
            --bg-card: #111a2e;
            --border: #1e2c4a;
            --accent-cyan: #06b6d4;
            --accent-blue: #3b82f6;
            --accent-red: #ef4444;
            --accent-amber: #f59e0b;
            --accent-emerald: #10b981;
            --text-primary: #f8fafc;
            --text-muted: #94a3b8;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
        }}
        body {{
            background: var(--bg-base);
            color: var(--text-primary);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        header {{
            background: rgba(17, 26, 46, 0.95);
            border-bottom: 1px solid var(--border);
            padding: 14px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(12px);
            z-index: 1000;
        }}
        .brand-container {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .brand-logo {{
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #06b6d4, #2563eb);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            box-shadow: 0 0 15px rgba(6, 182, 212, 0.4);
        }}
        .brand-title h1 {{
            font-size: 18px;
            font-weight: 700;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .brand-title h1 span.badge {{
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            background: rgba(6, 182, 212, 0.2);
            color: var(--accent-cyan);
            border: 1px solid rgba(6, 182, 212, 0.3);
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: 600;
        }}
        .brand-title p {{
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 2px;
        }}
        .status-pill {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.25);
            color: var(--accent-emerald);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
        }}
        .status-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-emerald);
            box-shadow: 0 0 8px var(--accent-emerald);
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.4; transform: scale(0.85); }}
        }}
        .metrics-strip {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 12px;
            padding: 12px 24px;
            background: #0d1424;
            border-bottom: 1px solid var(--border);
        }}
        .metric-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px 14px;
            display: flex;
            flex-direction: column;
        }}
        .metric-label {{
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.04em;
        }}
        .metric-val {{
            font-size: 20px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            margin-top: 4px;
            color: #fff;
        }}
        .app-body {{
            flex: 1;
            display: grid;
            grid-template-columns: 1fr 380px;
            overflow: hidden;
            position: relative;
        }}
        #map {{
            width: 100%;
            height: 100%;
            background: #0a0f1d;
        }}
        .sidebar {{
            background: var(--bg-card);
            border-left: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        .sidebar-header {{
            padding: 14px 18px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .sidebar-header h2 {{
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #fff;
        }}
        .feed-container {{
            flex: 1;
            overflow-y: auto;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .sensor-card {{
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px;
            transition: all 0.2s;
            cursor: pointer;
        }}
        .sensor-card:hover {{
            border-color: var(--accent-cyan);
            transform: translateY(-1px);
        }}
        .sensor-card.surge {{
            border-left: 3px solid var(--accent-red);
        }}
        .sensor-card.healed {{
            border-left: 3px solid var(--accent-emerald);
        }}
        .sensor-card.quarantine {{
            border-left: 3px solid var(--accent-amber);
            opacity: 0.8;
        }}
        .sc-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            font-family: 'JetBrains Mono', monospace;
        }}
        .sc-title {{
            font-size: 12px;
            font-weight: 600;
            color: #f1f5f9;
            margin-top: 4px;
        }}
        .sc-meta {{
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 6px;
            display: flex;
            justify-content: space-between;
        }}
        .leaflet-popup-content-wrapper {{
            background: #0f172a !important;
            color: #f8fafc !important;
            border: 1px solid #334155;
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }}
        .leaflet-popup-tip {{
            background: #0f172a !important;
        }}
        .popup-title {{
            font-weight: 700;
            font-size: 13px;
            border-bottom: 1px solid #334155;
            padding-bottom: 4px;
            margin-bottom: 6px;
            color: #38bdf8;
        }}
        .popup-row {{
            font-size: 11px;
            margin-bottom: 3px;
            display: flex;
            justify-content: space-between;
            gap: 12px;
        }}
    </style>
</head>
<body>

    <header>
        <div class="brand-container">
            <div class="brand-logo">🌊</div>
            <div class="brand-title">
                <h1>FloodWatch AI <span class="badge">Google Flood Hub Architecture</span></h1>
                <p>Autonomous Urban Inundation & Asset Risk Intelligence · Candidate: <b>Vartika Verma</b></p>
            </div>
        </div>
        <div class="status-pill">
            <div class="status-dot"></div>
            AUTONOMOUS REACT LOOP ACTIVE
        </div>
    </header>

    <div class="metrics-strip">
        <div class="metric-card">
            <span class="metric-label">Ingested Telemetry</span>
            <span class="metric-val">{total_telemetry} Streams</span>
        </div>
        <div class="metric-card">
            <span class="metric-label">Self-Healed Coordinates</span>
            <span class="metric-val" style="color: var(--accent-emerald);">{healed_count} Inversions</span>
        </div>
        <div class="metric-card">
            <span class="metric-label">Quarantined Sensor Drops</span>
            <span class="metric-val" style="color: var(--accent-amber);">{quarantine_count} Null Island</span>
        </div>
        <div class="metric-card">
            <span class="metric-label">Critical Surges (P1)</span>
            <span class="metric-val" style="color: var(--accent-red);">{critical_count} Assets Threat</span>
        </div>
        <div class="metric-card">
            <span class="metric-label">Inundation Corridors</span>
            <span class="metric-val" style="color: var(--accent-cyan);">{active_corridors} DBSCAN Clust</span>
        </div>
    </div>

    <div class="app-body">
        <div id="map"></div>
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>Real-Time Triage Stream</h2>
                <span style="font-size: 11px; color: var(--text-muted);">{len(curated)} Active</span>
            </div>
            <div class="feed-container">
    """

    for r in curated:
        is_surge = "P1_CRITICAL" in r["triage_priority"]
        is_healed = r["data_lineage"] == "HEALED_INVERTED_COORDINATES"
        card_class = "surge" if is_surge else ("healed" if is_healed else "")
        status_badge = "<span style='color: #ef4444; font-weight: 700;'>P1 CRITICAL</span>" if is_surge else "<span style='color: #38bdf8;'>P2 HIGH</span>"
        lineage_badge = " · <span style='color: #10b981;'>[HEALED INVERSION]</span>" if is_healed else ""

        html_content += f"""
                <div class="sensor-card {card_class}">
                    <div class="sc-top">
                        <span>{r['sensor_id']}</span>
                        <span>{status_badge}</span>
                    </div>
                    <div class="sc-title">{r['sensor_type']}{lineage_badge}</div>
                    <div class="sc-meta">
                        <span>Depth: <b>{r['water_depth_cm']} cm</b></span>
                        <span>Rate: <b>{r['rate_of_rise_cm_hr']} cm/h</b></span>
                    </div>
                    <div class="sc-meta" style="margin-top: 4px; font-size: 10px;">
                        <span>Near: {r['nearest_asset_name']}</span>
                        <span><b>{r['geodesic_distance_meters']}m</b></span>
                    </div>
                </div>
        """

    html_content += """
            </div>
        </div>
    </div>

    <script>
        const map = L.map('map', {
            center: [51.513, -0.115],
            zoom: 13,
            zoomControl: true
        });

        // CartoDB Dark Matter tile layer
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Tiles &copy; Esri, DeLorme, NAVTEQ | FloodWatch AI',
            maxZoom: 19
        }).addTo(map);

        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 16
        }).addTo(map);

        // Assets Data
        const assets = """ + json.dumps(assets) + """;
        const curated = """ + json.dumps(curated) + """;
        const clusterData = """ + json.dumps(cluster_data) + """;

        // Add Critical Infrastructure Markers
        assets.forEach(a => {
            const marker = L.circleMarker([a.latitude, a.longitude], {
                radius: 10,
                fillColor: '#ef4444',
                color: '#ffffff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.9
            }).addTo(map);

            marker.bindPopup(`
                <div class="popup-title">🏛️ ${a.asset_name}</div>
                <div class="popup-row"><span>Category:</span><b>${a.category}</b></div>
                <div class="popup-row"><span>Criticality:</span><b>${a.criticality_tier}</b></div>
                <div class="popup-row"><span>Max Flood Tol:</span><b>${a.max_tolerable_inundation_cm} cm</b></div>
            `);

            // Add 400m emergency buffer circle
            L.circle([a.latitude, a.longitude], {
                radius: 400,
                color: '#ef4444',
                weight: 1,
                dashArray: '4, 4',
                fillColor: '#ef4444',
                fillOpacity: 0.05
            }).addTo(map);
        });

        // Add Sensor Inundation Points
        curated.forEach(s => {
            const isHealed = s.data_lineage === "HEALED_INVERTED_COORDINATES";
            const isCritical = s.triage_priority.includes("P1_CRITICAL");
            const color = isCritical ? '#ef4444' : (isHealed ? '#10b981' : '#06b6d4');

            const marker = L.circleMarker([s.latitude, s.longitude], {
                radius: isCritical ? 8 : 6,
                fillColor: color,
                color: '#ffffff',
                weight: 1.5,
                opacity: 1,
                fillOpacity: 0.85
            }).addTo(map);

            marker.bindPopup(`
                <div class="popup-title">🌊 Sensor ${s.sensor_id}</div>
                <div class="popup-row"><span>Status:</span><b>${s.reported_severity}</b></div>
                <div class="popup-row"><span>Water Depth:</span><b>${s.water_depth_cm} cm</b></div>
                <div class="popup-row"><span>Rate of Rise:</span><b>${s.rate_of_rise_cm_hr} cm/hr</b></div>
                <div class="popup-row"><span>Nearest Asset:</span><b>${s.nearest_asset_name}</b></div>
                <div class="popup-row"><span>Geodesic Distance:</span><b>${s.geodesic_distance_meters} m</b></div>
                <div class="popup-row"><span>Lineage:</span><b>${s.data_lineage}</b></div>
            `);
        });

        // Add DBSCAN Corridors
        for (const [cid, cinfo] of Object.entries(clusterData.clusters)) {
            L.circle([cinfo.centroid_lat, cinfo.centroid_lon], {
                radius: 650,
                color: '#06b6d4',
                weight: 1.5,
                dashArray: '6, 6',
                fillColor: '#06b6d4',
                fillOpacity: 0.12
            }).addTo(map).bindPopup(`
                <div class="popup-title">⚡ Inundation Corridor ${cid}</div>
                <div class="popup-row"><span>Sensors Clustered:</span><b>${cinfo.incident_count}</b></div>
                <div class="popup-row"><span>Avg Water Depth:</span><b>${cinfo.avg_water_depth_cm} cm</b></div>
                <div class="popup-row"><span>Peak Rise Rate:</span><b>${cinfo.max_rate_of_rise} cm/hr</b></div>
            `);
        }
    </script>
</body>
</html>
"""
    with open(output_html, mode="w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✔ Successfully generated FloodWatch Dashboard: {output_html}")

if __name__ == "__main__":
    build_dashboard()
