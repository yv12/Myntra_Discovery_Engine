"""
Stage 1 Ingestion Runner.
Ingests Play Store, Reddit, and Survey corpora into a unified schema,
writes data/stages/stage_01_ingested.jsonl, and initializes data/output/funnel.json.
"""

import os
import sys
import json
from datetime import datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingest.play_store import load_play_store
from src.ingest.reddit import load_reddit
from src.ingest.survey import load_survey
from src.ingest.interview import load_interviews

def run_ingest(
    play_store_path: str = "data/input/play_store.jsonl",
    reddit_path: str = "data/input/reddit_threads.docx",
    survey_path: str = "data/input/survey_responses.xlsx",
    output_stage_path: str = "data/stages/stage_01_ingested.jsonl",
    funnel_path: str = "data/output/funnel.json"
):
    os.makedirs(os.path.dirname(output_stage_path), exist_ok=True)
    os.makedirs(os.path.dirname(funnel_path), exist_ok=True)

    counts = {
        "play_store": 0,
        "reddit": 0,
        "survey": 0,
        "interview": 0,
        "total": 0
    }

    print("Starting Stage 1 Ingestion...")
    with open(output_stage_path, "w", encoding="utf-8") as out_f:
        # 1. Ingest Play Store
        print("Ingesting Play Store records...")
        for rec in load_play_store(play_store_path):
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            counts["play_store"] += 1
            counts["total"] += 1
            if counts["play_store"] % 10000 == 0:
                print(f"  Processed {counts['play_store']:,} Play Store records...")

        # 2. Ingest Reddit
        print("Ingesting Reddit records...")
        for rec in load_reddit(reddit_path):
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            counts["reddit"] += 1
            counts["total"] += 1

        # 3. Ingest Survey
        print("Ingesting Survey records...")
        for rec in load_survey(survey_path):
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            counts["survey"] += 1
            counts["total"] += 1

        # 4. Ingest User Interviews
        print("Ingesting User Interviews (n=4)...")
        for rec in load_interviews():
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            counts["interview"] += 1
            counts["total"] += 1

    print(f"Ingestion complete. Total records written: {counts['total']:,}")
    print(f"  - Play Store: {counts['play_store']:,}")
    print(f"  - Reddit:     {counts['reddit']:,}")
    print(f"  - Survey:     {counts['survey']:,}")

    # Initialize or update funnel.json
    funnel_data = {}
    if os.path.exists(funnel_path):
        try:
            with open(funnel_path, "r", encoding="utf-8") as f:
                funnel_data = json.load(f)
        except Exception:
            funnel_data = {}

    funnel_data["stage_01_ingest"] = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "counts": counts,
        "description": "Normalized all three raw corpora into stage_01_ingested.jsonl"
    }

    with open(funnel_path, "w", encoding="utf-8") as f:
        json.dump(funnel_data, f, indent=2)
    print(f"Updated {funnel_path}")

    return counts

if __name__ == "__main__":
    run_ingest()
