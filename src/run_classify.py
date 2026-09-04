"""
Runner for Stage 3 Classification.
Reads stage_02_filtered.jsonl (380 records: 296 Play Store + 45 Reddit + 39 Survey),
classifies them using DiscoveryClassifier with batching, code-level enum enforcement,
retry-once, quarantine on persistent failure, and content-hash caching.
Writes stage_03_classified.jsonl and updates funnel.json.
"""

import os
import sys
import json
import time
from datetime import datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.classify import DiscoveryClassifier

def run_classification(
    input_path: str = "data/stages/stage_02_filtered.jsonl",
    output_path: str = "data/stages/stage_03_classified.jsonl",
    funnel_path: str = "data/output/funnel.json",
    batch_size: int = 10
):
    print("=" * 60)
    print("STAGE 3: BATCH CLASSIFICATION WITH ENUM ENFORCEMENT")
    print("=" * 60)

    assert os.path.exists(input_path), f"Missing {input_path}"
    
    records = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    total_records = len(records)
    print(f"Loaded {total_records} records to classify from {input_path}")
    print(f"  - Play Store: {sum(1 for r in records if r['source'] == 'play_store')}")
    print(f"  - Reddit:     {sum(1 for r in records if r['source'] == 'reddit')}")
    print(f"  - Survey:     {sum(1 for r in records if r['source'] == 'survey')}")

    classifier = DiscoveryClassifier()
    start_time = time.time()

    print(f"\nClassifying in batches of {batch_size}...")
    classified_records = classifier.classify_batch(records, batch_size=batch_size)
    elapsed = time.time() - start_time
    print(f"\nClassification completed in {elapsed:.1f}s")

    # Audit validation statuses
    status_counts = {"ok": 0, "quarantined": 0}
    for r in classified_records:
        st = r.get("validation_status", "unknown")
        status_counts[st] = status_counts.get(st, 0) + 1

    print(f"Validation summary: {status_counts}")

    # Write output stage file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for r in classified_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {len(classified_records)} classified records to {output_path}")

    # Update funnel.json
    funnel_data = {}
    if os.path.exists(funnel_path):
        try:
            with open(funnel_path, "r", encoding="utf-8") as f:
                funnel_data = json.load(f)
        except Exception:
            funnel_data = {}

    funnel_data["stage_03_classify"] = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_records": total_records,
        "validation_summary": status_counts,
        "model": classifier.model,
        "taxonomy_version": classifier.taxonomy_version,
        "elapsed_seconds": round(elapsed, 2)
    }

    with open(funnel_path, "w", encoding="utf-8") as f:
        json.dump(funnel_data, f, indent=2)
    print(f"Updated {funnel_path}")

    return classified_records

if __name__ == "__main__":
    run_classification()
