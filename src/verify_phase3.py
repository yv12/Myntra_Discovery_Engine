"""
Verification script for Phase 3 of the Discovery Engine.
Verifies:
1. Gate arithmetic balance: entering == surviving + dropped for all 4 gates.
2. Target ranges: Broad set near 1,590; Narrow set between 196 and 325.
3. Passthrough sources: Reddit (45) and Survey (39) present in broad and narrow sets.
4. Reads 20 records dropped by Gate 4 (checking for false negatives).
5. Reads 20 records kept by Gate 4 (checking for false positives).
6. Funnel JSON audit trail.
"""

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def verify_phase3():
    broad_path = os.path.join("data", "stages", "stage_02_broad.jsonl")
    narrow_path = os.path.join("data", "stages", "stage_02_filtered.jsonl")
    dropped_path = os.path.join("data", "stages", "stage_02_dropped_narrow.jsonl")
    funnel_path = os.path.join("data", "output", "funnel.json")

    assert os.path.exists(broad_path), f"Missing {broad_path}"
    assert os.path.exists(narrow_path), f"Missing {narrow_path}"
    assert os.path.exists(dropped_path), f"Missing {dropped_path}"
    assert os.path.exists(funnel_path), f"Missing {funnel_path}"

    with open(funnel_path, "r", encoding="utf-8") as f:
        funnel = json.load(f)

    stage2_data = funnel.get("stage_02_filter", {})
    gate_counts = stage2_data.get("play_store_funnel", {})

    print("=== 1. AUDITABLE GATE ARITHMETIC BALANCING ===")
    prev_surviving = None
    for g_id, (gate_name, counts) in enumerate(gate_counts.items(), 1):
        entering = counts["entering"]
        surviving = counts["surviving"]
        dropped = counts["dropped"]
        print(f"Gate {g_id} ({gate_name}):")
        print(f"  Entering:  {entering:,}")
        print(f"  Surviving: {surviving:,}")
        print(f"  Dropped:   {dropped:,}")
        print(f"  Balance Check: {entering} == {surviving} + {dropped} -> {entering == surviving + dropped}")
        assert entering == surviving + dropped, f"Arithmetic failure in {gate_name}"
        if prev_surviving is not None:
            assert entering == prev_surviving, f"Sequential leak: {entering} != {prev_surviving}"
        prev_surviving = surviving

    print("\n=== 2. TARGET BENCHMARK VERIFICATION ===")
    ps_broad = gate_counts["gate_3_wishlist_terms"]["surviving"]
    ps_narrow = gate_counts["gate_4_deliberation_and_blockers"]["surviving"]
    print(f"Play Store Broad set  : {ps_broad:,} (Spec target: ~1,590) -> Delta: {ps_broad - 1590:+d}")
    print(f"Play Store Narrow set : {ps_narrow:,} (Spec target: 196–325) -> Within target range: {196 <= ps_narrow <= 325}")
    assert abs(ps_broad - 1590) <= 20, f"Broad set deviated too far: {ps_broad}"
    assert 196 <= ps_narrow <= 325, f"Narrow set out of target range: {ps_narrow}"

    # Verify Broad file counts
    broad_by_source = {}
    with open(broad_path, "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            src = r["source"]
            broad_by_source[src] = broad_by_source.get(src, 0) + 1
    print("\nBroad set distribution by source:")
    for src, c in sorted(broad_by_source.items()):
        print(f"  - {src}: {c:,}")
    assert broad_by_source["play_store"] == ps_broad
    assert broad_by_source["reddit"] == 45
    assert broad_by_source["survey"] == 39

    # Verify Narrow file counts
    narrow_by_source = {}
    with open(narrow_path, "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            src = r["source"]
            narrow_by_source[src] = narrow_by_source.get(src, 0) + 1
    print("\nNarrow set distribution by source:")
    for src, c in sorted(narrow_by_source.items()):
        print(f"  - {src}: {c:,}")
    assert narrow_by_source["play_store"] == ps_narrow
    assert narrow_by_source["reddit"] == 45
    assert narrow_by_source["survey"] == 39

    # Read 20 Dropped Records
    print("\n=== 3. AUDIT OF 20 RECORDS DROPPED AT GATE 4 (Narrow Gate) ===")
    print("Verifying what was filtered out to ensure no relevant deliberation was discarded:")
    with open(dropped_path, "r", encoding="utf-8") as f:
        dropped_records = [json.loads(line) for line in f]
    
    sample_indices = [int(i * (len(dropped_records) - 1) / 19) for i in range(20)]
    for idx, sample_i in enumerate(sample_indices, 1):
        r = dropped_records[sample_i]
        txt = " ".join(r["text"].split())
        if len(txt) > 130:
            txt = txt[:127] + "..."
        matched = r.get("meta", {}).get("matched_wishlist_terms", [])
        print(f"  {idx:2d}. [Rating {r['meta'].get('rating')}*] (Matched terms: {matched}) -> {txt}")

    # Read 20 Kept Records
    print("\n=== 4. AUDIT OF 20 RECORDS KEPT AT GATE 4 (Narrow Gate - Play Store) ===")
    print("Verifying retained records for genuine structural blockers and deliberation:")
    with open(narrow_path, "r", encoding="utf-8") as f:
        kept_ps = [json.loads(line) for line in f if json.loads(line)["source"] == "play_store"]
        
    kept_sample_indices = [int(i * (len(kept_ps) - 1) / 19) for i in range(20)]
    for idx, sample_i in enumerate(kept_sample_indices, 1):
        r = kept_ps[sample_i]
        txt = " ".join(r["text"].split())
        if len(txt) > 130:
            txt = txt[:127] + "..."
        pattern = r.get("meta", {}).get("matched_filter_pattern")
        print(f"  {idx:2d}. [Rating {r['meta'].get('rating')}*] [Pattern: {pattern}] -> {txt}")

    print("\n[SUCCESS] Phase 3 verification completely passed!")

if __name__ == "__main__":
    verify_phase3()
