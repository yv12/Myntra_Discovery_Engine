import json
from collections import defaultdict

mapping = {
    "I'm waiting for the price to drop": "price_wait",
    "I'm not sure the quality will match the photos": "quality_doubt",
    "It's more than I want to spend right now": "budget_constraint",
    "I can't decide between this and something else": "decision_paralysis",
    "My size or the item isn't available": "size_unavailable",
    "I'm not sure it'll fit me": "fit_doubt"
}

records = [json.loads(line) for line in open('data/stages/stage_03_classified.jsonl', 'r', encoding='utf-8') if json.loads(line)['source'] == 'survey']

q_blocker = "What's the ONE thing most stopping you from buying it? Pick the biggest one."
q_elasticity = "If that were sorted out tomorrow, what would you honestly do?"

by_blocker = defaultdict(list)
for r in records:
    sb = r['meta'].get(q_blocker)
    b_enum = mapping.get(sb)
    if b_enum:
        ans = r['meta'].get(q_elasticity)
        by_blocker[b_enum].append(ans)

print("Computed Elasticities via explicit survey option mapping:")
for b, answers in sorted(by_blocker.items()):
    conv = sum(1 for a in answers if a in ['Buy it straight away', 'Buy it within a few weeks'])
    print(f"  - {b:20s}: {conv}/{len(answers)} ({conv/len(answers):.1%})")
