"""
Stage 3 Classifier for Discovery Engine.
Implements batch LLM classification with strict code-level closed-enum validation,
retry-once on failure, quarantine on second failure, content-hash caching,
and echoed ID alignment to prevent positional contamination.
"""

import os
import json
import yaml
import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple
from groq import Groq

class TaxonomyValidator:
    def __init__(self, taxonomy_path: str = "config/taxonomy.yaml"):
        with open(taxonomy_path, "r", encoding="utf-8") as f:
            self.raw_cfg = yaml.safe_load(f)
            
        self.version = self.raw_cfg.get("version", "v1")
        self.dimensions = {}
        for dim_name, dim_cfg in self.raw_cfg.get("dimensions", {}).items():
            self.dimensions[dim_name] = {
                "allowed": set(dim_cfg["allowed_values"]),
                "default": dim_cfg.get("default_fallback", "unclear")
            }

    def validate(self, tags: Dict[str, Any]) -> Tuple[bool, Dict[str, str], List[str]]:
        """
        Validates tags against taxonomy closed enums.
        Returns: (is_valid, validated_tags, error_list)
        No nearest-neighbour mapping. An invalid tag fails validation.
        """
        errors = []
        clean_tags = {}
        for dim, info in self.dimensions.items():
            val = tags.get(dim)
            if val is None:
                errors.append(f"Missing dimension: {dim}")
                clean_tags[dim] = info["default"]
            elif val not in info["allowed"]:
                errors.append(f"Invalid value for {dim}: '{val}'. Allowed: {sorted(list(info['allowed']))}")
                clean_tags[dim] = info["default"]
            else:
                clean_tags[dim] = str(val)
                
        is_valid = (len(errors) == 0)
        return is_valid, clean_tags, errors


