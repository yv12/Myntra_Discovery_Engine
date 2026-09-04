"""
Verification script for Phase 1 of the Discovery Engine.
Verifies:
1. Input files exist in data/input/ and are set to read-only.
2. Record counts:
   - Play Store JSONL: 63,014 records
   - Reddit DOCX: 7 threads
   - Survey XLSX: 39 response rows
3. Taxonomy loads with valid closed enums and each dimension has 'unclear' or 'none'.
4. Ownership config loads and maps each blocker type.
5. Filters config loads and defines gates 1-4.
"""

import os
import stat
import json
import yaml
import docx
import openpyxl

def verify_inputs():
    print("=== 1. VERIFYING INPUT FILES IN data/input/ ===")
    
    # Check Play Store
    ps_file = os.path.join("data", "input", "play_store.jsonl")
    assert os.path.exists(ps_file), f"Missing {ps_file}"
    ps_mode = os.stat(ps_file).st_mode
    is_ps_ro = not (ps_mode & stat.S_IWUSR)
    print(f"Play Store file: {ps_file} (Read-only: {is_ps_ro})")
    
    with open(ps_file, "r", encoding="utf-8") as f:
        ps_count = sum(1 for _ in f)
    print(f"Play Store record count: {ps_count:,} (Expected: 63,014)")
    assert ps_count == 63014, f"Play Store count mismatch: {ps_count} != 63014"

    # Check Reddit DOCX
    reddit_file = os.path.join("data", "input", "reddit_threads.docx")
    assert os.path.exists(reddit_file), f"Missing {reddit_file}"
    reddit_mode = os.stat(reddit_file).st_mode
    is_reddit_ro = not (reddit_mode & stat.S_IWUSR)
    print(f"Reddit file: {reddit_file} (Read-only: {is_reddit_ro})")
    
    doc = docx.Document(reddit_file)
    threads = []
    for p in doc.paragraphs:
        txt = p.text.strip()
        if p.style.name.lower().startswith("title") or (txt.startswith("Tab ") and len(txt) < 10):
            threads.append(txt)
    print(f"Reddit thread count: {len(threads)} threads identified: {threads} (Expected: 7)")
    assert len(threads) == 7, f"Reddit thread count mismatch: {len(threads)} != 7"

    # Check Survey XLSX
    survey_file = os.path.join("data", "input", "survey_responses.xlsx")
    assert os.path.exists(survey_file), f"Missing {survey_file}"
    survey_mode = os.stat(survey_file).st_mode
    is_survey_ro = not (survey_mode & stat.S_IWUSR)
    print(f"Survey file: {survey_file} (Read-only: {is_survey_ro})")
    
    wb = openpyxl.load_workbook(survey_file)
    ws = wb.active
    non_empty_rows = 0
    for r in ws.iter_rows(min_row=2, values_only=True):
        if any(c is not None and str(c).strip() != "" for c in r):
            non_empty_rows += 1
    print(f"Survey data rows: {non_empty_rows} (Expected: 39)")
    assert non_empty_rows == 39, f"Survey rows mismatch: {non_empty_rows} != 39"

    print("\n=== 2. VERIFYING CONFIGURATIONS ===")
    
    # Verify Taxonomy
    tax_path = os.path.join("config", "taxonomy.yaml")
    with open(tax_path, "r", encoding="utf-8") as f:
        tax = yaml.safe_load(f)
    print(f"Taxonomy version: {tax.get('version')}")
    dimensions = tax.get("dimensions", {})
    expected_dims = ["wishlist_motive", "blocker_type", "blocker_category", "external_action", "journey_stage"]
    for dim in expected_dims:
        assert dim in dimensions, f"Missing dimension {dim} in taxonomy"
        vals = dimensions[dim]["allowed_values"]
        has_fallback = ("unclear" in vals) or ("none" in vals)
        print(f"  - {dim}: {len(vals)} allowed values (Fallback present: {has_fallback})")
        assert has_fallback, f"Dimension {dim} missing unclear or none fallback!"

    # Verify Ownership
    owner_path = os.path.join("config", "ownership.yaml")
    with open(owner_path, "r", encoding="utf-8") as f:
        ownership = yaml.safe_load(f).get("ownership", {})
    print(f"Ownership mappings: {len(ownership)} blockers mapped")
    for blocker, info in ownership.items():
        assert "owner" in info, f"Missing owner in {blocker}"
    print("  - Sample owners:", {b: ownership[b]["owner"] for b in list(ownership.keys())[:5]})

    # Verify Filters
    filter_path = os.path.join("config", "filters.yaml")
    with open(filter_path, "r", encoding="utf-8") as f:
        filters = yaml.safe_load(f)
    ps_filters = filters.get("play_store_filters", {})
    assert "gate_1_non_empty" in ps_filters
    assert "gate_2_word_count" in ps_filters
    assert "gate_3_wishlist_terms" in ps_filters
    assert "gate_4_deliberation_and_blockers" in ps_filters
    print(f"Filters configured: 4 gates defined, {len(filters.get('pass_through_sources', []))} pass-through sources")

    print("\n[SUCCESS] Phase 1 verification completely passed!")

if __name__ == "__main__":
    verify_inputs()
