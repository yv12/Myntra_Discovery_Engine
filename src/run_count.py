"""
Runner for Stage 4 Counting.
Reads stage_03_classified.jsonl, computes all tag frequencies and co-occurrences
in pure Python with strict denominators and source breakdowns, and writes counts.json.
"""

import os
import sys
import json
import yaml
from datetime import datetime

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.count import (
    compute_dimension_frequencies,
    compute_co_occurrences,
    compute_category_totals
)

def run_counting(
    input_path: str = "data/stages/stage_03_classified.jsonl",
    taxonomy_path: str = "config/taxonomy.yaml",
    output_path: str = "data/output/counts.json",
    funnel_path: str = "data/output/funnel.json"
):
    print("=" * 60)
    print("STAGE 4: ARITHMETIC COUNTING & CO-OCCURRENCE (PURE PYTHON)")
    print("=" * 60)

    assert os.path.exists(input_path), f"Missing {input_path}"
    assert os.path.exists(taxonomy_path), f"Missing {taxonomy_path}"

    with open(taxonomy_path, "r", encoding="utf-8") as f:
        tax_cfg = yaml.safe_load(f)

    dimensions = list(tax_cfg.get("dimensions", {}).keys())
    allowed_values = {
        dim: tax_cfg["dimensions"][dim]["allowed_values"]
        for dim in dimensions
    }

    records = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    total_records = len(records)
    source_counts = {}
    for r in records:
        src = r["source"]
        source_counts[src] = source_counts.get(src, 0) + 1

    print(f"Loaded {total_records} records:")
    for src, c in sorted(source_counts.items()):
        print(f"  - {src}: {c} records")

    # 1. Dimension frequencies
    print("\nComputing dimension frequencies with source breakdown...")
    dim_frequencies = compute_dimension_frequencies(records, dimensions, allowed_values)

    # 2. Co-occurrences
    print("Computing co-occurrence pairs...")
    co_occ_blocker_cat = compute_co_occurrences(records, "blocker_type", "blocker_category")
    co_occ_blocker_act = compute_co_occurrences(records, "blocker_type", "external_action")
    co_occ_blocker_stage = compute_co_occurrences(records, "blocker_type", "journey_stage")
    co_occ_motive_blocker = compute_co_occurrences(records, "wishlist_motive", "blocker_type")

    # 3. Category totals
    print("Computing structural vs psychological category totals...")
    category_totals = compute_category_totals(records)

    # Assemble output payload
    output_data = {
        "metadata": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source_file": input_path,
            "total_records": total_records,
            "denominators": {
                "overall": total_records,
                "by_source": source_counts
            },
            "description": "Deterministic counts and co-occurrences computed in plain Python. Every count carries its explicit denominator and source breakdown."
        },
        "dimension_frequencies": dim_frequencies,
        "category_totals": category_totals,
        "co_occurrences": {
            "blocker_type__x__blocker_category": co_occ_blocker_cat,
            "blocker_type__x__external_action": co_occ_blocker_act,
            "blocker_type__x__journey_stage": co_occ_blocker_stage,
            "wishlist_motive__x__blocker_type": co_occ_motive_blocker
        }
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"\nWrote full auditable counts to {output_path}")

    # Update funnel.json
    funnel_data = {}
    if os.path.exists(funnel_path):
        try:
            with open(funnel_path, "r", encoding="utf-8") as f:
                funnel_data = json.load(f)
        except Exception:
            funnel_data = {}

    funnel_data["stage_04_count"] = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_records": total_records,
        "denominators": source_counts,
        "structural_total": category_totals["structural"]["overall"]["count"],
        "psychological_total": category_totals["psychological"]["overall"]["count"],
        "both_total": category_totals["both"]["overall"]["count"],
        "none_total": category_totals["none"]["overall"]["count"]
    }

    with open(funnel_path, "w", encoding="utf-8") as f:
        json.dump(funnel_data, f, indent=2)
    print(f"Updated funnel tracking in {funnel_path}")

    return output_data

if __name__ == "__main__":
    run_counting()
