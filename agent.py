"""
FloodWatch AI - Autonomous Urban Inundation & Asset Risk Agent
Inspired by Google Flood Hub & Google Crisis Response

Autonomously ingests raw storm and river telemetry, detects and heals coordinate
anomalies, isolates hardware timeouts to quarantine, computes spherical geodesic
proximity to critical infrastructure, and executes unsupervised spatial clustering (DBSCAN).
"""

import os
import sys
import csv
import math
import json
from typing import List, Dict, Tuple, Any

# Ensure UTF-8 output across Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

EARTH_RADIUS_METERS = 6371000.0

# Thames Basin / Greater London Operational Bounding Box
BOUNDS = {
    "min_lat": 51.25,
    "max_lat": 51.75,
    "min_lon": -0.55,
    "max_lon": 0.30
}

def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle geodesic distance between two points on Earth using the Haversine formula.
    Preserves metric physical truth across spherical geometry, preventing planar degree distortion.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    
    # Clip numerical floating-point inaccuracies
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_METERS * c

def is_within_bounds(lat: float, lon: float) -> bool:
    """Checks if coordinates reside within the operational flood basin boundary."""
    return (BOUNDS["min_lat"] <= lat <= BOUNDS["max_lat"] and
            BOUNDS["min_lon"] <= lon <= BOUNDS["max_lon"])

