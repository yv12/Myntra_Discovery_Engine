"""
Export script for Dashboard.
Copies generated outputs and classified records into dashboard/
and writes dashboard/data.js as an embedded JavaScript object
so the dashboard runs smoothly both from file:// and http://.
"""

import os
import sys
import json
import shutil

def export_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "data", "output")
    stages_dir = os.path.join(base_dir, "data", "stages")
    dash_dir = os.path.join(base_dir, "dashboard")
    dash_data_dir = os.path.join(dash_dir, "data")

    os.makedirs(dash_data_dir, exist_ok=True)

    # Load output JSON files
    with open(os.path.join(output_dir, "funnel.json"), "r", encoding="utf-8") as f:
        funnel_data = json.load(f)

    with open(os.path.join(output_dir, "counts.json"), "r", encoding="utf-8") as f:
        counts_data = json.load(f)

    with open(os.path.join(output_dir, "opportunities.json"), "r", encoding="utf-8") as f:
        opportunities_data = json.load(f)

    # Load RAG Q&A pairs
    rag_qa_data = []
    rag_qa_path = os.path.join(output_dir, "rag_qa.json")
    if os.path.exists(rag_qa_path):
        with open(rag_qa_path, "r", encoding="utf-8") as f:
            rag_qa_data = json.load(f).get("preset_qa", [])

    # Load all classified records for interactive drill-down
    classified_records = []
    with open(os.path.join(stages_dir, "stage_03_classified.jsonl"), "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                classified_records.append(json.loads(line))

    # Also copy JSON files directly to dashboard/data/
    shutil.copy2(os.path.join(output_dir, "funnel.json"), os.path.join(dash_data_dir, "funnel.json"))
    shutil.copy2(os.path.join(output_dir, "counts.json"), os.path.join(dash_data_dir, "counts.json"))
    shutil.copy2(os.path.join(output_dir, "opportunities.json"), os.path.join(dash_data_dir, "opportunities.json"))
    if os.path.exists(rag_qa_path):
        shutil.copy2(rag_qa_path, os.path.join(dash_data_dir, "rag_qa.json"))

    # Write data.js for zero-dependency static execution
    bundled_payload = {
        "funnel": funnel_data,
        "counts": counts_data,
        "opportunities": opportunities_data["opportunities"],
        "metadata": opportunities_data["metadata"],
        "records": classified_records,
        "rag_qa": rag_qa_data
    }

    data_js_path = os.path.join(dash_dir, "data.js")
    with open(data_js_path, "w", encoding="utf-8") as f:
        f.write("window.ENGINE_DATA = " + json.dumps(bundled_payload, ensure_ascii=False, indent=2) + ";\n")

    print(f"Exported dashboard data to {data_js_path} and {dash_data_dir}")

if __name__ == "__main__":
    export_data()
