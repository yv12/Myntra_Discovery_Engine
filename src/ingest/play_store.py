"""
Play Store loader for Discovery Engine.
Reads raw Play Store JSONL and converts records to the standard ingestion schema.
"""

import json
import hashlib
from typing import Iterator, Dict, Any

def load_play_store(file_path: str = "data/input/play_store.jsonl") -> Iterator[Dict[str, Any]]:
    """
    Yields normalized records from Play Store JSONL.
    Schema:
      - record_id: sha256 of "play_store:" + original id
      - source: "play_store"
      - text: review text
      - created_at: ISO 8601 string or None
      - meta: { rating, matched_terms, original_id, ... }
    """
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            orig_id = str(rec.get("id", ""))
            
            # SHA256 record_id
            record_id = hashlib.sha256(f"play_store:{orig_id}".encode("utf-8")).hexdigest()
            
            normalized = {
                "record_id": record_id,
                "source": "play_store",
                "text": rec.get("text", "") or "",
                "created_at": rec.get("created_at"),
                "meta": {
                    "original_id": orig_id,
                    "rating": rec.get("rating"),
                    "matched_terms": rec.get("matched_terms", []),
                    "app_id": rec.get("app_id", "com.myntra.android"),
                    "lang": rec.get("lang"),
                    "country": rec.get("country"),
                    "thumbs_up": rec.get("thumbs_up"),
                    "review_created_version": rec.get("review_created_version"),
                    "reply_content": rec.get("reply_content"),
                    "collected_at": rec.get("collected_at")
                }
            }
            yield normalized