class DiscoveryClassifier:
    def __init__(
        self,
        taxonomy_path: str = "config/taxonomy.yaml",
        cache_dir: str = "data/cache",
        quarantine_dir: str = "data/quarantine",
        model: str = "openai/gpt-oss-120b",
        api_key: Optional[str] = None
    ):
        self.validator = TaxonomyValidator(taxonomy_path)
        self.taxonomy_version = self.validator.version
        self.cache_dir = cache_dir
        self.quarantine_dir = quarantine_dir
        self.model = model
        
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(quarantine_dir, exist_ok=True)
        
        self.cache_file = os.path.join(cache_dir, f"classification_cache_{self.taxonomy_version}.json")
        self.cache: Dict[str, Dict[str, Any]] = self._load_cache()
        
        key = api_key or os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=key)

    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def get_cache_key(self, text: str) -> str:
        """Cache key includes both taxonomy version and text."""
        raw = f"{self.taxonomy_version}:{text}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _build_prompt(self, items: List[Dict[str, str]]) -> str:
        """
        Embeds taxonomy definitions and examples.
        Demands echo of exact item IDs in a JSON array.
        Explicitly instructs that 'unclear' / 'none' are valid and expected.
        """
        dim_desc = []
        for dim, info in self.validator.dimensions.items():
            vals = sorted(list(info["allowed"]))
            dim_desc.append(f"- {dim}: must be strictly one of {vals}")
        dimensions_block = "\n".join(dim_desc)

        items_json = json.dumps(items, ensure_ascii=False, indent=2)

        prompt = f"""You are a strict data classifier for an e-commerce fashion discovery engine studying why wishlisted/saved items do not convert to purchases.

Classify each item independently. Do NOT invent new tags. Only use values from the allowed closed taxonomy below.
'unclear' and 'none' are legitimate and expected answers when context is ambiguous or no blocker applies. Never guess a label.

ALLOWED TAXONOMY:
{dimensions_block}

DEFINITIONS & GUIDELINES:
1. wishlist_motive:
   - price_watch: saving to wait for price drop, sale, or discount
   - fit_uncertainty: saved because unsure about size, fit, or dimensions
   - budget_timing: saved until salary/payday or budget permits
   - occasion: saved for a specific upcoming event/function
   - aspirational: saved as inspiration, luxury item, or dream purchase
   - comparison_shortlist: saved alongside other options to decide between them
   - gifting: saved to buy for someone else
   - unclear: cannot tell motive from text

2. blocker_type:
   - price_wait: waiting for price drop or sale to happen
   - budget_constraint: lacks money / too expensive overall regardless of small discounts
   - quality_doubt: worried item will not match photos, fabric doubt, fake/poor quality concern
   - fit_doubt: uncertain about sizing chart, fit, or body match
   - decision_paralysis: cannot pick between shortlisted alternatives
   - size_unavailable: specific size needed is not in stock
   - out_of_stock: entire item is sold out / unavailable
   - serviceability: pincode not deliverable / courier cannot reach location
   - cod_unavailable: cash on delivery not offered or blocked
   - no_reviews: lack of customer photos or reviews to make informed choice
   - forgot_wishlist: forgot it was in wishlist, item got buried
   - none: no blocker mentioned

3. blocker_category:
   - structural: platform/operations prevented purchase (out of stock, size missing, pincode unserviceable, COD off, app bug)
   - psychological: user hesitated internally (quality doubt, price hesitation, paralysis, fit doubt)
   - both: compounds both structural and psychological factors
   - none: no blocker

4. external_action:
   - checked_other_platform: searched or compared on Amazon, Ajio, Flipkart, brand site
   - bought_elsewhere: purchased same or alternate item from another store/platform
   - asked_someone: asked friends/family for opinion
   - none: stayed on platform / no external action mentioned
   - unclear: not specified

5. journey_stage:
   - pre_save: browsing, deliberating before saving
   - saved_waiting: item is saved, waiting for price/time/decision
   - returned_blocked: came back to buy but hit a blocker (stock/price hike/pincode)
   - abandoned: decided definitely not to buy / removed from list
   - purchased: transacted or bought
   - unclear: stage unknown

ITEMS TO CLASSIFY:
{items_json}

Return a valid JSON array of objects, with NO surrounding Markdown fences or commentary.
Each object must have the exact echoed 'id' and the 5 dimension keys:
[
  {{
    "id": "item_id",
    "wishlist_motive": "...",
    "blocker_type": "...",
    "blocker_category": "...",
    "external_action": "...",
    "journey_stage": "..."
  }}
]"""
        return prompt

    def _call_model(self, prompt: str) -> List[Dict[str, Any]]:
        """Invokes Groq with temperature=0.0 for deterministic outputs."""
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=4096
        )
        content = resp.choices[0].message.content.strip()
        # Clean any accidental markdown fencing
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()
            
        parsed = json.loads(content)
        if isinstance(parsed, dict) and "items" in parsed:
            parsed = parsed["items"]
        if not isinstance(parsed, list):
            raise ValueError(f"Expected JSON list, got {type(parsed)}")
        return parsed

    def classify_batch(
        self,
        records: List[Dict[str, Any]],
        batch_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Classifies records in sub-batches of batch_size (default 10).
        Checks cache, calls LLM for uncached, validates enums in code, retries, and quarantines.
        """
        all_results = []
        total_records = len(records)
        
        for start_idx in range(0, total_records, batch_size):
            chunk = records[start_idx : start_idx + batch_size]
            b_num = start_idx // batch_size + 1
            total_b = (total_records + batch_size - 1) // batch_size
            print(f"  [Batch {b_num}/{total_b}] Processing {len(chunk)} records...", flush=True)
            chunk_res = self._process_sub_batch(chunk)
            all_results.extend(chunk_res)
            self._save_cache()
            
        return all_results

    def _process_sub_batch(
        self,
        chunk: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        results = [None] * len(chunk)
        uncached_indices = []
        items_to_send = []

        # 1. Cache lookup
        for idx, rec in enumerate(chunk):
            ck = self.get_cache_key(rec["text"])
            if ck in self.cache:
                cached_res = dict(self.cache[ck])
                out_rec = dict(rec)
                out_rec.update(cached_res)
                out_rec["validation_status"] = "ok"
                out_rec["classifier_version"] = self.taxonomy_version
                results[idx] = out_rec
            else:
                uncached_indices.append(idx)
                items_to_send.append({
                    "id": f"item_{idx}",
                    "text": rec["text"]
                })

        if not items_to_send:
            return results

        # 2. Call LLM for uncached items
        prompt = self._build_prompt(items_to_send)
        raw_outputs = []
        try:
            raw_outputs = self._call_model(prompt)
        except Exception as e:
            print(f"Model call failed: {e}. Retrying after 2s...", flush=True)
            time.sleep(2)
            try:
                raw_outputs = self._call_model(prompt)
            except Exception as e2:
                print(f"Model call failed second time: {e2}. Quarantining sub-batch.", flush=True)
                raw_outputs = []

        output_map = {item.get("id"): item for item in raw_outputs if isinstance(item, dict) and "id" in item}

        failed_indices = []

        # 3. Validate results in code
        for idx in uncached_indices:
            item_id = f"item_{idx}"
            item_tags = output_map.get(item_id, {})
            is_valid, clean_tags, errors = self.validator.validate(item_tags)
            
            rec = chunk[idx]
            out_rec = dict(rec)
            out_rec["classifier_version"] = self.taxonomy_version

            if is_valid:
                out_rec.update(clean_tags)
                out_rec["validation_status"] = "ok"
                ck = self.get_cache_key(rec["text"])
                self.cache[ck] = clean_tags
                results[idx] = out_rec
            else:
                failed_indices.append((idx, errors))

        # 4. Retry once for any failures
        if failed_indices:
            print(f"Retrying {len(failed_indices)} failed records individually...", flush=True)
            quarantined_file = os.path.join(self.quarantine_dir, "quarantined_records.jsonl")
            
            for idx, orig_errs in failed_indices:
                rec = chunk[idx]
                single_item = [{"id": f"retry_{idx}", "text": rec["text"]}]
                retry_prompt = self._build_prompt(single_item)
                retry_success = False
                try:
                    time.sleep(1)
                    retry_raw = self._call_model(retry_prompt)
                    if retry_raw and isinstance(retry_raw[0], dict):
                        is_valid, clean_tags, errs = self.validator.validate(retry_raw[0])
                        if is_valid:
                            out_rec = dict(rec)
                            out_rec.update(clean_tags)
                            out_rec["classifier_version"] = self.taxonomy_version
                            out_rec["validation_status"] = "ok"
                            ck = self.get_cache_key(rec["text"])
                            self.cache[ck] = clean_tags
                            results[idx] = out_rec
                            retry_success = True
                except Exception as ex:
                    print(f"Retry call failed for index {idx}: {ex}", flush=True)

                # 5. Quarantine on second failure
                if not retry_success:
                    print(f"Quarantining record {rec.get('record_id')}", flush=True)
                    out_rec = dict(rec)
                    for dim, info in self.validator.dimensions.items():
                        out_rec[dim] = info["default"]
                    out_rec["classifier_version"] = self.taxonomy_version
                    out_rec["validation_status"] = "quarantined"
                    out_rec["quarantine_reason"] = "; ".join(orig_errs)
                    results[idx] = out_rec
                    
                    with open(quarantined_file, "a", encoding="utf-8") as qf:
                        qf.write(json.dumps(out_rec, ensure_ascii=False) + "\n")

        return results
