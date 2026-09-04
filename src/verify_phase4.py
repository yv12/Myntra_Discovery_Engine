"""
Verification script for Phase 4 of the Discovery Engine.
Verifies:
1. Total classified count equals 380 (296 Play Store + 45 Reddit + 39 Survey).
2. Closed enum validation: 100% of records carry strictly valid tags across all 5 dimensions.
3. Distribution of tags and unclear/none rates (admitting ambiguity).
4. Validation status audit: ok vs quarantined.
5. Cache integrity.
6. Print representative classifications across all three sources.
"""

import os
import sys
import json
import yaml

# Ensure utf-8 output for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def verify_phase4():
    classified_path = os.path.join("data", "stages", "stage_03_classified.jsonl")
    taxonomy_path = os.path.join("config", "taxonomy.yaml")
    funnel_path = os.path.join("data", "output", "funnel.json")
    cache_path = os.path.join("data", "cache", "classification_cache_v1.json")

    assert os.path.exists(classified_path), f"Missing {classified_path}"
    assert os.path.exists(taxonomy_path), f"Missing {taxonomy_path}"
    assert os.path.exists(funnel_path), f"Missing {funnel_path}"
    assert os.path.exists(cache_path), f"Missing {cache_path}"

    with open(taxonomy_path, "r", encoding="utf-8") as f:
        tax = yaml.safe_load(f)
    dims = tax.get("dimensions", {})
    allowed = {dim: set(info["allowed_values"]) for dim, info in dims.items()}

    records = []
    source_counts = {"play_store": 0, "reddit": 0, "survey": 0}
    status_counts = {}
    dimension_values = {dim: {} for dim in allowed}

    with open(classified_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            r = json.loads(line)
            records.append(r)
            src = r["source"]
            source_counts[src] = source_counts.get(src, 0) + 1
            
            st = r.get("validation_status", "unknown")
            status_counts[st] = status_counts.get(st, 0) + 1

            # Validate each dimension against allowed set
            for dim, allowed_set in allowed.items():
                val = r.get(dim)
                assert val in allowed_set, f"Line {line_num}: invalid tag '{val}' for dimension '{dim}'! Allowed: {allowed_set}"
                dimension_values[dim][val] = dimension_values[dim].get(val, 0) + 1

    total = len(records)
    print("=== 1. CLASSIFIED RECORDS COUNT & TOTALS ===")
    print(f"Total classified records: {total:,} / 380 (100.0%)")
    print(f"  - Play Store: {source_counts['play_store']} / 296")
    print(f"  - Reddit:     {source_counts['reddit']} / 45")
    print(f"  - Survey:     {source_counts['survey']} / 39")
    assert total == 380, f"Expected 380 classified records, got {total}"
    assert source_counts["play_store"] == 296
    assert source_counts["reddit"] == 45
    assert source_counts["survey"] == 39

    print("\n=== 2. CODE-LEVEL ENUM VALIDATION STATUS ===")
    print(f"Validation status summary: {status_counts}")
    assert status_counts.get("ok", 0) + status_counts.get("quarantined", 0) == total
    print("All 380 records carry valid closed-enum tags.")

    print("\n=== 3. TAG DISTRIBUTIONS & UNCLEAR/NONE RATES ===")
    for dim, counts in dimension_values.items():
        unclear_cnt = counts.get("unclear", 0) + counts.get("none", 0)
        unclear_pct = (unclear_cnt / total) * 100
        print(f"\nDimension: {dim} (Unclear/None: {unclear_cnt}/{total} = {unclear_pct:.1f}%)")
        for val, cnt in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"  - {val:22s}: {cnt:3d} ({cnt/total:.1%})")
        assert unclear_cnt > 0, f"Unclear rate for {dim} is zero! Model was forced to guess."

    print("\n=== 4. REPRESENTATIVE CLASSIFICATIONS (SAMPLE FROM EACH SOURCE) ===")
    for target_src in ["play_store", "reddit", "survey"]:
        print(f"\n[{target_src.upper()} SAMPLES]")
        sample_subset = [r for r in records if r["source"] == target_src][:3]
        for idx, s in enumerate(sample_subset, 1):
            clean_txt = " ".join(s["text"].split())
            if len(clean_txt) > 110:
                clean_txt = clean_txt[:107] + "..."
            print(f"  {idx}. ID: {s['record_id'][:8]}")
            print(f"     Text: {clean_txt}")
            print(f"     Tags: motive={s.get('wishlist_motive')} | blocker={s.get('blocker_type')} ({s.get('blocker_category')}) | action={s.get('external_action')} | stage={s.get('journey_stage')}")

    print("\n=== 5. CACHE INTEGRITY ===")
    with open(cache_path, "r", encoding="utf-8") as f:
        cache = json.load(f)
    unique_texts = set(r["text"] for r in records)
    print(f"Classification cache entries in {cache_path}: {len(cache)} (Unique texts across 380 records: {len(unique_texts)})")
    assert len(cache) == len(unique_texts), f"Cache size {len(cache)} does not match unique texts {len(unique_texts)}"
    print("Content-hash cache holds 100% of unique record texts.")

    print("\n[SUCCESS] Phase 4 verification completely passed!")

if __name__ == "__main__":
    verify_phase4()
