"""
Stage 4 Counting Module for Discovery Engine.
Pure Python frequency and co-occurrence aggregation with denominators and source breakdown.
No LLM, no pandas. Every number is auditable by reading plain code.
"""

from collections import Counter
from typing import Dict, Any, List

def compute_dimension_frequencies(
    records: List[Dict[str, Any]],
    dimensions: List[str],
    allowed_values: Dict[str, List[str]]
) -> Dict[str, Any]:
    """
    Computes tag frequency per dimension, overall and broken down by source,
    with explicit counts, denominators, and percentages.
    """
    total_records = len(records)
    source_counts = Counter(r["source"] for r in records)

    dim_frequencies = {}

    for dim in dimensions:
        dim_frequencies[dim] = {
            "dimension": dim,
            "denominator": total_records,
            "tags": {}
        }
        
        # Count overall and by source
        overall_counts = Counter(r.get(dim) for r in records)
        source_tag_counts = {
            src: Counter(r.get(dim) for r in records if r["source"] == src)
            for src in source_counts
        }

        # Include all known allowed tags (even if 0 count)
        all_tags = sorted(list(set(allowed_values.get(dim, []) + list(overall_counts.keys()))))

        for tag in all_tags:
            cnt = overall_counts.get(tag, 0)
            tag_data = {
                "tag": tag,
                "overall": {
                    "count": cnt,
                    "denominator": total_records,
                    "rate": round(cnt / total_records, 4) if total_records else 0,
                    "percentage": round((cnt / total_records) * 100, 2) if total_records else 0
                },
                "by_source": {}
            }

            for src, src_total in source_counts.items():
                s_cnt = source_tag_counts[src].get(tag, 0)
                tag_data["by_source"][src] = {
                    "count": s_cnt,
                    "denominator": src_total,
                    "rate": round(s_cnt / src_total, 4) if src_total else 0,
                    "percentage": round((s_cnt / src_total) * 100, 2) if src_total else 0
                }

            dim_frequencies[dim]["tags"][tag] = tag_data

    return dim_frequencies


def compute_co_occurrences(
    records: List[Dict[str, Any]],
    dim1: str,
    dim2: str
) -> Dict[str, Any]:
    """
    Computes 2D co-occurrence pairs between two dimensions with denominators and source breakdowns.
    """
    total_records = len(records)
    source_counts = Counter(r["source"] for r in records)

    pair_counts = Counter((r.get(dim1), r.get(dim2)) for r in records)
    source_pair_counts = {
        src: Counter((r.get(dim1), r.get(dim2)) for r in records if r["source"] == src)
        for src in source_counts
    }

    pairs_list = []
    for (val1, val2), count in pair_counts.most_common():
        by_src = {}
        for src, src_total in source_counts.items():
            s_cnt = source_pair_counts[src].get((val1, val2), 0)
            by_src[src] = {
                "count": s_cnt,
                "denominator": src_total,
                "percentage": round((s_cnt / src_total) * 100, 2) if src_total else 0
            }

        pairs_list.append({
            dim1: val1,
            dim2: val2,
            "overall": {
                "count": count,
                "denominator": total_records,
                "percentage": round((count / total_records) * 100, 2) if total_records else 0
            },
            "by_source": by_src
        })

    return {
        "dimensions": [dim1, dim2],
        "total_pairs_evaluated": total_records,
        "pairs": pairs_list
    }


def compute_category_totals(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes structural vs psychological vs both vs none totals with denominators and source breakdowns.
    """
    total_records = len(records)
    source_counts = Counter(r["source"] for r in records)

    cat_counts = Counter(r.get("blocker_category") for r in records)
    by_source = {
        src: Counter(r.get("blocker_category") for r in records if r["source"] == src)
        for src in source_counts
    }

    categories = ["structural", "psychological", "both", "none"]
    totals = {}

    for cat in categories:
        cnt = cat_counts.get(cat, 0)
        totals[cat] = {
            "category": cat,
            "overall": {
                "count": cnt,
                "denominator": total_records,
                "percentage": round((cnt / total_records) * 100, 2) if total_records else 0
            },
            "by_source": {
                src: {
                    "count": by_source[src].get(cat, 0),
                    "denominator": source_counts[src],
                    "percentage": round((by_source[src].get(cat, 0) / source_counts[src]) * 100, 2) if source_counts[src] else 0
                }
                for src in source_counts
            }
        }

    return totals