def load_critical_assets(filepath: str) -> List[Dict[str, Any]]:
    """Ingests municipal critical infrastructure assets."""
    assets = []
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            assets.append({
                "asset_id": row["asset_id"],
                "asset_name": row["asset_name"],
                "category": row["category"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "criticality_tier": row["criticality_tier"],
                "max_tolerable_inundation_cm": float(row["max_tolerable_inundation_cm"])
            })
    return assets

def run_dbscan(points: List[Dict[str, Any]], eps_meters: float = 650.0, min_samples: int = 3) -> Dict[str, Any]:
    """
    Pure Python implementation of Density-Based Spatial Clustering of Applications with Noise (DBSCAN)
    using spherical Haversine distance. Discovers emergent inundation corridors.
    """
    n = len(points)
    visited = [False] * n
    cluster_labels = [-1] * n  # -1 = Noise
    cluster_id = 0

    def region_query(point_idx: int) -> List[int]:
        p = points[point_idx]
        neighbors = []
        for i, other in enumerate(points):
            dist = haversine_distance_meters(p["latitude"], p["longitude"], other["latitude"], other["longitude"])
            if dist <= eps_meters:
                neighbors.append(i)
        return neighbors

    for i in range(n):
        if visited[i]:
            continue
        visited[i] = True
        neighbors = region_query(i)

        if len(neighbors) < min_samples:
            cluster_labels[i] = -1
        else:
            cluster_id += 1
            cluster_labels[i] = cluster_id
            queue = [idx for idx in neighbors if idx != i]
            
            while queue:
                current_idx = queue.pop(0)
                if not visited[current_idx]:
                    visited[current_idx] = True
                    current_neighbors = region_query(current_idx)
                    if len(current_neighbors) >= min_samples:
                        queue.extend([idx for idx in current_neighbors if idx not in queue])
                if cluster_labels[current_idx] == -1:
                    cluster_labels[current_idx] = cluster_id

    # Aggregate cluster metadata
    clusters_summary = {}
    for i, cid in enumerate(cluster_labels):
        points[i]["cluster_id"] = cid
        if cid != -1:
            cid_str = f"CORRIDOR-{cid}"
            if cid_str not in clusters_summary:
                clusters_summary[cid_str] = {
                    "cluster_id": cid,
                    "incident_count": 0,
                    "total_water_depth_cm": 0.0,
                    "max_rate_of_rise": 0.0,
                    "lats": [],
                    "lons": [],
                    "critical_surge_count": 0
                }
            clusters_summary[cid_str]["incident_count"] += 1
            clusters_summary[cid_str]["total_water_depth_cm"] += points[i]["water_depth_cm"]
            clusters_summary[cid_str]["max_rate_of_rise"] = max(clusters_summary[cid_str]["max_rate_of_rise"], points[i]["rate_of_rise_cm_hr"])
            clusters_summary[cid_str]["lats"].append(points[i]["latitude"])
            clusters_summary[cid_str]["lons"].append(points[i]["longitude"])
            if points[i]["reported_severity"] == "CRITICAL_SURGE":
                clusters_summary[cid_str]["critical_surge_count"] += 1

    # Compute centroids
    for cid_str, data in clusters_summary.items():
        data["centroid_lat"] = round(sum(data["lats"]) / len(data["lats"]), 6)
        data["centroid_lon"] = round(sum(data["lons"]) / len(data["lons"]), 6)
        data["avg_water_depth_cm"] = round(data["total_water_depth_cm"] / data["incident_count"], 1)
        del data["lats"]
        del data["lons"]

    return {
        "total_clusters": cluster_id,
        "clusters": clusters_summary
    }

def execute_floodwatch_agent(
    raw_telemetry_path: str = "floodwatch/data/raw_inundation_telemetry.csv",
    critical_assets_path: str = "floodwatch/data/critical_assets.csv",
    output_dir: str = "floodwatch/output"
) -> Dict[str, Any]:
    """Autonomous ReAct Loop orchestrator for FloodWatch AI."""
    print("================================================================================")
    print("🌊 FloodWatch AI: Autonomous Urban Inundation & Asset Risk Agent")
    print("   Inspired by Google Flood Hub & Google Crisis Response")
    print("================================================================================")
    
    os.makedirs(output_dir, exist_ok=True)
    assets = load_critical_assets(critical_assets_path)
    print(f"[*] Phase 1: Loaded {len(assets)} municipal critical infrastructure assets.")

    curated_records = []
    quarantined_records = []
    
    raw_count = 0
    native_valid_count = 0
    healed_count = 0
    quarantine_count = 0
    retained_anomaly_count = 0

    print("[*] Phase 2: Ingesting raw inundation telemetry & testing coordinate anomalies...")
    with open(raw_telemetry_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_count += 1
            sensor_id = row["sensor_id"]
            raw_lat = float(row["raw_latitude"])
            raw_lon = float(row["raw_longitude"])
            water_depth = float(row["water_depth_cm"])
            rate_rise = float(row["rate_of_rise_cm_hr"])
            velocity = float(row["flow_velocity_mps"])
            sensor_type = row["sensor_type"]
            severity = row["reported_severity"]
            timestamp = row["timestamp"]

            # Anomaly Test 1: Null Island (0,0) Hardware Timeouts
            if abs(raw_lat) < 0.0001 and abs(raw_lon) < 0.0001:
                quarantined_records.append({
                    "sensor_id": sensor_id,
                    "timestamp": timestamp,
                    "raw_latitude": raw_lat,
                    "raw_longitude": raw_lon,
                    "quarantine_reason": "HARDWARE_ACQUISITION_TIMEOUT_NULL_ISLAND",
                    "action_required": "DISPATCH_FIELD_TECHNICIAN_REBOOT",
                    "sensor_type": sensor_type
                })
                quarantine_count += 1
                continue

            # Anomaly Test 2: In-bounds check
            if is_within_bounds(raw_lat, raw_lon):
                curated_records.append({
                    "sensor_id": sensor_id,
                    "timestamp": timestamp,
                    "latitude": raw_lat,
                    "longitude": raw_lon,
                    "water_depth_cm": water_depth,
                    "rate_of_rise_cm_hr": rate_rise,
                    "flow_velocity_mps": velocity,
                    "sensor_type": sensor_type,
                    "reported_severity": severity,
                    "data_lineage": "NATIVE_VERIFIED_VALID"
                })
                native_valid_count += 1
            else:
                # Anomaly Test 3: Coordinate Inversion Healing [Lon, Lat] -> [Lat, Lon]
                swapped_lat = raw_lon
                swapped_lon = raw_lat
                if is_within_bounds(swapped_lat, swapped_lon):
                    curated_records.append({
                        "sensor_id": sensor_id,
                        "timestamp": timestamp,
                        "latitude": swapped_lat,
                        "longitude": swapped_lon,
                        "water_depth_cm": water_depth,
                        "rate_of_rise_cm_hr": rate_rise,
                        "flow_velocity_mps": velocity,
                        "sensor_type": sensor_type,
                        "reported_severity": severity,
                        "data_lineage": "HEALED_INVERTED_COORDINATES"
                    })
                    healed_count += 1
                else:
                    # Not (0,0), and neither native nor swapped coordinates fall
                    # within the Thames Basin. Per policy, the quarantine file is
                    # reserved strictly for true (0,0) hardware dropouts, and no
                    # anomalous row may be silently deleted — so this record is
                    # retained in the curated set (using its raw, unhealed
                    # coordinates) and flagged for manual GIS review instead.
                    curated_records.append({
                        "sensor_id": sensor_id,
                        "timestamp": timestamp,
                        "latitude": raw_lat,
                        "longitude": raw_lon,
                        "water_depth_cm": water_depth,
                        "rate_of_rise_cm_hr": rate_rise,
                        "flow_velocity_mps": velocity,
                        "sensor_type": sensor_type,
                        "reported_severity": severity,
                        "data_lineage": "RETAINED_UNRESOLVED_ANOMALY_MANUAL_GIS_REVIEW"
                    })
                    retained_anomaly_count += 1

    print(f"    - Total Telemetry Ingested:     {raw_count}")
    print(f"    - Native Valid Coordinates:     {native_valid_count}")
    print(f"    - Self-Healed Inversions:       {healed_count}")
    print(f"    - Retained Unresolved Anomalies:{retained_anomaly_count} (flagged, not quarantined)")
    print(f"    - Quarantined (True 0,0 Only):  {quarantine_count}")

    # Phase 3: Geodesic Proximity Engine
    print("[*] Phase 3: Computing Haversine geodesic proximity to critical infrastructure...")
    for rec in curated_records:
        closest_asset = None
        min_dist = float("inf")
        for asset in assets:
            dist = haversine_distance_meters(
                rec["latitude"], rec["longitude"],
                asset["latitude"], asset["longitude"]
            )
            if dist < min_dist:
                min_dist = dist
                closest_asset = asset

        rec["nearest_asset_id"] = closest_asset["asset_id"]
        rec["nearest_asset_name"] = closest_asset["asset_name"]
        rec["nearest_asset_category"] = closest_asset["category"]
        rec["geodesic_distance_meters"] = round(min_dist, 1)

        # Operational Triage Matrix
        if min_dist <= 400.0 and (rec["water_depth_cm"] >= 120.0 or rec["rate_of_rise_cm_hr"] >= 25.0):
            rec["triage_priority"] = "P1_CRITICAL_SURGE"
        elif min_dist <= 800.0 or rec["water_depth_cm"] >= 100.0:
            rec["triage_priority"] = "P2_ELEVATED_RISK"
        else:
            rec["triage_priority"] = "P3_MONITORING"

    # Phase 4: Dynamic Spatial Clustering (DBSCAN)
    print("[*] Phase 4: Discovering emergent inundation corridors via DBSCAN (eps=650m, min=3)...")
    cluster_results = run_dbscan(curated_records, eps_meters=650.0, min_samples=3)
    print(f"    - Inundation Corridors Discovered: {cluster_results['total_clusters']}")
    for cid_str, cdata in cluster_results["clusters"].items():
        print(f"      • {cid_str}: {cdata['incident_count']} sensors, Centroid=({cdata['centroid_lat']}, {cdata['centroid_lon']}), Avg Depth={cdata['avg_water_depth_cm']}cm")

    # Phase 5: Synthesis & Export
    print("[*] Phase 5: Exporting curated datasets and audit logs...")
    curated_csv_path = os.path.join(output_dir, "floodwatch_curated_telemetry.csv")
    with open(curated_csv_path, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = list(curated_records[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(curated_records)

    quarantine_csv_path = os.path.join(output_dir, "floodwatch_quarantine_audit.csv")
    with open(quarantine_csv_path, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = list(quarantined_records[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(quarantined_records)

    clusters_json_path = os.path.join(output_dir, "floodwatch_clusters.json")
    with open(clusters_json_path, mode="w", encoding="utf-8") as f:
        json.dump(cluster_results, f, indent=2)

    print(f"    - Curated Telemetry: {curated_csv_path}")
    print(f"    - Quarantine Audit:  {quarantine_csv_path}")
    print(f"    - Spatial Clusters:  {clusters_json_path}")
    print("================================================================================")
    print("✔ FloodWatch AI Autonomous Run Complete. Conservation & Lineage 100% Intact.")
    print("================================================================================")

    return {
        "raw_count": raw_count,
        "valid_count": len(curated_records),
        "healed_count": healed_count,
        "retained_anomaly_count": retained_anomaly_count,
        "quarantine_count": quarantine_count,
        "clusters": cluster_results
    }

if __name__ == "__main__":
    execute_floodwatch_agent()
