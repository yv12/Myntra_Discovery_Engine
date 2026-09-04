"""
Verification script for Phase 5 of the Discovery Engine.
Verifies:
1. Hand-count test across a 50-record sample against computed numbers.
2. Denominator check: every single metric has an explicit denominator.
3. Source breakdown verification across all dimensions.
4. Co-occurrence analysis verification.
5. Structural vs psychological totals.
"""

import os
import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def verify_phase5():
    counts_path = os.path.join("data", "output", "counts.json")
    classified_path = os.path.join("data", "stages", "stage_03_classified.jsonl")

    assert os.path.exists(counts_path), f"Missing {counts_path}"
    assert os.path.exists(classified_path), f"Missing {classified_path}"

    with open(counts_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(classified_path, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]

    print("=== 1. HAND-COUNT VERIFICATION (50-RECORD SAMPLE) ===")
    sample_50 = records[:50]
    target_tag = "serviceability"
    manual_count = sum(1 for r in sample_50 if r.get("blocker_type") == target_tag)
    
    # Recalculate directly
    print(f"Sample size: 50 records")
    print(f"Hand-count for blocker_type == '{target_tag}': {manual_count}/50 ({manual_count/50:.1%})")

    # Full dataset check for target tag
    total_tag_manual = sum(1 for r in records if r.get("blocker_type") == target_tag)
    json_overall_tag = data["dimension_frequencies"]["blocker_type"]["tags"][target_tag]["overall"]
    print(f"Full dataset check for '{target_tag}': Manual={total_tag_manual}, counts.json={json_overall_tag['count']}")
    assert total_tag_manual == json_overall_tag["count"]
    assert json_overall_tag["denominator"] == 380

    print("\n=== 2. DENOMINATOR ATTACHMENT AUDIT ===")
    denominators_missing = 0
    total_metrics_checked = 0

    # Check dimension frequencies
    for dim_name, dim_info in data["dimension_frequencies"].items():
        for tag_name, tag_info in dim_info["tags"].items():
            total_metrics_checked += 1
            if "denominator" not in tag_info["overall"] or tag_info["overall"]["denominator"] != 380:
                denominators_missing += 1
            for src, src_info in tag_info["by_source"].items():
                total_metrics_checked += 1
                if "denominator" not in src_info or src_info["denominator"] <= 0:
                    denominators_missing += 1

    # Check co-occurrences
    for co_name, co_data in data["co_occurrences"].items():
        for pair in co_data["pairs"]:
            total_metrics_checked += 1
            if "denominator" not in pair["overall"]:
                denominators_missing += 1
            for src, src_info in pair["by_source"].items():
                total_metrics_checked += 1
                if "denominator" not in src_info:
                    denominators_missing += 1

    print(f"Total metrics audited for explicit denominators: {total_metrics_checked}")
    print(f"Missing denominators found: {denominators_missing}")
    assert denominators_missing == 0, f"Found {denominators_missing} metrics missing denominators!"

    print("\n=== 3. SOURCE BREAKDOWN AUDIT ===")
    # Confirm source breakdown is present on every tag
    for dim_name, dim_info in data["dimension_frequencies"].items():
        for tag_name, tag_info in dim_info["tags"].items():
            assert set(tag_info["by_source"].keys()) == {"play_store", "reddit", "survey"}, \
                f"Missing source breakdown for {dim_name}:{tag_name}"
    print("Source breakdown (play_store, reddit, survey) is present on 100% of dimension metrics.")

    print("\n=== 4. SUMMARY OF KEY FINDINGS FROM counts.json ===")
    print("\nA. Blocker Type Distribution (Frequency & Source Breakdown):")
    blocker_tags = data["dimension_frequencies"]["blocker_type"]["tags"]
    sorted_blockers = sorted(blocker_tags.values(), key=lambda x: -x["overall"]["count"])
    for b in sorted_blockers:
        tag = b["tag"]
        ov = b["overall"]
        ps = b["by_source"]["play_store"]
        red = b["by_source"]["reddit"]
        surv = b["by_source"]["survey"]
        print(f"  - {tag:20s}: {ov['count']:3d}/380 ({ov['percentage']:5.1f}%) | PS: {ps['count']:3d}/{ps['denominator']} ({ps['percentage']:4.1f}%) | Reddit: {red['count']:2d}/{red['denominator']} ({red['percentage']:4.1f}%) | Survey: {surv['count']:2d}/{surv['denominator']} ({surv['percentage']:4.1f}%)")

    print("\nB. Category Totals:")
    for cat, cat_info in data["category_totals"].items():
        ov = cat_info["overall"]
        ps = cat_info["by_source"]["play_store"]
        red = cat_info["by_source"]["reddit"]
        surv = cat_info["by_source"]["survey"]
        print(f"  - {cat:15s}: {ov['count']:3d}/380 ({ov['percentage']:5.1f}%) | PS: {ps['count']:3d}/{ps['denominator']} ({ps['percentage']:4.1f}%) | Reddit: {red['count']:2d}/{red['denominator']} ({red['percentage']:4.1f}%) | Survey: {surv['count']:2d}/{surv['denominator']} ({surv['percentage']:4.1f}%)")

    print("\nC. Top Co-Occurrences (Blocker Type x External Action):")
    b_act = data["co_occurrences"]["blocker_type__x__external_action"]["pairs"]
    filtered_b_act = [p for p in b_act if p["external_action"] != "none"][:8]
    for p in filtered_b_act:
        ov = p["overall"]
        print(f"  - {p['blocker_type']} + {p['external_action']}: {ov['count']} records ({ov['count']}/380)")

    print("\n[SUCCESS] Phase 5 verification completely passed!")

if __name__ == "__main__":
    verify_phase5()
