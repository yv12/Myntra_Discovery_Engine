import json
import time
import sys
sys.path.insert(0, ".")
from groq import Groq
from src.classify import DiscoveryClassifier

c = DiscoveryClassifier(model="openai/gpt-oss-120b")
with open("data/stages/stage_02_filtered.jsonl", "r", encoding="utf-8") as f:
    items = [json.loads(f.readline()) for _ in range(5)]

print(f"Loaded 5 items.")
t0 = time.time()
prompt = c._build_prompt([{"id": f"item_{i}", "text": it["text"]} for i, it in enumerate(items)])
print("Prompt length:", len(prompt))
print("Calling Groq with openai/gpt-oss-120b...")
try:
    resp = c.client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    print("Success in", time.time() - t0, "seconds!")
    print(resp.choices[0].message.content[:300])
except Exception as e:
    print("Failed:", e)
