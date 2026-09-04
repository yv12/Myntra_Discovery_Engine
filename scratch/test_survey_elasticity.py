import json
from collections import defaultdict

records = [json.loads(line) for line in open('data/stages/stage_03_classified.jsonl', 'r', encoding='utf-8') if json.loads(line)['source'] == 'survey']

q_screen = "Do you have something in your wishlist you saved more than two weeks ago and still haven't bought?"
q_blocker = "What's the ONE thing most stopping you from buying it? Pick the biggest one."
q_elasticity = "If that were sorted out tomorrow, what would you honestly do?"

print(f"Total survey records: {len(records)}")

for screened_only in [True, False]:
    print(f"\n==========================================")
    print(f"CALCULATING ELASTICITY (Screened only: {screened_only})")
    print(f"==========================================")
    
    subset = [r for r in records if (r['meta'].get(q_screen) == 'Yes')] if screened_only else records
    print(f"Sample size: n={len(subset)}")

    # Group by classifier blocker_type and survey blocker option
    by_blocker = defaultdict(list)
    for r in subset:
        b_type = r.get("blocker_type")
        ans = r["meta"].get(q_elasticity)
        by_blocker[b_type].append(ans)

    for b, answers in sorted(by_blocker.items()):
        total_citing = len(answers)
        # Elastic = would buy straight away OR within a few weeks
        elastic_count = sum(1 for a in answers if a in ['Buy it straight away', 'Buy it within a few weeks'])
        rate = elastic_count / total_citing if total_citing else 0
        print(f"  - {b:20s}: {elastic_count}/{total_citing} ({rate:.1%}) -> breakdown: {dict([(a, answers.count(a)) for a in set(answers)])}")
