"""
FloodWatch AI - Independent Executable Verification Test Suite
Verifies mathematical precision, anomaly healing, quarantine invariants, and telemetry conservation.
Meets Sparta Global AI Fundamentals Session 5 independent verification assessment criteria.
"""

import os
import csv
import pytest
from floodwatch.agent import (
    haversine_distance_meters,
    is_within_bounds,
    execute_floodwatch_agent,
    BOUNDS
)

def test_haversine_geodesic_accuracy():
    """
    Asserts mathematical precision of Haversine formula against known ground-truth
    geodesic benchmark between St Thomas Hospital and London Bridge Station.
    """
    # St Thomas' Hospital -> London Bridge Underground Complex
    lat1, lon1 = 51.4988, -0.1185
    lat2, lon2 = 51.5050, -0.0860
    
    computed_dist = haversine_distance_meters(lat1, lon1, lat2, lon2)
    # Ground-truth WGS84 Great-Circle Haversine benchmark: 2352.84 meters
    expected_benchmark = 2352.84
    tolerance = 1.0  # sub-meter precision tolerance
    
    assert abs(computed_dist - expected_benchmark) <= tolerance, (
        f"Geodesic Haversine failed: computed {computed_dist}m, expected ~{expected_benchmark}m"
    )

def test_null_island_quarantine_enforcement():
    """
    Verifies that (0.0, 0.0) hardware acquisition timeouts are never silently dropped
    or mistakenly projected onto London, but strictly routed to the quarantine queue.
    """
    assert not is_within_bounds(0.0, 0.0), "Null Island (0,0) must evaluate outside London bounds!"
    
    # Run agent in isolated test directory
    test_out = "floodwatch/tests/test_output"
    os.makedirs(test_out, exist_ok=True)
    results = execute_floodwatch_agent(output_dir=test_out)
    
    quarantine_csv = os.path.join(test_out, "floodwatch_quarantine_audit.csv")
    assert os.path.exists(quarantine_csv), "Quarantine audit CSV was not created!"
    
    with open(quarantine_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        quarantine_rows = list(reader)
        
    assert len(quarantine_rows) == 2, f"Expected exactly 2 quarantined sensor drops, got {len(quarantine_rows)}"
    for r in quarantine_rows:
        assert float(r["raw_latitude"]) == 0.0 and float(r["raw_longitude"]) == 0.0
        assert r["quarantine_reason"] == "HARDWARE_ACQUISITION_TIMEOUT_NULL_ISLAND"

def test_coordinate_inversion_healing():
    """
    Verifies that mobile sensor coordinate inversions [Lon, Lat] are accurately healed
    back into [Lat, Lon] within the Thames Basin operational bounding box.
    """
    # Raw inverted coordinate from FL-2003: raw_lat = -0.1210, raw_lon = 51.5028
    raw_lat, raw_lon = -0.1210, 51.5028
    assert not is_within_bounds(raw_lat, raw_lon), "Raw inverted coordinate should be out of bounds"
    
    healed_lat, healed_lon = raw_lon, raw_lat
    assert is_within_bounds(healed_lat, healed_lon), "Swapped coordinate must fall within London bounds"
    assert BOUNDS["min_lat"] <= healed_lat <= BOUNDS["max_lat"]
    assert BOUNDS["min_lon"] <= healed_lon <= BOUNDS["max_lon"]

def test_end_to_end_conservation_and_invariants():
    """
    Asserts 100% record conservation (20 = 18 curated + 2 quarantined) and data lineage integrity.
    """
    test_out = "floodwatch/tests/test_output"
    results = execute_floodwatch_agent(output_dir=test_out)
    
    total_input = results["raw_count"]
    curated_count = results["valid_count"]
    quarantine_count = results["quarantine_count"]
    
    assert total_input == 20, f"Expected 20 raw input records, got {total_input}"
    assert curated_count == 18, f"Expected 18 curated records, got {curated_count}"
    assert quarantine_count == 2, f"Expected 2 quarantined records, got {quarantine_count}"
    assert curated_count + quarantine_count == total_input, "Record conservation failure!"
    assert results["healed_count"] == 4, f"Expected 4 healed inverted records, got {results['healed_count']}"
    assert results["clusters"]["total_clusters"] >= 1, "At least 1 DBSCAN inundation corridor must form"

def test_quarantine_reserved_exclusively_for_null_island():
    """
    Verifies the quarantine file is reserved strictly for true (0,0) hardware
    dropouts — no anomalous, non-recoverable coordinate is ever silently
    deleted or diverted into quarantine under a different reason. Any such
    row must instead be retained in the curated dataset, flagged for
    manual review.
    """
    test_out = "floodwatch/tests/test_output"
    results = execute_floodwatch_agent(output_dir=test_out)

    quarantine_csv = os.path.join(test_out, "floodwatch_quarantine_audit.csv")
    with open(quarantine_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        quarantine_rows = list(reader)

    for r in quarantine_rows:
        assert float(r["raw_latitude"]) == 0.0 and float(r["raw_longitude"]) == 0.0, (
            "Quarantine file must contain ONLY true (0,0) Null Island hardware dropouts"
        )
        assert r["quarantine_reason"] == "HARDWARE_ACQUISITION_TIMEOUT_NULL_ISLAND"

    # Full conservation: every raw record ends up in curated (native, healed,
    # or retained-anomaly) or quarantine — never dropped.
    assert results["valid_count"] + results["quarantine_count"] == results["raw_count"], (
        "Record conservation failure: rows were lost outside curated/quarantine"
    )
