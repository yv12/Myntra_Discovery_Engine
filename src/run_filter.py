"""
Runner for Stage 2 Filter Funnel.
Reads stage_01_ingested.jsonl, executes sequential gates on Play Store reviews,
passes Reddit and Survey untouched, writes broad and narrow stage files,
and records balanced gate counts in funnel.json.
"""

import os
import sys
import json
from datetime import datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.filter import DiscoveryFilter

def run_filter(
    input_path: str = "data/stages/stage_01_ingested.jsonl",
    broad_output_path: str = "data/stages/stage_02_broad.jsonl",
    narrow_output_path: str = "data/stages/stage_02_filtered.jsonl",
    dropped_narrow_path: str = "data/stages/stage_02_dropped_narrow.jsonl",
    funnel_path: str = "data/output/funnel.json"
):
    print("Initializing DiscoveryFilter...")
    filter_engine = DiscoveryFilter()

    # Track funnel counts per gate
    gate_counts = {
        "gate_1_non_empty": {"entering": 0, "surviving": 0, "dropped": 0},
        "gate_2_word_count": {"entering": 0, "surviving": 0, "dropped": 0},
        "gate_3_wishlist_terms": {"entering": 0, "surviving": 0, "dropped": 0},
        "gate_4_deliberation_and_blockers": {"entering": 0, "surviving": 0, "dropped": 0}
    }
    passthrough_counts = {"reddit": 0, "survey": 0}
    total_ingested = 0

    broad_records = []
    narrow_records = []
    dropped_at_gate_4 = []

    print(f"Reading ingested records from {input_path}...")
    with open(input_path, "r", encoding="utf-8") as in_f:
        for line_num, line in enumerate(in_f, 1):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            total_ingested += 1
            src = rec.get("source")

            # Passthrough sources (Reddit & Survey)
            if src in filter_engine.pass_through_sources:
                passthrough_counts[src] = passthrough_counts.get(src, 0) + 1
                broad_records.append(rec)
                narrow_records.append(rec)
                continue

            # Play Store sequential gates
            # Gate 1: Non-empty text
            gate_counts["gate_1_non_empty"]["entering"] += 1
            if not filter_engine.gate_1_non_empty(rec):
                gate_counts["gate_1_non_empty"]["dropped"] += 1
                continue
            gate_counts["gate_1_non_empty"]["surviving"] += 1

            # Gate 2: Word count >= 15
            gate_counts["gate_2_word_count"]["entering"] += 1
            if not filter_engine.gate_2_word_count(rec):
                gate_counts["gate_2_word_count"]["dropped"] += 1
                continue
            gate_counts["gate_2_word_count"]["surviving"] += 1

            # Gate 3: Wishlist-relevant term
            gate_counts["gate_3_wishlist_terms"]["entering"] += 1
            is_wl, matched_terms = filter_engine.gate_3_wishlist_terms(rec)
            if not is_wl:
                gate_counts["gate_3_wishlist_terms"]["dropped"] += 1
                continue
            gate_counts["gate_3_wishlist_terms"]["surviving"] += 1
            
            # Record survives gates 1-3 -> Broad set
            rec_broad = dict(rec)
            rec_broad.setdefault("meta", {})["filter_stage"] = "broad"
            rec_broad["meta"]["matched_wishlist_terms"] = matched_terms
            broad_records.append(rec_broad)

            # Gate 4: Deliberation or structural blocker
            gate_counts["gate_4_deliberation_and_blockers"]["entering"] += 1
            is_delib, matched_pattern = filter_engine.gate_4_deliberation_and_blockers(rec)
            if not is_delib:
                gate_counts["gate_4_deliberation_and_blockers"]["dropped"] += 1
                rec_dropped = dict(rec_broad)
                rec_dropped["meta"]["dropped_at_gate"] = 4
                dropped_at_gate_4.append(rec_dropped)
                continue
            gate_counts["gate_4_deliberation_and_blockers"]["surviving"] += 1

            # Record survives all 4 gates -> Narrow set
            rec_narrow = dict(rec_broad)
            rec_narrow["meta"]["filter_stage"] = "narrow"
            rec_narrow["meta"]["matched_filter_pattern"] = matched_pattern
            narrow_records.append(rec_narrow)

    # Arithmetic balancing assertions
    print("\nVerifying gate arithmetic balance...")
    for gate_name, counts in gate_counts.items():
        entering = counts["entering"]
        surviving = counts["surviving"]
        dropped = counts["dropped"]
        print(f"  {gate_name}: Entering={entering:,} = Surviving={surviving:,} + Dropped={dropped:,}")
        assert entering == surviving + dropped, f"Arithmetic mismatch in {gate_name}: {entering} != {surviving} + {dropped}"

    # Sequential chain assertions
    assert gate_counts["gate_2_word_count"]["entering"] == gate_counts["gate_1_non_empty"]["surviving"]
    assert gate_counts["gate_3_wishlist_terms"]["entering"] == gate_counts["gate_2_word_count"]["surviving"]
    assert gate_counts["gate_4_deliberation_and_blockers"]["entering"] == gate_counts["gate_3_wishlist_terms"]["surviving"]
    print("Sequential gate chain balances perfectly without leaks.")

    # Write stage files
    os.makedirs(os.path.dirname(broad_output_path), exist_ok=True)
    os.makedirs(os.path.dirname(narrow_output_path), exist_ok=True)
    os.makedirs(os.path.dirname(dropped_narrow_path), exist_ok=True)

    print(f"\nWriting broad set ({len(broad_records):,} records) to {broad_output_path}...")
    with open(broad_output_path, "w", encoding="utf-8") as f:
        for r in broad_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Writing narrow set ({len(narrow_records):,} records) to {narrow_output_path}...")
    with open(narrow_output_path, "w", encoding="utf-8") as f:
        for r in narrow_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Writing gate 4 dropped records ({len(dropped_at_gate_4):,} records) to {dropped_narrow_path}...")
    with open(dropped_narrow_path, "w", encoding="utf-8") as f:
        for r in dropped_at_gate_4:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Update funnel.json
    funnel_data = {}
    if os.path.exists(funnel_path):
        try:
            with open(funnel_path, "r", encoding="utf-8") as f:
                funnel_data = json.load(f)
        except Exception:
            funnel_data = {}

    funnel_data["stage_02_filter"] = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "play_store_funnel": gate_counts,
        "passthrough": passthrough_counts,
        "broad_set_totals": {
            "play_store": gate_counts["gate_3_wishlist_terms"]["surviving"],
            "reddit": passthrough_counts.get("reddit", 0),
            "survey": passthrough_counts.get("survey", 0),
            "total": len(broad_records)
        },
        "narrow_set_totals": {
            "play_store": gate_counts["gate_4_deliberation_and_blockers"]["surviving"],
            "reddit": passthrough_counts.get("reddit", 0),
            "survey": passthrough_counts.get("survey", 0),
            "total": len(narrow_records)
        }
    }

    with open(funnel_path, "w", encoding="utf-8") as f:
        json.dump(funnel_data, f, indent=2)
    print(f"Updated funnel tracking in {funnel_path}")

    return {
        "gate_counts": gate_counts,
        "passthrough": passthrough_counts,
        "broad_total": len(broad_records),
        "narrow_total": len(narrow_records),
        "dropped_gate_4_total": len(dropped_at_gate_4)
    }

if __name__ == "__main__":
    run_filter()
