import os
import time
import json
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
sample = [{"id": "item_1", "text": "Waiting for the Big Billion Days sale to buy this jacket."}]

for m in ["qwen/qwen3.8-27b", "openai/gpt-oss-120b"]:
    t0 = time.time()
    try:
        resp = client.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": f'Classify as JSON array with id and blocker_type (e.g. price_wait): {json.dumps(sample)}'}],
            temperature=0.0
        )
        dt = time.time() - t0
        print(f"Model {m}: {dt:.2f}s -> {resp.choices[0].message.content.strip()[:100]}")
    except Exception as e:
        print(f"Model {m} failed: {e}")
