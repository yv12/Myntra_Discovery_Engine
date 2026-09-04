import json
from collections import defaultdict

records = [json.loads(line) for line in open('data/stages/stage_03_classified.jsonl', 'r', encoding='utf-8')]

source_totals = defaultdict(int)
for r in records:
    source_totals[r['source']] += 1

weights = {'interview': 4.0, 'survey': 3.0, 'reddit': 1.5, 'play_store': 1.0}

blocker_by_src = defaultdict(lambda: defaultdict(int))
for r in records:
    b = r.get('blocker_type')
    src = r.get('source')
    blocker_by_src[b][src] += 1

scored = []
for b, src_dict in blocker_by_src.items():
    if b == 'none': continue
    
    # Rate-weighted score
    rate_score = sum(
        weights[src] * (src_dict.get(src, 0) / source_totals[src])
        for src in weights
    )
    raw_cnt = sum(src_dict.values())
    scored.append((b, raw_cnt, rate_score, dict(src_dict)))

scored.sort(key=lambda x: x[2], reverse=True)

print(f"Total records: {len(records)}")
print(f"{'Blocker':20s} | Raw Count | Weighted Rate Score | Breakdown")
print("-" * 80)
for b, raw, s, bd in scored:
    print(f"{b:20s} | {raw:3d}/384   | {s:8.4f}             | {bd}")
