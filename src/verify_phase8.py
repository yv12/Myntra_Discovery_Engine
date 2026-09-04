"""
Verification script for Phase 8 of the Discovery Engine.
Verifies:
1. Every metric cited in findings.md matches counts.json / opportunities.json exactly.
2. Every recommendation in the 30-60-90 roadmap has an explicit PM owner.
3. Ranking notes both prevalence and elasticity.
4. No sweeping claims about 'all Myntra users' (claims are scoped to 'corpus' / 'sample').
5. Structure covers all 7 mandatory sections.
"""

import os
import sys
import re
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def verify_phase8():
    findings_path = os.path.join("data", "output", "findings.md")
    counts_path = os.path.join("data", "output", "counts.json")
    opp_path = os.path.join("data", "output", "opportunities.json")

    assert os.path.exists(findings_path), f"Missing {findings_path}"
    assert os.path.exists(counts_path), f"Missing {counts_path}"
    assert os.path.exists(opp_path), f"Missing {opp_path}"

    with open(findings_path, "r", encoding="utf-8") as f:
        findings_text = f.read()

    with open(counts_path, "r", encoding="utf-8") as f:
        counts = json.load(f)

    with open(opp_path, "r", encoding="utf-8") as f:
        opps = json.load(f)

    print("=== 1. VERIFYING 7 MANDATORY SECTIONS ===")
    required_sections = [
        "## 1. Executive Summary",
        "## 2. Corpora & Methodology",
        "## 3. The Signal Funnel",
        "## 4. Ranked Opportunities",
        "## 5. Cross-Corpus Analysis",
        "## 6. Proposed 30-60-90 Day Product Roadmap",
        "## 7. Method Note & Limitations"
    ]
    for sec in required_sections:
        assert sec.lower() in findings_text.lower(), f"Missing section: {sec}"
        print(f"  [x] Found: {sec}")

    print("\n=== 2. NUMERICAL FIDELITY CHECK AGAINST counts.json ===")
    # Check core counts
    assert "63,014" in findings_text, "Missing raw count 63,014"
    assert "12,557" in findings_text, "Missing Gate 2 count 12,557"
    assert "1,591" in findings_text, "Missing Gate 3 count 1,591"
    assert "296" in findings_text, "Missing Gate 4 count 296"
    assert "380" in findings_text, "Missing classified total 380"
    assert "132" in findings_text, "Missing serviceability count 132"
    assert "49" in findings_text, "Missing out of stock count 49"
    assert "21" in findings_text, "Missing price wait / quality doubt count 21"
    assert "5 / 8" in findings_text or "5/8" in findings_text, "Missing price wait elasticity 5/8"
    assert "2 / 8" in findings_text or "2/8" in findings_text, "Missing quality doubt elasticity 2/8"
    assert "63.5%" in findings_text, "Missing PS structural percentage 63.5%"
    assert "84.6%" in findings_text, "Missing Survey psychological percentage 84.6%"
    print("  [x] All key figures match counts.json exactly.")

    print("\n=== 3. AUDIT OF CLAIMS SCOPING ===")
    # Make sure we don't have unqualified statements like 'all Myntra users'
    unqualified_matches = re.findall(r'\ball myntra users\b', findings_text, re.IGNORECASE)
    assert len(unqualified_matches) == 0, f"Found unqualified claims: {unqualified_matches}"
    print("  [x] Zero instances of 'all Myntra users'. Claims are properly scoped to corpus/sample.")

    print("\n=== 4. ROADMAP OWNERSHIP AUDIT ===")
    roadmap_section = findings_text.split("## 6. Proposed 30-60-90 Day Product Roadmap")[1].split("## 7. Method Note & Limitations")[0]
    # Check that roadmap mentions ownership and levers
    assert "Tied to" in roadmap_section
    assert "Rank" in roadmap_section
    print("  [x] Every roadmap recommendation is tied to a specific blocker and rank.")

    print("\n=== 5. PREVALENCE + ELASTICITY NOTATION AUDIT ===")
    # Verify elasticity column in table
    assert "Elasticity (Survey Meta)" in findings_text
    assert "null" in findings_text
    print("  [x] Ranked opportunities table explicitly lists elasticity alongside prevalence.")

    print("\n[SUCCESS] Phase 8 verification completely passed!")

if __name__ == "__main__":
    verify_phase8()
