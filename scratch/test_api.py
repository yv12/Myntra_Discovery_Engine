import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
for m in ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "groq/compound"]:
    try:
        resp = client.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": 'Respond strictly in JSON: {"status": "ok"}'}],
            temperature=0.0
        )
        print(f"{m}: SUCCESS -> {resp.choices[0].message.content.strip()}")
    except Exception as e:
        print(f"{m}: FAILED -> {e}")
