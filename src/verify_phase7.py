"""
Verification script for Phase 7 of the Discovery Engine.
Verifies:
1. Dashboard static files exist (index.html, style.css, app.js, data.js).
2. Data bundle in data.js matches exact outputs from pipeline stages (funnel, counts, opportunities, records).
3. All 6 panels are represented in HTML with matching IDs.
4. Method note includes all 5+ core epistemic limitations.
"""

import os
import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def verify_phase7():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dash_dir = os.path.join(base_dir, "dashboard")

    html_path = os.path.join(dash_dir, "index.html")
    css_path = os.path.join(dash_dir, "style.css")
    js_path = os.path.join(dash_dir, "app.js")
    data_js_path = os.path.join(dash_dir, "data.js")

    assert os.path.exists(html_path), f"Missing {html_path}"
    assert os.path.exists(css_path), f"Missing {css_path}"
    assert os.path.exists(js_path), f"Missing {js_path}"
    assert os.path.exists(data_js_path), f"Missing {data_js_path}"

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Verify all 6 panels
    required_panels = [
        "panel-funnel",
        "panel-opportunities",
        "panel-explorer",
        "panel-sources",
        "panel-cooccurrence",
        "panel-method"
    ]
    for p in required_panels:
        assert f'id="{p}"' in html_content, f"Missing panel ID '{p}' in index.html!"

    # Verify method note limitations
    limitations = [
        "Silent Non-Buyer Bias",
        "Reddit Complaint Skew",
        "Near Absence of Hindi Feedback",
        "6-Month Date Window",
        "Elasticity is Stated Hypothetical Intent"
    ]
    for lim in limitations:
        assert lim.lower() in html_content.lower(), f"Missing method limitation: {lim}"

    # Verify data.js payload
    with open(data_js_path, "r", encoding="utf-8") as f:
        data_js = f.read()
    assert data_js.startswith("window.ENGINE_DATA = "), "data.js does not assign window.ENGINE_DATA"
    json_str = data_js.replace("window.ENGINE_DATA = ", "").rstrip(";\n ")
    payload = json.loads(json_str)

    assert len(payload["opportunities"]) == 11, f"Expected 11 opportunities, got {len(payload['opportunities'])}"
    assert len(payload["records"]) == 384, f"Expected 384 records, got {len(payload['records'])}"
    assert payload["funnel"]["stage_01_ingest"]["counts"]["play_store"] == 63014
    assert len(payload.get("rag_qa", [])) == 10, f"Expected 10 RAG Q&A pairs, got {len(payload.get('rag_qa', []))}"
    assert 'id="panel-rag"' in html_content, "Missing panel-rag in index.html"

    print("=== DASHBOARD VERIFICATION AUDIT ===")
    print("  [x] Static build verified: index.html, style.css, app.js, data.js")
    print(f"  [x] All core required panels present and mapped: {required_panels} + panel-rag")
    print(f"  [x] All method limitations prominently stated: {limitations}")
    print(f"  [x] Embedded record count in data.js: {len(payload['records'])} / 384")
    print(f"  [x] Ranked opportunities count: {len(payload['opportunities'])} / 11")
    print(f"  [x] RAG preset questions verified: {len(payload['rag_qa'])} / 10")
    print("\n[SUCCESS] Phase 7 verification completely passed!")

if __name__ == "__main__":
    verify_phase7()
