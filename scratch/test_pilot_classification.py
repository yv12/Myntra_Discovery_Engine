"""
Pilot classification test for Phase 4 verification.
Runs on 30 records first, prints side-by-side classifications,
tests invalid tag rejection, tests caching, and checks unclear rates.
"""

import os
import sys
import json

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.classify import DiscoveryClassifier, TaxonomyValidator

def run_pilot():
    narrow_path = "data/stages/stage_02_filtered.jsonl"
    assert os.path.exists(narrow_path), f"Missing {narrow_path}"

    records = []
    with open(narrow_path, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))

    # Pick 30 records: 15 Play Store, 10 Reddit, 5 Survey
    ps = [r for r in records if r["source"] == "play_store"][:15]
    red = [r for r in records if r["source"] == "reddit"][:10]
    surv = [r for r in records if r["source"] == "survey"][:5]
    sample_30 = ps + red + surv
    assert len(sample_30) == 30

    print("=== 1. CLASSIFYING 30 PILOT RECORDS ===")
    classifier = DiscoveryClassifier()
    
    start_cache_len = len(classifier.cache)
    classified_30 = classifier.classify_batch(sample_30)
    end_cache_len = len(classifier.cache)
    print(f"Initial cache entries: {start_cache_len}, New entries saved: {end_cache_len - start_cache_len}")

    unclear_counts = {"wishlist_motive": 0, "blocker_type": 0, "blocker_category": 0, "external_action": 0, "journey_stage": 0}

    print("\n--- 30 PILOT RECORDS REVIEW ---")
    for i, r in enumerate(classified_30, 1):
        txt = " ".join(r["text"].split())
        if len(txt) > 100:
            txt = txt[:97] + "..."
        print(f"\n[{i:2d}] Source: {r['source'].upper()} | ID: {r['record_id'][:8]}")
        print(f"     Text     : {txt}")
        print(f"     Motive   : {r.get('wishlist_motive')}")
        print(f"     Blocker  : {r.get('blocker_type')} ({r.get('blocker_category')})")
        print(f"     Action   : {r.get('external_action')}")
        print(f"     Stage    : {r.get('journey_stage')}")
        print(f"     Status   : {r.get('validation_status')}")

        for dim in unclear_counts:
            if r.get(dim) in ["unclear", "none"]:
                unclear_counts[dim] += 1

    print("\n=== 2. UNCLEAR / NONE RATE CHECK ===")
    for dim, cnt in unclear_counts.items():
        print(f"  {dim}: {cnt}/30 ({cnt/30:.1%}) classified as unclear/none")

    print("\n=== 3. CACHE VERIFICATION (RE-RUNNING SAME 30) ===")
    # Re-run: should be 100% cache hits, 0 new items
    classifier2 = DiscoveryClassifier()
    start_c = len(classifier2.cache)
    re_classified = classifier2.classify_batch(sample_30)
    assert len(re_classified) == 30
    assert len(classifier2.cache) == start_c
    print("Cache hit check passed: 30/30 records served directly from cache without API calls!")

    print("\n=== 4. DELIBERATE INVALID TAG INJECTION TEST ===")
    validator = TaxonomyValidator()
    invalid_record = {
        "wishlist_motive": "invented_motive_tag", # Invalid
        "blocker_type": "price_wait",
        "blocker_category": "psychological",
        "external_action": "none",
        "journey_stage": "saved_waiting"
    }
    is_valid, clean_tags, errors = validator.validate(invalid_record)
    print(f"Validator response on invented tag: is_valid={is_valid}")
    print(f"Reported errors: {errors}")
    assert not is_valid, "Validator should have rejected invented_motive_tag"
    assert clean_tags["wishlist_motive"] == "unclear", "Validator should fallback to unclear on invalid"
    print("Code-level rejection test passed: Invented tags are rejected in code and never silently mapped!")

    print("\n[SUCCESS] Pilot 30 verification complete.")

if __name__ == "__main__":
    run_pilot()
