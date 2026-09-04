"""
Runner for Stage 5 Scoring.
Reads stage_03_classified.jsonl, scores opportunities across Prevalence, Elasticity,
and Ownership, ranks them deterministically, and writes data/output/opportunities.json.
"""

import os
import sys
import json
from datetime import datetime

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.score import OpportunityScorer

def run_scoring(
    input_path: str = "data/stages/stage_03_classified.jsonl",
    output_path: str = "data/output/opportunities.json",
    funnel_path: str = "data/output/funnel.json"
):
    print("=" * 60)
    print("STAGE 5: OPPORTUNITY SCORING & RANKING")
    print("=" * 60)

    assert os.path.exists(input_path), f"Missing {input_path}"

    records = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    print(f"Loaded {len(records)} classified records from {input_path}")
    scorer = OpportunityScorer()

    print("Computing separate opportunity dimensions (Prevalence, Elasticity, Ownership)...")
    opportunities = scorer.score_opportunities(records)

    payload = {
        "metadata": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source_classified_file": input_path,
            "total_records_evaluated": len(records),
            "ranking_method": "Sorted by prevalence overall count (descending), then elasticity rate (descending). Dimensions are held strictly separate.",
            "elasticity_rule": "Derived from survey meta only. Blocker types not asked in survey are strictly null, never zero."
        },
        "opportunities": opportunities
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(opportunities)} ranked opportunities to {output_path}")

    # Update funnel.json
    funnel_data = {}
    if os.path.exists(funnel_path):
        try:
            with open(funnel_path, "r", encoding="utf-8") as f:
                funnel_data = json.load(f)
        except Exception:
            funnel_data = {}

    funnel_data["stage_05_score"] = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ranked_opportunity_count": len(opportunities),
        "top_3_opportunities": [
            {
                "rank": opp["rank"],
                "blocker": opp["blocker_type"],
                "prevalence": f"{opp['prevalence']['overall_count']}/{opp['prevalence']['overall_denominator']}",
                "elasticity": opp["elasticity"]["fraction"] if opp["elasticity"] else "null",
                "owner": opp["ownership"]["owner"]
            }
            for opp in opportunities[:3]
        ]
    }

    with open(funnel_path, "w", encoding="utf-8") as f:
        json.dump(funnel_data, f, indent=2)
    print(f"Updated funnel tracking in {funnel_path}")

    return payload

if __name__ == "__main__":
    run_scoring()
