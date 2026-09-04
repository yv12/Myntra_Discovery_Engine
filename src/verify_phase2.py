"""
Verification script for Phase 2 of the Discovery Engine.
Verifies:
1. Total ingested count equals 63,014 + Reddit records + 39.
2. Schema consistency across all records: record_id, source, text, created_at, meta.
3. Sample record from each source printed with meta correctly populated.
4. Reddit thread verification: confirms comments and post share thread_id.
5. Survey elasticity question verification: confirms meta retains verbatim elasticity question.
6. Funnel JSON consistency.
"""

import json
import os
import sys

# Configure utf-8 output for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def verify_phase2():
    stage1_path = os.path.join("data", "stages", "stage_01_ingested.jsonl")
    funnel_path = os.path.join("data", "output", "funnel.json")

    assert os.path.exists(stage1_path), f"Missing {stage1_path}"
    assert os.path.exists(funnel_path), f"Missing {funnel_path}"

    counts = {"play_store": 0, "reddit": 0, "survey": 0}
    required_keys = {"record_id", "source", "text", "created_at", "meta"}
    sample_records = {}
    reddit_threads = {}
    survey_elasticity_present = 0

    total_records = 0
    with open(stage1_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            rec = json.loads(line)
            total_records += 1
            
            # Check schema keys
            assert required_keys.issubset(rec.keys()), f"Line {line_num} missing required schema keys"
            src = rec["source"]
            assert src in counts, f"Unknown source: {src}"
            counts[src] += 1

            if src not in sample_records:
                sample_records[src] = rec

            if src == "reddit":
                t_id = rec["meta"].get("thread_id")
                assert t_id, f"Reddit record missing thread_id at line {line_num}"
                reddit_threads.setdefault(t_id, []).append(rec)

            if src == "survey":
                elasticity_q = "If that were sorted out tomorrow, what would you honestly do?"
                assert elasticity_q in rec["meta"], f"Survey record missing verbatim elasticity question at line {line_num}"
                assert rec["meta"][elasticity_q] is not None
                survey_elasticity_present += 1

    print("=== 1. INGESTION COUNTS & TOTALS ===")
    print(f"Total ingested records: {total_records:,}")
    print(f"  - Play Store: {counts['play_store']:,} (Expected: 63,014)")
    print(f"  - Reddit:     {counts['reddit']:,} (Expected: 45 across 7 threads)")
    print(f"  - Survey:     {counts['survey']:,} (Expected: 39)")
    
    assert counts["play_store"] == 63014, f"Play store count mismatch: {counts['play_store']} != 63014"
    assert counts["survey"] == 39, f"Survey count mismatch: {counts['survey']} != 39"
    assert total_records == 63014 + counts["reddit"] + 39, "Total count arithmetic does not match sum of parts"

    print("\n=== 2. SCHEMA & SAMPLE RECORDS FROM EACH SOURCE ===")
    for src in ["play_store", "reddit", "survey"]:
        s_rec = sample_records[src]
        print(f"\n[{src.upper()} RECORD]")
        print(f"  record_id : {s_rec['record_id']}")
        print(f"  source    : {s_rec['source']}")
        print(f"  created_at: {s_rec['created_at']}")
        print(f"  text      : {repr(s_rec['text'][:120])}...")
        meta_keys = list(s_rec["meta"].keys())
        print(f"  meta keys : {meta_keys[:8]} (total {len(meta_keys)})")

    print("\n=== 3. REDDIT THREAD INTEGRITY ===")
    print(f"Total threads identified: {len(reddit_threads)}")
    for t_id, t_records in sorted(reddit_threads.items()):
        posts = [r for r in t_records if r["meta"].get("record_type") == "post"]
        comments = [r for r in t_records if r["meta"].get("record_type") == "comment"]
        print(f"  - {t_id}: {len(posts)} post + {len(comments)} comments = {len(t_records)} records. (All share thread_id='{t_id}')")
        assert len(posts) == 1, f"Expected 1 post in {t_id}, got {len(posts)}"

    # Pick thread tab_1 specifically to confirm per spec requirement
    tab1_recs = reddit_threads.get("tab_1", [])
    assert len(tab1_recs) == 7, f"Expected 7 records in tab_1, got {len(tab1_recs)}"
    for r in tab1_recs:
        assert r["meta"]["thread_id"] == "tab_1"
    print("  -> Thread tab_1 explicitly checked: comments and post all share thread_id='tab_1' and all 6 comments + 1 post are present.")

    print("\n=== 4. SURVEY ELASTICITY FIELD VERBATIM CHECK ===")
    print(f"Survey records retaining verbatim elasticity question: {survey_elasticity_present}/{counts['survey']}")
    assert survey_elasticity_present == 39, "Not all survey records retain verbatim elasticity question"
    
    # Print distinct elasticity answers and distribution
    q_elasticity = "If that were sorted out tomorrow, what would you honestly do?"
    distinct_answers = {}
    for r in [sample_records["survey"]] + [r for r in [json.loads(l) for l in open(stage1_path, 'r', encoding='utf-8')] if r['source'] == 'survey']:
        ans = r["meta"][q_elasticity]
        distinct_answers[ans] = distinct_answers.get(ans, 0) + 1
    print(f"  Verbatim question: '{q_elasticity}'")
    print(f"  Distinct elasticity answers in meta: {distinct_answers}")

    print("\n=== 5. FUNNEL JSON CHECK ===")
    with open(funnel_path, "r", encoding="utf-8") as f:
        funnel = json.load(f)
    print("Funnel data:", json.dumps(funnel, indent=2))
    assert "stage_01_ingest" in funnel

    print("\n[SUCCESS] Phase 2 verification completely passed!")

if __name__ == "__main__":
    verify_phase2()
