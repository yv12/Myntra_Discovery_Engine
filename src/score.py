"""
Stage 5 Scoring Module for Discovery Engine.
Computes the independent opportunity dimensions:
1. Prevalence (with explicit denominator and 4-way source breakdown)
2. Source-Weighted Ranking (interview > survey > reddit > play_store)
3. Elasticity (derived from survey meta ONLY, strictly null where not surveyed, never zero)
4. PM Ownership (static mapping from config)

Keeps all dimensions separate — never collapsed into an opaque composite score.
"""

import os
import yaml
from collections import defaultdict
from typing import Dict, Any, List, Optional

class OpportunityScorer:
    def __init__(
        self,
        ownership_path: str = "config/ownership.yaml",
        taxonomy_path: str = "config/taxonomy.yaml",
        scoring_path: str = "config/scoring.yaml"
    ):
        with open(ownership_path, "r", encoding="utf-8") as f:
            self.ownership_cfg = yaml.safe_load(f).get("ownership", {})

        with open(taxonomy_path, "r", encoding="utf-8") as f:
            self.tax_cfg = yaml.safe_load(f)

        self.blocker_types = self.tax_cfg["dimensions"]["blocker_type"]["allowed_values"]
        self.survey_mapping = self.tax_cfg.get("survey_blocker_mapping", {})

        # Load source weights
        self.source_weights = {
            "interview": 4.0,
            "survey": 3.0,
            "reddit": 1.5,
            "play_store": 1.0
        }
        if os.path.exists(scoring_path):
            try:
                with open(scoring_path, "r", encoding="utf-8") as f:
                    sc_data = yaml.safe_load(f)
                    if sc_data and "source_weights" in sc_data:
                        self.source_weights = sc_data["source_weights"]
            except Exception:
                pass

    def compute_prevalence(
        self,
        records: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Computes prevalence count and percentage per blocker overall and per source.
        """
        total = len(records)
        sources = set(r["source"] for r in records)
        source_totals = {src: sum(1 for r in records if r["source"] == src) for src in sources}

        prevalence_by_blocker = {}
        for b in self.blocker_types:
            b_records = [r for r in records if r.get("blocker_type") == b]
            cnt = len(b_records)
            
            by_src = {}
            for src in sorted(sources):
                s_cnt = sum(1 for r in b_records if r["source"] == src)
                s_den = source_totals[src]
                by_src[src] = {
                    "count": s_cnt,
                    "denominator": s_den,
                    "percentage": round((s_cnt / s_den) * 100, 2) if s_den else 0.0
                }

            prevalence_by_blocker[b] = {
                "overall_count": cnt,
                "overall_denominator": total,
                "overall_percentage": round((cnt / total) * 100, 2) if total else 0.0,
                "by_source": by_src
            }

        return prevalence_by_blocker

    def compute_weighted_scores(
        self,
        records: List[Dict[str, Any]],
        prevalence: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Computes source-weighted prevalence rates where interview > survey > reddit > play_store.
        De-inflates complaint-volume bias from public app reviews.
        """
        sources = set(r["source"] for r in records)
        source_totals = {src: sum(1 for r in records if r["source"] == src) for src in sources}

        weighted_results = {}
        for b in self.blocker_types:
            prev_info = prevalence.get(b, {})
            by_src = prev_info.get("by_source", {})

            # Rate-based weighting: sum of (weight * intra_source_rate)
            weighted_rate = 0.0
            weighted_points = 0.0

            for src, s_info in by_src.items():
                w = self.source_weights.get(src, 1.0)
                cnt = s_info.get("count", 0)
                den = s_info.get("denominator", 1)
                rate = cnt / den if den else 0.0

                weighted_rate += w * rate
                weighted_points += w * cnt

            weighted_results[b] = {
                "weighted_rate": round(weighted_rate, 4),
                "weighted_points": round(weighted_points, 1),
                "applied_weights": self.source_weights
            }

        return weighted_results

    def compute_elasticity(
        self,
        records: List[Dict[str, Any]],
        q_blocker: str = "What's the ONE thing most stopping you from buying it? Pick the biggest one.",
        q_elasticity: str = "If that were sorted out tomorrow, what would you honestly do?"
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Computes elasticity strictly from survey meta using explicit option mapping from config.
        Formula: (Buy it straight away + Buy it within a few weeks) / Total citing this blocker in survey.
        For blockers not asked in survey, elasticity is strictly None (null).
        """
        survey_records = [r for r in records if r.get("source") == "survey"]
        
        # Group elasticity answers by blocker_type using explicit survey mapping
        survey_by_blocker = defaultdict(list)
        for r in survey_records:
            sb = r.get("meta", {}).get(q_blocker)
            b_type = self.survey_mapping.get(sb)
            ans = r.get("meta", {}).get(q_elasticity)
            if b_type and ans:
                survey_by_blocker[b_type].append(ans)

        elasticity_results = {}
        for b in self.blocker_types:
            if b not in survey_by_blocker or b == "none":
                # Blocker not covered by survey -> must be null, never zero
                elasticity_results[b] = None
                continue

            answers = survey_by_blocker[b]
            denominator = len(answers)
            if denominator == 0:
                elasticity_results[b] = None
                continue

            # Elastic = would buy straight away or within a few weeks
            converted = sum(1 for a in answers if a in ["Buy it straight away", "Buy it within a few weeks"])
            rate = converted / denominator

            flag = "small_sample" if denominator < 5 else "adequate"

            elasticity_results[b] = {
                "fraction": f"{converted}/{denominator}",
                "rate": round(rate, 4),
                "percentage": round(rate * 100, 2),
                "numerator": converted,
                "denominator": denominator,
                "sample_flag": flag,
                "answer_breakdown": {ans: answers.count(ans) for ans in set(answers)}
            }

        return elasticity_results

    def score_opportunities(
        self,
        records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Builds ranked opportunities list sorted by source-weighted rate then elasticity,
        holding all dimensions separate and attaching real evidence records.
        """
        prevalence = self.compute_prevalence(records)
        weighted_scores = self.compute_weighted_scores(records, prevalence)
        elasticity = self.compute_elasticity(records)

        opportunities = []
        for b in self.blocker_types:
            if b == "none":
                continue # 'none' indicates no blocker

            prev = prevalence.get(b, {})
            w_score = weighted_scores.get(b, {})
            elast = elasticity.get(b)
            owner_info = self.ownership_cfg.get(b, {"owner": "neither", "rationale": "Unmapped blocker"})

            # Pull real evidence records for drill-down across all sources
            matching_records = [r for r in records if r.get("blocker_type") == b]
            evidence_samples = []
            for r in matching_records[:8]:
                evidence_samples.append({
                    "record_id": r["record_id"],
                    "source": r["source"],
                    "text": r["text"],
                    "created_at": r.get("created_at"),
                    "motive": r.get("wishlist_motive"),
                    "journey_stage": r.get("journey_stage"),
                    "external_action": r.get("external_action"),
                    "category": r.get("blocker_category")
                })

            opportunities.append({
                "blocker_type": b,
                "prevalence": prev,
                "source_weighting": w_score,
                "elasticity": elast,
                "ownership": {
                    "owner": owner_info.get("owner", "neither"),
                    "rationale": owner_info.get("rationale", "")
                },
                "evidence_count": len(matching_records),
                "evidence_samples": evidence_samples
            })

        # Deterministic source-weighted ranking:
        # Primary sort: weighted_rate (desc)
        # Secondary sort: elasticity rate (desc; None treated as -1)
        opportunities.sort(
            key=lambda x: (
                x["source_weighting"]["weighted_rate"],
                x["elasticity"]["rate"] if x["elasticity"] is not None else -1
            ),
            reverse=True
        )

        # Assign rank numbers 1..N
        for rank_num, opp in enumerate(opportunities, 1):
            opp["rank"] = rank_num

        return opportunities
